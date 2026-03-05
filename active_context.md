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

## 已知行为问题

### 长 session 导致两个模型全部 timeout（严重）
- 现象：`All models failed (2): openai-codex: LLM request timed out | gemini: LLM request timed out`
- 根因：session bb331759 从 14:45 跑到 20:15，context 达 727KB，LLM 推理时间超过 10 分钟硬限制
- 日志特征：`embedded run timeout: timeoutMs=600000` + `durationMs=630166`
- 临时解法：`/reset` 或 `/new` 开新 session
- 长期方案：配置 `compaction` 或 `contextPruning`，防止单 session 无限增长

### Bot 长 session 后截断任务（只做3张就 NO_REPLY）
- 根因：session 上下文过长，Codex 做最小批次就退出（timeout 的前驱症状）

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- design-assets：`/root/.openclaw/media/design-assets/`（物理），`/root/.openclaw/design-assets/` 为软链接
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
- creo.md：`/root/.openclaw/memory/creo.md`（存在）
