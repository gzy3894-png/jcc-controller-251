#!/usr/bin/env python3
"""Reverse original libJCC.so: strings, ELF sections, ARM64 offset immediates near key xrefs."""
from __future__ import annotations

import json
import re
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog")
OUT.mkdir(parents=True, exist_ok=True)

# New season (from live scan) — for comparison
NEW = {
    "TACG_Hero_iID": 0x10,
    "TACG_Hero_sName": 0x18,
    "TACG_Hero_iCost": 0x60,
    "TACG_Hero_sHeroPaintSmall": 0xF8,
    "TACG_Hero_iSetNum": 0x114,
    "UnitData_heroId": 0x14,
    "UnitData_playerId": 0x24,
    "UnitData_col": 0x30,
    "UnitData_row": 0x34,
    "UnitData_Level": 0x148,
    "CBU_Data": 0x90,
    "CBU_screen_head": 0x1B0,
    "CBU_Show_Star": 0x1E0,
}


def parse_elf(data: bytes):
    assert data[:4] == b"\x7fELF"
    ei_class = data[4]  # 2 = 64
    assert ei_class == 2
    e_phoff = struct.unpack_from("<Q", data, 32)[0]
    e_shoff = struct.unpack_from("<Q", data, 40)[0]
    e_phentsize = struct.unpack_from("<H", data, 54)[0]
    e_phnum = struct.unpack_from("<H", data, 56)[0]
    e_shentsize = struct.unpack_from("<H", data, 58)[0]
    e_shnum = struct.unpack_from("<H", data, 60)[0]
    e_shstrndx = struct.unpack_from("<H", data, 62)[0]

    # program headers LOAD
    loads = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags = struct.unpack_from("<II", data, off)
        p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from(
            "<QQQQQQ", data, off + 8
        )
        if p_type == 1:  # PT_LOAD
            loads.append(
                {
                    "offset": p_offset,
                    "vaddr": p_vaddr,
                    "filesz": p_filesz,
                    "flags": p_flags,
                }
            )

    # sections
    shstr_off = e_shoff + e_shstrndx * e_shentsize
    shstr_sh_offset = struct.unpack_from("<Q", data, shstr_off + 24)[0]
    sections = []
    for i in range(e_shnum):
        off = e_shoff + i * e_shentsize
        sh_name = struct.unpack_from("<I", data, off)[0]
        sh_type = struct.unpack_from("<I", data, off + 4)[0]
        sh_flags = struct.unpack_from("<Q", data, off + 8)[0]
        sh_addr = struct.unpack_from("<Q", data, off + 16)[0]
        sh_offset = struct.unpack_from("<Q", data, off + 24)[0]
        sh_size = struct.unpack_from("<Q", data, off + 32)[0]
        name = data[shstr_sh_offset + sh_name :].split(b"\x00", 1)[0].decode("ascii", "ignore")
        sections.append(
            {
                "name": name,
                "type": sh_type,
                "flags": sh_flags,
                "addr": sh_addr,
                "offset": sh_offset,
                "size": sh_size,
            }
        )
    return loads, sections


def file_off_to_va(loads, file_off: int) -> int | None:
    for l in loads:
        if l["offset"] <= file_off < l["offset"] + l["filesz"]:
            return l["vaddr"] + (file_off - l["offset"])
    return None


def va_to_file_off(loads, va: int) -> int | None:
    for l in loads:
        if l["vaddr"] <= va < l["vaddr"] + l["filesz"]:
            return l["offset"] + (va - l["vaddr"])
    return None


def extract_strings(data: bytes, min_len=4):
    out = []
    for m in re.finditer(rb"[\x20-\x7e]{%d,120}" % min_len, data):
        out.append((m.start(), m.group().decode("ascii")))
    return out


def main():
    data = SO.read_bytes()
    loads, sections = parse_elf(data)
    report = []
    report.append(f"# libJCC.so reverse notes\nsize={len(data)}\n")
    report.append("## LOAD segments\n")
    for l in loads:
        report.append(
            f"- off=0x{l['offset']:x} va=0x{l['vaddr']:x} sz=0x{l['filesz']:x} flags={l['flags']}\n"
        )
    report.append("\n## Sections (exec/rodata)\n")
    text_secs = []
    for s in sections:
        if s["size"] == 0:
            continue
        if s["name"] in (".text", ".rodata", ".data", ".data.rel.ro") or (
            s["flags"] & 4
        ):  # SHF_EXECINSTR sometimes
            report.append(
                f"- {s['name']} va=0x{s['addr']:x} off=0x{s['offset']:x} sz=0x{s['size']:x}\n"
            )
        if s["name"] == ".text" or (s["flags"] & 4 and s["name"].startswith(".text")):
            text_secs.append(s)

    strings = extract_strings(data)
    interest = []
    key_sub = (
        "SearchACG",
        "OnRefresh",
        "ReqBuy",
        "BuyHero",
        "PlayerModel",
        "GetMyPlayer",
        "UnitData",
        "ChessBattle",
        "DataBase",
        "OPPONENT",
        "Hook",
        "hero",
        "Hero",
        "il2cpp",
        "field",
        "Field",
        "offset",
        "UpdateBattle",
        "GetMatch",
        "PlayerList",
        "Hextech",
        "Augment",
        "Shop",
        "牌库",
        "get_Instance",
        "HandleRefresh",
        "HandleBuy",
    )
    report.append("\n## Key strings (file offset + VA)\n")
    for off, s in strings:
        if any(k in s for k in key_sub):
            va = file_off_to_va(loads, off)
            interest.append((off, va, s))
            va_s = f"0x{va:x}" if va is not None else "None"
            report.append(f"- 0x{off:x} va={va_s}  `{s}`\n")

    # ADRP+ADD string xrefs: scan .text for adrp and add imm that form page+off to string VA
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = True

    # Build map va -> string
    str_by_va = {}
    for off, va, s in interest:
        if va is not None:
            str_by_va[va] = (off, s)

    # Disassemble all executable sections
    exec_secs = [s for s in sections if (s["flags"] & 4) or s["name"] == ".text"]
    if not exec_secs:
        # fallback: RX load segment
        for l in loads:
            if l["flags"] & 1:  # PF_X
                exec_secs.append(
                    {
                        "name": "LOAD_X",
                        "addr": l["vaddr"],
                        "offset": l["offset"],
                        "size": l["filesz"],
                    }
                )

    report.append("\n## String xrefs (approx ADRP/ADD or LDR literal)\n")
    xrefs = defaultdict(list)  # string -> list of code VAs

    for sec in exec_secs:
        blob = data[sec["offset"] : sec["offset"] + sec["size"]]
        base = sec["addr"]
        # ADRP Rd, page
        # ADD Rd, Rn, #imm
        last_adrp = {}  # reg -> page
        for insn in md.disasm(blob, base):
            if insn.mnemonic == "adrp":
                # op_str like "x0, #0x123000"
                m = re.match(r"(x\d+),\s*#?(0x[0-9a-fA-F]+|-?\d+)", insn.op_str)
                if m:
                    reg = m.group(1)
                    page = int(m.group(2), 0)
                    last_adrp[reg] = (page, insn.address)
            elif insn.mnemonic == "add":
                m = re.match(
                    r"(x\d+),\s*(x\d+),\s*#?(0x[0-9a-fA-F]+|\d+)", insn.op_str
                )
                if m:
                    rd, rn, imm = m.group(1), m.group(2), int(m.group(3), 0)
                    if rn in last_adrp:
                        page, adrp_addr = last_adrp[rn]
                        target = page + imm
                        # match string start (or within 0..len)
                        for sva, (soff, s) in str_by_va.items():
                            if sva <= target < sva + len(s) + 1:
                                xrefs[s].append(insn.address)
                                report.append(
                                    f"- `{s}` xref @ 0x{insn.address:x} (adrp 0x{adrp_addr:x})\n"
                                )
            elif insn.mnemonic in ("ldr", "adr"):
                # optional
                pass

    # Scan code for LDR Xt, [Xn, #imm] where imm is common field offsets
    report.append("\n## LDR/STR field-offset immediates (common values)\n")
    common_off = {
        0x10,
        0x14,
        0x18,
        0x20,
        0x24,
        0x28,
        0x30,
        0x34,
        0x38,
        0x60,
        0x90,
        0xF8,
        0x108,
        0x114,
        0x148,
        0x1A4,
        0x1B0,
        0x1C8,
        0x1E0,
    }
    imm_hits = defaultdict(list)
    for sec in exec_secs:
        blob = data[sec["offset"] : sec["offset"] + sec["size"]]
        base = sec["addr"]
        for insn in md.disasm(blob, base):
            if insn.mnemonic not in ("ldr", "str", "ldur", "stur", "ldrb", "strb", "ldrsw"):
                continue
            # [xN, #imm]
            m = re.search(r"\[(x\d+|sp),\s*#?(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
            if not m:
                continue
            imm = int(m.group(2), 0)
            if imm in common_off:
                imm_hits[imm].append(insn.address)

    for imm in sorted(imm_hits.keys()):
        addrs = imm_hits[imm]
        report.append(f"- imm 0x{imm:x} count={len(addrs)} e.g. {[hex(a) for a in addrs[:8]]}\n")

    # Method name strings that matter for hooks
    report.append("\n## Hook/API method strings present in SO\n")
    methods = [
        "OnRefreshHeroRet",
        "HandleRefreshBuyHero",
        "HandleBuyHero",
        "ReqBuyHero",
        "SearchACGHero",
        "SearchACGHero2",
        "GetMyPlayerModel",
        "get_MyPlayerId",
        "GetMatchPlayerId",
        "UpdateBattleMap",
        "BuyHeroView",
        "DataBaseManager",
        "PlayerModel",
        "ChessBattleUnit",
        "UnitData",
        "PlayerListPanel",
        "get_Instance",
    ]
    for name in methods:
        b = name.encode()
        c = data.count(b)
        pos = data.find(b)
        report.append(f"- `{name}` count={c} first={hex(pos) if pos>=0 else 'ABSENT'}\n")

    report.append("\n## New season offsets (scan reference)\n")
    for k, v in NEW.items():
        report.append(f"- {k} = 0x{v:x}\n")

    report.append(
        """
## Preliminary conclusion

1. Method/class names exist as C-strings for il2cpp resolve + hooks.
2. Field names like iID/iCost are NOT in the binary as strings → field access is
   almost certainly hardcoded LDR/STR immediates (or computed).
3. Next step: for each key string xref, disassemble surrounding function and list
   all field immediates; map to scan offsets; prepare binary patch table.

"""
    )

    outp = OUT / "REV-libJCC.md"
    outp.write_text("".join(report), encoding="utf-8")
    print("wrote", outp)
    print("xrefs", len(xrefs), "imm kinds", len(imm_hits))

    # dump denser json for patching later
    (OUT / "rev_summary.json").write_text(
        json.dumps(
            {
                "methods_present": {
                    m: data.find(m.encode()) for m in methods
                },
                "imm_hit_counts": {hex(k): len(v) for k, v in imm_hits.items()},
                "string_xrefs": {k: v[:20] for k, v in xrefs.items()},
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    import re

    main()
