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

### Phase 0: 准备工作与平台路由

1. 创建输出目录：

```bash
mkdir -p /tmp/store-teardown/screenshots
mkdir -p /tmp/store-teardown/images
```

2. 记录店铺基础信息：
   - 店铺 URL
   - 平台类型（淘宝 / 天猫 / 小红书 / 其他）
   - 分析时间戳

3. **判断采集路径**：

   根据 URL 域名选择数据采集路径：

   | URL 包含 | 平台 | 采集路径 |
   |----------|------|----------|
   | `taobao.com` | 淘宝 | **路径 A: ScraperAPI 代理抓取** |
   | `tmall.com` | 天猫 | **路径 A: ScraperAPI 代理抓取** |
   | 其他域名 | 小红书等 | **路径 B: OpenClaw 浏览器直连** |

   > **为什么需要双路径？**
   > 淘宝/天猫会对服务器 IP 触发反爬验证（参考 PIT-008），`openclaw browser` 直连会被拦截。
   > 路径 A 通过 ScraperAPI 代理访问，从页面嵌入的 JSON 中提取商品数据和 800x800 高清图，稳定可用。

---

### Phase 1+2 路径 A: 淘宝/天猫 — ScraperAPI 代理抓取

当 URL 属于 `taobao.com` 或 `tmall.com` 时，使用 `scripts/taobao_fetch.py` 抓取。

**步骤 A.1 — 运行 taobao_fetch.py 抓取商品数据和图片**

```bash
cd <skill_directory>
uv run scripts/taobao_fetch.py "<store_url>" \
  -o /tmp/store-teardown \
  --max-images 20 \
  --image-size 800x800
```

> 环境变量 `SCRAPERAPI_KEY` 必须已设置。此脚本会自动：
> - 通过 ScraperAPI 代理获取页面 HTML
> - 从 `window.staticConfig` 等嵌入 JSON 提取商品数据（itemId、标题、价格、图片 URL）
> - 下载商品的 800x800 白底高清图到 `/tmp/store-teardown/images/`
> - 生成 `/tmp/store-teardown/items.json`（结构化商品数据）
> - 生成 `/tmp/store-teardown/report.yaml`（抓取报告）

**步骤 A.2 — 检查抓取结果**

```bash
cat /tmp/store-teardown/report.yaml
cat /tmp/store-teardown/items.json
ls /tmp/store-teardown/images/
```

确认：
- `items.json` 中有商品数据（通常 8-30 个）
- `images/` 目录有下载好的商品图片（product_01.png ~ product_XX.png）
- `report.yaml` 中 `anti_scraping_signals` 为空（未触发反爬）

如果抓取失败（HTTP 非 200 或无商品数据），检查 `SCRAPERAPI_KEY` 是否有效，或尝试换一个店铺首页 URL。

**步骤 A.3 — 准备分析素材**

将下载的商品图片软链接到 screenshots 目录（供 Phase 4 色彩分析使用）：

```bash
cp /tmp/store-teardown/images/*.png /tmp/store-teardown/screenshots/ 2>/dev/null
cp /tmp/store-teardown/images/*.jpg /tmp/store-teardown/screenshots/ 2>/dev/null
```

> **路径 A 的数据特点：**
> - 有 800x800 高清商品白底图（适合分析图片风格、配色）
> - 有结构化商品数据（标题、价格、标签）
> - **没有全页截图**（ScraperAPI 免费套餐不支持截图，需 premium）
> - **没有 Banner/轮播图**（嵌入 JSON 不包含 Banner 数据）
>
> 因此 Phase 3 的分析需要基于商品图片进行，跳过 Banner 分析（步骤 3.4）。

完成后直接跳转到 **Phase 3**。

---

### Phase 1+2 路径 B: 其他平台 — OpenClaw 浏览器直连

当 URL 不属于淘宝/天猫时，使用 OpenClaw 浏览器直连。

**步骤 B.1 — 打开店铺首页**

```
openclaw browser open <store_url>
```

**步骤 B.2 — 等待页面完全加载**

等待 3-5 秒让页面渲染完成，尤其是懒加载的商品图片。

**步骤 B.3 — 全页截图**

```
openclaw browser screenshot --full-page
```

截图将自动保存。将截图复制到工作目录：

```bash
cp <screenshot_path> /tmp/store-teardown/screenshots/homepage_full.png
```

**步骤 B.4 — 首屏截图（Banner 区域）**

```
openclaw browser screenshot
```

保存为 `/tmp/store-teardown/screenshots/homepage_above_fold.png`。

**步骤 B.5 — 获取页面 ARIA 快照**

```
openclaw browser snapshot --format aria
```

ARIA 快照有助于理解页面结构层次（导航、分类、商品区块等）。

**步骤 B.6 — 提取商品卡片图片 URL**

对小红书平台：

```
openclaw browser evaluate "JSON.stringify(Array.from(document.querySelectorAll('img[src*=\"sns-webpic\"], img[src*=\"xhscdn\"], img.note-image')).map(img => ({src: img.src || img.dataset.src, alt: img.alt})))"
```

对其他平台：

```
openclaw browser evaluate "JSON.stringify(Array.from(document.querySelectorAll('img[src]')).map(img => ({src: img.src || img.dataset.src, alt: img.alt, width: img.naturalWidth, height: img.naturalHeight})).filter(i => i.width > 100))"
```

**步骤 B.7 — 提取 Banner / 轮播图**

```
openclaw browser evaluate "JSON.stringify(Array.from(document.querySelectorAll('.slider img, .banner img, [class*=\"carousel\"] img, [class*=\"slider\"] img, [class*=\"banner\"] img')).map(img => ({src: img.src || img.dataset.src, alt: img.alt})))"
```

**步骤 B.8 — 下载关键图片**

```bash
cd /tmp/store-teardown/images
curl -o product_01.jpg "<image_url>"
curl -o product_02.jpg "<image_url>"
curl -o banner_01.jpg "<banner_url>"
```

完成后继续 **Phase 3**。

---

### Phase 3: 多模态视觉分析

使用 gemini-3-pro-preview 模型对采集到的图片进行详细的视觉设计分析。

> **路径 A（淘宝/天猫）**：用商品白底图 + items.json 数据进行分析，跳过步骤 3.4（Banner 分析）。
> **路径 B（其他平台）**：用全页截图 + 商品图片进行完整分析。

**步骤 3.1 — 配色分析**

将商品图片（路径 A）或全页截图（路径 B）交给多模态模型：

路径 A prompt：

```
请分析这些电商店铺的商品主图配色方案。这些是该店铺的商品白底展示图。请提取：

1. 主色调（Primary Color）：商品图片中最常见的主体颜色，给出 HEX 值
2. 辅助色（Secondary Color）：第二常见的颜色，给出 HEX 值
3. 强调色（Accent Color）：商品中最抢眼的点缀色，给出 HEX 值
4. 背景色（Background）：商品图片的背景色（通常为白色），给出 HEX 值
5. 配色方案类型：是暖色调、冷色调、中性色、还是撞色？
6. 配色的情绪感受：专业、活泼、奢华、清新、甜美、硬朗？
7. 商品品类推测：基于图片内容判断这家店铺主营什么品类

输出格式为 YAML。
```

路径 B prompt：

```
请分析这张电商店铺截图的配色方案。请提取：

1. 主色调（Primary Color）：店铺最大面积使用的颜色，给出 HEX 值
2. 辅助色（Secondary Color）：第二多的颜色，给出 HEX 值
3. 强调色（Accent Color）：用于按钮、价格、标签等吸引注意力的颜色，给出 HEX 值
4. 背景色（Background）：页面主要背景色，给出 HEX 值
5. 文字色（Text Color）：主要正文和标题的文字颜色，给出 HEX 值
6. 配色方案类型：是暖色调、冷色调、中性色、还是撞色？
7. 配色的情绪感受：专业、活泼、奢华、清新、甜美、硬朗？

输出格式为 YAML。
```

**步骤 3.2 — 排版与字体分析**

> 路径 A 时：基于 items.json 的商品数据（标题风格、价格格式、标签文案）进行推测性分析。
> 路径 B 时：基于截图进行完整的视觉分析。

路径 A prompt：

```
以下是从一家淘宝/天猫店铺提取的商品数据（JSON 格式）和商品主图。
请基于商品数据和图片分析这家店铺可能的排版和设计特征：

商品数据：
<items.json 内容>

请分析：
1. 商品品类和风格定位
2. 商品图片的统一性：所有主图是否风格一致？
3. 标题命名风格：简洁型、关键词堆砌型、卖点型？
4. 价格带分布：低价走量、中端精品、还是高端？
5. 营销标签风格：促销导向（全网低价）、品质导向（大牌折扣）、还是服务导向（晚发必赔）？

输出格式为 YAML。
```

路径 B prompt：

```
请分析这张电商店铺截图的排版和字体风格：

1. 整体布局模式：是瀑布流、网格（几列）、大图列表、还是混合布局？
2. 间距风格：商品卡片之间的间距是紧凑、适中还是宽松？
3. 卡片样式：圆角还是直角？有无阴影？有无边框？
4. 字体印象：
   - 标题：是粗壮的黑体风格、纤细的宋体风格、还是手写/艺术字体？
   - 正文：标准黑体还是其他？
   - 价格：是否有特殊的字体处理（如大号加粗、颜色高亮）？
5. 文字层级：标题、副标题、价格、描述的大小比例关系
6. 中文字体家族猜测（如：思源黑体、阿里巴巴普惠体、方正兰亭黑等）

输出格式为 YAML。
```

**步骤 3.3 — 图片风格分析**

将商品图片交给多模态模型（两条路径使用相同的 prompt）：

```
请分析这些电商店铺的商品图片风格：

1. 摄影风格：棚拍（纯色背景）、场景拍（生活场景）、街拍、平铺拍摄、还是混合？
2. 背景处理：纯白底、浅灰底、渐变色底、场景底、还是抠图合成？
3. 光线风格：自然光、柔光棚拍、硬光、逆光、还是后期调色？
4. 后期风格：高饱和、低饱和、复古胶片感、日系清新、还是原片风格？
5. 模特/展示方式（如有）：
   - 是否使用模特？全身/半身/特写？
   - 模特姿态风格：自然随意、高冷、甜美、运动感？
   - 如无模特：是商品特写、使用场景、还是创意摆拍？
6. 图片比例：1:1 正方形、3:4 竖图、16:9 横图、还是混合？

输出格式为 YAML。
```

**步骤 3.4 — Banner 设计分析**

> **路径 A（淘宝/天猫）时跳过此步骤**：ScraperAPI 纯 HTML 模式无法获取 Banner 图片。
> 在设计简报中标注 `banner_design: "not_available (scraperapi_mode)"`。

路径 B prompt：

```
请分析这张电商店铺 Banner（轮播图/首屏大图）的设计特点：

1. Banner 尺寸比例
2. 构图方式：左文右图、居中排版、满屏图片、拼接式、还是其他？
3. 文字排版：标题字号感觉、是否有副标题、文字位置
4. 是否有促销元素：折扣标签、倒计时、活动标语？
5. 设计手法：渐变叠加、蒙版处理、动效暗示（如箭头、滑动提示）？
6. 整体质感：高端精致、大众促销、文艺小众、潮流年轻？

输出格式为 YAML。
```

**步骤 3.5 — 整体调性总结**

```
综合以上所有商品图片和数据，请用一段话总结这家店铺的整体设计调性：

1. 品牌定位感：奢侈品、轻奢、大众、快时尚、原创设计师、国潮、还是性价比？
2. 目标客群印象：年龄段、性别倾向、风格偏好
3. 设计成熟度（1-10 分）：与同类型头部店铺相比的设计水准
4. 最突出的设计优点（1-2 个）
5. 最明显的设计改进空间（1-2 个）
6. 风格关键词（3-5 个词，如：极简、甜美、街头、复古、未来感）

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
