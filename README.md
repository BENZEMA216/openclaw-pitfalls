# OpenClaw 部署踩坑记录

> 从零开始在腾讯云服务器上配置 OpenClaw AI Agent Gateway 的完整避坑指南。

**环境**: Ubuntu / 腾讯云 CVM / Node.js v22 / OpenClaw 2026.2.9

## 目录

- [1. Google Gemini CLI OAuth 集成](#1-google-gemini-cli-oauth-集成)
- [2. 模型配置与 API 端点](#2-模型配置与-api-端点)
- [3. 浏览器控制服务](#3-浏览器控制服务)
- [4. Skill 系统](#4-skill-系统)
- [5. Telegram Bot 集成](#5-telegram-bot-集成)
- [6. 实用脚本](#6-实用脚本)

---

## 快速参考

| 配置项 | 路径 |
|--------|------|
| 主配置 | `~/.openclaw/openclaw.json` |
| Auth Profiles | `~/.openclaw/agents/main/agent/auth-profiles.json` |
| OAuth 凭证 | `~/.openclaw/credentials/oauth.json` |
| 自定义 Skills | `~/.openclaw/skills/` |
| 工作区 Skills | `~/.openclaw/workspace/skills/` |
| 会话日志 | `~/.openclaw/agents/main/sessions/` |
| 浏览器数据 | `~/.openclaw/browser/openclaw/user-data/` |
