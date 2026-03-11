# OpenClaw Active Context

Last updated: 2026-03-12

## 当前优先级

Debugger 代码走查完成（12 轮迭代，~20 个 bug 修复）。新增 Claude Code 集成面板。

## 最近的关键决策

### Claude Code Bridge 功能 (2026-03-12)

在 Debugger 新增 **Code 标签页**，实现本地 Claude Code 与服务器调试工具的联动。

**架构：**
```
Browser (debugger at 43.160.242.46)
  ↕ fetch (CORS)
Local bridge (localhost:9988) → /tmp/claude-bridge.py
  ↕ subprocess
claude CLI (本地 Claude Code)
  ↓ 读写 /tmp/debugger_*.* 
Bridge → scp → 服务器部署
```

**文件：**
- `/tmp/claude-bridge.py` — 本地 HTTP bridge，端口 9988
- Debugger `index.html` — 新增 Code 标签页

**使用：**
```bash
python3 /tmp/claude-bridge.py  # 本地终端运行
# 打开 Debugger → Code tab → Connect
```

**功能：**
- 右侧 Chat 面板：对话 Claude Code，它知道 debugger 架构（system prompt 注入了 context）
- 左侧 Diff 面板：Claude 修改文件后实时展示 unified diff（红删绿增）
- Deploy 按钮：一键 scp 所有改动文件到服务器，main.py 变化时自动重启 uvicorn
- Bridge /ping 确认 claude CLI 可用

### Debugger Bug 修复总览 (Iter 5-12)

| Iter | 修复 |
|------|------|
| 5 | CSS specificity bug（graph 面板永远可见）、extractImgPaths 递归 |
| 6 | loadMoreMsgs 插入位置、refreshAssets cache bypass、**SCP 部署 bug** |
| 7 | path traversal 安全漏洞、res.ok 检查、loadSession try/catch |
| 8 | loadSessions/Memory/Assets 全无错误处理，copyMsg catch |
| 9 | renderMd + white-space:pre-wrap 双倍行距 |
| 10 | graph-detail-body pre-wrap bug、openGraphDetail res.ok |
| 11 | .tool-header-err CSS 未定义、loadGraph try/catch |
| 12 | **分页重复消息 bug**：backend offset=None 改为 Optional，前端 fetchLimit 精确计算 |

## 部署规范（重要）

```bash
# SCP 必须指定目标文件名：
sshpass -p 'Xz19990817.' scp -o StrictHostKeyChecking=no \
  /tmp/debugger_index.html root@43.160.242.46:/root/.openclaw/debugger/index.html
sshpass -p 'Xz19990817.' scp -o StrictHostKeyChecking=no \
  /tmp/debugger_main.py root@43.160.242.46:/root/.openclaw/debugger/main.py
```

## 服务器信息

- Server: 43.160.242.46:/root/.openclaw/debugger/
- Token: x_w-NfYtLw57mkbsipyifd9WIoGUR8vP
- Port: 8899 (uvicorn), proxied via nginx at /debugger/
- Restart: `cd /root/.openclaw/debugger && nohup python3 -m uvicorn main:app --host 127.0.0.1 --port 8899 > /tmp/debugger.log 2>&1 &`
