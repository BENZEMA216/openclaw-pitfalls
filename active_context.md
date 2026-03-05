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
- 根因：contextPruning 默认触发门槛（30% context ratio）对 Codex 大 context window 永远不触发；compaction safeguard 同理；推理时间超 10 分钟
- 修复：openclaw.json 新增配置：
  ```json
  "contextPruning": {
    "mode": "cache-ttl",
    "ttl": "15m",
    "softTrimRatio": 0.15,
    "hardClearRatio": 0.3,
    "minPrunableToolChars": 3000,
    "keepLastAssistants": 5
  },
  "contextTokens": 60000
  ```
- 已热更新（无需重启），下次对话起效

## 当前配置摘要

- 主模型：`openai-codex/gpt-5.2-codex`
- contextTokens: 60000（有效预算），pruning 每 15 分钟触发
- design-assets：`/root/.openclaw/media/design-assets/`（物理），`/root/.openclaw/design-assets/` 为软链接
- 生图输出：`/root/.openclaw/media/nano_banana2_output/`
