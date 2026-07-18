#!/usr/bin/env python3
"""Disassemble around key string xrefs; collect LDR/STR immediates per function region."""
from __future__ import annotations

import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\REV-funcs.md")

# From rev_summary / REV-libJCC (VA == file off for first LOAD)
SITES = {
    "OnRefreshHeroRet_str_use": 0x7D7F0,  # 514224 if wrong will fix by search
    "SearchACGHero2_use_a": 0x7E1BC,  # placeholder - resolve by string scan
}


def parse_loads(data):
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]
    loads = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type = struct.unpack_from("<I", data, off)[0]
        p_offset, p_vaddr, _, p_filesz, _, _ = struct.unpack_from("<QQQQQQ", data, off + 8)
        if p_type == 1:
            loads.append((p_offset, p_vaddr, p_filesz))
    return loads


def va_to_off(loads, va):
    for o, v, s in loads:
        if v <= va < v + s:
            return o + (va - v)
    return None


def find_string_va(data, loads, s: bytes):
    off = data.find(s)
    if off < 0:
        return None, None
    for o, v, sz in loads:
        if o <= off < o + sz:
            return off, v + (off - o)
    return off, off  # identity map common


def find_xrefs_to_va(data, loads, target_va, text_va=0x77BB0, text_off=0x77BB0, text_sz=0x94F28):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    blob = data[text_off : text_off + text_sz]
    last_adrp = {}
    xrefs = []
    for insn in md.disasm(blob, text_va):
        if insn.mnemonic == "adrp":
            m = re.match(r"(x\d+),\s*#?(0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
            if m:
                last_adrp[m.group(1)] = int(m.group(2), 0)
        elif insn.mnemonic == "add":
            m = re.match(r"(x\d+),\s*(x\d+),\s*#?(0x[0-9a-fA-F]+|\d+)", insn.op_str)
            if m and m.group(2) in last_adrp:
                tgt = last_adrp[m.group(2)] + int(m.group(3), 0)
                if tgt == target_va:
                    xrefs.append(insn.address)
    return xrefs


def disasm_window(data, loads, va, before=64, after=256):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    start = va - before
    off = va_to_off(loads, start)
    if off is None:
        return []
    size = before + after
    blob = data[off : off + size]
    return list(md.disasm(blob, start))


def imms_in_insns(insns):
    imms = []
    for insn in insns:
        if insn.mnemonic not in ("ldr", "str", "ldur", "stur", "ldrb", "strb", "ldrsw", "ldrh", "strh"):
            continue
        m = re.search(r"\[(x\d+|sp),\s*#?(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
        if m:
            imms.append((insn.address, insn.mnemonic, int(m.group(2), 0), insn.op_str))
    return imms


def main():
    data = SO.read_bytes()
    loads = parse_loads(data)
    lines = ["# Function windows around key strings\n"]

    targets = [
        b"OnRefreshHeroRet\x00",
        b"OnRefreshHeroRet",
        b"SearchACGHero2\x00",
        b"SearchACGHero2",
        b"ReqBuyHero\x00",
        b"GetMyPlayerModel\x00",
        b"GetMatchPlayerId\x00",
        b"PlayerListPanel\x00",
        b"OPPONENT_BOARD:\x00",
        b"HextechAugmentsCtrl/StaticField\x00",
        b"BuyHeroView\x00",
        b"UpdateBattleMap\x00",
        b"IsUseBuyheroview_iPad\x00",
    ]

    for ts in targets:
        off, va = find_string_va(data, loads, ts)
        s = ts.split(b"\x00")[0].decode()
        lines.append(f"\n## string `{s}`\n")
        if va is None:
            lines.append("ABSENT\n")
            continue
        lines.append(f"- file_off=0x{off:x} va=0x{va:x}\n")
        xrefs = find_xrefs_to_va(data, loads, va)
        lines.append(f"- xrefs ({len(xrefs)}): {[hex(x) for x in xrefs[:12]]}\n")
        for xr in xrefs[:5]:
            lines.append(f"\n### disasm around xref 0x{xr:x}\n```\n")
            insns = disasm_window(data, loads, xr, 32, 200)
            for insn in insns:
                mark = " <<<" if insn.address == xr else ""
                lines.append(f"0x{insn.address:x}:  {insn.mnemonic}\t{insn.op_str}{mark}\n")
            lines.append("```\n")
            imms = imms_in_insns(insns)
            if imms:
                lines.append("immediates:\n")
                for a, mn, imm, op in imms:
                    lines.append(f"- 0x{a:x} {mn} #0x{imm:x}  ({op})\n")

    # Also scan ALL ldr imm 0xf8 / 0x114 / 0x148 near SearchACGHero2 first xref
    lines.append("\n## Global: LDR #0xf8 / #0x114 / #0x60 near hero read (sample)\n")
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    text_off, text_va, text_sz = 0x77BB0, 0x77BB0, 0x94F28
    blob = data[text_off : text_off + text_sz]
    for insn in md.disasm(blob, text_va):
        if insn.mnemonic not in ("ldr", "ldur", "ldrsw"):
            continue
        m = re.search(r"#(0x[0-9a-fA-F]+|\d+)", insn.op_str)
        if not m:
            continue
        imm = int(m.group(1), 0)
        if imm in (0xF8, 0x114, 0x60, 0x148, 0x1B0, 0x1E0):
            # only first 40 of each
            pass
    # count already known; dump a few with context for 0xf8
    count = 0
    for insn in md.disasm(blob, text_va):
        if "0xf8" in insn.op_str or "#248" in insn.op_str:
            lines.append(f"- 0x{insn.address:x}: {insn.mnemonic} {insn.op_str}\n")
            count += 1
            if count >= 25:
                break

    OUT.write_text("".join(lines), encoding="utf-8")
    print("wrote", OUT, "chars", sum(len(x) for x in lines))


if __name__ == "__main__":
    main()
