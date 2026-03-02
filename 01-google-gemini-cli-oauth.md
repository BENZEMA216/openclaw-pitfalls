# 坑 1: Google Gemini CLI OAuth 集成

## 背景

使用 Google One AI Pro 订阅（通过 Gemini CLI 的 OAuth 认证）作为 OpenClaw 的模型提供商，替代免费 API Key。

## 坑点

### 1.1 OAuth 凭证格式

**问题**: 不知道 `oauth.json` 该怎么写，文档没有说明。

**解决**: 通过阅读 pi-ai 库源码 (`@mariozechner/pi-ai`) 发现格式：

```json
// ~/.openclaw/credentials/oauth.json
{
  "google-gemini-cli": {
    "refresh": "1//0gd2RGW1B...",
    "access": "ya29.a0ATkoCc...",
    "expires": 1772295524090,
    "projectId": "acoustic-vortex-b9jrc",
    "email": "your-email@gmail.com"
  }
}
```

关键字段：
- `refresh`: 通过 Gemini CLI 授权获取的 refresh token
- `access`: 当前的 access token（会过期）
- `expires`: access token 过期时间戳（毫秒）
- `projectId`: 通过 `discoverProject` API 获取
- `email`: Google 账号邮箱

### 1.2 OAuth 自动合并不生效

**问题**: pi-ai 有 `mergeOAuthFileIntoStore` 函数，理论上会自动把 `oauth.json` 合并到 `auth-profiles.json`，但实际不生效。模型调用报错：

```
⚠️ Agent failed before reply: No API key found for provider 'google-gemini-cli'
```

**解决**: 手动写入 auth-profiles.json：

```json
// ~/.openclaw/agents/main/agent/auth-profiles.json
{
  "version": 1,
  "profiles": {
    "google-gemini-cli:default": {
      "type": "oauth",
      "provider": "google-gemini-cli",
      "refresh": "1//0gd2RGW1B...",
      "access": "ya29.a0ATkoCc...",
      "expires": 1772295524090,
      "projectId": "acoustic-vortex-b9jrc",
      "email": "your-email@gmail.com"
    }
  }
}
```

**关键**: `type` 必须是 `"oauth"`，不是 `"api_key"`。

### 1.3 Token 刷新

**问题**: access token 会过期（通常 1 小时）。

**解决**: OpenClaw 会使用 `refreshGoogleCloudToken` 自动刷新，但前提是 `refresh` token 正确。可以用以下脚本手动刷新测试：

```javascript
// refresh_token.mjs
// 这两个值来自 Gemini CLI 开源代码，是公开的 OAuth 客户端凭证
// 在 Gemini CLI 源码中搜索 "apps.googleusercontent.com" 即可找到
const CLIENT_ID = "<GEMINI_CLI_CLIENT_ID>";      // 格式: xxx.apps.googleusercontent.com
const CLIENT_SECRET = "<GEMINI_CLI_CLIENT_SECRET>"; // 格式: GOCSPX-xxx

const resp = await fetch("https://oauth2.googleapis.com/token", {
  method: "POST",
  headers: { "Content-Type": "application/x-www-form-urlencoded" },
  body: new URLSearchParams({
    client_id: CLIENT_ID,
    client_secret: CLIENT_SECRET,
    refresh_token: "YOUR_REFRESH_TOKEN",
    grant_type: "refresh_token",
  }),
});
const data = await resp.json();
console.log("New access token:", data.access_token);
console.log("Expires in:", data.expires_in, "seconds");
```

> 注意: `CLIENT_ID` 和 `CLIENT_SECRET` 来自 Gemini CLI 源码，是公开的 OAuth 客户端凭证。

### 1.4 获取 projectId

**问题**: `projectId` 不是随便填的，需要通过 Cloud Code Assist API 发现。

**解决**:

```javascript
const resp = await fetch(
  "https://cloudcode-pa.googleapis.com/v1beta:loadCodeAssist",
  {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${accessToken}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({}),
  }
);
const data = await resp.json();
const projectId = data.projectId; // 例如 "acoustic-vortex-b9jrc"
```
