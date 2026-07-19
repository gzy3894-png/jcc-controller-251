#!/usr/bin/env python3
"""P1: SO method strings vs dump.cs presence."""
from pathlib import Path

METHODS = [
    "OnRefreshHeroRet",
    "ReqBuyHero",
    "SearchACGHero",
    "SearchACGHero2",
    "SearchACGHeroAndStar",
    "GetMyPlayerModel",
    "get_MyPlayerId",
    "GetMatchPlayerId",
    "GetPlayer",
    "GetPlayerRankByID",
    "UpdateBattleMap",
    "get_Instance",
    "IsUseBuyheroview_iPad",
    "CurBuyViewIsOpen",
    "GetBattleModel",
    "PlayerListPanel",
    "PlayerListItem",
    "PlayerHeadInfo",
    "HextechAugmentsCtrl",
    "ChessPlayerUnit",
    "ChessPlayerController",
    "BuyHeroView",
    "DataBaseManager",
    "PlayerModel",
    "ReqRefresh",
    "GetTinyModel",
    "UpdateNameAndMoney",
    "HandleRefreshBuyHero",
    "HandleBuyHero",
    "ChessBattleStage",
]

SO = Path(r"D:\grok-cli\workspace\jcc-controller-work\extract\assets\emu\libJCC.so")
DUMP = Path(r"D:\grok-cli\workspace\jcc-game-dump\il2cpp-out\dump.cs")
OUT = Path(r"D:\grok-cli\workspace\jcc-controller-251\worklog\P1-symbol-diff.md")

so = SO.read_bytes()
counts = {m: 0 for m in METHODS}
samples = {m: [] for m in METHODS}

with DUMP.open("r", encoding="utf-8", errors="ignore") as f:
    for i, line in enumerate(f, 1):
        for m in METHODS:
            if m not in line:
                continue
            counts[m] += 1
            if len(samples[m]) >= 3:
                continue
            if "(" in line or "IDMAP" in line or "class " in line:
                samples[m].append(f"L{i}: {line.strip()[:130]}")

lines = [
    "# P1 Symbol diff: original libJCC strings vs current dump.cs\n\n",
    "| Symbol | In SO? | dump hits | Notes |\n",
    "|--------|--------|-----------|-------|\n",
]
for m in METHODS:
    in_so = so.find(m.encode()) >= 0
    hits = counts[m]
    note = ""
    if in_so and hits == 0:
        note = "SO has string but dump has ZERO — critical rename?"
    elif in_so and hits > 0 and all("IDMAP" in s for s in samples[m]):
        note = "dump only IDMAP (no method body in dump?)"
    elif in_so and hits > 0:
        note = "present in dump"
    elif not in_so and hits > 0:
        note = "new season only (not in old SO)"
    else:
        note = "absent both"
    lines.append(f"| `{m}` | {in_so} | {hits} | {note} |\n")

lines.append("\n## Samples\n")
for m in METHODS:
    if not samples[m]:
        continue
    lines.append(f"\n### {m}\n")
    for s in samples[m]:
        lines.append(f"- {s}\n")

OUT.write_text("".join(lines), encoding="utf-8")
print("wrote", OUT)
for m in METHODS:
    print(f"{m}\tSO={so.find(m.encode())>=0}\tdump={counts[m]}")
