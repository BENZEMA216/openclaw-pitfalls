# OpenClaw Active Context

Last updated: 2026-03-12

## 当前优先级

Code 标签页重新设计：从过度工程化的 bridge 方案，改为 Browser File API + 服务器 deploy endpoint。

## 下一步要做

### Code Tab：Diff Viewer + Deploy（待实现）

**用户真实需求**：Claude Code 改了本地文件后，在 Debugger UI 里 review diff，确认无误再部署。

**正确方案（无任何本地依赖）：**
1. 浏览器 File API 读取用户选择的本地文件（原生，无需 bridge）
2. 从服务器 `/api/file/current?name=index.html` 拉当前部署版本
3. 浏览器内做 diff，左右或 unified 展示
4. 点 Deploy → POST 文件内容到 `/api/deploy` → 服务器写入 + 重启 uvicorn

**需要新增的后端 endpoint：**
- `GET /api/file/current?name=index.html|main.py` → 返回当前部署文件内容
- `POST /api/deploy` → multipart 接收文件，写入 /root/.openclaw/debugger/，可选重启

**前端改动：**
- Code tab 改为：文件选择器 + diff viewer + Deploy 按钮
- 删除旧的 bridge 相关代码（chat panel、SSE streaming、bridge 连接等）
- 保留已写好的 diff CSS 样式

**用户流程：**
1. Claude Code 改完文件（终端正常用）
2. Debugger → Code tab
3. 点"打开文件" → 选 /tmp/debugger_index.html
4. 看 diff
5. 点 Deploy

**废弃：** /tmp/claude-bridge.py（过度设计，不符合产品易用性原则）

## Debugger Bug 修复总览 (Iter 5-12，已完成)

| Iter | 修复 |
|------|------|
| 6 | **SCP 部署 bug**（目标必须指定文件名） |
| 7 | path traversal 安全漏洞 |
| 9 | renderMd + white-space:pre-wrap 双倍行距 |
| 12 | **分页重复消息 bug**（offset=None Optional） |

## 部署规范

```bash
sshpass -p 'Xz19990817.' scp -o StrictHostKeyChecking=no \
  /tmp/debugger_index.html root@43.160.242.46:/root/.openclaw/debugger/index.html
```

## 服务器信息

- Server: 43.160.242.46:/root/.openclaw/debugger/
- Token: x_w-NfYtLw57mkbsipyifd9WIoGUR8vP
- Port: 8899, nginx proxy at /debugger/
