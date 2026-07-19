#!/usr/bin/env python3
"""
Deep reverse: for each DobbyHook install (bl 0x10cb90),
recover (class, method, argc) from prior resolve + replacement function VA (adr x1),
disassemble replacement body, collect object-field LDR/STR immediates,
map to season offsets.h.

Output: worklog/HOOK-BODY-ANALYSIS.md + worklog/hook_field_matrix.json
"""
from __future__ import annotations

import json
import re
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
# use patched only for strings if needed - prefer original for hook sites
if Path(r"D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so").exists():
    # original hooks before NOP - use ORIGINAL for body analysis
    pass
OFFSETS = Path(r"D:\grok-cli\workspace\jcc-device-scan\out\from-phone-latest\jcc-scan\offsets.h")
if not OFFSETS.exists():
    OFFSETS = Path(r"D:\grok-cli\workspace\jcc-shell\data\season_offsets_full.h")
DUMP = Path(r"D:\grok-cli\workspace\jcc-game-dump\il2cpp-out\dump.cs")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\HOOK-BODY-ANALYSIS.md")
OUTJ = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\hook_field_matrix.json")

DOBBY = 0x10CB90
RESOLVE = 0x77E94


def load_season(path: Path):
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
    # reverse: offset -> list of Class.field
    by_off = defaultdict(list)
    for c, fs in classes.items():
        for f, o in fs.items():
            by_off[o].append(f"{c}.{f}")
    return classes, by_off


def read_cstr(data, va):
    if va is None or va < 0 or va >= len(data):
        return ""
    return data[va:].split(b"\x00", 1)[0].decode("utf-8", "replace")


def decode_adrp(word, pc):
    rd = word & 0x1F
    immlo = (word >> 29) & 3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return rd, (pc & ~0xFFF) + (imm << 12)


def decode_add(word):
    return word & 0x1F, (word >> 5) & 0x1F, (word >> 10) & 0xFFF


def decode_adr(word, pc):
    # ADR Rd, label — imm is signed
    rd = word & 0x1F
    immlo = (word >> 29) & 3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return rd, pc + imm


def parse_resolve_before(data, md, bl_pc):
    """Find class/method/argc for resolve call just before hook."""
    class_va = meth_va = None
    argc = None
    # look back 0x60
    last_page = {}
    for a in range(bl_pc - 0x80, bl_pc, 4):
        w = struct.unpack_from("<I", data, a)[0]
        # adrp
        if ((w >> 24) & 0x9F) == 0x90:
            rd, page = decode_adrp(w, a)
            last_page[rd] = page
        # add imm
        if (w & 0xFF800000) == 0x91000000:
            rd, rn, imm = decode_add(w)
            if rn in last_page:
                va = last_page[rn] + imm
                if rd == 1:
                    class_va = va
                elif rd == 2:
                    meth_va = va
        # mov w3
        if (w & 0xFF80001F) == 0x52800003 or (w & 0xFFE0001F) == 0x52800003:
            # MOVZ W3, #imm
            imm16 = (w >> 5) & 0xFFFF
            hw = (w >> 21) & 3
            argc = imm16 << (hw * 16)
        if w == 0x2A1F03E3:  # mov w3, wzr
            argc = 0
        # bl resolve
        if a < bl_pc and (w & 0xFC000000) == 0x94000000:
            imm26 = w & 0x3FFFFFF
            if imm26 & 0x2000000:
                imm26 -= 0x4000000
            target = a + imm26 * 4
            if target == RESOLVE:
                # reset class/meth for this resolve - already tracked
                pass
    return read_cstr(data, class_va), read_cstr(data, meth_va), argc


def find_replacement(data, md, hook_bl):
    """adr x1, #handler before DobbyHook"""
    for a in range(hook_bl - 0x30, hook_bl, 4):
        w = struct.unpack_from("<I", data, a)[0]
        # ADR: 0x10000000 pattern
        if (w & 0x9F000000) == 0x10000000:
            rd, target = decode_adr(w, a)
            if rd == 1 and 0x78000 <= target < 0x110000:
                return target
    return None


def disasm_func(data, start, limit=0x600):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    blob = data[start : start + limit]
    out = []
    for insn in md.disasm(blob, start):
        out.append(insn)
        if insn.mnemonic == "ret" and len(out) > 15:
            break
    return out


def object_field_imms(insns):
    imms = []
    for insn in insns:
        if not insn.mnemonic.startswith(("ldr", "str", "ldur", "stur")):
            continue
        if "[sp" in insn.op_str:
            continue
        m = re.search(r"\[x(\d+),\s*#(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
        if not m:
            continue
        imm = int(m.group(2), 0)
        if 0x10 <= imm <= 0x400:
            imms.append((insn.address, imm, insn.mnemonic, insn.op_str))
    return imms


def idmap_ok(dump: str, cls: str, meth: str) -> bool:
    if not meth:
        return False
    for line in dump.splitlines():
        if "IDMAP" not in line:
            continue
        if meth in line and (not cls or cls in line):
            return True
    return meth in dump


def main():
    data = SO.read_bytes()
    season, by_off = load_season(OFFSETS)
    dump = DUMP.read_text(encoding="utf-8", errors="ignore")
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)

    hooks = []
    for insn in md.disasm(data[0x77BB0:0x10F000], 0x77BB0):
        if insn.mnemonic != "bl":
            continue
        m = re.match(r"#?(0x[0-9a-fA-F]+)", insn.op_str)
        if not m or int(m.group(1), 0) != DOBBY:
            continue
        hooks.append(insn.address)

    rows = []
    lines = [
        "# Hook body deep analysis (original libJCC.so)\n\n",
        f"DobbyHook sites (bl 0x{DOBBY:x}): **{len(hooks)}**\n\n",
    ]

    for hpc in hooks:
        # find resolve within previous 0x50
        cls, meth, argc = "?", "?", None
        for a in range(hpc - 0x50, hpc, 4):
            w = struct.unpack_from("<I", data, a)[0]
            if (w & 0xFC000000) != 0x94000000:
                continue
            imm26 = w & 0x3FFFFFF
            if imm26 & 0x2000000:
                imm26 -= 0x4000000
            if a + imm26 * 4 != RESOLVE:
                continue
            cls, meth, argc = parse_resolve_before(data, md, a + 4)
            # better parse at resolve site
            cls, meth, argc = parse_resolve_at(data, a)
            break

        repl = find_replacement(data, md, hpc)
        imms = []
        if repl:
            imms = object_field_imms(disasm_func(data, repl))

        matched = []
        unknown = []
        for va, imm, mn, op in imms:
            owners = by_off.get(imm, [])
            if owners:
                matched.append({"va": va, "imm": imm, "owners": owners[:5], "op": op})
            else:
                unknown.append({"va": va, "imm": imm, "op": op})

        ok_idmap = idmap_ok(dump, cls if cls != "?" else "", meth if meth != "?" else "")
        rows.append(
            {
                "hook_pc": hpc,
                "class": cls,
                "method": meth,
                "argc": argc,
                "replacement": repl,
                "idmap_ok": ok_idmap,
                "matched_fields": matched,
                "unknown_fields": unknown,
            }
        )

        lines.append(f"## Hook @ `0x{hpc:x}`\n")
        lines.append(f"- resolve: `{cls}.{meth}` argc={argc} idmap={'OK' if ok_idmap else 'NO'}\n")
        lines.append(f"- replacement: `{hex(repl) if repl else 'NONE'}`\n")
        lines.append(f"- field LDR matched: **{len(matched)}** unknown: **{len(unknown)}**\n")
        if matched:
            lines.append("- matched:\n")
            for x in matched[:15]:
                lines.append(
                    f"  - `0x{x['va']:x}` #0x{x['imm']:x} → {', '.join(x['owners'][:3])}\n"
                )
        if unknown:
            lines.append("- unknown (not in scanned 17 classes):\n")
            for x in unknown[:12]:
                lines.append(f"  - `0x{x['va']:x}` #0x{x['imm']:x} `{x['op']}`\n")
        lines.append("\n")

    # summary table
    lines.insert(
        4,
        "## Summary table\n\n| Hook | Class.Method | IDMAP | repl | match | unk |\n|------|--------------|-------|------|-------|-----|\n",
    )
    table = []
    for r in rows:
        table.append(
            f"| 0x{r['hook_pc']:x} | `{r['class']}.{r['method']}` | "
            f"{'Y' if r['idmap_ok'] else 'N'} | "
            f"{hex(r['replacement']) if r['replacement'] else '-'} | "
            f"{len(r['matched_fields'])} | {len(r['unknown_fields'])} |\n"
        )
    lines.insert(5, "".join(table) + "\n")

    # overall certainty
    idmap_y = sum(1 for r in rows if r["idmap_ok"])
    with_repl = sum(1 for r in rows if r["replacement"])
    lines.append("## Certainty for product path\n\n")
    lines.append(f"- Hooks with IDMAP OK: **{idmap_y}/{len(rows)}**\n")
    lines.append(f"- Hooks with found replacement body: **{with_repl}/{len(rows)}**\n")
    lines.append(
        """
### Path A — Patch original SO (restore original handlers)
- Feasible for symbol retarget (done: OnRefresh→HandleRefresh)
- Field LDR in handlers mostly match scan when known; unknown often SO-internal or unscanned classes
- **Must NOT** hook LoadMap/LoadBody/Asset (causes 资源损坏) — disable those installs (2.5.5 approach)
- Combined: keep non-load hooks + correct symbols + matched fields → high confidence for non-load features

### Path B — Hybrid reader (no Dobby)
- Invoke same methods with same offsets; feed original UI protocol
- 100% control of crash surface (no asset hooks)
- Requires implementing each GET using verified reads only

### Recommendation for 100% confirmed product
1. Use Path B for stability (no resource hooks) OR Path A with load hooks permanently disabled
2. For each UI GET, implement only with fields listed as MATCH in this matrix
3. Refuse to claim feature until that feature's resolve IDMAP=Y and field chain MATCH
4. Ship only after offline checklist green for: 牌库, 下一局对手, 钱/血, 商店开关协议, 无加载崩溃

"""
    )

    OUT.write_text("".join(lines), encoding="utf-8")
    OUTJ.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    print("hooks", len(rows), "->", OUT)


def parse_resolve_before(data, md, bl_pc):
    return parse_resolve_at(data, bl_pc)


def parse_resolve_at(data, resolve_bl_pc):
    """resolve_bl_pc points to bl instruction of resolve."""
    class_va = meth_va = None
    argc = None
    last_page = {}
    for a in range(resolve_bl_pc - 0x40, resolve_bl_pc, 4):
        w = struct.unpack_from("<I", data, a)[0]
        if ((w >> 24) & 0x9F) == 0x90:
            rd, page = decode_adrp(w, a)
            last_page[rd] = page
        if (w & 0xFF800000) == 0x91000000:
            rd, rn, imm = decode_add(w)
            if rn in last_page:
                va = last_page[rn] + imm
                if rd == 1:
                    class_va = va
                elif rd == 2:
                    meth_va = va
        # movz w3
        if (w & 0xFF80001F) == 0x52800003:
            imm16 = (w >> 5) & 0xFFFF
            argc = imm16
        if w == 0x2A1F03E3:
            argc = 0
    return (
        read_cstr(data, class_va) if class_va else "?",
        read_cstr(data, meth_va) if meth_va else "?",
        argc,
    )


if __name__ == "__main__":
    main()
