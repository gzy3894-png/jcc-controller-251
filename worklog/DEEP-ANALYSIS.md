# 深度分析：原 SO 功能读点 × 新赛季扫描

## 前提（用户）
- 点功能闪退 = 读错内存/结构变了
- 只要把新数据放到原 SO 正确位置，功能逻辑已有
- 不靠猜业务，靠对照偏移

## 扫描 offsets.h 载入类数: 17
- **TACG_Hero_Client**: 77 fields
- **UnitData**: 110 fields
- **ChessBattleUnit**: 93 fields
- **PlayerModel**: 261 fields
- **ChessBattleModel**: 97 fields
- **BuyHeroView**: 45 fields
- **DataBaseManager**: 28 fields

## 已确认：英雄表读路径 MATCH（不闪退源）
函数 `0x7e4bc`：`#0x10 #0x18 #0xf0/#0xf8 #0x38 #0x60 #0x34` 与 TACG_Hero_Client 一致。
**牌库静态读表不是闪退主因。**

---

## 分功能分析

### 商店刷新/牌库更新 — `OnRefreshHeroRet`
- 字符串文件/VA: `0x48f70`
- ADRP/ADD 引用数: **1** → ['0x7d8b0']

#### 代码点 `0x7d8b0` 函数约 `0x7d88c`… 对象字段 LDR/STR
- `#0x850` ×3 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_pathCtrl)  e.g. `0x7d928`
- `#0x858` ×3 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_dirCtrl)  e.g. `0x7d938`

**本功能结论：** 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）

### 自动拿牌 — `ReqBuyHero`
- 字符串文件/VA: `0x4aa9b`
- ADRP/ADD 引用数: **1** → ['0x95220']

#### 代码点 `0x95220` 函数约 `0x94e20`… 对象字段 LDR/STR
- `#0x28` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x953b4`
- `#0x4d8` ×11 → **MATCH_SCAN** (PlayerModel._npcEquipmentDic, ChessPlayerUnit.m_run2RiseRestoreToMax)  e.g. `0x94ef8`
- `#0x7c8` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.onHeadPosChangedCB)  e.g. `0x95228`
- `#0x7d0` ×2 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_isRelease)  e.g. `0x95250`
- `#0x7d8` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x95278`
- `#0x7e0` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_initRot)  e.g. `0x9517c`
- `#0x7e8` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x951a4`
- `#0x7f0` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_centerPos)  e.g. `0x951d0`
- `#0x7f8` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_initScale)  e.g. `0x951fc`
- `#0x800` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x95290`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 英雄搜索 — `SearchACGHero`
- 字符串文件/VA: `0x4a672`
- ADRP/ADD 引用数: **8** → ['0x7e278', '0x7e63c', '0x7ef98', '0x81050', '0x825ac', '0x86198', '0x86aa0', '0x87fec']

#### 代码点 `0x7e278` 函数约 `0x7dfd4`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7dffc`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x7e10c`
- `#0x870` ×6 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_preDir)  e.g. `0x7e074`
- `#0x878` ×5 → **NO_SCAN_HIT** (-)  e.g. `0x7e010`
- `#0x880` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x7e040`

#### 代码点 `0x7e63c` 函数约 `0x7e5c4`… 对象字段 LDR/STR
- `#0x8` ×1 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x7e844`
- `#0x10` ×5 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x7e6d0`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7e5ec`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x7e6f8`
- `#0x870` ×5 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_preDir)  e.g. `0x7e5f8`
- `#0x878` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x7e650`

#### 代码点 `0x7ef98` 函数约 `0x7ef20`… 对象字段 LDR/STR
- `#0x8` ×2 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x7f42c`
- `#0x10` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x7f41c`
- `#0x18` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x7f428`
- `#0x20` ×6 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x7f430`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7ef44`
- `#0x30` ×5 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7f53c`
- `#0x50` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sClass, DataBaseManager.m_cacheCosSetIdList, PlayerModel._playerInfo, ChessPlayerController._cachedChessPlayerUnitDic, UnitData.onMoveNotifier, WarehouseModel.m_defaultQuickChatDic)  e.g. `0x7f728`
- `#0x698` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_isMorphedAsClone)  e.g. `0x7f060`
- `#0x6a0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInTransition)  e.g. `0x7f05c`
- `#0x6a8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInAtc)  e.g. `0x7f084`
- `#0x6b0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingScaleMillis)  e.g. `0x7f0c0`
- `#0x6c0` ×7 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x7f1fc`
- `#0x6c8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_proximityInteractionState)  e.g. `0x7f0f0`
- `#0x6d0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_lastStopMoveTime)  e.g. `0x7f0ec`
- `#0x870` ×5 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_preDir)  e.g. `0x7ef54`
- `#0x880` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x7efac`
- `#0x8b0` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_unReleaseEnterEvent)  e.g. `0x7f164`
- `#0x90c` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x7f8d8`
- `#0xf10` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x7f734`
- `#0xf50` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x7f73c`
- `#0xf80` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x7f71c`

#### 代码点 `0x81050` 函数约 `0x80f48`… 对象字段 LDR/STR
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x80fcc`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x80ff4`
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x80fd4`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x80f70`
- `#0x230` ×1 → **MATCH_SCAN** (BuyHeroView.AstralStars, ChessBattleModel.timeMachineDic, ChessBattleLogicPlayer.m_observeMorphedOnce, PlayerModel.m_fakeWaitHeroId, ChessBattleUnit.ShowModelTableId, PlayerListItem.m_hasFind)  e.g. `0x80fec`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x80fbc`
- `#0x928` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x8100c`
- `#0x938` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x80f7c`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 英雄搜索2 — `SearchACGHero2`
- 字符串文件/VA: `0x48f8c`
- ADRP/ADD 引用数: **0** → []
- **无 xref**：可能是日志拼接串，不是 resolve 参数

### 下一局对手 — `GetMatchPlayerId`
- 字符串文件/VA: `0x46c22`
- ADRP/ADD 引用数: **4** → ['0x839ec', '0x84b98', '0x84e18', '0x87d2c']

#### 代码点 `0x839ec` 函数约 `0x835ec`… 对象字段 LDR/STR
- `#0x8` ×1 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x83f54`
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x838ac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x839b0`
- `#0x1b8` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iHeroOccupyType, BuyHeroView.HextechAugmentStoreViewRef, ChessBattleModel._gameSwitchModel, ChessBattleLogicPlayer.sqrMaxIconDis, PlayerModel.curMapId, UnitData.m_originPhyiscResist)  e.g. `0x83ce0`
- `#0x268` ×2 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x839c0`
- `#0x698` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_isMorphedAsClone)  e.g. `0x836fc`
- `#0x6a0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInTransition)  e.g. `0x836f8`
- `#0x6a8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInAtc)  e.g. `0x83744`
- `#0x6b0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingScaleMillis)  e.g. `0x8375c`
- `#0x6c8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_proximityInteractionState)  e.g. `0x83778`
- `#0x6d0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_lastStopMoveTime)  e.g. `0x8378c`
- `#0x6d8` ×4 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x8395c`
- `#0x958` ×5 → **NO_SCAN_HIT** (-)  e.g. `0x83a3c`
- `#0x960` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x83b20`
- `#0x978` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83cf0`
- `#0x980` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x83600`
- `#0x988` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x8362c`
- `#0x990` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x8365c`
- `#0x998` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x83690`
- `#0x9a0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x836e8`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x839d0`
- `#0x9b0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x83bc4`
- `#0x9c8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83ee4`
- `#0x9d0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83f7c`

#### 代码点 `0x84b98` 函数约 `0x84a00`… 对象字段 LDR/STR
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84a90`
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x84ab4`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x84a28`
- `#0x34` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iStar)  e.g. `0x84ac8`
- `#0x38` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict, PlayerModel.onPlayerInfoNotifier, ChessPlayerController.ObservedChessPlayerUnitDic, ChessPlayerUnit.DefaultBlockTriggerAnimKeywords)  e.g. `0x84c18`
- `#0x5c` ×1 → **MATCH_SCAN** (PlayerModel.m_money, ChessPlayerController._battleFieldId)  e.g. `0x84ab0`
- `#0x64` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iPrice, ChessPlayerController._enemyPlayerId)  e.g. `0x84ab8`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84aac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x84a98`
- `#0x268` ×1 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x84aa8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84a48`
- `#0x6d8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84b4c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84b74`
- `#0x9d8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84a44`
- `#0x9e0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84af0`

#### 代码点 `0x84e18` 函数约 `0x84c94`… 对象字段 LDR/STR
- `#0x10` ×28 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84cf0`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x84d84`
- `#0x20` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x85034`
- `#0x40` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet, ChessPlayerUnit.DefaultInterruptAnimKeywords, UnitData.IsSelectEnable, WarehouseModel.m_personalityButtonDataClient)  e.g. `0x85084`
- `#0x60` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x84cfc`
- `#0x80` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty3, DataBaseManager.mapACG_ArkItems_Client_FastSearch, ChessPlayerController.m_observedPlayerIds, UnitData.onPropertyNotifier, WarehouseModel.m_RecordFetterRewardDictTemp, BattleMapManager.m_nextActiveMap)  e.g. `0x85338`
- `#0xa0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty11, DataBaseManager._unlockMain, PlayerModel.BreakoutCurrentId, UnitData.onEquipmentNotifier, WarehouseModel.m_TinyDamageMap, BattleMapManager.m_movablePartsGroupId)  e.g. `0x85384`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84e78`
- `#0xc0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty20, PlayerModel._iPlayerHpLeft_Timo, UnitData.onZaunEquipmentChangeNotifier, BattleMapManager.m_unloadMaps)  e.g. `0x853ac`
- `#0xe0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iShowherotag, UnitData.OnResetBoolColor, WarehouseModel.isNeedJumpFetterPanel, BattleMapManager.m_disableCullFrame)  e.g. `0x853f8`
- `#0x100` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEnterBuff, ChessBattleModel.m_currentPlayerId, PlayerModel.OnReFreshBuyHero, ChessBattleUnit._cacheType, UnitData.name, PlayerListPanel._itemLocalPosDic)  e.g. `0x85420`
- `#0x120` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iEffectScale, ChessBattleLogicPlayer.m_battleLogicField, PlayerModel.ReplaceHexTurn, ChessBattleUnit._targetAngle, WarehouseModel.ownedCelebrateEffectDate, BattleMapManager.isPlayCameraMoving)  e.g. `0x8546c`
- `#0x140` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sTransferConf, ChessBattleLogicPlayer.m_maxFrame, PlayerModel.AutoRemoveCount, ChessBattleUnit._nodeHandler, WarehouseModel.m_tinyHeroIDToCompleteRank, BattleMapManager.m_mapTriggerManagerDic)  e.g. `0x85494`
- `#0x160` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMoreFunIntParam, BuyHeroView._isAni, ChessBattleModel._conLoseDataMoney, ChessBattleLogicPlayer.m_run2RiseClickFrames, PlayerModel.HACountInfos, UnitData.m_originAttackMax)  e.g. `0x854e0`
- `#0x180` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sSummonWaitHeroStrParam, BuyHeroView._rootRay, ChessBattleModel.OnHeroStarUp, ChessBattleLogicPlayer.m_run2RiseHorizontalSpeed, ChessBattleUnit._initComponents, UnitData.m_originSkillAddRateVal)  e.g. `0x85508`
- `#0x1a0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sMoreFunStrFormat, BuyHeroView.EquipStoreViewS5Ref, ChessBattleStage.m_battleScreen, ChessBattleLogicPlayer.maxItemDis, PlayerModel.terrainGridPosList, UnitData.m_heroCritValue)  e.g. `0x84f48`
- `#0x1c0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iShowHeroPanel, BuyHeroView.HeavenChooserWeightPanelRef, ChessBattleStage.CoreVersion, ChessBattleModel.PlayMode, ChessBattleLogicPlayer.m_waitDropItems, PlayerModel._enemyPlayerID)  e.g. `0x84f94`
- `#0x1e0` ×2 → **MATCH_SCAN** (BuyHeroView._zapsBuyOriginLocalPos, ChessBattleModel.AllPlayerExpressionTitle, ChessBattleLogicPlayer.m_executingItems, ChessBattleUnit.Show_Star, UnitData.m_damageReduce, PlayerListItem.m_deadColor)  e.g. `0x84fbc`
- `#0x200` ×2 → **MATCH_SCAN** (BuyHeroView._refreshButtonBtn, ChessBattleModel.onTurnStartNotify, ChessBattleLogicPlayer.m_usedDropboxDict, ChessBattleUnit.Golod_l, UnitData.m_shield, PlayerListItem.m_deadHeadColor)  e.g. `0x8500c`
- `#0x6c0` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84e38`
- `#0x6d8` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84e5c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84dfc`
- `#0x9e0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x84e80`

#### 代码点 `0x87d2c` 函数约 `0x87b90`… 对象字段 LDR/STR
- `#0x10` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x87c18`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x87d90`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x87bbc`
- `#0x38` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict, PlayerModel.onPlayerInfoNotifier, ChessPlayerController.ObservedChessPlayerUnitDic, ChessPlayerUnit.DefaultBlockTriggerAnimKeywords)  e.g. `0x87d88`
- `#0x60` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x87cac`
- `#0x100` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEnterBuff, ChessBattleModel.m_currentPlayerId, PlayerModel.OnReFreshBuyHero, ChessBattleUnit._cacheType, UnitData.name, PlayerListPanel._itemLocalPosDic)  e.g. `0x87dd4`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x87c20`
- `#0x268` ×1 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x87c34`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x87c08`
- `#0x6d8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x87d64`
- `#0x868` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_myArrow)  e.g. `0x87d7c`
- `#0xa0d` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87e4c`
- `#0xa18` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87bc8`
- `#0xa20` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87c38`
- `#0xa28` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87ccc`
- `#0xa30` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87e10`
- `#0xa38` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x87d10`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 自己玩家 — `GetMyPlayerModel`
- 字符串文件/VA: `0x4c565`
- ADRP/ADD 引用数: **1** → ['0x788f4']

#### 代码点 `0x788f4` 函数约 `0x7880c`… 对象字段 LDR/STR
- `#0x480` ×3 → **MATCH_SCAN** (PlayerModel._arrNoCntLimit, ChessPlayerUnit.coroutines)  e.g. `0x78820`
- `#0x488` ×3 → **MATCH_SCAN** (PlayerModel._lastRoundActiveFettersKeyList, ChessPlayerUnit.allDmage)  e.g. `0x78850`
- `#0x4a0` ×2 → **MATCH_SCAN** (PlayerModel.heroDynamicClass, ChessPlayerUnit.casttime)  e.g. `0x788d8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x788a4`

**本功能结论：** 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）

### 自己ID — `get_MyPlayerId`
- 字符串文件/VA: `0x4a52f`
- ADRP/ADD 引用数: **1** → ['0x784d0']

#### 代码点 `0x784d0` 函数约 `0x78388`… 对象字段 LDR/STR
- `#0x1c` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x78524`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7851c`
- `#0x60` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x783f4`
- `#0xe0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iShowherotag, UnitData.OnResetBoolColor, WarehouseModel.isNeedJumpFetterPanel, BattleMapManager.m_disableCullFrame)  e.g. `0x783ec`
- `#0xf0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sHeroPaint, PlayerModel._iMaxHeroNum, ChessBattleUnit._inited, UnitData._isFighting, WarehouseModel.MaxSlotNum, BattleMapManager.m_mapAssetAvailableMap)  e.g. `0x78514`
- `#0x478` ×2 → **MATCH_SCAN** (PlayerModel.OnCommonBlankRecordDataChange, ChessPlayerUnit.m_actionStateController)  e.g. `0x783a0`
- `#0x480` ×3 → **MATCH_SCAN** (PlayerModel._arrNoCntLimit, ChessPlayerUnit.coroutines)  e.g. `0x78400`
- `#0x488` ×3 → **MATCH_SCAN** (PlayerModel._lastRoundActiveFettersKeyList, ChessPlayerUnit.allDmage)  e.g. `0x78434`
- `#0x490` ×2 → **MATCH_SCAN** (PlayerModel._fetterManager, ChessPlayerUnit.m_effectStates)  e.g. `0x784b4`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x783a4`
- `#0x6d8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x78500`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 玩家排名 — `GetPlayerRankByID`
- 字符串文件/VA: `0x4c375`
- ADRP/ADD 引用数: **4** → ['0x84b0c', '0x84e9c', '0x851d4', '0x86378']

#### 代码点 `0x84b0c` 函数约 `0x84a00`… 对象字段 LDR/STR
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84a90`
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x84ab4`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x84a28`
- `#0x34` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iStar)  e.g. `0x84ac8`
- `#0x38` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict, PlayerModel.onPlayerInfoNotifier, ChessPlayerController.ObservedChessPlayerUnitDic, ChessPlayerUnit.DefaultBlockTriggerAnimKeywords)  e.g. `0x84c18`
- `#0x5c` ×1 → **MATCH_SCAN** (PlayerModel.m_money, ChessPlayerController._battleFieldId)  e.g. `0x84ab0`
- `#0x64` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iPrice, ChessPlayerController._enemyPlayerId)  e.g. `0x84ab8`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84aac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x84a98`
- `#0x268` ×1 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x84aa8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84a48`
- `#0x6d8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84b4c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84b74`
- `#0x9d8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84a44`
- `#0x9e0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84af0`

#### 代码点 `0x84e9c` 函数约 `0x84c94`… 对象字段 LDR/STR
- `#0x10` ×28 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84cf0`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x84d84`
- `#0x20` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x85034`
- `#0x40` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet, ChessPlayerUnit.DefaultInterruptAnimKeywords, UnitData.IsSelectEnable, WarehouseModel.m_personalityButtonDataClient)  e.g. `0x85084`
- `#0x60` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x84cfc`
- `#0x80` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty3, DataBaseManager.mapACG_ArkItems_Client_FastSearch, ChessPlayerController.m_observedPlayerIds, UnitData.onPropertyNotifier, WarehouseModel.m_RecordFetterRewardDictTemp, BattleMapManager.m_nextActiveMap)  e.g. `0x85338`
- `#0xa0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty11, DataBaseManager._unlockMain, PlayerModel.BreakoutCurrentId, UnitData.onEquipmentNotifier, WarehouseModel.m_TinyDamageMap, BattleMapManager.m_movablePartsGroupId)  e.g. `0x85384`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84e78`
- `#0xc0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty20, PlayerModel._iPlayerHpLeft_Timo, UnitData.onZaunEquipmentChangeNotifier, BattleMapManager.m_unloadMaps)  e.g. `0x853ac`
- `#0xe0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iShowherotag, UnitData.OnResetBoolColor, WarehouseModel.isNeedJumpFetterPanel, BattleMapManager.m_disableCullFrame)  e.g. `0x853f8`
- `#0x100` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEnterBuff, ChessBattleModel.m_currentPlayerId, PlayerModel.OnReFreshBuyHero, ChessBattleUnit._cacheType, UnitData.name, PlayerListPanel._itemLocalPosDic)  e.g. `0x85420`
- `#0x120` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iEffectScale, ChessBattleLogicPlayer.m_battleLogicField, PlayerModel.ReplaceHexTurn, ChessBattleUnit._targetAngle, WarehouseModel.ownedCelebrateEffectDate, BattleMapManager.isPlayCameraMoving)  e.g. `0x8546c`
- `#0x140` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sTransferConf, ChessBattleLogicPlayer.m_maxFrame, PlayerModel.AutoRemoveCount, ChessBattleUnit._nodeHandler, WarehouseModel.m_tinyHeroIDToCompleteRank, BattleMapManager.m_mapTriggerManagerDic)  e.g. `0x85494`
- `#0x160` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMoreFunIntParam, BuyHeroView._isAni, ChessBattleModel._conLoseDataMoney, ChessBattleLogicPlayer.m_run2RiseClickFrames, PlayerModel.HACountInfos, UnitData.m_originAttackMax)  e.g. `0x854e0`
- `#0x180` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sSummonWaitHeroStrParam, BuyHeroView._rootRay, ChessBattleModel.OnHeroStarUp, ChessBattleLogicPlayer.m_run2RiseHorizontalSpeed, ChessBattleUnit._initComponents, UnitData.m_originSkillAddRateVal)  e.g. `0x85508`
- `#0x1a0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sMoreFunStrFormat, BuyHeroView.EquipStoreViewS5Ref, ChessBattleStage.m_battleScreen, ChessBattleLogicPlayer.maxItemDis, PlayerModel.terrainGridPosList, UnitData.m_heroCritValue)  e.g. `0x84f48`
- `#0x1c0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iShowHeroPanel, BuyHeroView.HeavenChooserWeightPanelRef, ChessBattleStage.CoreVersion, ChessBattleModel.PlayMode, ChessBattleLogicPlayer.m_waitDropItems, PlayerModel._enemyPlayerID)  e.g. `0x84f94`
- `#0x1e0` ×2 → **MATCH_SCAN** (BuyHeroView._zapsBuyOriginLocalPos, ChessBattleModel.AllPlayerExpressionTitle, ChessBattleLogicPlayer.m_executingItems, ChessBattleUnit.Show_Star, UnitData.m_damageReduce, PlayerListItem.m_deadColor)  e.g. `0x84fbc`
- `#0x200` ×2 → **MATCH_SCAN** (BuyHeroView._refreshButtonBtn, ChessBattleModel.onTurnStartNotify, ChessBattleLogicPlayer.m_usedDropboxDict, ChessBattleUnit.Golod_l, UnitData.m_shield, PlayerListItem.m_deadHeadColor)  e.g. `0x8500c`
- `#0x6c0` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84e38`
- `#0x6d8` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84e5c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84dfc`
- `#0x9e0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x84e80`

#### 代码点 `0x851d4` 函数约 `0x84dd4`… 对象字段 LDR/STR
- `#0x10` ×27 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84f3c`
- `#0x20` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x85034`
- `#0x40` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet, ChessPlayerUnit.DefaultInterruptAnimKeywords, UnitData.IsSelectEnable, WarehouseModel.m_personalityButtonDataClient)  e.g. `0x85084`
- `#0x60` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x85310`
- `#0x80` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty3, DataBaseManager.mapACG_ArkItems_Client_FastSearch, ChessPlayerController.m_observedPlayerIds, UnitData.onPropertyNotifier, WarehouseModel.m_RecordFetterRewardDictTemp, BattleMapManager.m_nextActiveMap)  e.g. `0x85338`
- `#0xa0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty11, DataBaseManager._unlockMain, PlayerModel.BreakoutCurrentId, UnitData.onEquipmentNotifier, WarehouseModel.m_TinyDamageMap, BattleMapManager.m_movablePartsGroupId)  e.g. `0x85384`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84e78`
- `#0xc0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty20, PlayerModel._iPlayerHpLeft_Timo, UnitData.onZaunEquipmentChangeNotifier, BattleMapManager.m_unloadMaps)  e.g. `0x853ac`
- `#0xe0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iShowherotag, UnitData.OnResetBoolColor, WarehouseModel.isNeedJumpFetterPanel, BattleMapManager.m_disableCullFrame)  e.g. `0x853f8`
- `#0x100` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEnterBuff, ChessBattleModel.m_currentPlayerId, PlayerModel.OnReFreshBuyHero, ChessBattleUnit._cacheType, UnitData.name, PlayerListPanel._itemLocalPosDic)  e.g. `0x85420`
- `#0x120` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iEffectScale, ChessBattleLogicPlayer.m_battleLogicField, PlayerModel.ReplaceHexTurn, ChessBattleUnit._targetAngle, WarehouseModel.ownedCelebrateEffectDate, BattleMapManager.isPlayCameraMoving)  e.g. `0x8546c`
- `#0x140` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sTransferConf, ChessBattleLogicPlayer.m_maxFrame, PlayerModel.AutoRemoveCount, ChessBattleUnit._nodeHandler, WarehouseModel.m_tinyHeroIDToCompleteRank, BattleMapManager.m_mapTriggerManagerDic)  e.g. `0x85494`
- `#0x160` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMoreFunIntParam, BuyHeroView._isAni, ChessBattleModel._conLoseDataMoney, ChessBattleLogicPlayer.m_run2RiseClickFrames, PlayerModel.HACountInfos, UnitData.m_originAttackMax)  e.g. `0x854e0`
- `#0x180` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sSummonWaitHeroStrParam, BuyHeroView._rootRay, ChessBattleModel.OnHeroStarUp, ChessBattleLogicPlayer.m_run2RiseHorizontalSpeed, ChessBattleUnit._initComponents, UnitData.m_originSkillAddRateVal)  e.g. `0x85508`
- `#0x1a0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sMoreFunStrFormat, BuyHeroView.EquipStoreViewS5Ref, ChessBattleStage.m_battleScreen, ChessBattleLogicPlayer.maxItemDis, PlayerModel.terrainGridPosList, UnitData.m_heroCritValue)  e.g. `0x84f48`
- `#0x1c0` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iShowHeroPanel, BuyHeroView.HeavenChooserWeightPanelRef, ChessBattleStage.CoreVersion, ChessBattleModel.PlayMode, ChessBattleLogicPlayer.m_waitDropItems, PlayerModel._enemyPlayerID)  e.g. `0x84f94`
- `#0x1e0` ×2 → **MATCH_SCAN** (BuyHeroView._zapsBuyOriginLocalPos, ChessBattleModel.AllPlayerExpressionTitle, ChessBattleLogicPlayer.m_executingItems, ChessBattleUnit.Show_Star, UnitData.m_damageReduce, PlayerListItem.m_deadColor)  e.g. `0x84fbc`
- `#0x200` ×2 → **MATCH_SCAN** (BuyHeroView._refreshButtonBtn, ChessBattleModel.onTurnStartNotify, ChessBattleLogicPlayer.m_usedDropboxDict, ChessBattleUnit.Golod_l, UnitData.m_shield, PlayerListItem.m_deadHeadColor)  e.g. `0x8500c`
- `#0x6c0` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84e38`
- `#0x6d8` ×3 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84e5c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84dfc`
- `#0x9e0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x84e80`

#### 代码点 `0x86378` 函数约 `0x86208`… 对象字段 LDR/STR
- `#0x8` ×4 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x86338`
- `#0x10` ×9 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x86270`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x86278`
- `#0x1c` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x865e0`
- `#0x20` ×7 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x863d8`
- `#0x40` ×10 → **MATCH_SCAN** (TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet, ChessPlayerUnit.DefaultInterruptAnimKeywords, UnitData.IsSelectEnable, WarehouseModel.m_personalityButtonDataClient)  e.g. `0x86264`
- `#0x48` ×7 → **MATCH_SCAN** (TACG_Hero_Client.sSpec, DataBaseManager.m_cacheCosSetIdListStr, ChessPlayerController.chessViewAttackSet, UnitData.onStateChangedNotifer, WarehouseModel.m_getBattleGraffitiResp, BattleMapManager.m_gameSceneColliders)  e.g. `0x8630c`
- `#0x50` ×7 → **MATCH_SCAN** (TACG_Hero_Client.sClass, DataBaseManager.m_cacheCosSetIdList, PlayerModel._playerInfo, ChessPlayerController._cachedChessPlayerUnitDic, UnitData.onMoveNotifier, WarehouseModel.m_defaultQuickChatDic)  e.g. `0x8641c`
- `#0x5c` ×1 → **MATCH_SCAN** (PlayerModel.m_money, ChessPlayerController._battleFieldId)  e.g. `0x8640c`
- `#0x80` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty3, DataBaseManager.mapACG_ArkItems_Client_FastSearch, ChessPlayerController.m_observedPlayerIds, UnitData.onPropertyNotifier, WarehouseModel.m_RecordFetterRewardDictTemp, BattleMapManager.m_nextActiveMap)  e.g. `0x8624c`
- `#0x88` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty5, DataBaseManager.mapSynthesis_Client_FragmentIdDIc, ChessPlayerController.m_viewGameObjectPool, UnitData.onBuddChildChange, WarehouseModel.m_RecordAchieveFetterDict, BattleMapManager.m_currentActiveMap)  e.g. `0x86258`
- `#0x90` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty7, DataBaseManager.mapSynthesis_Client_SyntheticIdDIc, ChessPlayerController.m_allHidePlayers, UnitData.onDraconicChange, WarehouseModel.m_RecordAchieveFetterDictTemp, BattleMapManager.m_listBlocks)  e.g. `0x86bd0`
- `#0x9c` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty10)  e.g. `0x863f0`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x86348`
- `#0xe4` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iHeroType, WarehouseModel.curSelectFetterId, BattleMapManager.m_maxLoadedMapCount)  e.g. `0x86400`
- `#0xe8` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iTag, UnitData._tabData, WarehouseModel.selectFetterId, BattleMapManager.m_loadDefaultMapWhenNeedDownload)  e.g. `0x86524`
- `#0x2b8` ×1 → **MATCH_SCAN** (ChessBattleModel._isHundredGameEnd, PlayerModel.onBeginFightNotifer)  e.g. `0x86444`
- `#0x2c0` ×1 → **MATCH_SCAN** (ChessBattleModel._pandoraBattleEndActivityData, PlayerModel.battleGrids)  e.g. `0x8645c`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x86398`
- `#0x9e8` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x86a58`
- `#0xa00` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x8635c`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 对局地图更新 — `UpdateBattleMap`
- 字符串文件/VA: `0x4c5b9`
- ADRP/ADD 引用数: **1** → ['0x7a800']

#### 代码点 `0x7a800` 函数约 `0x7a7d8`… 对象字段 LDR/STR
- `#0x28` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7a7f0`

**本功能结论：** 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）

### 头像列表 — `PlayerListPanel`
- 字符串文件/VA: `0x47b86`
- ADRP/ADD 引用数: **1** → ['0x83450']

#### 代码点 `0x83450` 函数约 `0x83268`… 对象字段 LDR/STR
- `#0x10` ×3 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x83394`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x83290`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x832a8`
- `#0x6d8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x832ac`
- `#0x948` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x832a4`
- `#0x950` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83314`
- `#0x968` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x8341c`
- `#0x970` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83484`
- `#0x978` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x834e8`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 列表项 — `PlayerListItem`
- 字符串文件/VA: `0x492a4`
- ADRP/ADD 引用数: **1** → ['0x83ab0']

#### 代码点 `0x83ab0` 函数约 `0x836b0`… 对象字段 LDR/STR
- `#0x8` ×2 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x83f54`
- `#0xc` ×1 → **MATCH_SCAN** (ChessBattleUnit.hasInitUnitScaleLimit, RoundSelectPlayerUnit.m_init)  e.g. `0x83ff8`
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x838ac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x839b0`
- `#0x1b8` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iHeroOccupyType, BuyHeroView.HextechAugmentStoreViewRef, ChessBattleModel._gameSwitchModel, ChessBattleLogicPlayer.sqrMaxIconDis, PlayerModel.curMapId, UnitData.m_originPhyiscResist)  e.g. `0x83ce0`
- `#0x268` ×2 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x839c0`
- `#0x698` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_isMorphedAsClone)  e.g. `0x836fc`
- `#0x6a0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInTransition)  e.g. `0x836f8`
- `#0x6a8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInAtc)  e.g. `0x83744`
- `#0x6b0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingScaleMillis)  e.g. `0x8375c`
- `#0x6c8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_proximityInteractionState)  e.g. `0x83778`
- `#0x6d0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_lastStopMoveTime)  e.g. `0x8378c`
- `#0x6d8` ×4 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x8395c`
- `#0x958` ×5 → **NO_SCAN_HIT** (-)  e.g. `0x83a3c`
- `#0x960` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x83b20`
- `#0x978` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83cf0`
- `#0x988` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x836d8`
- `#0x990` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x836c0`
- `#0x998` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x836c4`
- `#0x9a0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x836e8`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x839d0`
- `#0x9b0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x83bc4`
- `#0x9c8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83ee4`
- `#0x9d0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83f7c`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 海克斯 — `HextechAugmentsCtrl`
- 字符串文件/VA: `0x48fff`
- ADRP/ADD 引用数: **1** → ['0x88be0']

#### 代码点 `0x88be0` 函数约 `0x88ae0`… 对象字段 LDR/STR
- `#0x18` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x88b38`
- `#0x24` ×1 → **MATCH_SCAN** (ChessPlayerUnit.transScale, UnitData._playerId, BattleMapManager.UseJCELogic)  e.g. `0x88b40`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x88b04`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x88b44`
- `#0x58` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sSkill, DataBaseManager.m_cacheCosSetListStr, UnitData.onFightingStateChangedNotifer, WarehouseModel.m_isInit, BattleMapManager.m_roundSelectSceneCamera)  e.g. `0x88b18`
- `#0xb0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iSpec1, ChessBattleModel.encodedGameStatisticsData, PlayerModel.noActiveFetterHero, ChessPlayerController.minBloodInfoHeightDic, ChessBattleUnit.m_bodyAsset, UnitData.onChangeEquipNotifier)  e.g. `0x88b20`
- `#0x698` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_isMorphedAsClone)  e.g. `0x88b98`
- `#0x6a0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInTransition)  e.g. `0x88b94`
- `#0x6a8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInAtc)  e.g. `0x88bd8`
- `#0x6b0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingScaleMillis)  e.g. `0x88be4`
- `#0xd18` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x88b10`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 棋手单位 — `ChessPlayerUnit`
- 字符串文件/VA: `0x49e49`
- ADRP/ADD 引用数: **9** → ['0x78b38', '0x78b8c', '0x78c64', '0x791a4', '0x79288', '0x7be18', '0x7be94', '0x7c11c']

#### 代码点 `0x78b38` 函数约 `0x78b18`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x78b30`

#### 代码点 `0x78b8c` 函数约 `0x78b18`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x78b30`

#### 代码点 `0x78c64` 函数约 `0x78b18`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x78b30`

#### 代码点 `0x791a4` 函数约 `0x79144`… 对象字段 LDR/STR
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x7917c`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7915c`
- `#0x418` ×1 → **MATCH_SCAN** (PlayerModel.needUpdateStealGlovesDirectly, ChessPlayerUnit.originBodyLocalScale)  e.g. `0x79174`
- `#0x4f0` ×2 → **MATCH_SCAN** (PlayerModel._player_heroskins, ChessPlayerUnit.m_scoutCoordinator)  e.g. `0x79190`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x791d4`

**本功能结论：** 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）

### 站位推送串 — `OPPONENT_BOARD`
- 字符串文件/VA: `0x47466`
- ADRP/ADD 引用数: **1** → ['0x884c0']

#### 代码点 `0x884c0` 函数约 `0x880c0`… 对象字段 LDR/STR
- `#0x8` ×3 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x882f0`
- `#0xc` ×2 → **MATCH_SCAN** (ChessBattleUnit.hasInitUnitScaleLimit, RoundSelectPlayerUnit.m_init)  e.g. `0x88328`
- `#0x10` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x880c0`
- `#0x14` ×2 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_defaultRoundSelectId)  e.g. `0x880c4`
- `#0x18` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x88138`
- `#0x1c` ×8 → **NO_SCAN_HIT** (-)  e.g. `0x88228`
- `#0x20` ×3 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x880cc`
- `#0x24` ×10 → **MATCH_SCAN** (ChessPlayerUnit.transScale, UnitData._playerId, BattleMapManager.UseJCELogic)  e.g. `0x881ec`
- `#0x28` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x881e8`
- `#0x2c` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMinDelayFrame, ChessPlayerUnit.positionsID, UnitData.HostPlayerId)  e.g. `0x88388`
- `#0x44` ×1 → **MATCH_SCAN** (UnitData._curState)  e.g. `0x880c8`
- `#0x60` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x88160`
- `#0xc8` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sFetterSkill, PlayerModel._iChessPlayerUnitScaleEffect, ChessBattleUnit.socketData, UnitData.onSaleNotifier, WarehouseModel.m_storeAchieveFetterStateHashSet, BattleMapManager.m_camTransform)  e.g. `0x880f8`
- `#0xf8` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sHeroPaintSmall, ChessBattleModel.OnBRFinalPhaseChanged, PlayerModel.MaxHeroEquipCountDic, ChessBattleUnit._cacheAnim, WarehouseModel.initiativeMagicExpressionDict, BattleMapManager.m_sourceInterestDic)  e.g. `0x8814c`
- `#0x6d8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x883ec`
- `#0xa0d` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x888bc`
- `#0xa10` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x88910`
- `#0xce0` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x887a0`
- `#0xce8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x8839c`
- `#0xcf0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x883f0`
- `#0xcf8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x88450`
- `#0xd00` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x88108`
- `#0xd08` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x88600`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 商店视图 — `BuyHeroView`
- 字符串文件/VA: `0x46c16`
- ADRP/ADD 引用数: **3** → ['0x7d6cc', '0x7d8a8', '0x95240']

#### 代码点 `0x7d6cc` 函数约 `0x7d6b8`… 对象字段 LDR/STR
- `#0x8` ×1 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x7d73c`
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x7d6fc`
- `#0x18` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sName, DataBaseManager.m_itemReadableCheckingSet, ChessPlayerController._chessPlayerTrans, ChessBattleUnit.S11_RESET_TAG, UnitData.isTempMoveBattle, RoundSelectPlayerUnit.isShowCountDownEffect)  e.g. `0x7d704`
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x7d720`
- `#0x28` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7d730`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7d744`
- `#0x38` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict, PlayerModel.onPlayerInfoNotifier, ChessPlayerController.ObservedChessPlayerUnitDic, ChessPlayerUnit.DefaultBlockTriggerAnimKeywords)  e.g. `0x7d754`
- `#0x40` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sDesc, DataBaseManager.m_cacheNoBuildSetIdList, ChessPlayerController.chessViewBulletSet, ChessPlayerUnit.DefaultInterruptAnimKeywords, UnitData.IsSelectEnable, WarehouseModel.m_personalityButtonDataClient)  e.g. `0x7d764`
- `#0x148` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iPeopleCnt, BuyHeroView._listHeroRoot, ChessBattleModel._conWinDataCount, ChessBattleLogicPlayer.m_currentId, PlayerModel._ActiveHAConfigIDs, ChessBattleUnit._unitRecover)  e.g. `0x7d6f0`
- `#0x168` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sMoreFunStrParam, BuyHeroView.m_curPlayerModel, ChessBattleLogicPlayer.m_run2RiseClickStart, PlayerModel.RefreshHexCount, UnitData.m_skillAddRate, WarehouseModel.diyMapBanExchangeNotice)  e.g. `0x7d6e8`
- `#0x700` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_exitMatRestoreCoroutine)  e.g. `0x7d724`
- `#0x708` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_pos)  e.g. `0x7d6ec`

#### 代码点 `0x7d8a8` 函数约 `0x7d88c`… 对象字段 LDR/STR
- `#0x850` ×3 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_pathCtrl)  e.g. `0x7d928`
- `#0x858` ×3 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_dirCtrl)  e.g. `0x7d938`

#### 代码点 `0x95240` 函数约 `0x94e40`… 对象字段 LDR/STR
- `#0x28` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x953b4`
- `#0x4d8` ×11 → **MATCH_SCAN** (PlayerModel._npcEquipmentDic, ChessPlayerUnit.m_run2RiseRestoreToMax)  e.g. `0x94ef8`
- `#0x7c8` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.onHeadPosChangedCB)  e.g. `0x95228`
- `#0x7d0` ×2 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_isRelease)  e.g. `0x95250`
- `#0x7d8` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x95278`
- `#0x7e0` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_initRot)  e.g. `0x9517c`
- `#0x7e8` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x951a4`
- `#0x7f0` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_centerPos)  e.g. `0x951d0`
- `#0x7f8` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_initScale)  e.g. `0x951fc`
- `#0x800` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x95290`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 数据库 — `DataBaseManager`
- 字符串文件/VA: `0x47661`
- ADRP/ADD 引用数: **22** → ['0x78abc', '0x7ba34', '0x7c4b8', '0x7c5c0', '0x7cac8', '0x7cff0', '0x7e234', '0x7e270']

#### 代码点 `0x78abc` 函数约 `0x78a98`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x78b30`
- `#0x4a8` ×1 → **MATCH_SCAN** (PlayerModel._foreverRecordData)  e.g. `0x78b0c`
- `#0x4b0` ×2 → **MATCH_SCAN** (PlayerModel.heroTypeFetterAddCntDict, ChessPlayerUnit.m_triggerSystem)  e.g. `0x78aa8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x78ae4`

#### 代码点 `0x7ba34` 函数约 `0x7b9f4`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7ba0c`

#### 代码点 `0x7c4b8` 函数约 `0x7c454`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7c474`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7c4ec`
- `#0x600` ×2 → **MATCH_SCAN** (PlayerModel.OnOutFieldUnitPlayAnim, ChessPlayerUnit.m_lastTrigger)  e.g. `0x7c480`
- `#0x608` ×1 → **MATCH_SCAN** (ChessPlayerUnit.cacheFPos)  e.g. `0x7c484`
- `#0x808` ×2 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_strTransferEffect)  e.g. `0x7c4a4`

#### 代码点 `0x7c5c0` 函数约 `0x7c55c`… 对象字段 LDR/STR
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7c57c`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7c5f4`
- `#0x604` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x7c588`
- `#0x708` ×1 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_pos)  e.g. `0x7c58c`
- `#0x808` ×2 → **MATCH_SCAN** (RoundSelectPlayerUnit.m_strTransferEffect)  e.g. `0x7c5ac`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 玩家模型 — `PlayerModel`
- 字符串文件/VA: `0x487eb`
- ADRP/ADD 引用数: **1** → ['0x7a7f8']

#### 代码点 `0x7a7f8` 函数约 `0x7a7d8`… 对象字段 LDR/STR
- `#0x28` ×4 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x7a7f0`

**本功能结论：** 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类）

### 对战模型 — `ChessBattleModel`
- 字符串文件/VA: `0x4c267`
- ADRP/ADD 引用数: **11** → ['0x784c8', '0x788ec', '0x839e4', '0x84b04', '0x84b90', '0x84e10', '0x84e94', '0x851cc']

#### 代码点 `0x784c8` 函数约 `0x78388`… 对象字段 LDR/STR
- `#0x1c` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x78524`
- `#0x30` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iMaxDelayFrame, DataBaseManager.m_cacheNoBuildSetListArr, ChessBattleModel.battleTableInfo, PlayerModel.limitedHeroModel, ChessPlayerController.EnemyChessPlayerUnitDic, ChessPlayerUnit.DisplayPlayerResultPanel)  e.g. `0x7851c`
- `#0x60` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iCost, DataBaseManager.m_cacheCosSetList, ChessBattleModel.HundredRoundGroupDataFrameId, ChessPlayerController._chairId, UnitData.onPrepareChangedNotify, WarehouseModel.m_PassiveConfig)  e.g. `0x783f4`
- `#0xe0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iShowherotag, UnitData.OnResetBoolColor, WarehouseModel.isNeedJumpFetterPanel, BattleMapManager.m_disableCullFrame)  e.g. `0x783ec`
- `#0xf0` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sHeroPaint, PlayerModel._iMaxHeroNum, ChessBattleUnit._inited, UnitData._isFighting, WarehouseModel.MaxSlotNum, BattleMapManager.m_mapAssetAvailableMap)  e.g. `0x78514`
- `#0x478` ×2 → **MATCH_SCAN** (PlayerModel.OnCommonBlankRecordDataChange, ChessPlayerUnit.m_actionStateController)  e.g. `0x783a0`
- `#0x480` ×3 → **MATCH_SCAN** (PlayerModel._arrNoCntLimit, ChessPlayerUnit.coroutines)  e.g. `0x78400`
- `#0x488` ×3 → **MATCH_SCAN** (PlayerModel._lastRoundActiveFettersKeyList, ChessPlayerUnit.allDmage)  e.g. `0x78434`
- `#0x490` ×2 → **MATCH_SCAN** (PlayerModel._fetterManager, ChessPlayerUnit.m_effectStates)  e.g. `0x784b4`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x783a4`
- `#0x6d8` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x78500`

#### 代码点 `0x788ec` 函数约 `0x7880c`… 对象字段 LDR/STR
- `#0x480` ×3 → **MATCH_SCAN** (PlayerModel._arrNoCntLimit, ChessPlayerUnit.coroutines)  e.g. `0x78820`
- `#0x488` ×3 → **MATCH_SCAN** (PlayerModel._lastRoundActiveFettersKeyList, ChessPlayerUnit.allDmage)  e.g. `0x78850`
- `#0x4a0` ×2 → **MATCH_SCAN** (PlayerModel.heroDynamicClass, ChessPlayerUnit.casttime)  e.g. `0x788d8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x788a4`

#### 代码点 `0x839e4` 函数约 `0x835e4`… 对象字段 LDR/STR
- `#0x8` ×1 → **MATCH_SCAN** (DataBaseManager._alllocalData, BuyHeroView.VisitingFieldDelayShowTime, ChessBattleStage.m_UsedIngameParticleSystemAutoBatcher, PlayerModel.GlobalFetterCombineId, ChessPlayerUnit._animLoopList, ChessBattleUnit.maxUnitScale)  e.g. `0x83f54`
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x838ac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x839b0`
- `#0x1b8` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iHeroOccupyType, BuyHeroView.HextechAugmentStoreViewRef, ChessBattleModel._gameSwitchModel, ChessBattleLogicPlayer.sqrMaxIconDis, PlayerModel.curMapId, UnitData.m_originPhyiscResist)  e.g. `0x83ce0`
- `#0x268` ×2 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x839c0`
- `#0x698` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_isMorphedAsClone)  e.g. `0x836fc`
- `#0x6a0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInTransition)  e.g. `0x836f8`
- `#0x6a8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cloneMorphInAtc)  e.g. `0x83744`
- `#0x6b0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingScaleMillis)  e.g. `0x8375c`
- `#0x6c8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_proximityInteractionState)  e.g. `0x83778`
- `#0x6d0` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_lastStopMoveTime)  e.g. `0x8378c`
- `#0x6d8` ×4 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x8395c`
- `#0x958` ×5 → **NO_SCAN_HIT** (-)  e.g. `0x83a3c`
- `#0x960` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x83b20`
- `#0x978` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83cf0`
- `#0x980` ×1 → **NO_SCAN_HIT** (-)  e.g. `0x83600`
- `#0x988` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x8362c`
- `#0x990` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x8365c`
- `#0x998` ×3 → **NO_SCAN_HIT** (-)  e.g. `0x83690`
- `#0x9a0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x836e8`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x839d0`
- `#0x9b0` ×4 → **NO_SCAN_HIT** (-)  e.g. `0x83bc4`
- `#0x9c8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83ee4`
- `#0x9d0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x83f7c`

#### 代码点 `0x84b04` 函数约 `0x84a00`… 对象字段 LDR/STR
- `#0x10` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iID, DataBaseManager.allServerData, DataBaseManager.m_enableCheckItemReadable, ChessPlayerController._started, ChessPlayerUnit._animComboList, ChessBattleUnit.ms_editor_prefab)  e.g. `0x84a90`
- `#0x20` ×2 → **MATCH_SCAN** (TACG_Hero_Client.sAIName, DataBaseManager._initialzied, DataBaseManager.m_itemReadableLock, ChessBattleModel.SoGameData_View, PlayerModel.battleTurnModel, ChessPlayerController._victoryAnimator)  e.g. `0x84ab4`
- `#0x28` ×2 → **MATCH_SCAN** (TACG_Hero_Client.iDelayLeadTime, DataBaseManager.ms_missItemConfig, DataBaseManager.m_cacheNoBuildSetListStr, ChessBattleModel.stExecutor, PlayerModel.hexAugmentModel, ChessPlayerController.ChessPlayerUnitDic)  e.g. `0x84a28`
- `#0x34` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iStar)  e.g. `0x84ac8`
- `#0x38` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iQuality, DataBaseManager.m_cacheNoBuildSetIdListStr, ChessBattleModel.playerModelDict, PlayerModel.onPlayerInfoNotifier, ChessPlayerController.ObservedChessPlayerUnitDic, ChessPlayerUnit.DefaultBlockTriggerAnimKeywords)  e.g. `0x84c18`
- `#0x5c` ×1 → **MATCH_SCAN** (PlayerModel.m_money, ChessPlayerController._battleFieldId)  e.g. `0x84ab0`
- `#0x64` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iPrice, ChessPlayerController._enemyPlayerId)  e.g. `0x84ab8`
- `#0xbc` ×1 → **MATCH_SCAN** (TACG_Hero_Client.iProperty19, PlayerModel._iPlayerHpLeft)  e.g. `0x84aac`
- `#0x190` ×1 → **MATCH_SCAN** (TACG_Hero_Client.sEquipmentGet, BuyHeroView._heavenSelectBuffDock, ChessBattleStage.switchTimer, ChessBattleModel.NSendLogtrackToOthersLocalFrameInterval, ChessBattleLogicPlayer.maxBoxDis, PlayerModel.TormentedCheckId)  e.g. `0x84a98`
- `#0x268` ×1 → **MATCH_SCAN** (BuyHeroView._teamMarkTagList, ChessBattleModel.my_match_list, ChessBattleLogicPlayer.CanCollision, PlayerModel.freeRefreshCnt, UnitData.OriConfID)  e.g. `0x84aa8`
- `#0x6c0` ×1 → **MATCH_SCAN** (ChessPlayerUnit.m_morphPendingImmediate)  e.g. `0x84a48`
- `#0x6d8` ×2 → **MATCH_SCAN** (ChessPlayerUnit.m_cachedProximityInteractionCfg)  e.g. `0x84b4c`
- `#0x9a8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84b74`
- `#0x9d8` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84a44`
- `#0x9e0` ×2 → **NO_SCAN_HIT** (-)  e.g. `0x84af0`

**本功能结论：** 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源**

### 战斗单位 — `ChessBattleUnit`
- 字符串：**不在 SO 内** → 原逻辑可能不走这个名字

### UnitData — `UnitData`
- 字符串：**不在 SO 内** → 原逻辑可能不走这个名字

---

## 总表

| 功能 | 符号 | 定位 | 字段立即数 | 结论 |
|------|------|------|------------|------|
| 商店刷新/牌库更新 | `OnRefreshHeroRet` | 1 xrefs | match_imm=2 unk=0 | 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类） |
| 自动拿牌 | `ReqBuyHero` | 1 xrefs | match_imm=7 unk=3 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 英雄搜索 | `SearchACGHero` | 8 xrefs | match_imm=17 unk=8 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 英雄搜索2 | `SearchACGHero2` | NO_XREF | 0x48f8c | 需其它定位 |
| 下一局对手 | `GetMatchPlayerId` | 4 xrefs | match_imm=37 unk=20 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 自己玩家 | `GetMyPlayerModel` | 1 xrefs | match_imm=4 unk=0 | 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类） |
| 自己ID | `get_MyPlayerId` | 1 xrefs | match_imm=10 unk=1 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 玩家排名 | `GetPlayerRankByID` | 4 xrefs | match_imm=38 unk=6 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 对局地图更新 | `UpdateBattleMap` | 1 xrefs | match_imm=1 unk=0 | 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类） |
| 头像列表 | `PlayerListPanel` | 1 xrefs | match_imm=4 unk=5 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 列表项 | `PlayerListItem` | 1 xrefs | match_imm=13 unk=11 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 海克斯 | `HextechAugmentsCtrl` | 1 xrefs | match_imm=10 unk=1 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 棋手单位 | `ChessPlayerUnit` | 9 xrefs | match_imm=5 unk=0 | 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类） |
| 站位推送串 | `OPPONENT_BOARD` | 1 xrefs | match_imm=14 unk=9 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 商店视图 | `BuyHeroView` | 3 xrefs | match_imm=20 unk=3 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 数据库 | `DataBaseManager` | 22 xrefs | match_imm=9 unk=1 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 玩家模型 | `PlayerModel` | 1 xrefs | match_imm=1 unk=0 | 窗口内字段立即数均能在扫描表中找到同值（仍需确认是否同一类） |
| 对战模型 | `ChessBattleModel` | 11 xrefs | match_imm=29 unk=15 | 部分立即数能对上扫描；**未对上的是优先怀疑的闪退源** |
| 战斗单位 | `ChessBattleUnit` | ABSENT | - | 无法字符串定位 |
| UnitData | `UnitData` | ABSENT | - | 无法字符串定位 |

---

## 综合判断（给后续补丁用）

1. **闪退 = 读错字段/对象**，不是业务要重写。  
2. **英雄表路径已 MATCH**，不是主闪退源。  
3. 原 SO 用 **类名/方法名字符串 + DobbyHook**；方法名大多仍在 dump 里。  
4. 字段靠 **LDR 立即数**；补丁要改 **指令编码**，不能只改配置文件。  
5. 下一步工程：  
   - 对「unk 立即数」密集的功能函数，对照 scan 同类字段，找「旧 imm → 新 imm」；  
   - 优先：**GetMatchPlayerId 调用链、UpdateBattleMap、PlayerList*、Hextech、ReqBuyHero 之后的对象遍历**；  
   - 改完只动不匹配点，重签固定 keystore 出包。

6. **在未完成上述对照前，不声称全功能可用。**

