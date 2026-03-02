---
name: design-pipeline
description: "美工全流程 - 从参考店铺到成品设计，自动分析风格并生成同风格电商素材（主图、海报、Banner）。激活条件：(1) 用户需要分析店铺/竞品视觉风格 (2) 用户需要生成电商产品主图 (3) 用户需要制作活动Banner/海报 (4) 用户需要批量生成同风格产品图 (5) 用户需要从参考URL提取设计语言并复用。关键词：美工、设计、主图、海报、Banner、批量生成、风格分析、店铺拆解、电商素材、详情页、小红书、产品图、视觉风格"
user-invocable: true
metadata: {"openclaw": {"emoji": "🖼️"}}
---

# 美工全流程 (Design Pipeline)

从参考店铺到成品设计的自动化电商美工工作流。串联浏览器截图、风格分析、AI 生图三大环节，一条龙输出同风格电商素材。

## 核心能力链

```
参考URL/图片 → 浏览器截图 → 风格拆解分析 → 设计简报生成 → nano-banana2 AI生图 → 成品素材
     ↑              ↑              ↑                ↑                ↑              ↑
  用户输入     OpenClaw浏览器   store-teardown   本技能核心     Gemini图像生成   输出交付
```

## 依赖工具

| 工具 | 用途 | 调用方式 |
|------|------|----------|
| OpenClaw 浏览器 | 截取参考页面 | `take_screenshot` MCP 工具 |
| store-teardown | 店铺视觉拆解分析 | `{baseDir}/../store-teardown/scripts/` |
| nano-banana2 | Gemini AI 图像生成 | 见下方命令格式 |
| ecommerce-designer | 模版渲染（可选） | `{baseDir}/../ecommerce-designer/scripts/` |

### nano-banana2 命令格式

```bash
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "提示词" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/"
```

### 画幅比例速查

| 素材类型 | 比例 | 适用场景 |
|----------|------|----------|
| 主图 | 1:1 | 淘宝/天猫/京东/拼多多产品主图 |
| 详情页 | 3:4 或 2:3 | 商品详情长图分段 |
| Banner (宽幅) | 21:9 | 店铺首页通栏 Banner |
| Banner (标准) | 16:9 | 活动专区 Banner |
| 小红书封面 | 3:4 | 小红书笔记封面图 |
| 抖音封面 | 9:16 | 抖音/快手竖版封面 |
| 公众号封面 | 16:9 | 微信公众号文章头图 |

---

## 工作模式

本技能支持 4 种工作模式，根据用户输入自动判断或由用户指定。

---

### 模式 1: 参考生成 (Reference-based Generation)

**触发词**: "参考这个店铺生成"、"照着这个风格做"、"分析这个链接的设计"

**输入**: 店铺 URL 或产品页面 URL

**流程**:

#### Step 1: 截取参考页面

使用 OpenClaw 浏览器打开目标 URL 并截图。截取首页、产品页、详情页等关键页面。

```
操作: 使用 take_screenshot MCP 工具
目标: 截取 3-5 张关键页面截图
保存: /tmp/design-pipeline/reference/
```

#### Step 2: 风格拆解分析

对截图进行视觉风格分析，提取以下要素:

```
分析维度:
├── 色彩体系
│   ├── 主色 (dominant color + hex)
│   ├── 辅色 (secondary colors)
│   ├── 强调色 (accent color)
│   └── 整体色温 (暖/冷/中性)
├── 字体风格
│   ├── 标题字体特征 (衬线/无衬线/手写/艺术)
│   ├── 正文字体特征
│   └── 字重分布
├── 布局特征
│   ├── 构图模式 (对称/非对称/网格/自由)
│   ├── 留白比例 (紧凑/适中/通透)
│   └── 视觉层级 (主副标题/图文比例)
├── 视觉情绪
│   ├── 风格标签 (科技/清新/奢华/促销/日系/韩系)
│   ├── 目标人群推测
│   └── 品牌调性关键词
└── 素材特征
    ├── 产品图风格 (实拍/渲染/抠图/场景)
    ├── 背景处理 (纯色/渐变/场景/纹理)
    └── 装饰元素 (几何/花卉/光效/无)
```

#### Step 3: 生成设计简报 (Design Brief)

将分析结果整理为结构化设计简报:

```markdown
## 设计简报

**参考来源**: [URL]
**风格定义**: [3-5个关键词，如: 日系极简、暖色调、留白通透]

**色彩方案**:
- 主色: #XXXXXX (色名)
- 辅色: #XXXXXX, #XXXXXX
- 强调色: #XXXXXX
- 背景: #XXXXXX

**视觉规范**:
- 构图: [对称居中 / 左图右文 / 通栏大图]
- 留白: [高 / 中 / 低]
- 情绪: [关键词]

**适用提示词模板**: (见 Step 4)
```

将设计简报保存到 `/tmp/design-pipeline/brief.md`。

#### Step 4: AI 生图

根据设计简报构造 nano-banana2 提示词并生成图像:

```bash
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[根据简报构造的提示词]" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/output/"
```

**提示词构造规则** (将风格要素注入提示词):

```
[产品/场景主体描述],
[风格关键词] style,
color palette: [主色名] with [辅色名] accents,
[背景描述: 如 clean white background / gradient from #XXX to #XXX],
[光线描述: 如 soft natural lighting / studio lighting with rim light],
[构图描述: 如 centered composition / rule of thirds],
[情绪关键词: 如 premium, minimalist, warm, inviting],
product photography, e-commerce ready, high resolution
```

#### Step 5: 输出交付

```
输出目录: /tmp/design-pipeline/output/
├── brief.md          # 设计简报
├── reference/        # 参考截图
└── generated/        # 生成的素材图片
```

---

### 模式 2: 产品主图 (Product Main Image)

**触发词**: "做主图"、"生成产品图"、"产品主图"

**输入**:
- 必填: 产品名称/描述
- 可选: 风格参考 URL 或风格描述

**流程**:

#### Step 1: 风格确认

如果提供了参考 URL，执行模式 1 的 Step 1-3 获取风格简报。
如果提供了文字描述，直接提取风格关键词。
如果都未提供，使用默认电商主图风格 (干净白底、产品居中、柔光)。

#### Step 2: 构造主图提示词

主图提示词模板:

```
[产品名称] product photo,
[产品材质/颜色/特征描述],
[风格关键词] style,
[背景: 默认 clean white background, 或根据风格调整],
centered composition, studio lighting,
soft shadows, product photography,
e-commerce main image, high resolution, 8K detail
```

**变体策略** (为同一产品生成多个变体):

| 变体 | 调整维度 | 示例 |
|------|----------|------|
| A - 标准白底 | background: pure white | 淘宝标准主图 |
| B - 场景化 | background: lifestyle scene | 使用场景展示 |
| C - 氛围感 | lighting: dramatic | 品牌质感图 |
| D - 细节特写 | composition: macro close-up | 材质/工艺展示 |

#### Step 3: 批量调用生图

为每个变体调用 nano-banana2:

```bash
# 变体 A: 白底标准
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品名] product photo, clean white background, centered, studio lighting, soft shadows, e-commerce main image, 8K" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/product-main/variant-a/"

# 变体 B: 场景化
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品名] in a [场景] setting, lifestyle photography, natural lighting, warm tones, 8K" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/product-main/variant-b/"

# 变体 C: 氛围感
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品名], dramatic studio lighting, rim light, dark moody background, premium feel, 8K" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/product-main/variant-c/"

# 变体 D: 细节特写
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品名] macro close-up, texture detail, shallow depth of field, studio lighting, 8K" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/product-main/variant-d/"
```

#### Step 4: 输出

```
/tmp/design-pipeline/product-main/
├── variant-a/    # 白底标准主图
├── variant-b/    # 场景化主图
├── variant-c/    # 氛围感主图
└── variant-d/    # 细节特写主图
```

向用户展示所有变体，询问偏好方向后可进一步迭代。

---

### 模式 3: 店铺 Banner

**触发词**: "做Banner"、"做海报"、"做活动图"、"促销Banner"

**输入**:
- 必填: 活动信息 (活动名称、折扣力度、时间)
- 可选: 风格参考 URL 或风格描述
- 可选: 需要的文案内容

**流程**:

#### Step 1: 提取活动信息

解析用户输入，提取:

```yaml
activity_name: "618年中大促"        # 活动名称
discount: "全场5折起"               # 折扣信息
date_range: "6.1 - 6.18"           # 活动日期
tagline: "年中钜惠，不负好时光"      # 宣传语 (如无则生成)
products: ["产品A", "产品B"]         # 主推产品 (如有)
cta: "立即抢购"                     # 行动号召 (如无则生成)
```

#### Step 2: 确定风格

如果提供了参考 URL，执行模式 1 的 Step 1-3。
否则根据活动类型匹配预设风格:

| 活动类型 | 推荐风格 | 色彩方向 |
|----------|----------|----------|
| 618/双11/双12 | 热烈促销 | 红金/橙红 |
| 年货节/春节 | 国潮喜庆 | 正红/金色 |
| 38女王节 | 优雅精致 | 粉紫/玫瑰金 |
| 夏季清仓 | 清凉活力 | 蓝绿/冰蓝 |
| 日常上新 | 简约时尚 | 品牌主色 |
| 会员日 | 尊享高端 | 黑金/深蓝 |

#### Step 3: 构造 Banner 提示词

Banner 提示词模板:

```
E-commerce promotional banner design,
[活动名称] sale event,
[风格关键词] style,
color scheme: [色彩方案],
[布局描述: 如 large bold text on left, product images on right],
text area reserved for: "[活动名称]" "[折扣信息]" "[行动号召]",
[装饰元素: 如 geometric shapes, confetti, light effects, ribbon],
festive and eye-catching, high contrast,
wide format banner, e-commerce ready, high resolution
```

**重要**: Banner 通常需要留出文字区域。在提示词中明确指示文案放置位置和空间，生成后用 ecommerce-designer 或手工叠加文字层。

#### Step 4: 生成多尺寸 Banner

```bash
# 通栏 Banner (21:9)
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[Banner提示词]" \
  --aspect-ratio "21:9" \
  --output "/tmp/design-pipeline/banner/wide/"

# 标准 Banner (16:9)
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[Banner提示词]" \
  --aspect-ratio "16:9" \
  --output "/tmp/design-pipeline/banner/standard/"

# 移动端 Banner (如需要, 3:4)
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[Banner提示词, 竖版构图调整]" \
  --aspect-ratio "3:4" \
  --output "/tmp/design-pipeline/banner/mobile/"
```

#### Step 5: 文字叠加 (可选)

如果 ecommerce-designer 可用，调用其模版渲染:

```bash
cd {baseDir}/../ecommerce-designer/scripts && .venv/bin/python render_template.py \
  --type poster \
  --title "[活动名称]" \
  --subtitle "[折扣信息]" \
  --discount "[折扣]" \
  --style "[风格]" \
  --background "/tmp/design-pipeline/banner/wide/[生成的图片]" \
  --output "/tmp/design-pipeline/banner/final/"
```

否则在输出中注明: 文字需要后期在 PS/Figma/Canva 中叠加。

#### Step 6: 输出

```
/tmp/design-pipeline/banner/
├── wide/       # 21:9 通栏Banner
├── standard/   # 16:9 标准Banner
├── mobile/     # 3:4 移动端Banner (如生成)
└── final/      # 叠加文字后的成品 (如可用)
```

---

### 模式 4: 批量生成 (Batch Generation)

**触发词**: "批量生成"、"一组产品图"、"全店主图"、"系列产品图"

**输入**:
- 必填: 产品列表 (名称 + 简要描述)
- 必填: 风格参考 (URL 或风格描述，仅需提供一次)

**流程**:

#### Step 1: 风格锁定

执行一次风格分析 (模式 1 的 Step 1-3 或从文字描述提取)。
生成全局风格锚点:

```yaml
style_anchor:
  keywords: ["日系极简", "暖色调", "留白通透"]
  primary_color: "#F5E6D3"
  accent_color: "#C4956A"
  background: "warm beige gradient"
  lighting: "soft natural window light"
  mood: "warm, inviting, premium"
  composition: "centered, generous whitespace"
```

此风格锚点将注入到每一个产品的提示词中，确保全系列视觉一致。

#### Step 2: 构造产品提示词矩阵

为每个产品构造独立提示词，但共享风格锚点:

```
产品提示词 =
  [产品具体描述] +
  [style_anchor.keywords] style +
  color palette: [style_anchor.primary_color] with [style_anchor.accent_color] +
  [style_anchor.background] +
  [style_anchor.lighting] +
  [style_anchor.mood] +
  [style_anchor.composition] +
  product photography, e-commerce ready, high resolution
```

示例 (假设 3 个产品):

```
产品矩阵:
├── Product 1: 保温杯 → "[保温杯描述], 日系极简 style, warm beige gradient bg, ..."
├── Product 2: 咖啡壶 → "[咖啡壶描述], 日系极简 style, warm beige gradient bg, ..."
└── Product 3: 茶具套装 → "[茶具描述], 日系极简 style, warm beige gradient bg, ..."
```

#### Step 3: 顺序执行生图

为每个产品调用 nano-banana2 (顺序执行，避免并发限制):

```bash
# 产品 1
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品1完整提示词]" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/batch/product-01/"

# 产品 2
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品2完整提示词]" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/batch/product-02/"

# 产品 N ...
cd {baseDir}/../nano-banana2/scripts && .venv/bin/python nano_banana2.py \
  --mode image \
  --prompt "[产品N完整提示词]" \
  --aspect-ratio "1:1" \
  --output "/tmp/design-pipeline/batch/product-NN/"
```

#### Step 4: 一致性审查

生成完所有产品图后，将结果截图或路径汇总展示给用户:

```
批量生成结果:
├── product-01/ 保温杯     ✅ 已生成
├── product-02/ 咖啡壶     ✅ 已生成
├── product-03/ 茶具套装   ✅ 已生成
└── 风格一致性: [简要评估]
```

如果某个产品图风格偏离，调整该产品提示词后单独重新生成。

#### Step 5: 输出

```
/tmp/design-pipeline/batch/
├── style-anchor.yaml    # 风格锚点文件
├── product-01/          # 产品1的主图
├── product-02/          # 产品2的主图
├── product-03/          # 产品3的主图
└── ...
```

---

## 提示词工程最佳实践

### 电商图像通用提示词结构

```
[主体] + [材质/颜色/特征] + [风格] + [色彩方案] + [背景] + [光线] + [构图] + [情绪] + [用途] + [品质]
```

### 风格关键词速查

| 风格 | 英文关键词 | 适用品类 |
|------|------------|----------|
| 日系极简 | Japanese minimalist, clean, zen | 家居、文具、茶具 |
| 韩系清新 | Korean fresh, pastel, soft | 美妆、服装、食品 |
| 国潮 | Chinese style, traditional motifs, bold | 茶叶、白酒、国货 |
| 科技感 | futuristic, tech, sleek, metallic | 数码、3C、智能设备 |
| 轻奢 | luxury, premium, elegant, gold accent | 珠宝、护肤、箱包 |
| 自然有机 | organic, natural, earthy tones | 食品、保健品、母婴 |
| 活力促销 | vibrant, bold colors, energetic, sale | 大促活动、清仓 |
| ins风 | Instagram aesthetic, lifestyle, trendy | 时尚、潮牌、生活 |

### 背景处理关键词

| 类型 | 提示词片段 |
|------|------------|
| 纯白底 | `clean white background, pure white` |
| 渐变底 | `gradient background from [色A] to [色B]` |
| 场景化 | `in a [场景] setting, lifestyle` |
| 纹理底 | `[marble/wood/fabric] texture background` |
| 虚化场景 | `blurred [场景] background, bokeh` |

### 光线关键词

| 类型 | 提示词片段 |
|------|------------|
| 柔光棚拍 | `soft studio lighting, even illumination` |
| 自然光 | `natural daylight, window light` |
| 戏剧光 | `dramatic lighting, strong contrast, rim light` |
| 暖光 | `warm golden hour lighting` |
| 冷光 | `cool blue-toned lighting, clinical` |

---

## 交互规范

### 接收需求时

1. 识别工作模式 (参考生成 / 产品主图 / Banner / 批量生成)
2. 确认必填参数是否齐全
3. 缺少信息时主动追问，追问简洁直接

### 追问模板

```
收到! 需要确认几个信息:
1. [缺少的信息A]?
2. [缺少的信息B]?
3. 风格偏好: [给出2-3个选项]?
```

### 执行过程中

- 每完成一个关键步骤，简要汇报进度
- 风格分析完成后，先展示设计简报让用户确认再生图
- 生图完成后展示结果并询问是否需要调整

### 交付时

```
设计完成!

📁 文件位置: /tmp/design-pipeline/[子目录]/
📐 尺寸: [具体尺寸]
🎨 风格: [风格关键词]

生成了 [N] 张素材:
1. [文件名] - [描述]
2. [文件名] - [描述]
...

需要调整吗? 我可以:
- 换个风格方向
- 调整配色
- 重新生成某张
- 出其他尺寸
```

---

## 输出目录结构

所有产出统一存放在 `/tmp/design-pipeline/`:

```
/tmp/design-pipeline/
├── reference/           # 参考截图 (模式1)
├── brief.md             # 设计简报 (模式1)
├── output/              # 参考生成产出 (模式1)
├── product-main/        # 产品主图 (模式2)
│   ├── variant-a/
│   ├── variant-b/
│   ├── variant-c/
│   └── variant-d/
├── banner/              # Banner素材 (模式3)
│   ├── wide/
│   ├── standard/
│   ├── mobile/
│   └── final/
└── batch/               # 批量生成 (模式4)
    ├── style-anchor.yaml
    ├── product-01/
    ├── product-02/
    └── ...
```

## 注意事项

1. **风格一致性**: 批量生成时始终使用同一份 style_anchor，不要中途修改
2. **提示词语言**: nano-banana2 提示词统一使用英文，效果最佳
3. **比例匹配**: 严格按照目标平台要求选择 aspect-ratio，不要混用
4. **迭代优先**: 先生成少量样本确认方向，再批量铺开
5. **文字叠加**: AI 生图不擅长生成精确文字，Banner/海报的文案部分建议后期叠加
6. **版权意识**: 不要在提示词中引用具体品牌名/IP名称，用风格描述替代
