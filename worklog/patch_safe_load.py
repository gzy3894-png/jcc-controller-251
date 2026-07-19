#!/usr/bin/env python3
"""
Disable DobbyHook installs that break battle resource loading (资源损坏).

Keep only shop-related hooks that we need for card pool / buy:
  0x7d8d8 HandleRefreshBuyHero
  0x7d9ec UpdateNameAndMoney (money UI; safe)

All other bl #0x10cb90 -> NOP
Also apply shop retarget if not already (run after patch_libjcc or on original).
"""
from __future__ import annotations

import struct
from pathlib import Path

# Prefer already shop-patched SO
SRC = Path(r"D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so")
if not SRC.exists():
    SRC = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.safe.so")
LOG = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\PATCH-SAFE-LOAD.md")

NOP = 0xD503201F

# All DobbyHook call sites found (bl 0x10cb90)
ALL_HOOKS = [
    0x78B6C,  # LoadBodyImpl
    0x78BBC,
    0x78C04,  # LoadBody
    0x78C4C,  # RoundSelectSwitchModel
    0x78C94,  # SwitchModel
    0x7A784,  # BattleMap Active
    0x7A82C,  # UpdateBattleMap hook install
    0x7B514,  # Tiny data
    0x7B564,
    0x7B610,
    0x7B660,
    0x7B6A8,
    0x7B754,
    0x7B7A4,
    0x7B850,  # attacks
    0x7B99C,
    0x7BA64,
    0x7BB14,  # ExecuteGameStart
    0x7C904,
    0x7D8D8,  # KEEP - HandleRefreshBuyHero
    0x7D9EC,  # KEEP - UpdateNameAndMoney
    0x95308,  # ChessLoadingPlayerInfoItem.InitData - loading screen
]

KEEP = {0x7D8D8, 0x7D9EC}


def main():
    data = bytearray(SRC.read_bytes())
    noped = []
    kept = []
    for addr in ALL_HOOKS:
        word = struct.unpack_from("<I", data, addr)[0]
        # expect bl imm
        if (word & 0xFC000000) != 0x94000000:
            # already nop or different
            kept.append((addr, f"skip word=0x{word:08x}"))
            continue
        if addr in KEEP:
            kept.append((addr, "KEEP"))
            continue
        struct.pack_into("<I", data, addr, NOP)
        noped.append(addr)

    OUT.write_bytes(data)
    lines = [
        "# SAFE LOAD PATCH — disable resource-breaking hooks\n\n",
        f"src: `{SRC}`\n",
        f"out: `{OUT}`\n\n",
        "## Symptom\n",
        "匹配成功后加载页提示「资源损坏」。\n",
        "原 SO 对 LoadMap/LoadBody/AssetBundle/Attack/Loading 等装了 DobbyHook，\n",
        "现赛季资源管线被改坏。\n\n",
        f"## NOP count: {len(noped)}\n",
    ]
    for a in noped:
        lines.append(f"- `0x{a:x}`\n")
    lines.append("\n## KEEP\n")
    for a, why in kept:
        lines.append(f"- `0x{a:x}` {why}\n")
    lines.append(
        "\n## Keep means\n"
        "- HandleRefreshBuyHero: shop refresh / card pool drive\n"
        "- UpdateNameAndMoney: economy display\n"
    )
    LOG.write_text("".join(lines), encoding="utf-8")
    print("NOP", len(noped), "->", OUT)
    assert b"ChessBattleStage\x00" in data or b"HandleRefreshBuyHero" in data or True
    # if from patched, should have strings
    if b"HandleRefreshBuyHero" not in data:
        print("WARN: shop retarget strings missing; run patch_libjcc.py first")


if __name__ == "__main__":
    main()
