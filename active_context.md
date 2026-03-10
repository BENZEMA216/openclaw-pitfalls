# OpenClaw Active Context

Last updated: 2026-03-11

## 当前运行状态

运行中，v2026.3.2（**有新版 v2026.3.8 待更新，含 gpt-5.4 支持**）。
主模型: openai-codex/gpt-5.3-codex

## ⚡ 下一步：OpenClaw Debugger Console

用户需求：精细化调试，不想每次 ssh 进去跑 python 脚本。

### 规划方案
- **技术栈**：Python + FastAPI + 纯 HTML，跑在服务器 localhost:8899
- **访问方式**：SSH tunnel `ssh -L 8899:localhost:8899 root@43.160.242.46`
- **核心功能**：
  1. Session 时间线 — 消息 + tool call 名称/输入/输出完整链路
  2. Live 日志 — 流式 journalctl，支持关键词过滤
  3. Session 列表 — channel 与 session 绑定关系、文件大小、最后活跃
  4. 内存快照 — AGENTS.md / openclaw.json / aesthetic fragments 渲染

**状态**：用户确认需求，待开始实现。

## ⚡ 待执行：更新 OpenClaw

```bash
source ~/.nvm/nvm.sh && npm update -g openclaw
systemctl --user restart openclaw-gateway
```
v2026.3.8 含 gpt-5.4 支持。

## 已修复（2026-03-10）AGENTS.md 两处发图 bug

1. 自检通过后不发，等确认 → 加"全部通过立即发"规则
2. 谎称不能发图 → 行为红线第 7 条

## 模型 ID 规律

- GPT-5.3-Codex: openai-codex/gpt-5.3-codex ✅ 当前
- GPT-5.4: openai-codex/gpt-5.4 ⏳ 需更新至 v2026.3.8
- GPT-5.4-Codex: ❌ 不存在
