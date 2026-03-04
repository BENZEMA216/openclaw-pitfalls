---
name: openclaw-deploy
description: "OpenClaw 部署避坑经验库 - 包含 14 条在腾讯云上部署 OpenClaw AI Agent Gateway 的踩坑记录。加载后 Agent 自带所有历史部署经验，遇到已知问题直接走正确路径。激活条件：(1) 新部署 OpenClaw gateway (2) 遇到 OpenClaw 配置/环境/修复问题 (3) 在腾讯云 CVM 上运行 OpenClaw (4) 调试 google-gemini-cli 提供商 (5) 配置 OpenClaw 浏览器功能 (6) 管理 OpenClaw 进程和 skill。关键词：OpenClaw、部署、gateway、腾讯云、gemini、浏览器、headless、systemd、skill、session、踩坑"
user-invocable: true
metadata:
  openclaw:
    emoji: "🛡️"
  env_fingerprint:
    platform: "linux (Ubuntu, 6.1.0-42-cloud-amd64)"
    cloud: "腾讯云 CVM"
    node: "v22.22.0"
    openclaw: "2026.2.9"
    model_provider: "google-gemini-cli (Google One AI Pro)"
    model: "gemini-3-pro-preview"
---

# OpenClaw 部署避坑经验库

> 14 条从零开始在腾讯云上部署 OpenClaw AI Agent Gateway 的实战踩坑记录。
> 每条记录包含错误信号、错误路径、正确路径和根因分析。
> 详细 YAML 记录存放在 `capsules/` 目录下。

---

## 使用场景

- 首次部署 OpenClaw gateway 到服务器
- 遇到 OpenClaw 运行时错误需要排查
- 配置 google-gemini-cli 模型提供商
- 配置无头浏览器功能
- 管理 OpenClaw 进程（启动/停止/重启）
- 安装或调试 skill
- 调试淘宝/天猫相关功能

---

## 快速配置参考

| 配置项 | 路径 |
|--------|------|
| 主配置 | `~/.openclaw/openclaw.json` |
| Auth Profiles | `~/.openclaw/agents/main/agent/auth-profiles.json` |
| OAuth 凭证 | `~/.openclaw/credentials/oauth.json` |
| 自定义 Skills | `~/.openclaw/skills/` |
| 工作区 Skills | `~/.openclaw/workspace/skills/` |
| 会话日志 | `~/.openclaw/agents/main/sessions/` |
| 浏览器数据 | `~/.openclaw/browser/openclaw/user-data/` |
| systemd 用户级服务 | `~/.config/systemd/user/openclaw-gateway.service` |

---

## 踩坑快速索引

遇到问题时，先按错误信号匹配，直接跳转到正确处理方式。

### CONFIG 类 -- 配置问题

#### PIT-001 [CRITICAL] OAuth 凭证自动合并不生效

- **信号**: `No API key found for provider 'google-gemini-cli'`
- **根因**: oauth.json 写入后，gateway 不会自动合并到 auth-profiles.json
- **正确做法**:
  1. 手动在 `~/.openclaw/agents/main/agent/auth-profiles.json` 的 profiles 中添加 `"google-gemini-cli:default"` 条目
  2. 条目格式: `{"type": "oauth", "provider": "google-gemini-cli", "refresh": "<token>", "access": "<token>", "expires": <ms>, "projectId": "<id>", "email": "<email>"}`
  3. 重启 gateway，发送测试消息验证

#### PIT-002 [CRITICAL] Cloud Code Assist API 端点 404

- **信号**: `HTTP 404 on https://cloudcode-pa.googleapis.com/v1beta/models/...`
- **根因**: google-gemini-cli 用的是 Cloud Code Assist API，不是标准 Gemini API
- **正确做法**:
  1. 端点: `POST https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse`
  2. 请求体需要外层包装: `{"project": "<id>", "model": "gemini-3-pro-preview", "request": {"contents": [...], "generationConfig": {...}}, "userAgent": "pi-coding-agent", "requestId": "pi-<ts>-<rand>"}`
  3. Headers 必须包含: `Authorization: Bearer <token>`, `User-Agent: google-cloud-sdk vscode_cloudshelleditor/0.1`, `X-Goog-Api-Client: gl-node/22.17.0`
  4. 这三大区别 (端点路径 / 认证方式 / 请求体结构) 是手动调试 API 时必须知道的

#### PIT-003 [HIGH] 浏览器 profile 选错致服务不可达

- **信号**: `Can't reach the OpenClaw browser control service`
- **根因**: 默认 profile 是 chrome (需扩展通信)，无头服务器必须用 openclaw profile (内置 Playwright/CDP)
- **正确做法**:
  在 `openclaw.json` 中设置:
  ```json
  {
    "browser": {
      "defaultProfile": "openclaw",
      "headless": true,
      "noSandbox": true
    }
  }
  ```

#### PIT-004 [HIGH] headless/noSandbox 配置位置错误

- **信号**: `Config validation error` 或 Chrome 以 headed+sandbox 模式启动
- **根因**: headless 和 noSandbox 是 browser 顶级配置，不是 per-profile 配置
- **正确做法**:
  headless 和 noSandbox 放在 `browser` 对象顶层，不要放在 `browser.profiles.openclaw` 内部。profile 对象只接受 `cdpPort / cdpUrl / driver / color` 四个字段。

#### PIT-006 [MEDIUM] baidu-search 缺少 API KEY

- **信号**: `Error: BAIDU_API_KEY must be set`
- **根因**: baidu-search 技能缺少环境变量，OpenClaw 不会自动禁用缺依赖的技能
- **正确做法**:
  - 方案 A: 在 openclaw.json 的 `agents.defaults.env` 中添加 `BAIDU_API_KEY`
  - 方案 B (推荐): `mv ~/.openclaw/skills/baidu-search/SKILL.md ~/.openclaw/skills/baidu-search/SKILL.md.disabled`，用内置 Brave Web Search 替代

#### PIT-014 [CRITICAL] Agent 不知道新安装的 skill

- **信号**: Agent 在对话中不使用新安装的 skill，继续用旧方法
- **根因**: OpenClaw session 创建时拍 skillsSnapshot，之后不会更新。重启 gateway 不会更新已有 session
- **正确做法**:
  1. 归档旧 session: `mv ~/.openclaw/agents/main/sessions/<session-id>.jsonl archive/`
  2. 清理 sessions.json 中对应条目
  3. `systemctl --user restart openclaw-gateway`
  4. 发送新消息触发新 session 创建，检查 skillsSnapshot 包含新 skill

---

### ENV 类 -- 环境问题

#### PIT-005 [MEDIUM] browser-use Python CLI 超时

- **信号**: `BrowserStartEvent timed out after 30.0s`
- **根因**: browser-use v0.12.0 的 CLI 在无头环境有事件循环 bug
- **正确做法**:
  用 Playwright 直接编写替代脚本: `pip install playwright && playwright install chromium`，编写 browse.py 使用 `playwright.sync_api`。放到 `~/.openclaw/skills/browser-use/scripts/browse.py`

#### PIT-007 [MEDIUM] taobao skill 缺少 uv 依赖

- **信号**: `uv: command not found`
- **根因**: maishou 技能的 metadata 只声明了 python3，漏了 uv
- **正确做法**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  source ~/.bashrc
  uv --version
  ```

#### PIT-008 [LOW] 淘宝反爬触发 punish tab

- **信号**: 大量 `bixi.alicdn.com/punish/` tab 弹出
- **根因**: 服务器 IP + headless Chrome 默认 UA 触发淘宝风控
- **正确做法**:
  1. 定期清理: `openclaw browser tabs` → `openclaw browser close <tab-id>`
  2. 脚本中用 `wait_until="load"` 做 fallback (淘宝 networkidle 可能永不触发)
  3. 设置 `Accept-Language: zh-CN,zh;q=0.9,en;q=0.8`
  4. 控制访问频率，考虑代理

#### PIT-009 [MEDIUM] NVM 环境未加载致命令找不到

- **信号**: `nohup: failed to run command 'openclaw': No such file or directory`
- **根因**: SSH non-interactive shell 不会自动 source .bashrc，NVM PATH 未加载
- **正确做法**:
  ```bash
  # 方案 A: 先加载 NVM
  export NVM_DIR="/root/.nvm"
  [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
  nohup openclaw gateway > /root/openclaw-gateway.log 2>&1 &

  # 方案 B: 用完整路径
  nohup /root/.nvm/versions/node/v22.22.0/bin/openclaw gateway > /root/openclaw-gateway.log 2>&1 &
  ```

#### PIT-011 [MEDIUM] kill 进程后自动重启 (systemd --user)

- **信号**: `kill -9` 后进程秒级重新出现 (新 PID)
- **根因**: OpenClaw 安装时创建了用户级 systemd 服务 (Restart=always)，`systemctl list-units` 看不到用户级服务
- **正确做法**:
  ```bash
  # 查找: 检查进程父进程 → systemd --user
  cat /proc/<PID>/status | grep PPid
  systemctl --user list-units --type=service | grep openclaw

  # 管理:
  systemctl --user restart openclaw-gateway.service   # 重启
  systemctl --user stop openclaw-gateway.service      # 停止
  systemctl --user status openclaw-gateway.service    # 状态
  journalctl --user -u openclaw-gateway.service -f    # 日志
  ```
  **关键**: 系统级 `systemctl` 和用户级 `systemctl --user` 是两套独立系统

#### PIT-012 [CRITICAL] store-teardown 技能 Telegram 执行超时

- **信号**: `600s embedded run timeout`，agent 尝试多种搜索方式全部失败
- **根因**: SKILL.md 没有告诉 agent 用什么工具，agent 自行探索浪费 5+ 轮工具调用
- **正确做法**:
  1. SKILL.md 必须明确指定搜索工具: 关键词搜索用 maishou 技能 (`uv run scripts/main.py search --source=1 --keyword='<品牌>'`，2 秒出结果)
  2. SKILL.md 开头加禁止事项 (禁止浏览器搜索淘宝、禁止安装 Playwright 等)
  3. **教训**: SKILL.md 必须告诉 agent "用什么工具做什么事"，不能让 agent 自己探索

---

### REPAIR 类 -- 修复与诊断

#### PIT-010 [HIGH] 模型超时误判为 API 故障

- **信号**: `Profile google-gemini-cli:default timed out (possible rate limit). Trying next account...`
- **根因**: 误诊链: gateway 超时 → 以为 API 有问题 → 用错误格式测 API → 404 → 更确信 API 坏了。实际 API 完全正常
- **正确做法**:
  1. 先用正确端点格式测 API (见 PIT-002)，确认 API 本身是否正常
  2. 超时可能原因: model warm-up / apiTimeout 过低 / 复杂工具链累积
  3. 调整超时:
     ```json
     {
       "agents": {
         "defaults": {
           "runTimeout": 900,
           "apiTimeout": 120
         }
       }
     }
     ```
  4. **教训**: 排查问题时，先确认测试方法本身是正确的，再下结论

#### PIT-013 [HIGH] curl 下载 alicdn 图片返回 1x1 GIF

- **信号**: 下载结果为 49 bytes 的 `GIF image data, version 89a, 1 x 1`
- **根因**: 阿里 CDN 防盗链基于 HTTP Accept header (不是 IP)，curl 默认 `Accept: */*` 被拦截
- **正确做法**:
  用 Python urllib，关键是 Accept header:
  ```python
  headers = {
      "User-Agent": "Mozilla/5.0 ... Chrome/131",
      "Referer": "https://www.taobao.com/",
      "Accept": "image/webp,image/apng,image/*,*/*;q=0.8",
      "Accept-Language": "zh-CN,zh;q=0.9",
  }
  req = urllib.request.Request(url, headers=headers)
  resp = urllib.request.urlopen(req)
  ```
  或使用封装好的 `download_images.py` 脚本。**不要用 curl、ScraperAPI 或 weserv.nl**

---

## 部署检查清单

首次部署或重新部署时，按此顺序检查：

### 1. 基础环境
- [ ] NVM 已安装且 Node v22 可用 (PIT-009)
- [ ] uv (Python 包管理器) 已安装 (PIT-007)
- [ ] Playwright + Chromium 已安装 (`pip install playwright && playwright install chromium`)

### 2. OpenClaw 核心配置
- [ ] `openclaw.json` 中 browser 配置正确 -- `defaultProfile: "openclaw"`, `headless: true`, `noSandbox: true` 均在 browser 顶级 (PIT-003, PIT-004)
- [ ] `auth-profiles.json` 中有 `google-gemini-cli:default` 条目 (PIT-001)
- [ ] 超时配置合理 -- `runTimeout: 900`, `apiTimeout: 120` (PIT-010)

### 3. Skill 管理
- [ ] 不需要的 skill (如 baidu-search) 已禁用 (PIT-006)
- [ ] 每次安装新 skill 后，清理旧 session 让 agent 重建 skillsSnapshot (PIT-014)
- [ ] SKILL.md 中明确指定了工具链，不要让 agent 自行探索 (PIT-012)

### 4. 进程管理
- [ ] 确认 OpenClaw 是 systemd --user 管理的还是 nohup 手动启动的 (PIT-011)
- [ ] 如果是 systemd，用 `systemctl --user` 系列命令管理 (PIT-011)

### 5. 淘宝/天猫相关
- [ ] 图片下载用 Python urllib / download_images.py，不用 curl (PIT-013)
- [ ] 控制浏览器访问淘宝的频率，处理 punish tab (PIT-008)

---

## 诊断流程

遇到未知问题时，按以下顺序排查：

```
1. 读取 gateway 日志
   journalctl --user -u openclaw-gateway.service -f
   或 cat /root/openclaw-gateway.log

2. 检查 session 日志
   ls -lt ~/.openclaw/agents/main/sessions/*.jsonl | head -5
   查看最新 session 的 jsonl 文件

3. 确认环境
   node --version     # 应为 v22.22.0
   openclaw --version # 应为 2026.2.9
   uv --version       # 应已安装

4. 确认配置
   cat ~/.openclaw/openclaw.json
   cat ~/.openclaw/agents/main/agent/auth-profiles.json

5. 确认进程状态
   systemctl --user status openclaw-gateway.service
   ps -ef | grep openclaw

6. 如果怀疑 API 问题，用 PIT-002 的正确端点格式直接测试
   不要用标准 Gemini API 格式
```

---

## 关键路径配置模板

以下是经过验证的 `openclaw.json` 核心配置:

```json
{
  "browser": {
    "defaultProfile": "openclaw",
    "headless": true,
    "noSandbox": true
  },
  "agents": {
    "defaults": {
      "runTimeout": 900,
      "apiTimeout": 120,
      "env": {
        "BAIDU_API_KEY": "<如需百度搜索则填写>"
      }
    }
  }
}
```

---

## 如何追加新的踩坑记录

遇到新坑时，按以下步骤记录：

### 1. 创建 YAML 文件

在 `capsules/` 目录下创建 `PIT-0XX.yaml`，编号递增 (当前最大为 PIT-014)。

### 2. 使用标准格式

```yaml
id: PIT-015
trigger_time: "YYYY-MM-DD HH:MM"
category: config | env | repair
severity: critical | high | medium | low

problem:
  signal: "具体的错误信号/日志（用户看到的第一现象）"
  description: |
    问题的本质描述。
  env_fingerprint:
    platform: linux
    node: v22.22.0
    openclaw: "2026.2.9"

error_process:
  - step: "做了什么"
    result: "得到了什么错误结果"

correct_process:
  - step: "应该怎么做"
    detail: "具体操作细节"

root_cause: |
  根因分析。
confidence: 0.9
blast_radius:
  files: ["受影响的文件"]
  scope: "影响范围描述"
```

### 3. 更新本文件

在上方对应分类 (CONFIG / ENV / REPAIR) 中添加快速索引条目，格式:

```markdown
#### PIT-0XX [SEVERITY] 简短标题

- **信号**: `错误信号`
- **根因**: 一句话根因
- **正确做法**: 简明步骤
```

### 4. 更新 README.md 的踩坑索引表

在 README.md 的索引表中添加新行。

---

## 详细记录

所有 14 条踩坑记录的完整 YAML 文件存放在 `capsules/` 目录下:

| ID | 文件 | 严重度 | 分类 | 问题 |
|----|------|--------|------|------|
| PIT-001 | `capsules/PIT-001.yaml` | critical | config | OAuth 自动合并不生效 |
| PIT-002 | `capsules/PIT-002.yaml` | critical | config | Cloud Code Assist API 端点 404 |
| PIT-003 | `capsules/PIT-003.yaml` | high | config | 浏览器 profile 选错致服务不可达 |
| PIT-004 | `capsules/PIT-004.yaml` | high | config | headless/noSandbox 配置位置错误 |
| PIT-005 | `capsules/PIT-005.yaml` | medium | env | browser-use Python CLI 超时 |
| PIT-006 | `capsules/PIT-006.yaml` | medium | config | baidu-search 缺少 API KEY |
| PIT-007 | `capsules/PIT-007.yaml` | medium | env | taobao skill 缺少 uv 依赖 |
| PIT-008 | `capsules/PIT-008.yaml` | low | env | 淘宝反爬触发 punish tab |
| PIT-009 | `capsules/PIT-009.yaml` | medium | env | NVM 环境未加载致命令找不到 |
| PIT-010 | `capsules/PIT-010.yaml` | high | repair | 模型超时误判为 API 故障 |
| PIT-011 | `capsules/PIT-011.yaml` | medium | env | kill 进程后自动重启 (systemd --user) |
| PIT-012 | `capsules/PIT-012.yaml` | critical | env | store-teardown 技能执行超时 |
| PIT-013 | `capsules/PIT-013.yaml` | high | env | curl 下载 alicdn 图片返回 1x1 GIF |
| PIT-014 | `capsules/PIT-014.yaml` | critical | config | Agent 不知道新安装的 skill |

需要查看某条记录的完整错误路径和详细根因分析时，读取对应的 YAML 文件。
