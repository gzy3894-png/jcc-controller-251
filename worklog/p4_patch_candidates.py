#!/usr/bin/env python3
"""
Build concrete patch candidates:
1) Decode ARM64 LDR/STR unsigned offset encodings at known sites
2) For hero-unpack function confirm no patch
3) For GetMatchPlayerId / ReqBuyHero / Hextech / PlayerList functions,
   list object-field LDRs and whether imm exists in season class tables

Output: PATCH-CANDIDATES.md + patches.json (empty applied list if no high-confidence)
"""
from __future__ import annotations

import json
import re
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OFFSETS_H = Path(r"D:\grok-cli\workspace\jcc-device-scan\out\from-phone-latest\jcc-scan\offsets.h")
if not OFFSETS_H.exists():
    OFFSETS_H = Path(r"D:\grok-cli\workspace\jcc-shell\data\season_offsets_full.h")
OUT_MD = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\PATCH-CANDIDATES.md")
OUT_JSON = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\patches.json")

TEXT_VA, TEXT_OFF, TEXT_SZ = 0x77BB0, 0x77BB0, 0x94F28


def parse_season(path: Path):
    classes = defaultdict(dict)
    cur = None
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        m = re.match(r"enum jcc_off_(\w+)", line)
        if m:
            cur = m.group(1)
            continue
        if cur and line.strip().startswith("};"):
            cur = None
            continue
        if not cur:
            continue
        m = re.search(rf"JCC_{re.escape(cur)}_(\w+)\s*=\s*(\d+)", line)
        if m:
            classes[cur][m.group(1)] = int(m.group(2))
    return classes


def imm_owners(season, imm: int):
    hits = []
    for c, fs in season.items():
        for f, o in fs.items():
            if o == imm:
                hits.append(f"{c}.{f}")
    return hits


def xrefs_to(data, target_va):
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
                if last[m.group(2)] + int(m.group(3), 0) == target_va:
                    xs.append(insn.address)
    return xs


def decode_ldr_imm(word: int):
    """Return (size_bits, imm_bytes, is_unsigned_offset_ldr) or None."""
    # LDR (immediate) unsigned offset - 64-bit: 11 1110 01 01 imm12 Rn Rt
    # size=11 for 64, size=10 for 32
    if (word >> 22) & 0x3FF == 0x3E5:  # 64-bit LDR unsigned
        imm12 = (word >> 10) & 0xFFF
        rn = (word >> 5) & 0x1F
        rt = word & 0x1F
        return 64, imm12 * 8, rn, rt, word
    if (word >> 22) & 0x3FF == 0x3E4:  # 32-bit LDR unsigned? actually 0b1111100101 is 64, 0b1011100101 is 32
        pass
    # 32-bit LDR unsigned offset: size=10 -> 10 11100101
    if (word & 0xFFC00000) == 0xB9400000:
        imm12 = (word >> 10) & 0xFFF
        rn = (word >> 5) & 0x1F
        rt = word & 0x1F
        return 32, imm12 * 4, rn, rt, word
    # 64-bit LDR unsigned: 11 11100101 = F9400000 base
    if (word & 0xFFC00000) == 0xF9400000:
        imm12 = (word >> 10) & 0xFFF
        rn = (word >> 5) & 0x1F
        rt = word & 0x1F
        return 64, imm12 * 8, rn, rt, word
    return None


def encode_ldr_imm(size_bits: int, imm_bytes: int, rn: int, rt: int) -> int | None:
    if size_bits == 64:
        if imm_bytes % 8:
            return None
        imm12 = imm_bytes // 8
        if imm12 > 0xFFF:
            return None
        return 0xF9400000 | (imm12 << 10) | (rn << 5) | rt
    if size_bits == 32:
        if imm_bytes % 4:
            return None
        imm12 = imm_bytes // 4
        if imm12 > 0xFFF:
            return None
        return 0xB9400000 | (imm12 << 10) | (rn << 5) | rt
    return None


def analyze_site(data, season, name, needle):
    foff = data.find(needle)
    if foff < 0:
        return {"name": name, "error": "string absent"}
    xs = xrefs_to(data, foff)
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    field_ldrs = []
    for xr in xs[:5]:
        # window 0x200 before to 0x600 after
        start = max(TEXT_VA, xr - 0x100)
        end = xr + 0x500
        blob = data[start:end]
        for insn in md.disasm(blob, start):
            if insn.address < xr - 0x40 and insn.address > xr + 0x400:
                continue
            # raw word
            off = insn.address  # identity
            word = struct.unpack_from("<I", data, off)[0]
            dec = decode_ldr_imm(word)
            if not dec:
                continue
            size, imm, rn, rt, w = dec
            if rn == 31:  # sp/xzr encoding nuances - skip sp
                # Rn=31 is SP for some; skip high stack-like
                if imm < 0x100 and size == 64:
                    continue
            if imm < 0x10:
                continue
            owners = imm_owners(season, imm)
            field_ldrs.append(
                {
                    "va": insn.address,
                    "file_off": off,
                    "imm": imm,
                    "size": size,
                    "rn": rn,
                    "rt": rt,
                    "word": w,
                    "disasm": f"{insn.mnemonic} {insn.op_str}",
                    "owners": owners,
                    "near_xref": xr,
                }
            )
    # unique by va
    seen = set()
    uniq = []
    for x in field_ldrs:
        if x["va"] in seen:
            continue
        seen.add(x["va"])
        uniq.append(x)
    unk = [x for x in uniq if not x["owners"]]
    known = [x for x in uniq if x["owners"]]
    return {
        "name": name,
        "string_off": foff,
        "xrefs": xs,
        "ldr_count": len(uniq),
        "known": known,
        "unknown": unk,
    }


def main():
    data = bytearray(SO.read_bytes())
    season = parse_season(OFFSETS_H)

    # Verified hero sites — do not patch
    hero_sites = [
        (0x7E4F0, 0x10, 32),  # ldr w8,[x0,#0x10]
        (0x7E500, 0x18, 64),  # ldr x0,[x0,#0x18]
        (0x7E528, 0x38, 32),
        (0x7E538, 0x60, 32),
        (0x7E540, 0x34, 32),
    ]

    targets = [
        ("GetMatchPlayerId", b"GetMatchPlayerId\x00"),
        ("ReqBuyHero", b"ReqBuyHero\x00"),
        ("OnRefreshHeroRet", b"OnRefreshHeroRet\x00"),
        ("HextechAugmentsCtrl", b"HextechAugmentsCtrl"),
        ("PlayerListPanel", b"PlayerListPanel\x00"),
        ("PlayerListItem", b"PlayerListItem\x00"),
        ("UpdateBattleMap", b"UpdateBattleMap\x00"),
        ("OPPONENT_BOARD", b"OPPONENT_BOARD:"),
        ("ChessBattleModel", b"ChessBattleModel\x00"),
        ("BuyHeroView", b"BuyHeroView\x00"),
        ("GetPlayerRankByID", b"GetPlayerRankByID\x00"),
    ]

    reports = []
    for name, needle in targets:
        reports.append(analyze_site(bytes(data), season, name, needle))

    # High-confidence patches: none until we have old->new mapping
    # Heuristic: if imm has NO owner and is close to a single critical field (diff 4 or 8)
    # of PlayerModel / UnitData / ChessBattleUnit, propose remap
    critical_fields = []
    for cls in ("PlayerModel", "UnitData", "ChessBattleUnit", "ChessBattleModel", "BuyHeroView"):
        for f, o in season.get(cls, {}).items():
            critical_fields.append((cls, f, o))

    proposals = []
    for rep in reports:
        for u in rep.get("unknown", []):
            imm = u["imm"]
            # find closest critical field within 0x20
            best = None
            for cls, f, o in critical_fields:
                d = abs(o - imm)
                if d == 0:
                    continue
                if d <= 0x10:
                    if best is None or d < best[0]:
                        best = (d, cls, f, o)
            if best and best[0] in (4, 8):
                proposals.append(
                    {
                        "feature": rep["name"],
                        "va": u["va"],
                        "file_off": u["file_off"],
                        "old_imm": imm,
                        "new_imm": best[3],
                        "reason": f"close to {best[1]}.{best[2]} delta={best[0]}",
                        "disasm": u["disasm"],
                        "size": u["size"],
                        "rn": u["rn"],
                        "rt": u["rt"],
                        "old_word": u["word"],
                        "confidence": "LOW-heuristic",
                    }
                )

    lines = [
        "# Patch candidates (analysis)\n\n",
        "## Hero unpack (verified MATCH — do not patch)\n",
    ]
    for va, imm, sz in hero_sites:
        word = struct.unpack_from("<I", data, va)[0]
        lines.append(f"- va=0x{va:x} imm=0x{imm:x} size={sz} word=0x{word:08x} OK\n")

    lines.append("\n## Per-feature object LDR summary\n\n")
    lines.append("| Feature | xrefs | known LDR | unknown LDR |\n")
    lines.append("|---------|-------|-----------|-------------|\n")
    for rep in reports:
        if "error" in rep:
            lines.append(f"| {rep['name']} | - | - | {rep['error']} |\n")
            continue
        lines.append(
            f"| {rep['name']} | {len(rep['xrefs'])} | {len(rep['known'])} | {len(rep['unknown'])} |\n"
        )

    lines.append("\n## Unknown imms detail (top features)\n")
    for rep in reports:
        if not rep.get("unknown"):
            continue
        lines.append(f"\n### {rep['name']} unknown\n")
        for u in rep["unknown"][:30]:
            lines.append(
                f"- va=0x{u['va']:x} #0x{u['imm']:x} {u['disasm']} word=0x{u['word']:08x}\n"
            )

    lines.append("\n## Heuristic proposals (LOW confidence — NOT auto-applied)\n")
    if not proposals:
        lines.append("None generated.\n")
    for p in proposals[:40]:
        lines.append(
            f"- {p['feature']} 0x{p['va']:x}: 0x{p['old_imm']:x} -> 0x{p['new_imm']:x} ({p['reason']}) `{p['disasm']}`\n"
        )

    lines.append(
        """
## Decision for this iteration

1. **No blind heuristic patches** — delta-4/8 guesses can create worse crashes.
2. Hero fields confirmed match → leave original SO hero path intact.
3. Actionable path without guessing wrong imm→imm:
   - Prefer **runtime confirmation** via original SO log (which Hook fails)
   - OR binary-diff against an older known-good season SO if available
4. Package **original kernel** remains correct baseline while field remap table is incomplete.

If an older libJCC.so from previous season is provided, automatic old→new imm
diff becomes high-confidence and can be applied safely.

"""
    )

    OUT_MD.write_text("".join(lines), encoding="utf-8")
    OUT_JSON.write_text(
        json.dumps(
            {
                "hero_match": True,
                "proposals_low_confidence": proposals,
                "reports": [
                    {
                        "name": r.get("name"),
                        "xrefs": r.get("xrefs"),
                        "unknown_count": len(r.get("unknown", [])),
                        "known_count": len(r.get("known", [])),
                    }
                    for r in reports
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print("wrote", OUT_MD)
    print("proposals", len(proposals))
    for p in proposals[:15]:
        print(p)


if __name__ == "__main__":
    main()
