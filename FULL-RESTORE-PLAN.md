# Controller 完整恢复计划（不含转区）

## 用户约定

- 本次安装只是验证「换新数据可行」
- **下次给用户装的必须是完整恢复版**
- **不做转区**

## 原版功能清单与状态

| 功能 | 协议 | 状态 | 说明 |
|------|------|------|------|
| 牌库列表 | GET:牌库 | **已有** | 新赛季字段 OK |
| 牌库剩余/总数 | GET:牌库 rem:total | **进行中** | 已接费用池 total；owned 需局内统计 |
| 商店显示 | SET:商店显示 | **协议已接** | 开关已存 |
| 自动购买 | SET:自动购买 | **协议已接** | 购牌逻辑待接商店槽 |
| 弹窗拦截 | SET:弹窗拦截 | **协议已接** | 需 hook 弹窗关闭 |
| 对手站位 | SET+PUSH OPPONENT_BOARD | **协议已接** | 需局内坐标/棋子 |
| 三星预警 | GET:三星预警 | **协议已接** | 格式已按 UI 解析器定义 |
| 海克斯品质 | GET:海克斯品质 | **协议已接** | `q0,q1,q2` |
| 头像位置 | GET:头像位置 | **协议已接** | `WxH:n:op\|x,y,self\|...` |
| 对手预测 | GET:对手预测 | **协议已接** | 暂 EMPTY |
| 日志 | GET:日志 / DO:清空日志 | **已有** | |
| 退出游戏 | DO:退出游戏 | 安全忽略 | 不强制杀进程 |
| 转区 | * | **不做** | 固定回 0/OK |

## 协议格式（UI 硬编码）

### 牌库
`id:name:cost:rem:total[:icon],...`

### 海克斯
`0-3,0-3,0-3`

### 头像位置
`{W}x{H}:{count}:{opIdx}|{x},{y},{0|1}|...`

### 三星预警
`meta|rank,a,b,c,name:id,nm,cnt,cost,star,icon;...|...`

### 对手站位 PUSH
`PUSH:OPPONENT_BOARD:{w},{h}|{x},{y},{id},{star},{cost},{icon}|...`  
`PUSH:OPPONENT_BOARD_CLEAR`

## 实现路径

1. **协议层** — 全部 key 合法应答（避免 UI 空转/崩）← 本轮已铺
2. **牌库 remaining** — 统计全场棋子 owned，hook 商店刷新
3. **站位 PUSH** — 读对手棋盘单位 + 坐标换算
4. **预警** — 按玩家聚合棋子计数
5. **海克斯** — HextechAugments 字段
6. **自动购买 / 弹窗** — ReqBuyHero + 弹窗类 hook
7. **打进 39MB 原包 + v2/v3 签名** — 完整版再让用户装

## 仓库

- 内核开发：`jcc-shell-apk`（libJCC.so）
- 成品大包：`jcc-controller-251`（原 Controller + 新 SO）
- 扫描：`jcc-scan`
