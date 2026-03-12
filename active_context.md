# OpenClaw Active Context

Last updated: 2026-03-12

## 当前阻塞问题（未解决）

Code tab 架构被用户否定，正在重新设计。

### 用户核心诉求
"为什么 Pencil 可以直接连接本地 Claude Code，而我们的 web UI 不行？"

### 技术根因
- Pencil 是本地 MCP 服务器，Claude Code CLI 通过 MCP 协议（同机进程间通信）直接调用
- Web UI 在浏览器里，浏览器无法反向访问本地机器（安全沙箱），只能连远程服务器
- 所以 diff / deploy 需要在 Claude Code 侧解决，不是在浏览器侧

### 待决策：两个方案

**方案 A: Claude Code Hook 自动部署**
- 在 ~/.claude/settings.json 加 PostToolUse hook
- 每次 Claude Code 修改 /tmp/debugger_*.html|py 后，自动 SCP 到服务器
- Web UI 只展示当前服务器状态 + 上次部署时间
- 优点：零手动操作；缺点：无 diff 审阅机会

**方案 B: 本地 MCP 服务器**
- 写一个本地 MCP server，提供 deploy_file / get_server_file / show_diff 工具
- Claude Code 修改文件后主动调用 MCP 工具展示 diff、请用户确认、再部署
- 真正复刻 Pencil 模式
- 优点：有交互确认；缺点：需要配置 MCP

**用户未做选择**，session 在此结束。

## 已完成

### Code tab 第一版（已部署，但方案被否）
- 添加了 Browser File API diff viewer（用户手动选文件）
- 新增 /api/file/current 和 /api/deploy 端点
- 问题：file-panel 锁在 Code tab，不是全局可访问

### 历史 Bug 修复（iter 10-12）
- #graph-detail-body white-space pre-wrap 双空行 bug
- .tool-header-err CSS 缺失
- 分页重复 bug（offset=0 作双义）

