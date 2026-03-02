---
name: store-teardown
description: "店铺设计拆解 - 分析电商店铺的配色、排版、字体、图片风格，输出结构化设计简报"
user-invocable: true
metadata:
  openclaw:
    emoji: "🎨"
  requires:
    bins: ["python3", "uv"]
    models: ["gemini-3-pro-preview"]
    env: ["SCRAPERAPI_KEY"]
---

# 店铺设计拆解 (Store Teardown)

拆解电商店铺的视觉设计，提取配色方案、排版风格、字体印象、图片风格等要素，输出结构化的设计简报。

## 禁止事项（必读）

- **禁止** 用浏览器打开淘宝/天猫（会被反爬拦截，白白浪费时间）
- **禁止** 安装 Playwright 或 selenium
- **禁止** 用 Google/Bing 搜索店铺（太慢且经常失败）
- **禁止** 自己写 Python 爬虫脚本
- 只用下面列出的工具：**买手搜索**、**taobao_fetch.py**、**download_images.py**

## 使用方式

用户输入示例：
- "找一下1747的店铺风格"（关键词搜索 → 用买手搜索）
- "拆解这个淘宝店铺: https://shop123456.taobao.com"（直接 URL → 用 taobao_fetch.py）

## 完整工作流

### Phase 0: 准备

```bash
mkdir -p /tmp/store-teardown/screenshots /tmp/store-teardown/images
```

### Phase 1: 判断输入类型并采集数据

先判断用户给的是 **URL** 还是 **品牌名/关键词**：

---

#### 路径 A：用户提供了品牌名或关键词（如 "1747"、"韩都衣舍"）

**步骤 1 — 用买手技能搜索商品**

```bash
cd /root/.openclaw/skills/taobao && uv run scripts/main.py search --source=1 --keyword='<品牌名>'
```

> source 参数：1=淘宝/天猫, 2=京东, 3=拼多多, 7=抖音, 8=快手
> 默认搜索淘宝（source=1），如果用户提到其他平台可以调整。

此命令返回 CSV 格式数据，每行包含：
`idx, goodsId, title, shopName, originalPrice, actualPrice, couponPrice, commission, monthSales, picUrl`

**步骤 2 — 保存搜索数据**

将搜索结果中的关键信息提取并保存为 JSON：

```bash
cat > /tmp/store-teardown/items.json << 'ITEMS_EOF'
[
  {"item_id": "<goodsId>", "title": "<title>", "price": "<actualPrice>", "shop_name": "<shopName>", "image": "<picUrl>", "sales": "<monthSales>"},
  ...
]
ITEMS_EOF
```

**步骤 3 — 下载商品图片**

> **重要**: 不能用 curl 直接下载 alicdn.com 图片（会被防盗链返回 1x1 GIF）！必须用 download_images.py。

先将搜索结果中的 picUrl 逐行写入文件，然后用脚本下载：

```bash
# 将搜索结果的 picUrl 写入文件（每行一个 URL）
cat > /tmp/store-teardown/urls.txt << 'URL_EOF'
<picUrl_1>
<picUrl_2>
<picUrl_3>
...
URL_EOF

# 用 download_images.py 下载（自动带正确 headers 绕过防盗链）
cd <skill_directory>
uv run scripts/download_images.py -o /tmp/store-teardown/images -f /tmp/store-teardown/urls.txt --max 15
```

下载完成后，复制到 screenshots 目录供色彩分析使用：

```bash
cp /tmp/store-teardown/images/* /tmp/store-teardown/screenshots/ 2>/dev/null
```

跳到 **Phase 2**。

---

#### 路径 B：用户提供了淘宝/天猫 URL

```bash
cd <skill_directory>
uv run scripts/taobao_fetch.py "<url>" -o /tmp/store-teardown --max-images 20
```

脚本会自动识别 URL 类型并选择最佳模式：
- 首页 (www.taobao.com) → 纯 HTML（1 credit），提取商品 + 800x800 图片
- 店铺页 (shop*.taobao.com) → 截图+渲染（10 credits）
- 短链接 (m.tb.cn) → 自动解析后再抓取
- 商品页 → 纯 HTML（1 credit）

检查结果：`cat /tmp/store-teardown/report.yaml`

如果店铺页只有截图没有商品数据，用买手搜索补充：

```bash
cd /root/.openclaw/skills/taobao && uv run scripts/main.py search --source=1 --keyword='<从截图或URL中判断的店铺名>'
```

然后按路径 A 的步骤 2-3 下载商品图片。

复制图片到 screenshots：

```bash
cp /tmp/store-teardown/images/* /tmp/store-teardown/screenshots/ 2>/dev/null
```

跳到 **Phase 2**。

---

#### 路径 C：非淘宝/天猫平台（小红书等）

使用 OpenClaw 浏览器：

```
openclaw browser open <store_url>
openclaw browser screenshot --full-page
```

然后用 `openclaw browser evaluate` 提取图片 URL 并用 curl 下载到 `/tmp/store-teardown/images/`。

---

### Phase 2: 多模态视觉分析

用 gemini-3-pro-preview 分析采集到的图片。对 `/tmp/store-teardown/images/` 和 `/tmp/store-teardown/screenshots/` 中的图片逐步分析。

**2.1 配色分析** — 读取图片后提问：

```
请分析这些电商店铺图片的配色方案：
1. 主色调（Primary）HEX 值
2. 辅助色（Secondary）HEX 值
3. 强调色（Accent）HEX 值
4. 背景色 HEX 值
5. 配色类型：暖色调/冷色调/中性/撞色
6. 情绪感受：专业/活泼/奢华/清新/甜美/硬朗
输出 YAML 格式。
```

**2.2 商品数据分析** — 读取 items.json 后分析：

```
分析以下商品数据：
1. 品类和风格定位
2. 标题命名风格
3. 价格带分布
4. 营销标签风格
<items.json 内容>
输出 YAML 格式。
```

**2.3 图片风格分析** — 读取商品图片后：

```
分析这些商品图片风格：
1. 摄影风格：棚拍/场景拍/街拍/平铺/混合
2. 背景处理：纯白底/浅灰/渐变/场景底
3. 光线和后期风格
4. 模特/展示方式
5. 图片比例
输出 YAML 格式。
```

**2.4 整体调性总结**：

```
综合所有图片和数据，总结设计调性：
1. 品牌定位感
2. 目标客群印象
3. 设计成熟度（1-10）
4. 优点和改进空间
5. 风格关键词（3-5 个）
输出 YAML 格式。
```

### Phase 3: 色彩量化分析

```bash
cd <skill_directory>
uv run scripts/analyze_images.py \
  --input /tmp/store-teardown/screenshots \
  --output /tmp/store-teardown/color_analysis.yaml
```

> 如果 analyze_images.py 执行失败，可以跳过此步，用 Phase 2 的视觉分析结果代替。

### Phase 4: 汇总输出

将分析结果合并，写入 `/tmp/store-teardown/design_brief.yaml`：

```yaml
store_teardown:
  meta:
    store_url: "<url 或 搜索关键词>"
    platform: "taobao | tmall | douyin | other"
    store_name: "<name>"
    analyzed_at: "<ISO timestamp>"
    analyzed_by: "openclaw/store-teardown"
    data_source: "maishou_search | scraperapi | browser"

  color_palette:
    primary: { hex: "#XXXXXX", name: "颜色名" }
    secondary: { hex: "#XXXXXX", name: "颜色名" }
    accent: { hex: "#XXXXXX", name: "颜色名" }
    background: { hex: "#XXXXXX", name: "颜色名" }
    scheme_type: "暖色调 | 冷色调 | 中性 | 撞色"
    mood: "奢华 | 清新 | 活泼 | 硬朗 | 甜美"

  product_data:
    total_items: 10
    price_range: { min: "xx", max: "xx" }
    top_shop_name: "店铺名"
    categories_detected: ["品类1", "品类2"]
    items:
      - { item_id: "xxx", title: "xxx", price: "xx", sales: "xx" }

  image_style:
    photography: "studio | lifestyle | mixed"
    background: "pure_white | scene | gradient"
    post_processing: "high_saturation | natural | vintage"
    aspect_ratio: "1:1 | 3:4 | mixed"

  overall_assessment:
    brand_positioning: "定位描述"
    target_audience: "目标客群描述"
    design_maturity_score: 7
    style_keywords: ["关键词1", "关键词2", "关键词3"]
    top_strengths: ["优点1", "优点2"]
    improvement_areas: ["改进点1", "改进点2"]
```

### Phase 5: 向用户呈现结果

用清晰的中文汇报：

1. **数据来源**：说明搜索了什么关键词 / 抓取了什么 URL
2. **一句话总结**：整体设计风格
3. **配色方案**：主要颜色 + HEX 值
4. **商品概览**：数量、价格带、主要品类、代表店铺
5. **图片风格**：摄影和后期风格
6. **设计评分与建议**：成熟度评分、优点和改进空间
7. **文件位置**：告知 `/tmp/store-teardown/design_brief.yaml`

## 注意事项

- 买手搜索是免费 API，不消耗 ScraperAPI credits
- ScraperAPI 免费套餐每月 5000 credits，首页纯 HTML 仅 1 credit
- 总时间控制在 5 分钟以内，避免超时
- **图片下载必须用 download_images.py**，不能用 curl（alicdn.com 会根据 HTTP Accept header 拦截非浏览器请求，返回 1x1 GIF）
- 如果 download_images.py 下载失败，可以跳过图片分析，仅基于商品文本数据做分析
