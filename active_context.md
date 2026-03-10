# OpenClaw Active Context

Last updated: 2026-03-11

## 当前运行状态

运行中，v2026.3.2（**有新版 v2026.3.8 待更新，含 gpt-5.4 支持**）。
主模型: openai-codex/gpt-5.3-codex

## ✅ OpenClaw Debugger Console（已上线）

- **路径**：/root/.openclaw/debugger/（main.py + index.html）
- **服务**：systemd user service `openclaw-debugger`，端口 8899，开机自启
- **访问**：`ssh -L 8899:localhost:8899 root@43.160.242.46 -N` → http://localhost:8899
- **功能**：Sessions 时间线 / Memory 预览 / Assets Gallery / Logs 实时流 / Config 高亮

```bash
# 管理
systemctl --user status openclaw-debugger
systemctl --user restart openclaw-debugger
```

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
