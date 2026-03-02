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
    capabilities: ["browser"]
    env: ["SCRAPERAPI_KEY"]
---

# 店铺设计拆解 (Store Teardown)

拆解电商店铺（淘宝、小红书、天猫等）的视觉设计，提取配色方案、排版风格、字体印象、图片风格等要素，输出结构化的设计简报（YAML）。

## 使用方式

用户输入示例：

```
拆解这个淘宝店铺: https://shop123456.taobao.com
```

```
分析一下这个小红书店铺的设计风格: https://www.xiaohongshu.com/store/xxxx
```

```
store teardown https://shop.m.taobao.com/shop/xxx
```

## 完整工作流

### Phase 0: 准备工作

1. 创建输出目录：

```bash
mkdir -p /tmp/store-teardown/screenshots
mkdir -p /tmp/store-teardown/images
```

2. 记录店铺基础信息：
   - 店铺 URL
   - 平台类型（淘宝 / 天猫 / 小红书 / 其他）
   - 分析时间戳

---

### Phase 1+2: 数据采集

**所有淘宝/天猫 URL 统一使用 `taobao_fetch.py`**，脚本会自动识别 URL 类型并选择最佳抓取模式：

- 首页 (www.taobao.com) → 纯 HTML，1 credit，提取商品数据 + 800x800 图片
- 店铺页 (shop*.taobao.com) → 截图+渲染，10 credits，获取截图
- 短链接 (m.tb.cn) → 自动解析真实 URL 后再抓取
- 商品页 → 纯 HTML，1 credit

> **重要**: 淘宝/天猫服务器 IP 会被反爬拦截（PIT-008），不要用 `openclaw browser`，只用 `taobao_fetch.py`。

**步骤 1 — 运行 taobao_fetch.py**

```bash
cd <skill_directory>
uv run scripts/taobao_fetch.py "<url>" \
  -o /tmp/store-teardown \
  --max-images 20
```

脚本会自动：
- 识别 URL 类型（首页/店铺/商品/短链接）
- 选择最佳抓取模式（纯 HTML 或截图+渲染）
- 解析短链接（m.tb.cn → 真实 URL）
- 提取商品数据和图片
- 生成 `report.yaml`、`items.json`、`screenshot.png`（如有）

**步骤 2 — 检查抓取结果**

```bash
cat /tmp/store-teardown/report.yaml
```

根据结果判断获取到的素材：
- **有截图** (`screenshot.png`): 可用于全页视觉分析
- **有商品数据** (`items.json`): 可用于商品风格分析
- **有商品图片** (`images/`): 可用于色彩和图片风格分析

**步骤 3 — 如果需要更多商品图片**

如果店铺页只拿到截图没有商品图片，可以额外抓取淘宝首页获取推荐商品图片：

```bash
uv run scripts/taobao_fetch.py "https://www.taobao.com" \
  -o /tmp/store-teardown/homepage \
  --max-images 20
```

将图片复制到分析目录：

```bash
cp /tmp/store-teardown/homepage/images/* /tmp/store-teardown/images/ 2>/dev/null
cp /tmp/store-teardown/images/*.png /tmp/store-teardown/screenshots/ 2>/dev/null
cp /tmp/store-teardown/images/*.jpg /tmp/store-teardown/screenshots/ 2>/dev/null
```

**对于非淘宝/天猫平台（如小红书）**，使用 OpenClaw 浏览器：

```
openclaw browser open <store_url>
openclaw browser screenshot --full-page
```

然后使用 `openclaw browser evaluate` 提取图片 URL 并用 curl 下载。

完成后继续 **Phase 3**。

---

### Phase 3: 多模态视觉分析

使用 gemini-3-pro-preview 模型对采集到的图片进行视觉设计分析。

根据获取到的素材（截图 和/或 商品图片），选择对应的分析 prompt。

**步骤 3.1 — 配色分析**

将截图或商品图片交给多模态模型：

```
请分析这些电商店铺图片的配色方案。请提取：

1. 主色调（Primary Color）：最大面积使用的颜色，给出 HEX 值
2. 辅助色（Secondary Color）：第二多的颜色，给出 HEX 值
3. 强调色（Accent Color）：最抢眼的点缀色，给出 HEX 值
4. 背景色（Background）：主要背景色，给出 HEX 值
5. 配色方案类型：暖色调、冷色调、中性色、还是撞色？
6. 配色的情绪感受：专业、活泼、奢华、清新、甜美、硬朗？

输出格式为 YAML。
```

**步骤 3.2 — 排版与风格分析**

如果有截图：

```
请分析这张电商店铺截图的排版和字体风格：
1. 整体布局模式：瀑布流、网格、大图列表、还是混合？
2. 卡片样式：圆角/直角？有无阴影/边框？
3. 字体印象和文字层级
4. 中文字体家族猜测
输出格式为 YAML。
```

如果只有 items.json（无截图）：

```
以下是从店铺提取的商品数据。请分析：
1. 商品品类和风格定位
2. 标题命名风格：简洁型、关键词堆砌型、卖点型？
3. 价格带分布：低价走量、中端精品、高端？
4. 营销标签风格
<items.json 内容>
输出格式为 YAML。
```

**步骤 3.3 — 图片风格分析**

```
请分析这些商品图片风格：
1. 摄影风格：棚拍、场景拍、街拍、平铺拍摄、混合？
2. 背景处理：纯白底、浅灰底、渐变色底、场景底？
3. 光线和后期风格
4. 模特/展示方式
5. 图片比例
输出格式为 YAML。
```

**步骤 3.4 — 整体调性总结**

```
综合所有图片和数据，总结这家店铺的设计调性：
1. 品牌定位感
2. 目标客群印象
3. 设计成熟度（1-10 分）
4. 设计优点和改进空间
5. 风格关键词（3-5 个）
输出格式为 YAML。
```

### Phase 4: 色彩量化分析（Python 脚本）

使用 `scripts/analyze_images.py` 对图片做精确的色彩量化提取。

```bash
cd <skill_directory>
uv run scripts/analyze_images.py \
  --input /tmp/store-teardown/screenshots \
  --output /tmp/store-teardown/color_analysis.yaml
```

> 路径 A 时 screenshots 目录包含的是商品白底图的副本，色彩分析结果反映的是商品主体配色。
> 路径 B 时 screenshots 目录包含全页截图，色彩分析结果反映整体页面配色。

此脚本使用 Pillow + KMeans 聚类提取图片中的主色调，输出精确的 HEX 色值和占比。

### Phase 5: 汇总输出设计简报

将 Phase 3 的多模态分析结果与 Phase 4 的量化色彩数据合并，生成最终的设计简报文件。

最终输出文件：`/tmp/store-teardown/design_brief.yaml`

输出结构：

```yaml
store_teardown:
  meta:
    store_url: "<url>"
    platform: "taobao | tmall | xiaohongshu | other"
    store_name: "<name>"
    analyzed_at: "<ISO timestamp>"
    analyzed_by: "openclaw/store-teardown"
    fetch_mode: "scraperapi | browser"  # 标注使用了哪条路径

  color_palette:
    primary: { hex: "#XXXXXX", name: "颜色名", percentage: 35 }
    secondary: { hex: "#XXXXXX", name: "颜色名", percentage: 20 }
    accent: { hex: "#XXXXXX", name: "颜色名", percentage: 8 }
    background: { hex: "#XXXXXX", name: "颜色名" }
    text: { hex: "#XXXXXX", name: "颜色名" }
    scheme_type: "暖色调 | 冷色调 | 中性 | 撞色"
    mood: "奢华 | 清新 | 活泼 | 硬朗 | 甜美"
    quantized_top_colors:
      - { hex: "#XXXXXX", percentage: 35.2 }
      - { hex: "#XXXXXX", percentage: 20.1 }
      - { hex: "#XXXXXX", percentage: 15.4 }

  typography:
    layout_pattern: "grid_3col | grid_2col | waterfall | list | mixed"
    spacing: "tight | normal | loose"
    card_style:
      border_radius: "rounded | square"
      shadow: true
      border: false
    heading_style: "bold_gothic | thin_serif | handwritten | decorative"
    body_style: "standard_gothic"
    price_style: "large_bold_red | highlighted | subtle"
    font_family_guess: "思源黑体 | 阿里巴巴普惠体 | 方正兰亭黑 | ..."
    text_hierarchy:
      heading_size: "large"
      subheading_size: "medium"
      price_size: "large"
      description_size: "small"

  product_data:  # 路径 A 独有，路径 B 为空
    total_items: 8
    price_range: { min: "4.9", max: "139" }
    categories_detected: ["食品饮料", "服装", "运动户外", "家居"]
    marketing_tags: ["全网低价", "大牌折扣", "晚发必赔", "火爆热卖中"]
    items:
      - { item_id: "xxx", title: "xxx", price: "xx", benefit: "xx" }

  image_style:
    photography: "studio | lifestyle | street | flatlay | mixed"
    background: "pure_white | light_gray | gradient | scene | cutout"
    lighting: "natural | soft_studio | hard | backlit | post_processed"
    post_processing: "high_saturation | low_saturation | vintage | japanese_fresh | raw"
    model_usage:
      has_model: true
      framing: "full_body | half_body | closeup"
      pose_style: "casual | cool | sweet | athletic"
    aspect_ratio: "1:1 | 3:4 | 16:9 | mixed"

  banner_design:  # 路径 A 时标注不可用
    aspect_ratio: "16:9 | 2:1 | custom | not_available"
    composition: "left_text_right_image | centered | full_image | collage"
    text_layout:
      heading_scale: "large | medium | small"
      has_subtitle: true
      text_position: "left | center | right"
    has_promo_elements: true
    design_technique: "gradient_overlay | mask | motion_hint"
    quality_feel: "premium | mass_market | artistic | trendy"

  overall_assessment:
    brand_positioning: "luxury | affordable_luxury | mass | fast_fashion | designer | guochao | value"
    target_audience:
      age_range: "18-25 | 25-35 | 35-45"
      gender_lean: "female | male | neutral"
      style_preference: "关键词"
    design_maturity_score: 7
    top_strengths:
      - "优点 1"
      - "优点 2"
    improvement_areas:
      - "改进点 1"
      - "改进点 2"
    style_keywords:
      - "极简"
      - "甜美"
      - "日系"

  raw_data:
    fetch_mode: "scraperapi | browser"
    screenshots:
      - /tmp/store-teardown/screenshots/homepage_full.png
    images_extracted: 15
    items_json: /tmp/store-teardown/items.json  # 路径 A 独有
    color_analysis_file: /tmp/store-teardown/color_analysis.yaml
    report_file: /tmp/store-teardown/report.yaml  # 路径 A 独有
```

将上述 YAML 写入 `/tmp/store-teardown/design_brief.yaml`。

### Phase 6: 向用户呈现结果

以清晰的中文向用户汇报分析结果：

1. **数据来源说明**：
   - 路径 A：说明"通过 ScraperAPI 代理抓取，提取到 X 个商品和 Y 张商品图片"
   - 路径 B：说明"通过浏览器直连采集截图和商品图片"
2. **一句话总结**：这家店铺的整体设计风格是什么
3. **配色方案**：列出主要颜色（带色块 emoji 近似表示）和 HEX 值
4. **商品数据概览**（路径 A）：商品数量、价格带、主要品类
5. **排版特点**：布局模式、卡片风格
6. **图片风格**：摄影风格、后期风格
7. **Banner 设计**（路径 B）：构图方式、质感评价；路径 A 标注"Banner 数据暂不可用"
8. **设计评分与建议**：成熟度评分、优点和改进空间
9. **文件位置**：告知用户完整的设计简报保存在 `/tmp/store-teardown/design_brief.yaml`

## 注意事项

- 淘宝/天猫使用路径 A（ScraperAPI），需要 `SCRAPERAPI_KEY` 环境变量
- ScraperAPI 免费套餐每月 5000 credits，淘宝纯 HTML 模式每次消耗 1 credit
- 路径 A 无法获取全页截图和 Banner，设计分析主要基于商品图片和结构化数据
- 路径 B 使用 OpenClaw 浏览器直连，需要目标平台不拦截服务器 IP
- 图片 CDN 链接可能有防盗链限制，下载时可能需要设置 Referer header
- 分析结果基于 AI 视觉判断，色彩 HEX 值为近似值；Python 脚本提取的量化颜色更精确
- 建议每次分析间隔 30 秒以上，避免频繁触发平台风控
