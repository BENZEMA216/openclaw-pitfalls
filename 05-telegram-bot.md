# 坑 5: Telegram Bot 集成

## 坑点

### 5.1 启动方式

**问题**: OpenClaw gateway 需要在后台持续运行，且需要 NVM 环境。

**正确启动方式**:
```bash
export NVM_DIR="/root/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

nohup openclaw gateway > /root/openclaw-gateway.log 2>&1 &
```

**常见错误**: 直接 `nohup openclaw gateway` 不加载 NVM → `command not found`。

### 5.2 日志查看

**问题**: OpenClaw gateway 不会自动创建日志文件，stdout/stderr 被重定向到 socket。

**查看方法**:
- 会话记录: `~/.openclaw/agents/main/sessions/*.jsonl`
- 用 `tail -f` 跟踪最新 jsonl 文件
- 解析技巧:
  ```bash
  tail -c 50000 ~/.openclaw/agents/main/sessions/SESSION_ID.jsonl | \
    python3 -c "
  import sys, json
  for line in sys.stdin:
    try:
      d = json.loads(line.strip())
      msg = d.get('message',{})
      role = msg.get('role','')
      ts = d.get('timestamp','')
      if role == 'assistant':
        model = msg.get('model','')
        print(f'{ts} [{role}] model={model}')
      elif role == 'user':
        print(f'{ts} [{role}]')
    except: pass
  "
  ```

### 5.3 Bot 配置字段

**注意**: Telegram 配置中的 token 字段名是 `botToken`，不是 `token`：

```json
{
  "channels": {
    "telegram": {
      "enabled": true,
      "botToken": "123456:ABC-DEF...",
      "dmPolicy": "pairing",
      "streamMode": "partial",
      "groups": {
        "-100xxxxxxxxxx": {
          "requireMention": false,
          "allowFrom": ["user_id_1", "user_id_2"]
        }
      }
    }
  }
}
```

### 5.4 重启后 Browser 状态

**问题**: 重启 OpenClaw 后，之前的浏览器 tab 仍然保留（Chrome 进程没有被杀掉）。

**影响**: 可能导致内存占用过高，建议重启时清理：
```bash
# 停止旧浏览器
openclaw browser stop

# 或者直接杀掉 Chrome
pkill -f chrome

# 然后重启 gateway
nohup openclaw gateway > /root/openclaw-gateway.log 2>&1 &
```
