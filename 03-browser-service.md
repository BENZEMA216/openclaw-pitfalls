# 坑 3: 浏览器控制服务

## 背景

OpenClaw 内置浏览器控制服务，通过 Chrome DevTools Protocol (CDP) 控制 Chromium/Chrome。在无头服务器上配置有很多坑。

## 坑点

### 3.1 默认 Profile 选择

**问题**: 默认浏览器 profile 是 `chrome`，这个 profile 需要安装 Chrome 扩展来与 OpenClaw 通信。在无头服务器上无法安装扩展，导致报错：

```
⚠️ Can't reach the OpenClaw browser control service
```

**解决**: 使用 `openclaw` profile（内置 Playwright/Chromium），在 `openclaw.json` 中配置：

```json
{
  "browser": {
    "defaultProfile": "openclaw",
    "headless": true,
    "noSandbox": true
  }
}
```

### 3.2 headless 和 noSandbox 位置

**问题**: 把 `headless` 和 `noSandbox` 放在 profile 对象里面，导致配置校验失败。

**正确**: 这两个是**顶级** browser 配置，不是 per-profile 的：

```json
// ❌ 错误：放在 profile 里
{
  "browser": {
    "profiles": {
      "openclaw": {
        "headless": true,
        "noSandbox": true
      }
    }
  }
}

// ✅ 正确：顶级配置
{
  "browser": {
    "defaultProfile": "openclaw",
    "headless": true,
    "noSandbox": true
  }
}
```

Profile 对象只接受: `cdpPort`, `cdpUrl`, `driver`, `color`。

### 3.3 root 用户运行 Chrome

**问题**: 在 root 用户下启动 Chrome 报错 sandbox 相关错误。

**解决**: 必须设置 `noSandbox: true`。Chrome 启动参数会自动加上：
```
--no-sandbox --disable-setuid-sandbox --disable-dev-shm-usage
```

### 3.4 淘宝反爬机制

**问题**: 浏览器打开淘宝搜索页面后，会触发大量 `bixi.alicdn.com/punish/` 验证弹窗 tab，占用内存。

**应对**:
- 定期清理多余 tab: `openclaw browser close <tab-id>`
- 使用 `openclaw browser tabs` 列出所有 tab
- 设置合理的 viewport 和 User-Agent 来减少触发几率
- `networkidle` 加载策略可能超时，建议 fallback 到 `load`:
  ```python
  try:
      page.goto(url, timeout=20000, wait_until="networkidle")
  except:
      page.goto(url, timeout=30000, wait_until="load")
  ```

### 3.5 browser-use Python CLI 不可用

**问题**: 从 ClawHub 安装的 `browser-use` 技能使用 Python CLI (`browser-use` 命令)，但在服务器上启动浏览器时超时：

```
BrowserStartEvent timed out after 30.0s
```

**解决**: 自行编写 Playwright 脚本 (`browse.py`) 作为替代，直接使用 Playwright API。参见 [scripts/browse.py](scripts/browse.py)。

### 3.6 OpenClaw browser 命令参考

```bash
# 启动浏览器
openclaw browser start

# 打开 URL（新 tab）
openclaw browser open "https://example.com"

# 列出所有 tab
openclaw browser tabs

# 聚焦 tab（用 ID 前缀即可）
openclaw browser focus 77A67E

# 截图（当前 tab）
openclaw browser screenshot              # 保存到 ~/.openclaw/media/browser/
openclaw browser screenshot --full-page   # 全页面截图

# 页面快照（提取结构化内容）
openclaw browser snapshot
openclaw browser snapshot --format aria   # 无障碍树格式

# 关闭 tab
openclaw browser close <tab-id>

# 停止浏览器
openclaw browser stop
```
