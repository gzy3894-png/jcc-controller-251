#!/usr/bin/env python3
"""
Find LDR/STR immediates in original libJCC near feature symbols.
Compare to new-season scan offsets for UnitData / ChessBattleUnit / etc.
Crash-on-click almost always = wrong field read (bad imm).
"""
from __future__ import annotations

import re
import struct
from collections import defaultdict
from pathlib import Path

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\P2-crash-offset-candidates.md")

# New season from live scan (offsets.h)
NEW = {
    # UnitData
    "UnitData.heroId": 0x14,
    "UnitData.playerId": 0x24,
    "UnitData.col": 0x30,
    "UnitData.row": 0x34,
    "UnitData.Level": 0x148,
    "UnitData.heroName": 0x120,
    "UnitData.heroHeadIcon": 0x140,
    # ChessBattleUnit
    "CBU.Data": 0x90,
    "CBU.battleData": 0x1C8,
    "CBU.screen_top": 0x1A4,
    "CBU.screen_head": 0x1B0,
    "CBU.Show_Star": 0x1E0,
    # PlayerModel (partial interesting)
    "PlayerModel.hexAugmentModel": 0x28,
    # ChessBattleModel
    "ChessBattleModel.playerModelDict": 0x38,
}

# Common OLD wrong offsets we might see if season shifted (unknown old - collect all)
INTEREST_IMMS = set(NEW.values()) | {
    0x0C,
    0x10,
    0x14,
    0x18,
    0x1C,
    0x20,
    0x24,
    0x28,
    0x2C,
    0x30,
    0x34,
    0x38,
    0x3C,
    0x40,
    0x48,
    0x50,
    0x58,
    0x60,
    0x68,
    0x70,
    0x78,
    0x80,
    0x88,
    0x90,
    0x98,
    0xA0,
    0xB0,
    0xC0,
    0xD0,
    0xE0,
    0xF0,
    0xF8,
    0x100,
    0x108,
    0x110,
    0x114,
    0x118,
    0x120,
    0x128,
    0x130,
    0x140,
    0x148,
    0x150,
    0x160,
    0x180,
    0x1A0,
    0x1A4,
    0x1B0,
    0x1C0,
    0x1C8,
    0x1D0,
    0x1E0,
    0x200,
}


def xrefs_to(data: bytes, target_va: int, text_va=0x77BB0, text_off=0x77BB0, text_sz=0x94F28):
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


def disasm_range(data, va, size=0x400):
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    # identity map first load
    blob = data[va : va + size]
    return list(md.disasm(blob, va))


def collect_imms(insns):
    out = []
    for insn in insns:
        if not insn.mnemonic.startswith(("ldr", "str", "ldur", "stur")):
            continue
        m = re.search(r"\[(x\d+|sp),\s*#(0x[0-9a-fA-F]+|\d+)\]", insn.op_str)
        if not m:
            continue
        imm = int(m.group(2), 0)
        if imm in INTEREST_IMMS:
            out.append((insn.address, insn.mnemonic, imm, insn.op_str))
    return out


def main():
    data = SO.read_bytes()
    lines = [
        "# P2 Crash-offset candidates\n\n",
        "User report: original features crash on click → wrong memory/layout.\n",
        "Hero table path already MATCHES season; crash likely other structs.\n\n",
        "## New season reference offsets\n",
    ]
    for k, v in NEW.items():
        lines.append(f"- `{k}` = 0x{v:x}\n")

    # Feature string → likely code
    features = [
        ("GetMatchPlayerId", b"GetMatchPlayerId\x00"),  # next opponent
        ("ReqBuyHero", b"ReqBuyHero\x00"),
        ("OnRefreshHeroRet", b"OnRefreshHeroRet\x00"),
        ("PlayerListPanel", b"PlayerListPanel\x00"),
        ("PlayerListItem", b"PlayerListItem\x00"),
        ("HextechAugmentsCtrl/StaticField", b"HextechAugmentsCtrl/StaticField"),
        ("UpdateBattleMap", b"UpdateBattleMap\x00"),
        ("OPPONENT_BOARD:", b"OPPONENT_BOARD:"),
        ("ChessPlayerUnit", b"ChessPlayerUnit\x00"),
        ("get_MyPlayerId", b"get_MyPlayerId\x00"),
        ("GetPlayerRankByID", b"GetPlayerRankByID\x00"),
        ("RoundSelectPlayerUnit", b"RoundSelectPlayerUnit\x00"),
    ]

    all_patch_sites = []  # (file_off_of_insn, imm, feature, disasm)

    for fname, needle in features:
        foff = data.find(needle)
        lines.append(f"\n## Feature `{fname}`\n")
        if foff < 0:
            lines.append("string ABSENT\n")
            continue
        va = foff  # identity map
        xs = xrefs_to(data, va)
        lines.append(f"- string va=0x{va:x} xrefs={list(map(hex, xs))}\n")
        for xr in xs[:6]:
            # window around xref: function may be large; scan 0x800 after and 0x100 before
            start = max(0x77BB0, xr - 0x80)
            # find rough function start: previous ret within 0x200
            insns = disasm_range(data, start, 0x600)
            imms = collect_imms(insns)
            lines.append(f"\n### window near 0x{xr:x} (imm sample)\n")
            # unique imms
            by_imm = defaultdict(list)
            for a, mn, imm, op in imms:
                by_imm[imm].append((a, mn, op))
            for imm in sorted(by_imm.keys()):
                sites = by_imm[imm]
                match = [k for k, v in NEW.items() if v == imm]
                tag = f" NEW={match}" if match else ""
                lines.append(f"- #0x{imm:x} x{len(sites)}{tag} e.g. 0x{sites[0][0]:x} {sites[0][1]} {sites[0][2]}\n")
                for a, mn, op in sites[:3]:
                    # ARM64 LDR unsigned offset encoding for 32/64-bit: need careful patch later
                    all_patch_sites.append(
                        {"va": a, "imm": imm, "feature": fname, "op": op, "mn": mn}
                    )

    # Cross: imms used near ChessPlayerUnit that are NOT in NEW set as known-good
    lines.append("\n## Notes for patching\n")
    lines.append(
        """
ARM64 LDR (64-bit) imm12 is scaled by 8; LDR (32-bit) scaled by 4.
Patching requires re-encoding the instruction, not just writing a byte.

Next step: for each crash feature, pick the LDR that reads object fields
(not stack #0x10/#0x20) and verify against scan; re-encode if mismatch.

Hero path @0x7e4bc already verified MATCH — do not touch.

"""
    )

    # dump raw list json-ish
    lines.append(f"\n## Total candidate sites: {len(all_patch_sites)}\n")

    OUT.write_text("".join(lines), encoding="utf-8")
    print("wrote", OUT, "sites", len(all_patch_sites))


if __name__ == "__main__":
    main()
