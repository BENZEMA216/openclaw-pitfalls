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
- 根因：vision 自检 prompt 只检查服装/文字/比例，从不验证模特姿势是否与 prompt 一致
- 现象：bot 生成"走路姿态"图但模特实际在站立，自检仍 PASS，图被发出
- 修复：AGENTS.md 自检清单新增一项：
  `- [ ] 姿势/场景是否与 prompt 一致？（要求走路就必须有走路动作，不能用其他姿势顶替）`

## 已调查但不修复的问题

### Codex server_error 不触发 fallback
- 全量日志只出现 1 次，偶发抖动，无需修复
- Interactive agent 无 server_error retry 机制（只有 cron 有）

### Bot 长 session 后截断任务（只做3张就 NO_REPLY）
- 根因：session 上下文过长（445KB+），Codex 做最小可交付批次就退出
- 临时解法：新开 session 重新触发

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- design-assets：`/root/.openclaw/media/design-assets/`（物理），`/root/.openclaw/design-assets/` 为软链接
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
- creo.md：`/root/.openclaw/memory/creo.md`（存在）
