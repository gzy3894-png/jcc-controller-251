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

## 2026-07-19T12:25:09.9966112+08:00
### P1 DONE
- Hero field chain @0x7e4bc matches scan (no binary patch needed for hero)
- Symbol diff written P1-symbol-diff.md
- PATCH-TABLE.md: HERO no-op
- Released v2.5.3 original-kernel APK (fixed sign)
### Next P2/P3
- Runtime hook logs if user reports still broken
- Patch only confirmed mismatches (OnRefresh rename etc.)

## 2026-07-19T13:11:31.8522489+08:00
User clarified: crash on click = data/layout wrong, not guesswork.
P1 hero path MATCH does NOT mean all features safe.
P2: mapping feature xrefs to LDR imms for UnitData/board/hex/match player.

## 2026-07-19T13:32:38.0300788+08:00
### DEEP ANALYSIS DONE (no claim full fix)
- User right: crash = wrong data layout
- Hero path MATCH; crash hotspots: GetMatchPlayerId (unk20), PlayerListItem (unk11), ChessBattleModel (unk15), OPPONENT_BOARD, ReqBuyHero
- Wrote 分析结论-人话.md + DEEP-ANALYSIS.md
- Next: only patch proven imm mismatches
