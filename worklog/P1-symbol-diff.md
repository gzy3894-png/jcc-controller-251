# P1 Symbol diff: original libJCC strings vs current dump.cs

| Symbol | In SO? | dump hits | Notes |
|--------|--------|-----------|-------|
| `OnRefreshHeroRet` | True | 1 | dump only IDMAP (no method body in dump?) |
| `ReqBuyHero` | True | 7 | dump only IDMAP (no method body in dump?) |
| `SearchACGHero` | True | 7 | dump only IDMAP (no method body in dump?) |
| `SearchACGHero2` | True | 1 | dump only IDMAP (no method body in dump?) |
| `SearchACGHeroAndStar` | False | 2 | new season only (not in old SO) |
| `GetMyPlayerModel` | True | 2 | dump only IDMAP (no method body in dump?) |
| `get_MyPlayerId` | True | 1 | dump only IDMAP (no method body in dump?) |
| `GetMatchPlayerId` | True | 1 | dump only IDMAP (no method body in dump?) |
| `GetPlayer` | True | 250 | present in dump |
| `GetPlayerRankByID` | True | 1 | dump only IDMAP (no method body in dump?) |
| `UpdateBattleMap` | True | 1 | dump only IDMAP (no method body in dump?) |
| `get_Instance` | True | 179 | present in dump |
| `IsUseBuyheroview_iPad` | True | 2 | dump only IDMAP (no method body in dump?) |
| `CurBuyViewIsOpen` | True | 1 | dump only IDMAP (no method body in dump?) |
| `GetBattleModel` | True | 4 | dump only IDMAP (no method body in dump?) |
| `PlayerListPanel` | True | 131 | present in dump |
| `PlayerListItem` | True | 216 | present in dump |
| `PlayerHeadInfo` | True | 0 | SO has string but dump has ZERO — critical rename? |
| `HextechAugmentsCtrl` | True | 366 | present in dump |
| `ChessPlayerUnit` | True | 729 | present in dump |
| `ChessPlayerController` | True | 87 | present in dump |
| `BuyHeroView` | True | 317 | present in dump |
| `DataBaseManager` | True | 680 | present in dump |
| `PlayerModel` | True | 585 | present in dump |
| `ReqRefresh` | True | 10 | dump only IDMAP (no method body in dump?) |
| `GetTinyModel` | True | 2 | dump only IDMAP (no method body in dump?) |
| `UpdateNameAndMoney` | True | 2 | dump only IDMAP (no method body in dump?) |
| `HandleRefreshBuyHero` | False | 2 | new season only (not in old SO) |
| `HandleBuyHero` | False | 2 | new season only (not in old SO) |
| `ChessBattleStage` | False | 124 | new season only (not in old SO) |

## Samples

### OnRefreshHeroRet
- L701210: public const IDMAP1 ZGameChess-BuyHeroView-OnRefreshHeroRet0 = 42193; // 0x0

### ReqBuyHero
- L680924: public const IDMAP0 Z_PVE-CPlayer-TAC_OnReqBuyHero0 = 16987; // 0x0
- L680925: public const IDMAP0 CSoGame-TAC_OnReqBuyHero0 = 16975; // 0x0
- L680929: public const IDMAP0 Z_PVE-CPlayer-TAC_OnReqBuyHeroToBattleGround0 = 17047; // 0x0

### SearchACGHero
- L671537: public const IDMAP0 TableCore-SearchACGHero0 = 5613; // 0x0
- L671538: public const IDMAP0 ZGame-DataBaseManager-SearchACGHero20 = 5614; // 0x0
- L671539: public const IDMAP0 TableDataDelegate-SearchACGHero0 = 5612; // 0x0

### SearchACGHero2
- L671538: public const IDMAP0 ZGame-DataBaseManager-SearchACGHero20 = 5614; // 0x0

### SearchACGHeroAndStar
- L671551: public const IDMAP0 ZGame-DataBaseManager-SearchACGHeroAndStar20 = 5626; // 0x0
- L671552: public const IDMAP0 TableDataDelegate-SearchACGHeroAndStar0 = 5625; // 0x0

### GetMyPlayerModel
- L676943: public const IDMAP0 ZGameChess-ChessBattleModel-GetMyPlayerModel0 = 12159; // 0x0
- L748500: public const IDMAP2 ZGameChess-V_ArsenalEquipStoreCtrl-GetMyPlayerModel0 = 107836; // 0x0

### get_MyPlayerId
- L676942: public const IDMAP0 ZGameChess-ChessBattleModel-get_MyPlayerId0 = 12160; // 0x0

### GetMatchPlayerId
- L701104: public const IDMAP1 ZGameChess-ChessBattleModel-GetMatchPlayerId0 = 42051; // 0x0

### GetPlayer
- L178859: public sealed class TAC_TCmdC2SRequestBatchGetPlayerInfo : JceStruct
- L225512: public const IDMAP0 ZGameClient-TAC_TCmdC2SRequestBatchGetPlayerInfo-get_i8ChairID0 = 9077; // 0x0
- L225513: public const IDMAP0 ZGameClient-TAC_TCmdC2SRequestBatchGetPlayerInfo-set_i8ChairID0 = 9078; // 0x0

### GetPlayerRankByID
- L686587: public const IDMAP0 ZGameChess-ChessBattleModel-GetPlayerRankByID0 = 24986; // 0x0

### UpdateBattleMap
- L704488: public const IDMAP1 ZGameChess-PlayerModel-UpdateBattleMap0 = 46795; // 0x0

### get_Instance
- L29906: public static TraceLoggingTypeInfo`1 get_Instance() { }
- L56248: public static Func`2 get_Instance() { }
- L56268: internal TElement <get_Instance>b__1_0(TElement x) { }

### IsUseBuyheroview_iPad
- L700355: public const IDMAP1 ZGameChess-ChessUtil-IsUseBuyheroview_iPad0 = 40782; // 0x0
- L764389: public const IDMAP2 ZGameChess-GuideStageBattleScreen-IsUseBuyheroview_iPad0 = 138347; // 0x0

### CurBuyViewIsOpen
- L701171: public const IDMAP1 ZGameChess-CommonBattleScreen-CurBuyViewIsOpen0 = 42126; // 0x0

### GetBattleModel
- L672345: public const IDMAP0 ZGameChess-ChessModelManager-GetBattleModel0 = 6751; // 0x0

### PlayerListPanel
- L620812: public class AllInPlayerListPanel : TKUIBehaviour
- L628770: public class OBPlayerListPanel : UIPanel
- L629484: public class PlayerListPanel : UIPanel

### PlayerListItem
- L374344: public class RoundSelectPlayerListItem : TKUIBehaviour
- L482947: public class PlayerListItem_pc : PlayerListItem
- L483484: public class RoundSelectPlayerListItem_pc : RoundSelectPlayerListItem

### HextechAugmentsCtrl
- L296745: public class HeroHextechAugmentsCtrl
- L511932: public class HextechAugmentsCtrl : BaseStore
- L671917: public const IDMAP0 Z_PVE-HextechAugmentsCtrl-HasChangeHexTurn0 = 6017; // 0x0

### ChessPlayerUnit
- L370936: public class ChessPlayerUnitExpressionController
- L371197: public class ChessPlayerUnitMountModuleBase
- L371210: public class ChessPlayerUnitMountModulesController

### ChessPlayerController
- L618313: public class ChessPlayerController : IService
- L677487: public const IDMAP0 ZGameChess-ChessPlayerController-SetActive0 = 12818; // 0x0
- L677617: public const IDMAP0 ZGameChess-ChessPlayerController-UpdateAllUnitInfoPos0 = 13001; // 0x0

### BuyHeroView
- L285750: public class UICommandBuyHeroViewStatus : BaseChessUICommand
- L287880: public class OPT_BuyHeroViewStatus : IOperationProcess, IWorldObject
- L290926: public class AITreeNode_ManageBuyHeroView : AITreeNodeBase

### DataBaseManager
- L283872: public class DataBaseManagerExtend : Singleton`1
- L284635: public class DataBaseManagerUnique : Singleton`1
- L493909: public class DataBaseManager : Singleton`1

### PlayerModel
- L370810: protected override Void OnProcessPlayerModelMessage(ObservableMessage msg) { }
- L542317: public class PlayerModel : ObservableObject
- L614693: protected virtual Void OnMyPlayerModelMessage(ObservableMessage msg) { }

### ReqRefresh
- L675734: public const IDMAP0 Z_PVE-CPlayer-TAC_OnReqRefreshSameHero0 = 10700; // 0x0
- L675737: public const IDMAP0 Z_PVE-CPlayer-TAC_OnReqRefreshTargetLevelHeroBuyList0 = 10708; // 0x0
- L680920: public const IDMAP0 Z_PVE-CPlayer-TAC_OnReqRefreshBuyHeroList0 = 17032; // 0x0

### GetTinyModel
- L678006: public const IDMAP0 ZGameChess-ChessModelManager-GetTinyModel0 = 13482; // 0x0
- L684180: public const IDMAP0 ZGameChess-PlayableResManager-GetTinyModelType0 = 21548; // 0x0

### UpdateNameAndMoney
- L718284: public const IDMAP1 ZGameChess-HeroRoot-UpdateNameAndMoney0 = 69526; // 0x0
- L751467: public const IDMAP2 ZGameChess-HeroCardShow-UpdateNameAndMoney0 = 113187; // 0x0

### HandleRefreshBuyHero
- L617700: protected virtual Void HandleRefreshBuyHero(Object payloadParam) { }
- L701211: public const IDMAP1 ZGameChess-ChessBattleStage-HandleRefreshBuyHero0 = 42192; // 0x0

### HandleBuyHero
- L617698: protected virtual Void HandleBuyHero(Object payloadParam) { }
- L701209: public const IDMAP1 ZGameChess-ChessBattleStage-HandleBuyHero0 = 42147; // 0x0

### ChessBattleStage
- L329909: public class ChessTeamLeaderBattleStage : ChessBattleStage
- L374546: public class ChallengeModeBattleStage : ChessBattleStage
- L374695: public class ChessTrainBattleStage : ChessBattleStage
