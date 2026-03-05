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
- 全量日志中只出现 1 次 — 偶发抖动，无需修复
- Interactive agent 消息无 server_error retry 机制（只有 cron 有）

## 已知行为问题（未修复）

### Bot 长 session 后截断任务（只做3张就 NO_REPLY）
- 现象：用户要求每个产品出5张场景图，bot 只做了3张第一个产品就停
- 根因：session 文件过长（445KB，从下午14:00跑到17:43），context 过长时 Codex 偷懒，做最小可交付批次就退出
- 触发条件：session 持续数小时、context 极长的多产品批量任务
- 临时解法：新开 session 重新触发（@bot 继续做完所有产品）
- 长期方案：考虑设置 `contextPruning` 或 `compaction` 配置，或让 bot 做完批次后用 cron/subagent 继续

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- design-assets 路径：`/root/.openclaw/media/design-assets/`（物理路径，软链接在 `/root/.openclaw/design-assets/`）
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
- creo.md：`/root/.openclaw/memory/creo.md`（存在，Preflight 正常）
