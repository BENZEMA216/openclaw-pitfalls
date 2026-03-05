# OpenClaw Active Context

Last updated: 2026-03-06

## 当前运行状态

正常运行，v2026.3.2，last restart 2026-03-05 23:00，uptime ~3h。
主模型: openai-codex/gpt-5.2-codex

## 待处理问题

### ⚠️ HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张）写在 HEARTBEAT.md，bot 每次心跳都报告一次（已重复 20+ 次）
- 需要：清掉该条目，或明确决定是否继续这个任务

### ⚠️ bb331759 群聊 session 膨胀
- 文件大小：2.7MB（群聊 BENZEMA & 飞天螺旋桨）
- 已配置 contextPruning 但对已膨胀 session 效果有限
- 建议：群里发 `/reset` 开新 session

## 已修复（2026-03-05）

### PIT-016: Context Bloat → Timeout
- 加了 contextPruning (mode: cache-ttl, ttl: 15m, softTrimRatio: 0.15)
- contextTokens: 60000（让剪枝比例有意义）
- timeoutSeconds: 1800（防止超时双模型全失败）

### PIT-017: imageModel 429 Fallback
- imageModel.fallbacks 已配置：gemini-3-flash-preview + gemini-2.5-flash

### AGENTS.md 更新
- 自检加入姿势/场景一致性检查
- Logo/文字处理协议：4条路径 + 禁止从AI图裁切

## Creo Fragments 状态

当前 F-001 ～ F-010（最新 5 条 F-006~F-010 写于 2026-03-05，均为 negative 类型）
- F-006: 不看图发图
- F-007: 抠图合成割裂感
- F-008: 被否方案不能复用
- F-009: 废话过多/自我表扬
- F-010: 面料光泽中间状态

## 已知非阻塞错误

- wecom 插件启动失败：`api.registerHttpHandler is not a function`（每次重启都有，不影响主功能）
