# OpenClaw Active Context

Last updated: 2026-03-06

## 当前运行状态

正常运行，v2026.3.2，last restart 2026-03-05 23:00。
**主模型: openai-codex/gpt-5.3-codex**

## 模型 ID 规律（已验证）

| 模型 | Provider ID | 状态 |
|------|-------------|------|
| GPT-5.3-Codex | openai-codex/gpt-5.3-codex | 可用 ✅ 当前 |
| GPT-5.4 | openai-codex/gpt-5.4 | ⏳ 等 OpenClaw 更新 |
| GPT-5.4-Codex | openai-codex/gpt-5.4-codex | ❌ 不存在 |

## GPT-5.4 为何不可用（已确认根因）

- gpt-5.4 在 Codex CLI 官方已正式支持（推荐模型）
- OpenClaw PR #36590 (feat: add gpt-5.4 support for API and Codex OAuth) 已合并
- 但**尚未发布到 npm**，当前 npm 最新版仍是 2026.3.2
- 等 OpenClaw 新版发布后，`npm update -g openclaw` 即可用

## ⚠️ 已知坑：session model 覆盖

`sessions.json` 里每个 session 有独立 `model` 字段，优先级高于全局配置。
`/model` 命令设置会持久化，`/reset` 不会清它。
修复：手动把对应 session 的 `model` 字段设为 null。

## 待处理问题

### ⚠️ HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张），bot 每次心跳都报告
- 需要：清掉该条目，或明确是否继续任务

## 已修复（2026-03-05）

- contextPruning + contextTokens: 60000 + timeoutSeconds: 1800
- imageModel fallbacks
- AGENTS.md: 姿势自检 + Logo 4路径协议
