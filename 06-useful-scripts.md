# 坑 6: 实用脚本与调试技巧

## 调试脚本

### 6.1 直接测试 Cloud Code Assist API

不依赖 OpenClaw，直接测试模型 API 是否可用：

```bash
#!/bin/bash
# test_gemini_api.sh - 直接测试 google-gemini-cli API

ACCESS=$(python3 -c "
import json
d = json.load(open('$HOME/.openclaw/agents/main/agent/auth-profiles.json'))
print(d['profiles']['google-gemini-cli:default']['access'])
")
PROJECT=$(python3 -c "
import json
d = json.load(open('$HOME/.openclaw/agents/main/agent/auth-profiles.json'))
print(d['profiles']['google-gemini-cli:default']['projectId'])
")

curl -s --max-time 30 \
  -X POST "https://cloudcode-pa.googleapis.com/v1internal:streamGenerateContent?alt=sse" \
  -H "Authorization: Bearer $ACCESS" \
  -H "Content-Type: application/json" \
  -H "User-Agent: google-cloud-sdk vscode_cloudshelleditor/0.1" \
  -H "X-Goog-Api-Client: gl-node/22.17.0" \
  -H 'Client-Metadata: {"ideType":"IDE_UNSPECIFIED","platform":"PLATFORM_UNSPECIFIED","pluginType":"GEMINI"}' \
  -d '{
    "project": "'"$PROJECT"'",
    "model": "gemini-3-pro-preview",
    "request": {
      "contents": [{"role":"user","parts":[{"text":"Say hello"}]}],
      "generationConfig": {"maxOutputTokens": 50}
    },
    "userAgent": "pi-coding-agent",
    "requestId": "test-'"$(date +%s)"'"
  }'
```

### 6.2 OAuth Token 刷新脚本

```bash
#!/bin/bash
# refresh_oauth.sh - 刷新 Google OAuth token

# 这两个值来自 Gemini CLI 开源代码 (搜索 "apps.googleusercontent.com")
CLIENT_ID="<GEMINI_CLI_CLIENT_ID>"        # 格式: xxx.apps.googleusercontent.com
CLIENT_SECRET="<GEMINI_CLI_CLIENT_SECRET>" # 格式: GOCSPX-xxx

REFRESH=$(python3 -c "
import json
d = json.load(open('$HOME/.openclaw/agents/main/agent/auth-profiles.json'))
print(d['profiles']['google-gemini-cli:default']['refresh'])
")

RESULT=$(curl -s -X POST "https://oauth2.googleapis.com/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=$CLIENT_ID&client_secret=$CLIENT_SECRET&refresh_token=$REFRESH&grant_type=refresh_token")

echo "$RESULT" | python3 -m json.tool
```

### 6.3 自定义浏览器截图脚本 (Playwright)

当 `browser-use` CLI 不可用时，用 Playwright 直接操作浏览器：

```python
#!/usr/bin/env python3
"""browse.py - 简单的 Playwright 浏览器自动化工具"""
import argparse, os, sys, time
from playwright.sync_api import sync_playwright

def navigate(page, url, wait_secs=3):
    try:
        page.goto(url, timeout=20000, wait_until="networkidle")
    except Exception:
        page.goto(url, timeout=30000, wait_until="load")
    if wait_secs:
        time.sleep(wait_secs)

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="cmd")

    p = sub.add_parser("screenshot")
    p.add_argument("url")
    p.add_argument("--output", "-o", default="/tmp/screenshot.png")
    p.add_argument("--full", action="store_true")
    p.add_argument("--width", type=int, default=1280)
    p.add_argument("--height", type=int, default=800)
    p.add_argument("--wait", type=int, default=3)

    args = parser.parse_args()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": args.width, "height": args.height})
        page.set_extra_http_headers({"Accept-Language": "zh-CN,zh;q=0.9"})
        navigate(page, args.url, args.wait)
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        page.screenshot(path=args.output, full_page=args.full)
        print(f"Screenshot: {args.output}")
        browser.close()

if __name__ == "__main__":
    main()
```

安装依赖：
```bash
pip install playwright
playwright install chromium
```

## 调试检查清单

遇到问题时按顺序排查：

1. **进程是否运行**: `pgrep -f openclaw-gateway`
2. **Token 是否过期**: 检查 auth-profiles.json 中的 `expires` 字段
3. **API 是否可达**: 用 6.1 的脚本直接测试
4. **Chrome 是否启动**: `pgrep -f chrome`
5. **Tab 状态**: `openclaw browser tabs`
6. **最近的会话**: `tail -c 10000 ~/.openclaw/agents/main/sessions/*.jsonl`
7. **Skill 是否加载**: 检查 SKILL.md 是否存在且格式正确

## 服务器环境要求

```bash
# 必要软件
node >= 22
python3
chromium 或 google-chrome
playwright (pip install)

# 可选
uv                    # 淘宝搜索 skill 需要
requests              # nano-banana2 skill 需要
```
