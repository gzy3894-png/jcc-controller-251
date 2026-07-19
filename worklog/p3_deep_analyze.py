#!/usr/bin/env python3
"""
Deep analysis: for each feature symbol in original libJCC.so,
disassemble the surrounding function(s) and classify LDR/STR
immediates as stack vs object-field candidates.

Then load season offsets.h and mark MATCH / UNKNOWN / NEED_CHECK.

Output: worklog/DEEP-ANALYSIS.md
"""
from __future__ import annotations

import re
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OFFSETS_H = Path(r"D:\grok-cli\workspace\jcc-device-scan\out\from-phone-latest\jcc-scan\offsets.h")
if not OFFSETS_H.exists():
    OFFSETS_H = Path(r"D:\grok-cli\workspace\jcc-shell\data\season_offsets_full.h")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\DEEP-ANALYSIS.md")

TEXT_VA = 0x77BB0
TEXT_OFF = 0x77BB0
TEXT_SZ = 0x94F28

FEATURES = [
    ("商店刷新/牌库更新", "OnRefreshHeroRet", b"OnRefreshHeroRet\x00"),
    ("自动拿牌", "ReqBuyHero", b"ReqBuyHero\x00"),
    ("英雄搜索", "SearchACGHero", b"SearchACGHero\x00"),
    ("英雄搜索2", "SearchACGHero2", b"SearchACGHero2\x00"),
    ("下一局对手", "GetMatchPlayerId", b"GetMatchPlayerId\x00"),
    ("自己玩家", "GetMyPlayerModel", b"GetMyPlayerModel\x00"),
    ("自己ID", "get_MyPlayerId", b"get_MyPlayerId\x00"),
    ("玩家排名", "GetPlayerRankByID", b"GetPlayerRankByID\x00"),
    ("对局地图更新", "UpdateBattleMap", b"UpdateBattleMap\x00"),
    ("头像列表", "PlayerListPanel", b"PlayerListPanel\x00"),
    ("列表项", "PlayerListItem", b"PlayerListItem\x00"),
    ("海克斯", "HextechAugmentsCtrl", b"HextechAugmentsCtrl"),
    ("棋手单位", "ChessPlayerUnit", b"ChessPlayerUnit\x00"),
    ("站位推送串", "OPPONENT_BOARD", b"OPPONENT_BOARD:"),
    ("商店视图", "BuyHeroView", b"BuyHeroView\x00"),
    ("数据库", "DataBaseManager", b"DataBaseManager\x00"),
    ("玩家模型", "PlayerModel", b"PlayerModel\x00"),
    ("对战模型", "ChessBattleModel", b"ChessBattleModel\x00"),
    ("战斗单位", "ChessBattleUnit", b"ChessBattleUnit\x00"),  # may absent
    ("UnitData", "UnitData", b"UnitData\x00"),  # may absent
]


def parse_offsets_h(path: Path) -> dict[str, dict[str, int]]:
    """class -> {field: offset}"""
    text = path.read_text(encoding="utf-8", errors="ignore")
    classes: dict[str, dict[str, int]] = defaultdict(dict)
    cur = None
    for line in text.splitlines():
        m = re.match(r"enum jcc_off_(\w+)", line)
        if m:
            cur = m.group(1)
            continue
        if cur and line.strip().startswith("};"):
            cur = None
            continue
        if not cur:
            continue
        # JCC_UnitData_heroId = 20, /* Int32 0x14 */
        m = re.search(r"JCC_" + re.escape(cur) + r"_(\w+)\s*=\s*(\d+)", line)
        if m:
            classes[cur][m.group(1)] = int(m.group(2))
        m2 = re.search(r"/\*.*?(0x[0-9a-fA-F]+)", line)
        # also store hex from comment if present
    return classes


def xrefs_to(data: bytes, target_va: int) -> list[int]:
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    blob = data[TEXT_OFF : TEXT_OFF + TEXT_SZ]
    last = {}
    xs = []
    for insn in md.disasm(blob, TEXT_VA):
        if insn.mnemonic == "adrp":
            m = re.match(r"(x\d+),\s*#?(0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
            if m:
                last[m.group(1)] = int(m.group(2), 0)
        elif insn.mnemonic == "add":
            m = re.match(r"(x\d+),\s*(x\d+),\s*#?(0x[0-9a-fA-F]+|\d+)", insn.op_str)
            if m and m.group(2) in last:
                tgt = last[m.group(2)] + int(m.group(3), 0)
                if tgt == target_va:
                    xs.append(insn.address)
    return xs


def find_func_start(data: bytes, va: int, max_back=0x400) -> int:
    """Heuristic: walk back for stp x29,x30,[sp,#-...] or paciasp-less prolog."""
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    start = max(TEXT_VA, va - max_back)
    off = start  # identity
    blob = data[off:va]
    insns = list(md.disasm(blob, start))
    last_good = start
    for insn in reversed(insns):
        if insn.mnemonic == "ret":
            # function after this ret
            last_good = insn.address + 4
            break
        if insn.mnemonic == "stp" and "x29" in insn.op_str and "sp" in insn.op_str:
            last_good = insn.address
            break
    return last_good


def disasm_func(data: bytes, start: int, max_size=0x800) -> list:
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    blob = data[start : start + max_size]
    insns = []
    for insn in md.disasm(blob, start):
        insns.append(insn)
        if insn.mnemonic == "ret" and len(insns) > 8:
            # allow a few more for tail
            if len(insns) > 40:
                break
    return insns


def collect_object_field_imms(insns) -> list[tuple[int, str, int, str]]:
    """Return (addr, mnemonic, imm, op) for [xN,#imm] where N is not sp and imm>=8."""
    out = []
    for insn in insns:
        if not any(insn.mnemonic.startswith(p) for p in ("ldr", "str", "ldur", "stur")):
            continue
        m = re.search(r"\[(x\d+|sp),\s*#(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
        if not m:
            continue
        base, imm_s = m.group(1), m.group(2)
        imm = int(imm_s, 0)
        if base == "sp":
            continue  # stack frame, not object field
        if imm < 8:
            continue
        out.append((insn.address, insn.mnemonic, imm, insn.op_str))
    return out


def match_imm_to_scan(imm: int, season: dict[str, dict[str, int]]) -> list[str]:
    hits = []
    for cls, fields in season.items():
        for fname, off in fields.items():
            if off == imm:
                hits.append(f"{cls}.{fname}")
    return hits


def main():
    data = SO.read_bytes()
    season = parse_offsets_h(OFFSETS_H)
    lines = []
    lines.append("# 深度分析：原 SO 功能读点 × 新赛季扫描\n\n")
    lines.append("## 前提（用户）\n")
    lines.append("- 点功能闪退 = 读错内存/结构变了\n")
    lines.append("- 只要把新数据放到原 SO 正确位置，功能逻辑已有\n")
    lines.append("- 不靠猜业务，靠对照偏移\n\n")

    lines.append(f"## 扫描 offsets.h 载入类数: {len(season)}\n")
    for c in (
        "TACG_Hero_Client",
        "UnitData",
        "ChessBattleUnit",
        "PlayerModel",
        "ChessBattleModel",
        "BuyHeroView",
        "DataBaseManager",
    ):
        if c in season:
            lines.append(f"- **{c}**: {len(season[c])} fields\n")

    lines.append("\n## 已确认：英雄表读路径 MATCH（不闪退源）\n")
    lines.append("函数 `0x7e4bc`：`#0x10 #0x18 #0xf0/#0xf8 #0x38 #0x60 #0x34` 与 TACG_Hero_Client 一致。\n")
    lines.append("**牌库静态读表不是闪退主因。**\n")

    lines.append("\n---\n\n## 分功能分析\n")

    summary_rows = []

    for cn_name, sym, needle in FEATURES:
        lines.append(f"\n### {cn_name} — `{sym}`\n")
        foff = data.find(needle)
        if foff < 0:
            # try without null
            foff = data.find(needle.rstrip(b"\x00"))
        if foff < 0:
            lines.append("- 字符串：**不在 SO 内** → 原逻辑可能不走这个名字\n")
            summary_rows.append((cn_name, sym, "ABSENT", "-", "无法字符串定位"))
            continue
        va = foff
        xs = xrefs_to(data, va)
        lines.append(f"- 字符串文件/VA: `0x{va:x}`\n")
        lines.append(f"- ADRP/ADD 引用数: **{len(xs)}** → {[hex(x) for x in xs[:8]]}\n")
        if not xs:
            lines.append("- **无 xref**：可能是日志拼接串，不是 resolve 参数\n")
            summary_rows.append((cn_name, sym, "NO_XREF", hex(va), "需其它定位"))
            continue

        # analyze first 3 xrefs as function windows
        all_obj_imms = []
        for xr in xs[:4]:
            fstart = find_func_start(data, xr)
            insns = disasm_func(data, fstart, 0xA00)
            imms = collect_object_field_imms(insns)
            lines.append(f"\n#### 代码点 `0x{xr:x}` 函数约 `0x{fstart:x}`… 对象字段 LDR/STR\n")
            if not imms:
                lines.append("- （窗口内无明确对象字段立即数，可能全在 callee）\n")
            # unique imms
            by = defaultdict(list)
            for a, mn, imm, op in imms:
                by[imm].append((a, mn, op))
                all_obj_imms.append(imm)
            for imm in sorted(by.keys()):
                hits = match_imm_to_scan(imm, season)
                if hits:
                    status = "MATCH_SCAN"
                    hit_s = ", ".join(hits[:6])
                else:
                    status = "NO_SCAN_HIT"
                    hit_s = "-"
                lines.append(
                    f"- `#0x{imm:x}` ×{len(by[imm])} → **{status}** ({hit_s})  e.g. `0x{by[imm][0][0]:x}`\n"
                )

        # feature-level conclusion
        matched = set()
        unknown = set()
        for imm in set(all_obj_imms):
            hits = match_imm_to_scan(imm, season)
            if hits:
                matched.add(imm)
            else:
                unknown.add(imm)
        if matched and not unknown:
            concl = "窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）"
        elif matched and unknown:
            concl = "部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**"
        elif not all_obj_imms:
            concl = "本窗口看不到字段读；逻辑在其它函数/寄存器传参"
        else:
            concl = "窗口内立即数均未直接命中扫描字段表 → 重点怀疑"
        lines.append(f"\n**本功能结论：** {concl}\n")
        summary_rows.append(
            (
                cn_name,
                sym,
                f"{len(xs)} xrefs",
                f"match_imm={len(matched)} unk={len(unknown)}",
                concl[:40],
            )
        )

    lines.append("\n---\n\n## 总表\n\n")
    lines.append("| 功能 | 符号 | 定位 | 字段立即数 | 结论 |\n")
    lines.append("|------|------|------|------------|------|\n")
    for row in summary_rows:
        lines.append(f"| {row[0]} | `{row[1]}` | {row[2]} | {row[3]} | {row[4]} |\n")

    lines.append(
        """
---

## 综合判断（给后续补丁用）

1. **闪退 = 读错字段/对象**，不是业务要重写。  
2. **英雄表路径已 MATCH**，不是主闪退源。  
3. 原 SO 用 **类名/方法名字符串 + DobbyHook**；方法名大多仍在 dump 里。  
4. 字段靠 **LDR 立即数**；补丁要改 **指令编码**，不能只改配置文件。  
5. 下一步工程：  
   - 对「unk 立即数」密集的功能函数，对照 scan 同类字段，找「旧 imm → 新 imm」；  
   - 优先：**GetMatchPlayerId 调用链、UpdateBattleMap、PlayerList*、Hextech、ReqBuyHero 之后的对象遍历**；  
   - 改完只动不匹配点，重签固定 keystore 出包。

6. **在未完成上述对照前，不声称全功能可用。**

"""
    )

    OUT.write_text("".join(lines), encoding="utf-8")
    print("wrote", OUT)
    print("features", len(FEATURES), "season_classes", len(season))


if __name__ == "__main__":
    main()
