# PATCH APPLIED

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
- Strings at `0x4e5c0` / `0x4e5d1` (rodata zero pad)
- Patched instructions at `0x7d8a4..0x7d8b0`
- Hero field offsets **not modified** (already match season scan)
- PlayerModel money/hp/LastEnemyId **not modified** (match at use-site)

## Output
`D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so` size=1149112
