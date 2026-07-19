#!/usr/bin/env python3
"""Find code near SearchACGHero2 xrefs and list field LDR immediates (hero struct)."""
from __future__ import annotations

import re
import struct
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\P1-hero-offset-chain.md")

# new season scan
NEW = {"iID": 0x10, "sName": 0x18, "iCost": 0x60, "paint": 0xF8, "setNum": 0x114}


def loads(data):
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]
    out = []
    for i in range(e_phnum):
        o = e_phoff + i * e_phentsize
        t = struct.unpack_from("<I", data, o)[0]
        if t != 1:
            continue
        p_offset, p_vaddr, _, p_filesz, _, _ = struct.unpack_from("<QQQQQQ", data, o + 8)
        out.append((p_offset, p_vaddr, p_filesz))
    return out


def va_off(loads_, va):
    for o, v, s in loads_:
        if v <= va < v + s:
            return o + (va - v)
    return None


def xrefs_to(data, target_va, text_va=0x77BB0, text_off=0x77BB0, text_sz=0x94F28):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    blob = data[text_off : text_off + text_sz]
    last = {}
    xs = []
    for insn in md.disasm(blob, text_va):
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


def window(data, loads_, va, before=0x40, after=0x300):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    start = va - before
    off = va_off(loads_, start)
    blob = data[off : off + before + after]
    return list(md.disasm(blob, start))


def main():
    data = SO.read_bytes()
    L = loads(data)
    lines = ["# P1 Hero field offset evidence chain\n\n"]
    lines.append("## New season (scan)\n")
    for k, v in NEW.items():
        lines.append(f"- {k} = 0x{v:x}\n")

    # null-terminated SearchACGHero2
    targets = {
        "SearchACGHero2": data.find(b"SearchACGHero2\x00"),
        "SearchACGHero\x00": data.find(b"SearchACGHero\x00"),
        "OnRefreshHeroRet": data.find(b"OnRefreshHeroRet\x00"),
        "GetMatchPlayerId": data.find(b"GetMatchPlayerId\x00"),
        "ReqBuyHero": data.find(b"ReqBuyHero\x00"),
        "HextechAugmentsCtrl/StaticField": data.find(b"HextechAugmentsCtrl/StaticField"),
    }
    for name, foff in targets.items():
        if foff < 0:
            lines.append(f"\n## {name} ABSENT\n")
            continue
        # identity map LOAD
        va = foff
        xs = xrefs_to(data, va)
        lines.append(f"\n## {name} va=0x{va:x} xrefs={list(map(hex, xs))}\n")
        for xr in xs[:4]:
            insns = window(data, L, xr)
            imms = []
            lines.append(f"\n### @0x{xr:x}\n```\n")
            for insn in insns:
                mk = " <<<" if insn.address == xr else ""
                lines.append(f"{insn.address:08x}: {insn.mnemonic:8} {insn.op_str}{mk}\n")
                m = re.search(r"\[(x\d+|sp),\s*#?(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
                if m and insn.mnemonic.startswith(("ldr", "str", "ldur", "stur")):
                    imm = int(m.group(2), 0)
                    if 0x8 <= imm <= 0x200:
                        imms.append((insn.address, imm, insn.mnemonic, insn.op_str))
            lines.append("```\n")
            if imms:
                lines.append("field-like immediates:\n")
                for a, imm, mn, op in imms:
                    tag = ""
                    for k, v in NEW.items():
                        if v == imm:
                            tag = f"  == NEW.{k}"
                    lines.append(f"- 0x{a:x} {mn} #0x{imm:x}{tag}  `{op}`\n")

    # Summary: if SO already uses 0x10,0x18,0x60,0xf8 for hero path, field patch may be no-op
    lines.append(
        """
## Interpretation

If hero-read chains already use 0x10/0x18/0x60/0xf8 matching scan, **hero table
offsets did not change** and season break is more likely **method resolve / hook
target / other class layouts**.

Patch priority then:
1. Confirm OnRefreshHeroRet still resolves at runtime (log)
2. If not, retarget hook to HandleRefreshBuyHero (code patch, not just string)
3. Patch only LDR immediates that differ from scan on non-hero structures

"""
    )
    OUT.write_text("".join(lines), encoding="utf-8")
    print("wrote", OUT)


if __name__ == "__main__":
    main()
