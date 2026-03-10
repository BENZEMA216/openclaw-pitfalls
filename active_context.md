# OpenClaw Active Context

Last updated: 2026-03-10

## 当前运行状态

运行中，v2026.3.2（**有新版 v2026.3.8 待更新，含 gpt-5.4 支持**）。
主模型: openai-codex/gpt-5.3-codex

## ⚡ 待执行：更新 OpenClaw

```bash
source ~/.nvm/nvm.sh && npm update -g openclaw
systemctl --user restart openclaw-gateway
```

## 已修复（2026-03-10）AGENTS.md 两处发图 bug

### Bug 1：自检通过后不发，等用户确认
- 自检协议只写了"不通过→不发"，没写"通过→立即发"
- bot 养成了生图后只报路径、等用户说"发"的习惯
- 修复：加第 4 条"全部通过 → 立即调用 message 工具发图，不等确认"

### Bug 2：谎称"不能把本地文件发到群里"
- 根因：AGENTS.md 有"软链接路径会被拦截"的警告，bot 泛化成"本地文件不能发"
- 修复：行为红线加第 7 条，明确 message 工具完全支持发图到群聊

## 模型 ID 规律（已验证）

| 模型 | Provider ID | 状态 |
|------|-------------|------|
| GPT-5.3-Codex | openai-codex/gpt-5.3-codex | 可用 ✅ 当前 |
| GPT-5.4 | openai-codex/gpt-5.4 | ⏳ 需更新至 v2026.3.8 |
| GPT-5.4-Codex | openai-codex/gpt-5.4-codex | ❌ 不存在 |

## ⚠️ 已知坑：session model 覆盖

sessions.json 里每个 session 有独立 model 字段，优先级高于全局配置。
修复：手动把对应 session 的 model 字段设为 null。

## 待处理问题

### HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张），bot 每次心跳都报告
- 需要清掉或明确是否继续
