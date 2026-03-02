# OpenClaw 部署踩坑记录

> 从零开始在腾讯云服务器上配置 OpenClaw AI Agent Gateway 的完整避坑指南。
>
> 记录格式参考 [EvoMap GEP 协议](https://github.com/EvoMap/evolver) 的 Capsule（实战记录）结构。

## 记录协议

每条踩坑记录采用统一的结构化格式（参考 GEP Capsule）：

```yaml
id: PIT-001                        # 唯一编号
trigger_time: "2026-03-01 14:30"   # 触发时间
category: repair | config | env    # 分类
severity: critical | high | medium | low

problem:                           # 问题描述
  signal: "具体的错误信号/日志"
  description: "问题的本质是什么"
  env_fingerprint:                 # 环境指纹
    platform: linux
    node: v22.22.0
    openclaw: 2026.2.9

error_process:                     # 错误过程（踩坑路径）
  - step: "做了什么"
    result: "得到了什么错误结果"
  - step: "又尝试了什么"
    result: "还是错"

correct_process:                   # 正确过程（正确路径）
  - step: "应该怎么做"
    detail: "具体操作"
  - step: "验证"
    detail: "如何确认修复成功"

root_cause: "根因分析"             # 为什么会踩这个坑
confidence: 0.9                    # 置信度（这个方案有多可靠）
blast_radius:                      # 影响范围
  files: ["openclaw.json"]
  scope: "模型调用"
```

## 踩坑索引

| ID | 严重度 | 时间 | 问题 | 分类 |
|----|--------|------|------|------|
| [PIT-001](capsules/PIT-001.yaml) | critical | 03-01 | OAuth 自动合并不生效 | config |
| [PIT-002](capsules/PIT-002.yaml) | critical | 03-02 | Cloud Code Assist API 端点 404 | config |
| [PIT-003](capsules/PIT-003.yaml) | high | 03-01 | 浏览器 profile 选错致服务不可达 | config |
| [PIT-004](capsules/PIT-004.yaml) | high | 03-01 | headless/noSandbox 配置位置错误 | config |
| [PIT-005](capsules/PIT-005.yaml) | medium | 03-02 | browser-use Python CLI 超时 | env |
| [PIT-006](capsules/PIT-006.yaml) | medium | 03-02 | baidu-search 缺少 API KEY | config |
| [PIT-007](capsules/PIT-007.yaml) | medium | 03-01 | taobao skill 缺少 uv 依赖 | env |
| [PIT-008](capsules/PIT-008.yaml) | low | 03-02 | 淘宝反爬触发大量 punish tab | env |
| [PIT-009](capsules/PIT-009.yaml) | medium | 03-01 | NVM 环境未加载致 openclaw 命令找不到 | env |
| [PIT-010](capsules/PIT-010.yaml) | high | 03-02 | 模型超时误判为 API 故障 | repair |
| [PIT-011](capsules/PIT-011.yaml) | medium | 03-02 | kill 进程后自动重启（systemd --user 服务） | env |

## 环境指纹

```yaml
platform: linux (Ubuntu, 6.1.0-42-cloud-amd64)
cloud: 腾讯云 CVM
node: v22.22.0
openclaw: 2026.2.9
model_provider: google-gemini-cli (Google One AI Pro)
model: gemini-3-pro-preview
```

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

## 致谢

记录格式灵感来自 [EvoMap GEP 协议](https://evomap.ai) 的 Capsule 数据结构。

Sources:
- [EvoMap/evolver - GitHub](https://github.com/EvoMap/evolver)
- [GEP Protocol Deep Dive](https://evomap.ai/blog/gep-protocol-deep-dive)
