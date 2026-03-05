# OpenClaw Active Context

Last updated: 2026-03-05

## 当前状态

服务正常运行，v2026.3.2，主模型 openai-codex/gpt-5.2-codex。

## 近期已解决问题

### PIT-020: Bot 拒绝发图（SOUL.md 规则幻觉）
- 修复：SOUL.md 加明确例外；AGENTS.md 加 message 工具调用示范

### PIT-021: ⚠️ Message failed — design-assets 路径被拦截
- 修复：反转软链接方向，design-assets 物理在 media/ 下

### 自检漏洞：姿势/场景不验证
- 修复：AGENTS.md 自检清单新增「姿势/场景是否与 prompt 一致」

### 长 session 双模型 timeout — 已修复
- 修复：contextPruning（ttl=15m, softTrimRatio=0.15）+ contextTokens=60000 + timeoutSeconds=1800

### imageModel 429 容量限流 — 已修复
- 根因：`google-gemini-cli/gemini-3-pro-preview` 走 Google Cloud Code Assist 免费后端，高峰期服务端容量不足返回 429
- 修复：imageModel 加 fallbacks：gemini-3-flash-preview → google/gemini-2.5-flash
- 已热更新生效

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- imageModel：`gemini-3-pro-preview`（fallbacks: gemini-3-flash-preview, gemini-2.5-flash）
- timeoutSeconds: 1800，contextTokens: 60000，pruning ttl=15m
- design-assets：`/root/.openclaw/media/design-assets/`（物理路径）
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
