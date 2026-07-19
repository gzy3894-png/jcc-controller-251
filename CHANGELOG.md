# Changelog

## [1.1.0] — 2026-07-20

### 版本治理
- **统一下载入口**：仅本仓库 `Releases/Latest` → `JCC-Controller.apk`
- 废弃随意标签名（full-1.0.x / 2.6.x 仅历史）
- 固定直链：`.../releases/latest/download/JCC-Controller.apk`

### 功能（继承 full-1.0.7）
- 真机注入：hybrid 内核嵌进 `JCC.sh`（不再只换 emu/libJCC.so）
- 日志：只写 `files/log.txt`，标记 `[FULL-1.1.0]`
- 对局探测：`hb lobby why=` / `hb IN_BATTLE`
- 牌库扫表、阵容自动买、预测/预警协议（进局后）

## 历史（勿再装）

| 旧标签 | 说明 |
|--------|------|
| full-1.0.0～1.0.7 | 迭代中，入口混乱 |
| 2.6.x / hybrid | 更早试验包 |
