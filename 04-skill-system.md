# 坑 4: Skill 系统

## 坑点

### 4.1 Skill 目录优先级

**问题**: 不清楚 OpenClaw 从哪里加载 Skills。

**实际优先级**:
1. `~/.openclaw/skills/` — 自定义/手动安装的 skills
2. `~/.openclaw/workspace/skills/` — 通过 ClawHub 安装的 skills
3. OpenClaw 内置的 bundled skills（约 52 个）

如果同名 skill 在多个目录存在，优先级按上述顺序。

### 4.2 Skill 识别机制

**问题**: 放了脚本但 OpenClaw 不认。

**必要条件**: 每个 skill 目录下必须有 `SKILL.md` 文件，且包含 YAML frontmatter：

```markdown
---
name: my-skill
description: "技能描述"
user-invocable: true
metadata: {"openclaw": {"emoji": "🔧", "requires": {"bins": ["python3"]}}}
---

# Skill 使用说明
...
```

**禁用 Skill**: 重命名 `SKILL.md` 为其他名字（如 `SKILL.md.disabled`），OpenClaw 就不会加载。

### 4.3 ClawHub 安装限流

**问题**: `npx clawhub install browser-use` 返回 "Rate limit exceeded"。

**解决**: 等待 30+ 秒后重试。ClawHub 对免费用户有请求频率限制。

### 4.4 taobao (maishou) 技能需要 uv

**问题**: 淘宝搜索技能依赖 `uv` (Python 包管理器)，服务器没有预装。

**解决**:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
source ~/.bashrc
```

**注意**: maishou 技能只支持**商品关键词搜索**，不支持按店铺/品牌搜索。

### 4.5 baidu-search 需要 API Key

**问题**: `baidu-search` 技能需要 `BAIDU_API_KEY` 环境变量，不配置会报错：

```
Error: BAIDU_API_KEY must be set
```

**解决**:
- 方案 A: 获取百度 AI 搜索 API Key 并配置
- 方案 B: 禁用该技能（重命名 SKILL.md）
- 替代: 使用 OpenClaw 内置的 Brave Web Search

### 4.6 Skill 的 venv 管理

**问题**: Python-based skills 需要虚拟环境，但 OpenClaw 不会自动创建。

**解决**: 手动创建：
```bash
cd ~/.openclaw/skills/my-skill/scripts/
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

在 SKILL.md 中引用时使用 `.venv/bin/python`：
```bash
cd {baseDir}/scripts && .venv/bin/python my_script.py --arg value
```

### 4.7 Skill 环境变量配置

**问题**: 某些 skills 需要环境变量（如 API Key），但不知道在哪里配置。

**解决**: 在 `openclaw.json` 中设置：
```json
{
  "agents": {
    "defaults": {
      "env": {
        "BAIDU_API_KEY": "your-key-here",
        "GEMINI_API_KEY": "your-key-here"
      }
    }
  }
}
```
