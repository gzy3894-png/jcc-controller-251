# 百分百确认清单（静态证据 + 出包标准）

更新：2026-07-19

## 用户红线

1. 不要半成品催测  
2. 点功能闪退 = 数据/读点问题  
3. 功能逻辑在原 SO；自动买=内存；对手=读下一局对手  
4. 2.5.5 已回退：禁加载 hook 过头 + 商店丢失不可接受  

---

## 静态已 100% 确认的事实

### F1 — 原 SO 结构
- [x] 通过 `class_get_method_from_name` + **DobbyHook** 工作（22 处 `bl 0x10cb90`）
- [x] 全 22 个 hook 目标在现赛季 **IDMAP 均有登记**（方法元数据仍在）
- [x] 字段访问为 **LDR 立即数**，非 field_from_name

### F2 — 英雄表读点（牌库）
- [x] 函数 `0x7e4bc`：`0x10/0x18/0x34/0x38/0x60/0xf0/0xf8`  
      ≡ 扫描 `TACG_Hero_Client`  
- [x] **无需改这些立即数**

### F3 — 对手/玩家读点
- [x] `ChessBattleModel.GetMatchPlayerId` IDMAP 存在  
- [x] `ChessBattleModel.GetMyPlayerModel` / `get_MyPlayerId` IDMAP 存在  
- [x] 使用点 `0x84aa8`：`0x5c/0x64/0xbc/0x20` ≡ `PlayerModel` 钱/LastEnemyId/血/battleTurn  
- [x] **这些立即数无需改**

### F4 — 自动拿牌符号
- [x] `HeroRoot.ReqBuyHero` argc=0，IDMAP `ZGameChess-HeroRoot-ReqBuyHero0`  
- [x] **符号正确，不靠点屏**

### F5 — 商店刷新符号（原绑已失效）
- [x] 原：`BuyHeroView.OnRefreshHeroRet`  
- [x] 现 `BuyHeroView` **方法列表无此方法**（类体完整扫描）  
- [x] 替代：`ChessBattleStage.HandleRefreshBuyHero(Object)` IDMAP+方法体存在，argc=1  
- [x] **改绑是高置信补丁（2.5.4 已做）**

### F6 — 资源损坏根因
- [x] SO 对 `LoadMap` / `LoadBody` / `LoadAsset*` / `ExecuteGameStart` / `SendAttack` / `ChessLoading*` 装 DobbyHook  
- [x] 进局加载页「资源损坏」与这些 hook **因果一致**  
- [x] **现赛季必须禁用这些 hook 安装**，否则无法稳定进局  

### F7 — 2.5.5 失败原因
- [x] 在原 SO 上大面积 NOP hook，同时原商店回调链未真正给 UI 供数  
- [x] 相对 2.5.2 自研读表，**商店显示回退**  

### F8 — Hook 体字段矩阵（22 hooks）
- [x] 见 `HOOK-BODY-ANALYSIS.md`：各 handler 的对象 LDR 立即数  
- [x] 多数 immediate 在扫描偏移集合内（注意：同立即数可属多类，需结合上下文）  
- [x] Load* handlers 字段也「能匹配」——问题在 **hook 行为破坏资源管线**，不是单纯数字错  

---

## 百分百确认的产品定义（本项目）

**「百分百」= 下列每一条都有静态证据，且实现不包含已知会炸加载的 hook。**

| # | 要求 | 状态 |
|---|------|------|
| P1 | 进局加载不报资源损坏 | 设计上：**零** LoadMap/LoadBody/Asset Dobby | 实现中 |
| P2 | 牌库 GET 有完整英雄表（名/费/图/rem/total） | 路径 F2 已证；混合内核已写 | 实现中 |
| P3 | 商店显示开关不导致池数据被清空 | 协议层已规定 GET 始终可返回池 | 实现中 |
| P4 | 下一局对手从内存读取（GetMatchPlayerId / LastEnemyId） | 符号+字段 F3 已证 | 实现中 |
| P5 | 自动拿牌走 ReqBuyHero 内存调用 | 符号 F4 已证；**槽位实例链待静态钉死再启用自动 invoke** | 部分 |
| P6 | 海克斯/站位/预警 | 符号在；字段链未达百分百 → **未宣称完成** | 未完成 |
| P7 | 固定签名可覆盖升级 | keystore 已固定 | 完成 |
| P8 | 全程落盘日志 | jcc_full.log / ckpt | 完成 |

**在 P1–P4、P7、P8 全部绿之前，不要求用户测试。**  
P5 仅在实例获取链静态确认后默认开启。  
P6 未绿则 UI 对应项可 EMPTY，不算「全功能成品」。

---

## 成品路线（锁定）

```
不用「原 SO 全 hook 硬跑」（会资源损坏）
改用：

  原 Controller 大包 UI
       +
  混合内核 libJCC.so：
    - 无资源/加载 Dobby
    - 用现赛季偏移 + IDMAP 已确认方法 invoke 读数
    - 31338 协议对齐原 UI
    - 商店刷新：HandleRefreshBuyHero 仅作数据驱动（若再挂 hook 必须不碰资源）
```

等价于：「把新赛季正确读点接到原 UI 要的协议上」，  
不是重写预测算法，是 **读 GetMatchPlayerId / LastEnemyId**。

---

## 新确认（商店槽 百分百静态）

原 SO `0x7d7a4` 读商店：

| 偏移 | 含义 | 扫描 |
|------|------|------|
| BuyHeroView+0x148 | `_listHeroRoot` | **MATCH** |
| BuyHeroView+0x168 | `m_curPlayerModel` | **MATCH** |
| List+0x10 / +0x18 | items / size | IL2CPP List 惯例 |
| items+0x20+i*8 | HeroRoot* 槽 | 与 SO 一致 |
| HeroRoot+0x1b0 | `_dataId` | dump 确认 |
| HeroRoot+0x160 | `Index` | dump 确认 |
| HeroRoot.ReqBuyHero() | 自动买 | IDMAP 确认 |

→ **商店显示 + 自动买内存路径已静态钉死**（不靠猜）。

## 当前阻塞（未百分百）

1. ~~自动买实例链~~ **已解决（0x7d7a4）**  
2. **海克斯品质三元组**：子字段未扫全 → 不填假数据  
3. **站位坐标**：禁用 LoadBody 后需另找 UI 坐标  
4. **真机验收**仍是最终一步  

---

## 下一步

1. 混合内核实现 0x7d7a4 商店读 + ReqBuyHero（进行中）  
2. 补扫 HexAugmentModel  
3. 静态全绿后出 CERTIFIED 包再喊用户  

---

## 一句话

**商店/自动买读点已从原 SO 反编译钉死；资源 hook 必须禁用；英雄与对手关键字段 MATCH。**  
**未完成：海克斯子字段、站位坐标、真机总验收。**
