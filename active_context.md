# OpenClaw Active Context

Last updated: 2026-03-06

## 当前运行状态

正常运行，v2026.3.2，last restart 2026-03-05 23:00。
**主模型: openai-codex/gpt-5.3-codex**（刚切换，2026-03-06）

## 模型切换记录

- `gpt-5.4-codex` → Unknown model，不存在
- `gpt-5.3-codex` → 可用，hot reload 成功，无报错
- 用户确认是否保持 5.3 或回滚 5.2（待回复）

## 待处理问题

### ⚠️ HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张）写在 HEARTBEAT.md，bot 每次心跳都报告
- 需要：清掉该条目，或明确是否继续任务

### ⚠️ bb331759 群聊 session 膨胀
- 文件大小：~3MB（群聊 BENZEMA & 飞天螺旋桨）
- 建议：群里发 `/reset` 开新 session

## 已修复（2026-03-05）

- contextPruning (ttl: 15m, softTrimRatio: 0.15, contextTokens: 60000)
- timeoutSeconds: 1800
- imageModel fallbacks: gemini-3-flash-preview + gemini-2.5-flash
- AGENTS.md: 姿势自检 + Logo 4路径协议

## Creo Fragments

F-001 ～ F-010，最新5条（F-006~F-010）写于 2026-03-05，均为 negative 类型
