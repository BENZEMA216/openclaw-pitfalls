# OpenClaw Active Context

Last updated: 2026-03-05

## 当前状态

服务正常运行，v2026.3.2，主模型 openai-codex/gpt-5.2-codex。

## 近期已解决问题

### PIT-020: Bot 拒绝发图（SOUL.md 规则幻觉）
- 根因：模型误读"外部操作前先确认"+"群聊不过度发言"为禁止发图
- 修复：SOUL.md Boundaries 加了明确例外条款；AGENTS.md 加了 message 工具调用示范

### PIT-021: ⚠️ Message failed — design-assets 路径被拦截
- 根因：`/root/.openclaw/media/design-assets` 是软链接，`realpath()` 解析到 `/root/.openclaw/design-assets/`，不在 allowed roots 里
- 修复：反转软链接方向 — 把 design-assets 物理移入 `media/`，原路径变软链接

## 已调查但不修复的问题

### Codex server_error 不触发 fallback
- 现象：`{"type":"server_error"}` 导致 agent run 失败，无自动重试/切换
- 调查结论：
  - 全量日志中只出现 1 次（Mar 05 17:14:51）— 偶发抖动，非系统性问题
  - `shouldFallbackOnError()` 只处理 embedding 错误，不匹配 server_error
  - `retryOn: ["server_error"]` 仅在 cron schema 存在，interactive agent 无此机制
  - `fallbacks` 数组在 AgentModelSchema 里存在，但 runtime 层没有 API 错误触发的切换逻辑
- 结论：无需修复。偶发时用户重发消息即可；Gemini 不作为基模。

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- 配置 fallback：`google-gemini-cli/gemini-3-pro-preview`（仅 embedding fallback 有效）
- design-assets 路径：`/root/.openclaw/media/design-assets/`（物理路径，软链接在 `/root/.openclaw/design-assets/`）
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
