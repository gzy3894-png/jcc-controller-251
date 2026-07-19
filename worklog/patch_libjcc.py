#!/usr/bin/env python3
"""Patch original libJCC.so: retarget shop refresh hook to HandleRefreshBuyHero."""
from __future__ import annotations

import struct
from pathlib import Path

SRC = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
if not SRC.exists():
    SRC = Path(r"D:\grok-cli\workspace\jcc-controller-251\libJCC-original.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so")
LOG = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\PATCH-APPLIED.md")

STR_BASE = 0x4E5C0
ADR_CLASS, ADD_CLASS = 0x7D8A4, 0x7D8A8
ADR_METH, ADD_METH = 0x7D8AC, 0x7D8B0


def encode_adrp(rd: int, pc: int, target: int) -> int:
    pc_page = pc & ~0xFFF
    tgt_page = target & ~0xFFF
    imm = (tgt_page - pc_page) >> 12
    imm &= (1 << 21) - 1
    immlo = imm & 0x3
    immhi = (imm >> 2) & 0x7FFFF
    return 0x90000000 | (immlo << 29) | (immhi << 5) | rd


def encode_add_imm64(rd: int, rn: int, imm12: int) -> int:
    if not 0 <= imm12 <= 0xFFF:
        raise ValueError(imm12)
    return 0x91000000 | (imm12 << 10) | (rn << 5) | rd


def decode_adrp(word: int, pc: int) -> tuple[int, int]:
    rd = word & 0x1F
    immlo = (word >> 29) & 3
    immhi = (word >> 5) & 0x7FFFF
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return rd, (pc & ~0xFFF) + (imm << 12)


def main():
    raw = SRC.read_bytes()
    data = bytearray(raw)

    # verify known original site
    assert struct.unpack_from("<I", data, ADR_CLASS)[0] == 0xB0FFFE41
    assert struct.unpack_from("<I", data, ADD_CLASS)[0] == 0x91305821
    assert struct.unpack_from("<I", data, ADR_METH)[0] == 0xF0FFFE42
    assert struct.unpack_from("<I", data, ADD_METH)[0] == 0x913DC042

    s_class = b"ChessBattleStage\x00"
    s_meth = b"HandleRefreshBuyHero\x00"
    p_class = STR_BASE
    p_meth = STR_BASE + len(s_class)
    end = p_meth + len(s_meth)
    if any(data[STR_BASE:end]):
        raise SystemExit("string hole not empty")

    data[p_class : p_class + len(s_class)] = s_class
    data[p_meth : p_meth + len(s_meth)] = s_meth

    nw = [
        encode_adrp(1, ADR_CLASS, p_class),
        encode_add_imm64(1, 1, p_class & 0xFFF),
        encode_adrp(2, ADR_METH, p_meth),
        encode_add_imm64(2, 2, p_meth & 0xFFF),
    ]
    # verify encode
    _, pg = decode_adrp(nw[0], ADR_CLASS)
    assert pg + (p_class & 0xFFF) == p_class
    _, pg = decode_adrp(nw[2], ADR_METH)
    assert pg + (p_meth & 0xFFF) == p_meth

    struct.pack_into("<I", data, ADR_CLASS, nw[0])
    struct.pack_into("<I", data, ADD_CLASS, nw[1])
    struct.pack_into("<I", data, ADR_METH, nw[2])
    struct.pack_into("<I", data, ADD_METH, nw[3])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_bytes(data)

    log = f"""# PATCH APPLIED

## Change
Shop refresh hook retarget:

| | Before | After |
|--|--------|-------|
| Class | BuyHeroView | **ChessBattleStage** |
| Method | OnRefreshHeroRet | **HandleRefreshBuyHero** |
| argc | 1 | 1 (unchanged) |

## Why
Current dump: `BuyHeroView` has **no** `OnRefreshHeroRet` method body (only leftover IDMAP).
`ChessBattleStage.HandleRefreshBuyHero(Object)` exists with argc=1.

## Technical
- Strings at `0x{p_class:x}` / `0x{p_meth:x}` (rodata zero pad)
- Patched instructions at `0x7d8a4..0x7d8b0`
- Hero field offsets **not modified** (already match season scan)
- PlayerModel money/hp/LastEnemyId **not modified** (match at use-site)

## Output
`{OUT}` size={len(data)}
"""
    LOG.write_text(log, encoding="utf-8")
    print("OK", OUT, len(data))
    print(log)


if __name__ == "__main__":
    main()
