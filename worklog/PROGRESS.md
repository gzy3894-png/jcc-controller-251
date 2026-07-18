# Controller 原 SO 补丁进度

## 正确目标（用户确认）
- 不重写功能逻辑
- 只把新赛季数据（偏移/符号）放到原 libJCC.so 正确位置
- 自动拿牌=内存操作；对手预测=读下一局对手（内存）

## 会话记录

## 2026-07-19T02:01:01.8156450+08:00 RESEARCH phase
- Confirmed: original SO uses string resolve for methods + DobbyHook
- No il2cpp_field_* APIs → field access is hardcoded LDR immediates
- Key symbols: OnRefreshHeroRet, ReqBuyHero, GetMatchPlayerId, HextechAugmentsCtrl, PlayerListPanel
- ChessBattleStage ABSENT in SO (uses other classes)
- Wrote worklog/RESEARCH.md REV-libJCC.md REV-funcs.md rev_summary.json
- Next: per-function offset evidence chains + PATCH-TABLE
