# PATCH-TABLE（原 libJCC.so × 新赛季扫描）

## 结论摘要（P1 完成）

### 英雄表 TACG_Hero_Client — **无需改二进制**

原 SO 解包函数 `@0x7e4bc` 读字段：

| 指令 | 立即数 | 含义 | 新赛季扫描 | 动作 |
|------|--------|------|------------|------|
| `ldr w,[x0,#0x10]` | 0x10 | iID | 0x10 | **MATCH 不改** |
| `ldr x,[x0,#0x18]` | 0x18 | sName* | 0x18 | **MATCH 不改** |
| `ldp x,[x21,#0xf0]` | 0xf0/0xf8 | sHeroPaint / Small | 0xf0/0xf8 | **MATCH 不改** |
| `ldr w,[x21,#0x38]` | 0x38 | iQuality | 0x38 | **MATCH 不改** |
| `ldr w,[x21,#0x60]` | 0x60 | iCost | 0x60 | **MATCH 不改** |
| `ldr w,[x21,#0x34]` | 0x34 | iStar | 0x34 | **MATCH 不改** |

→ **「牌库读表」相关字段布局与当前赛季一致。**  
原 SO 若注入成功且 `SearchACGHero*` resolve 成功，英雄表应能读。  
用户看到的「只商店有进度」来自我们**自研 SO**，不能说明原 SO 字段过期。

### 方法符号 — 原 SO 字符串 vs dump

| 符号 | 原 SO | dump | 动作 |
|------|-------|------|------|
| OnRefreshHeroRet | 有 | 仅 IDMAP 1 处 | 运行时验证 hook；若失败再改绑 HandleRefreshBuyHero |
| ReqBuyHero | 有 | 有 | 不改字符串 |
| SearchACGHero2 | 有 | 有 | 不改 |
| GetMatchPlayerId | 有 | 有 | 不改（下一局对手） |
| GetMyPlayerModel | 有 | 有 | 不改 |
| HextechAugmentsCtrl | 有 | 有 | 不改 |
| PlayerListPanel | 有 | 有 | 不改 |
| PlayerHeadInfo | 有 | **dump 0 hits** | 可能改名；待运行时 log |
| HandleRefreshBuyHero | **无** | 有 | 仅当 OnRefresh 失败时才做代码级改绑 |
| ChessBattleStage | **无** | 有 | 原 SO 未用此名 |

### 字段 API

原 SO **无** `il2cpp_field_from_name` 等字符串 → 字段靠 **硬编码 LDR**。  
英雄链已核对 MATCH。其它结构（UnitData/PlayerModel）需按函数逐个对，有差异再进表。

---

## 实际失效点（优先级）

1. **注入/Hook 失败**（OnRefreshHeroRet resolve 失败、Dobby 失败）→ 功能全哑  
2. **非英雄结构偏移变了** → 站位/对手/海克斯错  
3. **不是** 英雄 0x10/0x18/0x60 过期（已否定）

---

## 可执行补丁列表（当前）

| ID | 文件偏移 | 旧 | 新 | 状态 |
|----|----------|----|----|------|
| HERO-* | — | — | — | **无补丁（已匹配）** |

后续有差异再追加行：`file_off, size, old_bytes, new_bytes, reason`

---

## 交付策略（本阶段）

1. 发布 **原版逻辑 SO**（未乱改立即数）+ 正确 v2/v3 签名的 Controller 大包  
2. 文档说明：字段匹配；若仍挂看原 SO `files/log.txt` 里 Hook 计数  
3. 下一阶段：根据 log 失败项做 **定点** 字符串/立即数补丁  

---

## 证据文件

- `P1-symbol-diff.md`
- `P1-hero-offset-chain.md`
- `REV-funcs.md` / `REV-libJCC.md`
- 解包函数 VA `0x7e4bc`
