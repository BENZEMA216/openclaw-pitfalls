# OpenClaw Active Context

Last updated: 2026-03-06

## 当前运行状态

正常运行，v2026.3.2，last restart 2026-03-05 23:00。
**主模型: openai-codex/gpt-5.4**（全局配置 + sessions.json 覆盖已清除）

## 模型 ID 规律（已验证）

| 模型 | Provider ID | 状态 |
|------|-------------|------|
| GPT-5.2-Codex | openai-codex/gpt-5.2-codex | 可用 |
| GPT-5.3-Codex | openai-codex/gpt-5.3-codex | 可用 |
| GPT-5.4 | openai-codex/gpt-5.4 | 可用 ✅ 当前 |
| GPT-5.4-Codex | openai-codex/gpt-5.4-codex | ❌ 不存在 |

**规律**：GPT-5.4 起不再有 `-codex` 后缀，直接用 `gpt-5.4`。

## ⚠️ 已知坑：session model 覆盖

`sessions.json` 里每个 session 有独立 `model` 字段，优先级高于全局配置。
用 `/model xxx` 命令设置的模型会持久化到这里，`/reset` 不会清它。

**症状**：全局改了模型，新 session 还是显示旧模型。
**修复**：手动把 sessions.json 里对应 session 的 `model` 字段设为 null。

已清除：`agent:main:telegram:group:-1003314716158` 的 `model: gpt-5.2-codex` 覆盖。

## 待处理问题

### ⚠️ HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张）写在 HEARTBEAT.md，bot 每次心跳都报告
- 需要：清掉该条目，或明确是否继续任务

## 已修复（2026-03-05）

- contextPruning (ttl: 15m, softTrimRatio: 0.15, contextTokens: 60000)
- timeoutSeconds: 1800
- imageModel fallbacks: gemini-3-flash-preview + gemini-2.5-flash
- AGENTS.md: 姿势自检 + Logo 4路径协议
