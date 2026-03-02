# 坑 2: 模型配置与 API 端点

## 坑点

### 2.1 Cloud Code Assist API 端点格式

**问题**: `google-gemini-cli` 提供商使用的 **不是** 标准 Google Generative AI API，而是 Cloud Code Assist API。用标准 Gemini API 格式调用会返回 404。

**错误示范**:
```
# 404！格式完全错误
https://cloudcode-pa.googleapis.com/v1beta/models/gemini-3-pro-preview:generateContent
```

**正确格式**:
```
POST https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse
```

请求体也不同于标准 Gemini API：

```json
// ❌ 标准 Gemini API 格式（不适用）
{
  "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
  "generationConfig": {}
}

// ✅ Cloud Code Assist API 格式
{
  "project": "acoustic-vortex-b9jrc",
  "model": "gemini-3-pro-preview",
  "request": {
    "contents": [{"role": "user", "parts": [{"text": "hello"}]}],
    "generationConfig": {"maxOutputTokens": 8192}
  },
  "userAgent": "pi-coding-agent",
  "requestId": "pi-1709123456-abc123"
}
```

**关键区别**:
- 端点路径: `/v1internal:streamGenerateContent` (不是 `/v1beta/models/{model}:generateContent`)
- 认证: `Bearer` token (不是 `?key=` 参数)
- 请求体: `contents` 包在 `request` 对象内，外层还有 `project`, `model`, `userAgent`
- 必须带特定 Headers:
  ```
  User-Agent: google-cloud-sdk vscode_cloudshelleditor/0.1
  X-Goog-Api-Client: gl-node/22.17.0
  Client-Metadata: {"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}
  ```

### 2.2 模型名切换

**问题**: 从 `google/gemini-3-flash-preview`（免费 API Key）切换到 `google-gemini-cli/gemini-3-pro-preview`（OAuth）时，配置格式。

**openclaw.json 配置**:
```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "google-gemini-cli/gemini-3-pro-preview"
      }
    }
  }
}
```

格式是 `{provider}/{model-id}`。可用的 provider 包括:
- `google` — 使用标准 Google Generative AI API + API Key
- `google-gemini-cli` — 使用 Cloud Code Assist API + OAuth
- `kimi-coding` — 使用 Moonshot/Kimi API

### 2.3 超时误判

**问题**: 日志显示 "Profile google-gemini-cli:default timed out (possible rate limit)"，误以为是 API 故障。

**真相**: 直接测试 API 响应时间仅 0.1 秒。超时是因为首次请求可能需要更长时间（模型加载），或者是 OpenClaw 网关的 `runTimeout` 配置过低。

**建议**: 在 openclaw.json 中显式设置超时：
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

### 2.4 可用模型列表

通过 Google One AI Pro 订阅（google-gemini-cli），以下模型确认可用：
- `gemini-2.5-flash` ✅
- `gemini-2.5-pro` ✅
- `gemini-3-flash-preview` ✅
- `gemini-3-pro-preview` ✅

> 源码位置: `node_modules/@mariozechner/pi-ai/dist/providers/google-gemini-cli.js`
