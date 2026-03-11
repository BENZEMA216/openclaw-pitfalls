# OpenClaw Active Context

Last updated: 2026-03-12

## 最近完成

Code tab 重构完成：从 bridge 方案改为 Browser File API + 服务器端 deploy：

- **删除**：bridge/chat panel CSS+HTML+JS（~350行，需要本地跑 python3 claude-bridge.py）
- **新增**：`LOCAL FILES` 右侧面板（280px），两个文件行各有 `Open…` 按钮（Browser File API）
- **新增**：纯 JS LCS diff 引擎（patience sort），浏览器端实时计算 unified diff
- **新增** main.py 两个 endpoint：
  - `GET /api/file/current?name=` — 返回服务器文件内容（用于 diff 基线）
  - `POST /api/deploy` — 接收 `{name, content}`，写入服务器；main.py 变更时自动重启 uvicorn
- `deployChanges()` 直接调 `/api/deploy`，零本地依赖

## 使用方式

1. Claude Code 改完本地文件
2. Debugger → Code tab → Open… 选本地文件
3. 左侧看 diff（红删绿增）
4. 确认后 Deploy to Server

## 历史 Bug 修复（迭代10-12）

- iter 10: `#graph-detail-body` white-space pre-wrap 双空行 bug + openGraphDetail res.ok check
- iter 11: `.tool-header-err` CSS 缺失 + loadGraph try/catch
- iter 12: 分页重复 bug（offset=0 作双义），改为 `offset: int = None`

## 服务器状态

- uvicorn 运行在 127.0.0.1:8899
- 文件路径：/root/.openclaw/debugger/
- index.html + main.py 均已部署
