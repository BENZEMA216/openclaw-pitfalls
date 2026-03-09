# OpenClaw Active Context

Last updated: 2026-03-10

## 当前运行状态

运行中，v2026.3.2（**有新版 v2026.3.8 待更新**）。
主模型: openai-codex/gpt-5.3-codex

## ⚡ 待执行：更新 OpenClaw

```bash
source ~/.nvm/nvm.sh && npm update -g openclaw
# 然后重启 gateway
systemctl --user restart openclaw-gateway
```

v2026.3.8 可能包含 gpt-5.4 支持（PR #36590 已合并）。

## 已修复（2026-03-10）

### 图片生成后不发送的问题
- **根因**：AGENTS.md 自检协议只写了"不通过→不发"，没写"通过→立即发"
- bot 养成了生成图后告知文件路径、等用户再说一遍"发"的习惯
- **修复**：在自检协议第 3 条后加了第 4 条：
  "全部通过 → 立即调用 `message` 工具发图，不等用户确认，不说「你要的话我再发」"

## 模型 ID 规律（已验证）

| 模型 | Provider ID | 状态 |
|------|-------------|------|
| GPT-5.3-Codex | openai-codex/gpt-5.3-codex | 可用 ✅ 当前 |
| GPT-5.4 | openai-codex/gpt-5.4 | ⏳ 需更新至 v2026.3.8 |
| GPT-5.4-Codex | openai-codex/gpt-5.4-codex | ❌ 不存在 |

## ⚠️ 已知坑：session model 覆盖

`sessions.json` 里每个 session 有独立 `model` 字段，优先级高于全局配置。
修复：手动把对应 session 的 `model` 字段设为 null。

## 待处理问题

### ⚠️ HEARTBEAT.md 有遗留 PENDING 任务
- 1747 wellbeing 场景图（3张）写在 HEARTBEAT.md，bot 每次心跳都报告
- 需要清掉或明确是否继续
