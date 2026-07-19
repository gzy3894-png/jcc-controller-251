# SAFE LOAD PATCH — disable resource-breaking hooks

src: `D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.patched.so`
out: `D:\grok-cli\workspace\jcc-controller-251\dist\libJCC.safe.so`

## Symptom
匹配成功后加载页提示「资源损坏」。
原 SO 对 LoadMap/LoadBody/AssetBundle/Attack/Loading 等装了 DobbyHook，
现赛季资源管线被改坏。

## NOP count: 20
- `0x78b6c`
- `0x78bbc`
- `0x78c04`
- `0x78c4c`
- `0x78c94`
- `0x7a784`
- `0x7a82c`
- `0x7b514`
- `0x7b564`
- `0x7b610`
- `0x7b660`
- `0x7b6a8`
- `0x7b754`
- `0x7b7a4`
- `0x7b850`
- `0x7b99c`
- `0x7ba64`
- `0x7bb14`
- `0x7c904`
- `0x95308`

## KEEP
- `0x7d8d8` KEEP
- `0x7d9ec` KEEP

## Keep means
- HandleRefreshBuyHero: shop refresh / card pool drive
- UpdateNameAndMoney: economy display
