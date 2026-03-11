# OpenClaw Active Context

Last updated: 2026-03-11

## 当前优先级

Debugger 代码走查持续进行中，10 轮迭代完成，累计修复 ~18 个 bug。

## 最近的关键决策

### Debugger 走查进展 (10 轮迭代，2026-03-11)

**Iter 5 修复：**
- `#panel-graph { display: flex }` CSS specificity bug → Graph 面板始终可见 → 移除 display:flex
- Assets 侧边栏 refresh 按钮
- `switchTab` 切换时重置 nav-status
- `extractImgPaths` 改为递归 walk 处理嵌套对象

**Iter 6 修复：**
- `loadMoreMsgs` insertBefore 位置错误 → 旧消息插入到 trace panel 之前 → 改用 `querySelector('.msg')` 作为锚点
- `refreshAssets` 不绕过后端缓存 → 加 `?_=timestamp` + 后端 `list_assets(request: Request)` 支持 force-bypass
- 移除 `renderTracePanel` 中死代码 `maxCount`
- **发现部署 bug**: scp 多文件到目录时保留 basename，`/tmp/debugger_index.html` → `debugger_index.html`（不是 `index.html`）→ 此前所有部署都打到了错误文件名

**Iter 7 修复：**
- `jumpToMemory` 缺少 `res.ok` 检查 → 404 时静默失败
- `loadSession` 无 try/catch → 网络错误时 "Loading…" 永不消失
- `toolResult` 消息无 tool-cat 类 → 无语义左边框颜色
- 后端 `get_session` / `get_session_trace` 路径穿越漏洞 → session_id 未校验 → 加 `^[\w.-]+$` 正则 + resolved path 前缀检查

**Iter 8 修复：**
- `loadSessions`、`loadMemory`、`loadAssets` 全无 try/catch + res.ok 检查 → 静默失败 → 统一加错误展示
- `copyMsg` 无 `.catch()` → 剪贴板拒绝时静默失败

**Iter 9 修复：**
- `renderMd` + `white-space: pre-wrap` 双倍行距 bug → HTML 块元素间的 `
` 在 pre-wrap 容器中渲染为空行 → 改为 plain text 包 `<div>`、`join('')`、移除 `.mem-side-body` 和 `.mem-content-area` 的 `pre-wrap`
- `loadMoreMsgs` 无 error handling

**Iter 10 修复：**
- `#graph-detail-body` 也用 `renderMd()` 但仍有 `white-space: pre-wrap` → 移除
- `openGraphDetail` 无 `res.ok` 检查 → 404/403 时静默显示空内容 → 加检查+错误展示

## 部署规范（重要）

SCP 必须指定目标文件名，不能用目录作为目标：
```bash
# 正确:
sshpass ... scp /tmp/debugger_index.html root@43.160.242.46:/root/.openclaw/debugger/index.html
sshpass ... scp /tmp/debugger_main.py root@43.160.242.46:/root/.openclaw/debugger/main.py
```

## 服务器信息

- Server: 43.160.242.46:/root/.openclaw/debugger/
- Token: x_w-NfYtLw57mkbsipyifd9WIoGUR8vP
- Port: 8899 (uvicorn), proxied via nginx at /debugger/
- Restart: `cd /root/.openclaw/debugger && nohup python3 -m uvicorn main:app --host 127.0.0.1 --port 8899 > /tmp/debugger.log 2>&1 &`
