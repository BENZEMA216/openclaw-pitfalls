# OpenClaw Active Context

Last updated: 2026-03-11

## 当前优先级

Debugger 代码走查完成 5 轮迭代，主要 bug 已修复。

## 最近的关键决策

### Debugger 走查进展 (5 轮迭代，2026-03-11)

**已修复的关键 bug：**
- CSS specificity bug：`#panel-graph { display: flex }` (1-0-0) 覆盖 `.panel { display: none }` (0-1-0) → Graph 面板始终可见 → 已移除 display:flex
- `#graph-container { display: flex }` CSS rule 多余 → 已删除
- Copy button XSS：data-text attribute 不安全 → 改用 `_copyMap` (JS Map)
- `loadMoreMsgs` DOM bug：Regex 无法移除旧按钮 → 改用 `querySelector('.load-more-wrap')?.remove()`
- `selectMemChip` onclick 单引号不安全 → 改用 data attributes
- `Math.max(...[])` → `-Infinity`：空数组时崩溃 → 加长度守卫
- Assets 加载全尺寸图：`/api/image` → 改为 `/api/thumb`
- `extractImgPaths` 无法处理嵌套对象 → 改为递归 walk
- Memory 侧边栏 border 动画不可靠 → 改用 box-shadow

**新增功能：**
- Sessions 侧边栏：搜索过滤 + 刷新按钮 + 键盘导航
- Assets 侧边栏：刷新按钮
- Memory tab：刷新按钮 + 错误处理
- Trace panel：TOOL CALLS 分区（按类别着色）
- `renderMd`：支持 ul/ol 列表、HR、空行间距
- Memory file chips 显示频次 ×N
- `switchTab` 切换时重置 nav-status
- D3 CDN 加载失败错误处理
- `_copyMap` session 切换时清空

**后端修复：**
- `/api/sessions` + `/api/memory` 支持 `?_=timestamp` 强制刷新
- Assets API 加 `/api/thumb` 缩略图端点

## 阻塞项

无。Debugger 功能稳定，可继续使用。

## 部署信息

- Server: 43.160.242.46:/root/.openclaw/debugger/
- Token: x_w-NfYtLw57mkbsipyifd9WIoGUR8vP
- Port: 8899 (uvicorn), proxied via nginx at /debugger/
