# Hook body deep analysis (original libJCC.so)

DobbyHook sites (bl 0x10cb90): **22**

## Hook @ `0x78b6c`
- resolve: `ChessPlayerUnit.LoadBodyImpl` argc=2 idmap=OK
## Summary table

| Hook | Class.Method | IDMAP | repl | match | unk |
|------|--------------|-------|------|-------|-----|
| 0x78b6c | `ChessPlayerUnit.LoadBodyImpl` | Y | 0x78cd8 | 4 | 0 |
| 0x78bbc | `ChessPlayerUnit.LoadBodyImpl` | Y | 0x78d9c | 4 | 0 |
| 0x78c04 | `RoundSelectPlayerUnit.LoadBody` | Y | 0x78e84 | 3 | 0 |
| 0x78c4c | `RoundSelectPlayerUnit.RoundSelectSwitchModel` | Y | 0x78ef8 | 3 | 0 |
| 0x78c94 | `ChessPlayerUnit.SwitchModel` | Y | 0x78f3c | 3 | 0 |
| 0x7a784 | `BattleMapManager.Active` | Y | 0x7a478 | 4 | 0 |
| 0x7a82c | `PlayerModel.UpdateBattleMap` | Y | 0x7a238 | 6 | 0 |
| 0x7b514 | `TAC_GameTinyData.ReadFrom` | Y | 0x7a950 | 8 | 1 |
| 0x7b564 | `TAC_GameTinyData.WriteTo` | Y | 0x7abb4 | 4 | 0 |
| 0x7b610 | `TinyAttackData.GetRealDamageId` | Y | 0x7ac64 | 4 | 0 |
| 0x7b660 | `TinyAttackData.InitAttackData` | Y | 0x7ac70 | 4 | 0 |
| 0x7b6a8 | `ChessBattleLogicPlayer.SetAttack` | Y | 0x7ad78 | 2 | 0 |
| 0x7b754 | `BaseLogicMovement.LoadAttackConfig` | Y | 0x7ad84 | 2 | 0 |
| 0x7b7a4 | `BaseLogicMovement.GetDamageId` | Y | 0x7aee4 | 8 | 0 |
| 0x7b850 | `ChessViewAttackSet.InitAttacks` | Y | 0x7aef0 | 8 | 0 |
| 0x7b99c | `ChessViewAttackSet.SendAttack` | Y | 0x7b008 | 8 | 0 |
| 0x7ba64 | `DataBaseManager.SearchACGAttackEffect` | Y | 0x7b3ec | 2 | 0 |
| 0x7bb14 | `BattleMapTriggerManager.ExecuteGameStart` | Y | 0x7bb34 | 1 | 0 |
| 0x7c904 | `BaseLogicMovement.GetEliminateId` | Y | 0x7c774 | 4 | 0 |
| 0x7d8d8 | `BuyHeroView.OnRefreshHeroRet` | Y | 0x7da28 | 6 | 0 |
| 0x7d9ec | `HeroRoot.UpdateNameAndMoney` | Y | 0x7dbbc | 7 | 0 |
| 0x95308 | `ChessLoadingPlayerInfoItem.InitData` | Y | 0x94904 | 5 | 0 |

- replacement: `0x78cd8`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x78d20` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x78d4c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78d54` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78d5c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock

## Hook @ `0x78bbc`
- resolve: `ChessPlayerUnit.LoadBodyImpl` argc=4 idmap=OK
- replacement: `0x78d9c`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x78df0` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x78e28` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78e2c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78e34` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock

## Hook @ `0x78c04`
- resolve: `RoundSelectPlayerUnit.LoadBody` argc=0 idmap=OK
- replacement: `0x78e84`
- field LDR matched: **3** unknown: **0**
- matched:
  - `0x78ec4` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78ec8` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x78ed4` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock

## Hook @ `0x78c4c`
- resolve: `RoundSelectPlayerUnit.RoundSelectSwitchModel` argc=1 idmap=OK
- replacement: `0x78ef8`
- field LDR matched: **3** unknown: **0**
- matched:
  - `0x78f7c` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x79010` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x79044` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x78c94`
- resolve: `ChessPlayerUnit.SwitchModel` argc=1 idmap=OK
- replacement: `0x78f3c`
- field LDR matched: **3** unknown: **0**
- matched:
  - `0x78f7c` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x79010` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x79044` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7a784`
- resolve: `BattleMapManager.Active` argc=4 idmap=OK
- replacement: `0x7a478`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x7a588` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7a684` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7a68c` #0x80 → TACG_Hero_Client.iProperty3, DataBaseManager.mapACG_ArkItems_Client_FastSearch, ChessPlayerController.m_observedPlayerIds
  - `0x7a70c` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7a82c`
- resolve: `PlayerModel.UpdateBattleMap` argc=1 idmap=OK
- replacement: `0x7a238`
- field LDR matched: **6** unknown: **0**
- matched:
  - `0x7a258` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7a2b4` #0x1b0 → TACG_Hero_Client.iSummonCondition, BuyHeroView.EquipStoreViewS5_Dragon_Ref, ChessBattleStage.loadRoundSelect
  - `0x7a2c8` #0x200 → BuyHeroView._refreshButtonBtn, ChessBattleModel.onTurnStartNotify, ChessBattleLogicPlayer.m_usedDropboxDict
  - `0x7a318` #0x1b0 → TACG_Hero_Client.iSummonCondition, BuyHeroView.EquipStoreViewS5_Dragon_Ref, ChessBattleStage.loadRoundSelect
  - `0x7a33c` #0x200 → BuyHeroView._refreshButtonBtn, ChessBattleModel.onTurnStartNotify, ChessBattleLogicPlayer.m_usedDropboxDict
  - `0x7a3a8` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b514`
- resolve: `TAC_GameTinyData.ReadFrom` argc=1 idmap=OK
- replacement: `0x7a950`
- field LDR matched: **8** unknown: **1**
- matched:
  - `0x7a970` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7a990` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7a994` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7a99c` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict
  - `0x7a9c0` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7a9c8` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7aadc` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict
  - `0x7aae4` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
- unknown (not in scanned 17 classes):
  - `0x7a9ac` #0x3c `w8, [x0, #0x3c]`

## Hook @ `0x7b564`
- resolve: `TAC_GameTinyData.WriteTo` argc=1 idmap=OK
- replacement: `0x7abb4`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x7abdc` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7ac0c` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict
  - `0x7ac20` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict
  - `0x7ac30` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict

## Hook @ `0x7b610`
- resolve: `TinyAttackData.GetRealDamageId` argc=2 idmap=OK
- replacement: `0x7ac64`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x7ac8c` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7acd8` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7ad4c` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7ad50` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b660`
- resolve: `TinyAttackData.InitAttackData` argc=6 idmap=OK
- replacement: `0x7ac70`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x7ac8c` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7acd8` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7ad4c` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7ad50` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b6a8`
- resolve: `ChessBattleLogicPlayer.SetAttack` argc=5 idmap=OK
- replacement: `0x7ad78`
- field LDR matched: **2** unknown: **0**
- matched:
  - `0x7adac` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7aeb8` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b754`
- resolve: `BaseLogicMovement.LoadAttackConfig` argc=2 idmap=OK
- replacement: `0x7ad84`
- field LDR matched: **2** unknown: **0**
- matched:
  - `0x7adac` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7aeb8` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b7a4`
- resolve: `BaseLogicMovement.GetDamageId` argc=0 idmap=OK
- replacement: `0x7aee4`
- field LDR matched: **8** unknown: **0**
- matched:
  - `0x7b034` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7b1d0` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b254` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b278` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b284` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b37c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b388` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b3b4` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b850`
- resolve: `ChessViewAttackSet.InitAttacks` argc=6 idmap=OK
- replacement: `0x7aef0`
- field LDR matched: **8** unknown: **0**
- matched:
  - `0x7b034` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7b1d0` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b254` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b278` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b284` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b37c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b388` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b3b4` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7b99c`
- resolve: `ChessViewAttackSet.SendAttack` argc=5 idmap=OK
- replacement: `0x7b008`
- field LDR matched: **8** unknown: **0**
- matched:
  - `0x7b034` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7b1d0` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b254` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7b278` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b284` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b37c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b388` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7b3b4` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7ba64`
- resolve: `DataBaseManager.SearchACGAttackEffect` argc=1 idmap=OK
- replacement: `0x7b3ec`
- field LDR matched: **2** unknown: **0**
- matched:
  - `0x7b4d8` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7b594` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7bb14`
- resolve: `BattleMapTriggerManager.ExecuteGameStart` argc=3 idmap=OK
- replacement: `0x7bb34`
- field LDR matched: **1** unknown: **0**
- matched:
  - `0x7bb78` #0x40 → TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet

## Hook @ `0x7c904`
- resolve: `BaseLogicMovement.GetEliminateId` argc=0 idmap=OK
- replacement: `0x7c774`
- field LDR matched: **4** unknown: **0**
- matched:
  - `0x7c790` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7c7e0` #0x30 → TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo
  - `0x7c7e8` #0x38 → TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict
  - `0x7c888` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x7d8d8`
- resolve: `BuyHeroView.OnRefreshHeroRet` argc=1 idmap=OK
- replacement: `0x7da28`
- field LDR matched: **6** unknown: **0**
- matched:
  - `0x7db0c` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7db2c` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7db44` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7db64` #0x18 → TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans
  - `0x7db7c` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock
  - `0x7db98` #0x20 → TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock

## Hook @ `0x7d9ec`
- resolve: `HeroRoot.UpdateNameAndMoney` argc=1 idmap=OK
- replacement: `0x7dbbc`
- field LDR matched: **7** unknown: **0**
- matched:
  - `0x7dbe0` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr
  - `0x7dc0c` #0x1a8 → TACG_Hero_Client.sNameKey, BuyHeroView.EquipStoreViewS5_Daul_TFT_Ref, ChessBattleStage.m_abRequestList
  - `0x7dc14` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7dc1c` #0x14 → RoundSelectPlayerUnit.m_defaultRoundSelectId
  - `0x7dcf8` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x7dd44` #0x68 → TACG_Hero_Client.sPrefabShowID, DataBaseManager.m_cacheBuildSetListArr, ChessBattleModel.hideBodyHeroList
  - `0x7dde8` #0x28 → TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr

## Hook @ `0x95308`
- resolve: `ChessLoadingPlayerInfoItem.InitData` argc=1 idmap=OK
- replacement: `0x94904`
- field LDR matched: **5** unknown: **0**
- matched:
  - `0x94944` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x94968` #0x60 → TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId
  - `0x94978` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x9497c` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable
  - `0x949d0` #0x10 → TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable

## Certainty for product path

- Hooks with IDMAP OK: **22/22**
- Hooks with found replacement body: **22/22**

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

