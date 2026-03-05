# OpenClaw Active Context

Last updated: 2026-03-05

## 当前状态

服务正常运行，v2026.3.2，主模型 openai-codex/gpt-5.2-codex。

## 近期已解决问题

### PIT-020~021: 发图/路径修复（已完成）
### 自检漏洞：姿势/场景不验证（已修复）
### 长 session 双模型 timeout（已修复）
- contextPruning（ttl=15m, softTrimRatio=0.15）+ contextTokens=60000 + timeoutSeconds=1800
### imageModel 429 容量限流（已修复）
- imageModel fallbacks: gemini-3-flash-preview → google/gemini-2.5-flash
### browser tool token mismatch（已修复）
- 每次 restart 后旧 agent-browser 进程残留导致 token 不匹配，需完整重启

## 已知行为问题（未修复）

### Bot 对"logo拆取"的理解错误
- 现象：用户说"没有源文件，你直接拆下"，bot 用 PIL 从 AI 生成图里裁文字区域+抠背景，生成了带面料纹理/模糊的 173×100px 残图
- 根因：bot 把"拆 logo"理解为像素裁切，但 AI 图里文字是渲染进面料的，无法干净分离
- 正确做法：用 Gemini 重新生成干净的透明底文字图，或在生图 prompt 里直接描述文字位置让模型渲染
- 建议在 AGENTS.md 或 SOUL.md 加说明：从 AI 生成图里无法提取干净 logo，应重新生成

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- imageModel：`gemini-3-pro-preview`（fallbacks: gemini-3-flash-preview, gemini-2.5-flash）
- timeoutSeconds: 1800，contextTokens: 60000，pruning ttl=15m
- design-assets：`/root/.openclaw/media/design-assets/`（物理路径）
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
