# OpenClaw Active Context

Last updated: 2026-03-05

## 当前状态

服务正常运行，v2026.3.2，主模型 openai-codex/gpt-5.2-codex。

## 近期已解决问题

### PIT-020~021: 发图相关修复（已完成）

### 自检漏洞：姿势/场景不验证（已修复）

### 长 session 双模型 timeout（已修复）
- contextPruning（ttl=15m, softTrimRatio=0.15）+ contextTokens=60000 + timeoutSeconds=1800

### imageModel 429 容量限流（已修复）
- imageModel 加 fallbacks：gemini-3-flash-preview → google/gemini-2.5-flash

### browser tool token mismatch（已修复）
- 现象：`browser failed: gateway closed (1008): unauthorized: gateway token mismatch`
- 根因：gateway restart 后旧 agent-browser 进程（pid 230491）未被 systemd 干净杀掉，用旧 token 占着 browser server，新 gateway 连不上
- 修复：手动 kill 旧进程 + 完整重启 gateway（23:00）
- 规律：每次 gateway restart 后如果看到 "Found left-over process" 日志，需确认 browser tool 是否正常

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- imageModel：`gemini-3-pro-preview`（fallbacks: gemini-3-flash-preview, gemini-2.5-flash）
- timeoutSeconds: 1800，contextTokens: 60000，pruning ttl=15m
- design-assets：`/root/.openclaw/media/design-assets/`（物理路径）
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
