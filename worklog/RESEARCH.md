# 原版 libJCC.so 研究结论（纠正方向后）

日期: 2026-07-19  
样本: `jcc-controller-work/extract/assets/emu/libJCC.so` (1149112 bytes)  
对照: 真机 jcc-scan 2026-07-18 / dump.cs

---

## 用户纠正（必须遵守）

1. **不要重写功能**。自动拿牌、对手、海克斯等逻辑在原 SO 内已实现。  
2. **只要把新赛季「读内存用的数据」放到正确位置**。  
3. 自动拿牌 = **纯内存**（`ReqBuyHero` 等），不是点屏幕。  
4. 「对手预测」= **读内存里下一局对手是谁**（`GetMatchPlayerId` 等），不是行为预测。

---

## 原 SO 工作方式（已搞清）

### 启动与 IL2CPP

日志字符串完整描述了启动流水线：

- xdl_open(`libil2cpp.so`)
- resolve: `il2cpp_domain_get`, `class_from_name`, `class_get_method_from_name`, `runtime_invoke`, …
- `il2cpp_thread_attach`
- 多组 **DobbyHook**（TinyHero / Network / Logic / View / Database / OnRefreshHeroRet / UpdateBattleMap …）

### 类/方法：字符串 resolve（符号敏感）

二进制内可见、且被 ADRP/ADD 引用的关键符号包括：

| 符号 | 用途（推断） |
|------|----------------|
| `BuyHeroView` + `OnRefreshHeroRet` | 商店刷新 hook |
| `ReqBuyHero` | 购买（自动拿牌） |
| `SearchACGHero` / `SearchACGHero2` | 英雄表 |
| `DataBaseManager` + `get_Instance` | 表单例 |
| `GetMyPlayerModel` / `get_MyPlayerId` | 自己 |
| `GetMatchPlayerId` / `GetPlayer` / `GetPlayerRankByID` | **下一局对手/对阵** |
| `PlayerListPanel` / `PlayerListItem` / `PlayerHeadInfo` | 头像列表 |
| `ChessBattleModel` / `ChessBattleGlobal` / `ChessBattleLogicPlayer` | 对局 |
| `PlayerModel` + `UpdateBattleMap` | 地图/对局更新 hook |
| `HextechAugmentsCtrl/StaticField` | **海克斯** |
| `ChessPlayerUnit` / `ChessPlayerController` | 棋手单位 |
| `OPPONENT_BOARD:` / `CLEAR` | 站位推送协议 |
| `IsUseBuyheroview_iPad` / `CurBuyViewIsOpen` | 商店 UI 状态 |

**未见** `HandleRefreshBuyHero` 字符串 → 原版绑的是 `OnRefreshHeroRet`。  
当前 dump 仍有 IDMAP `BuyHeroView-OnRefreshHeroRet`；是否还有方法体需运行时验证。

### 字段：未见 iID/iCost 等字段名字符串

→ 字段访问**大概率是 LDR/STR 立即数**（或 field API 但未导出符号名字符串）。  
`.text` 中常见立即数统计（样本）:

| imm | 出现次数 | 扫描新赛季对应 |
|-----|----------|----------------|
| 0x10 | 很多 | Hero iID |
| 0x18 | 很多 | Hero sName |
| 0x60 | 239 | Hero iCost |
| 0xf8 | 39 | Hero sHeroPaintSmall |
| 0x14 | 61 | UnitData heroId |
| 0x148 | 6 | UnitData Level |
| 0x1b0 | 37 | CBU screen head |

**注意**：0x10/0x18 极常见，不能无脑全部当成 Hero 字段。  
**可靠改法**：在「SearchACGHero2 返回值使用点」反汇编，只 patch 那条读链路上的立即数。

### 协议（与 Java UI）

- TCP `127.0.0.1:31338`
- GET/SET/DO/PUSH 中文 key（牌库、海克斯品质、头像位置、三星预警、对手预测、自动购买、弹窗拦截、对手站位…）
- **不含「我们重写功能」**；我们只要让 SO 内部读数正确，协议输出就会恢复。

---

## 赛季失效真正原因（推断优先级）

1. **Hook 目标方法改名/argc 变** → `class_get_method_from_name` 失败 → 商店/自动买全死  
2. **关键类字段布局变** → LDR 立即数错 → 读到垃圾/空  
3. **类命名空间变** → `class_from_name` 失败  
4. 次要：反作弊/注入时机  

牌库「有点用」若来自**我们自己写的 SO**，不能说明原 SO 已修好。

---

## 正确工程路线

```
A. 清单
   - 原 SO 符号表（已有 strings + xrefs）
   - 新赛季 dump/scan：同名方法是否存在、字段偏移

B. 验证（需设备，最少打扰用户）
   - 原 SO 注入后看 log.txt：哪些 Hook %d/N 是 0
   - 定位「第一个失败的 resolve」

C. 补丁（按失败点）
   1) 方法名字符串 / 旁路到新方法名（等长或洞穴跳转）
   2) 字段立即数：仅 patch 证据链上的 LDR
   3) 类名/命名空间字符串

D. 打回 Controller + 固定 keystore → 发布
```

---

## 当前产物位置

- `worklog/REV-libJCC.md` — 段、字符串、xref、立即数统计  
- `worklog/REV-funcs.md` — OnRefreshHeroRet / ReqBuyHero / GetMyPlayerModel 反汇编窗口  
- `worklog/rev_summary.json` — 机器可读摘要  
- 固定签名：`signing/jcc-controller.release.keystore`

---

## 下一步（研究继续，暂不扰用户）

1. 对 `SearchACGHero2` / `ReqBuyHero` / `GetMatchPlayerId` / `HextechAugmentsCtrl` 做完整函数级反汇编与「字段立即数证据链」  
2. 对照 dump.cs：这些方法是否仍在、签名是否变  
3. 起草 `PATCH-TABLE.md`（文件偏移 → 旧值 → 新值）  
4. 自动化 patch 脚本 + 本地校验  
5. 有 PATCH 可测时再找用户装一局看原版 log  

---

## 明确不做

- 再写一套自动买/预测/海克斯「业务逻辑」  
- 用点击屏幕代替内存购买  
- 在未搞清原 SO 读点前发布「完整功能」大包  
