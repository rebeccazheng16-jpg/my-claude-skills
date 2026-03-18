---
name: indonesia-tiktok-market-research
description: |
  印尼 TikTok 市场调研全流程工具。输入产品信息（文本/文件），自动完成：
  竞品分析、价格带研究、用户痛点挖掘、真实评论采集、TikTok 内容趋势分析，
  生成完整市场调研报告（Markdown + PDF）。
  触发词：市场调研、印尼调研、TikTok调研、竞品分析、产品调研、market research、印尼市场分析
---

# Indonesia TikTok Market Research

印尼 TikTok 市场调研全流程引擎。从产品输入到完整报告，一条龙完成。

---

## 执行流程

```
用户输入产品信息（文本/图片/文件）
        │
        ▼
  ┌─ Step 1: 产品解析 ─────────────────────────┐
  │  提取品类、特征、价位、目标人群              │
  └─────────────────────────────────────────────┘
        │
        ▼
  ┌─ Step 2: 生成调研查询 ─────────────────────┐
  │  8个维度 × 3-4条查询 = ~30条搜索指令        │
  │  双语（English + Bahasa Indonesia）          │
  └─────────────────────────────────────────────┘
        │
        ▼
  ┌─ Step 3: Firecrawl 数据采集 ───────────────┐
  │  并行执行搜索 → 重点页面深度抓取            │
  │  原始数据存入 /tmp/market-research/          │
  └─────────────────────────────────────────────┘
        │
        ▼
  ┌─ Step 4: 分析与报告 ───────────────────────┐
  │  结构化分析 → Markdown 报告 → PDF 导出      │
  └─────────────────────────────────────────────┘
```

---

## Step 1: 产品解析

### 接受输入格式
- **文本描述**：用户直接打字
- **文件**：图片、PDF、文档（用 Read 工具读取）
- **链接**：产品页面 URL（用 Firecrawl scrape 抓取）

### 必须提取的信息

解析用户输入，提取并确认以下字段。**缺失的字段必须追问用户**（前 3 项为必填）：

| 字段 | 示例 | 必填 |
|------|------|:----:|
| `product_name` | 防晒霜 / Sunscreen | Y |
| `category` | 美妆护肤 / Beauty & Skincare | Y |
| `category_id` | 印尼语品类名（如 skincare, kecantikan） | Y（自动生成） |
| `price_range` | $5-15 / Rp 75k-200k | N |
| `target_audience` | 18-35 岁印尼女性 | N |
| `key_features` | SPF50+, 不泛白, 清爽 | N |
| `competitors_known` | 用户已知竞品 | N |

解析完成后，向用户确认：
```
产品解析结果：
- 产品：{product_name}
- 品类：{category}（印尼语：{category_id}）
- 价位：{price_range}
- 目标人群：{target_audience}
- 核心特征：{key_features}

确认无误后开始调研？
```

---

## Step 2: 生成调研查询

基于产品信息，为 8 个调研维度生成搜索查询。**每条查询同时准备英语和印尼语版本**。

### 关键词构造规则

引用 `indonesia-market-context` skill 中的关键词库：
- 痛点词汇：keluhan, masalah, susah, gagal, ulasan
- 正面词汇：rekomendasi, terbaik, best, review
- 平台词汇：TikTok Shop, Tokopedia, Shopee, Lazada

### 8 个调研维度

#### D1: 市场概况 (Market Overview)
```
查询模板：
1. "{category} market size Indonesia 2025 2026"
2. "pasar {category_id} Indonesia tren pertumbuhan"
3. "{category} industry report Southeast Asia ecommerce"
4. "{category} Indonesia market opportunity TikTok Shop"
```
**目标**：市场规模、增长率、关键趋势

#### D2: 头部竞品 (Top Competitors)
```
查询模板：
1. "top {category} brand Indonesia TikTok Shop best selling"
2. "merek {category_id} terpopuler Indonesia 2025"
3. "{product_name} competitor Indonesia market share"
4. "brand {category_id} viral TikTok Indonesia"
```
**目标**：Top 10 品牌、市场份额、品牌定位

#### D3: 头部产品 (Top Products)
```
查询模板：
1. "best selling {product_name} Indonesia Tokopedia Shopee"
2. "produk {category_id} terlaris TikTok Shop Indonesia"
3. "{product_name} recommendation Indonesia 2025 review"
4. "rekomendasi {category_id} terbaik Indonesia"
```
**目标**：畅销单品、爆款特征、差异化卖点

#### D4: 价格带分布 (Price Band)
```
查询模板：
1. "harga {product_name} Indonesia Tokopedia range"
2. "{product_name} price comparison Indonesia cheap premium"
3. "{category_id} harga murah vs mahal Indonesia"
4. site:tokopedia.com "{product_name}" OR site:shopee.co.id "{product_name}"
```
**目标**：价格区间分布、甜点价位、高中低端占比

#### D5: 核心用户群体 (Target Users)
```
查询模板：
1. "{product_name} target consumer Indonesia demographics"
2. "siapa yang beli {category_id} Indonesia profil konsumen"
3. "{category} buyer persona Indonesia female TikTok"
4. "{category_id} konsumen Indonesia usia pendapatan"
```
**目标**：年龄/性别/收入/地域分布、购买动机

#### D6: 用户痛点与真实评论 (Pain Points & Reviews)
```
查询模板：
1. "{product_name} review Indonesia keluhan complaint"
2. "{category_id} masalah problem Indonesia user experience"
3. site:reddit.com "{product_name}" Indonesia
4. "{product_name} ulasan Tokopedia bintang 1 2 3"
5. "{category_id} kekurangan disadvantage Indonesia"
```
**重要**：这个维度要多抓。用户真实声音是报告核心价值。
- 搜索 Reddit、论坛帖子、电商评论
- 优先 scrape 有真实评论的页面
- 保留原始印尼语评论 + 翻译

#### D7: TikTok 内容趋势 (TikTok Content Trends)
```
查询模板：
1. "{product_name} TikTok Indonesia viral video trend"
2. "{category_id} TikTok content strategy Indonesia 2025"
3. "TikTok Shop {category} Indonesia top creator seller"
4. "{product_name} hashtag TikTok Indonesia views"
```
**目标**：热门内容形式、高播放量视频特征、头部创作者

#### D8: 短视频脚本方向 (Video Script Direction)
```
查询模板：
1. "cara jualan {category_id} TikTok Indonesia tips"
2. "{product_name} TikTok marketing strategy Indonesia"
3. "{product_name} unboxing review TikTok viral Indonesia"
4. "{category_id} TikTok hook opening viral Indonesia"
```
**目标**：有效的脚本类型、开头 Hook、卖点呈现方式

---

## Step 3: Firecrawl 数据采集

### 执行策略

**阶段 A：广度搜索**（~30 条查询）

使用 `mcp__firecrawl-mcp__firecrawl_search`，并行执行所有查询：

```json
{
  "query": "具体搜索词",
  "limit": 5,
  "sources": [{"type": "web"}]
}
```

**执行顺序**：
1. D1-D5 并行执行（市场/竞品/产品/价格/用户）
2. D6 单独执行（痛点需要更多条查询）
3. D7-D8 并行执行（TikTok 内容）

**阶段 B：深度抓取**（精选 5-10 个高价值页面）

从阶段 A 结果中，筛选以下类型页面进行 scrape：
- 含真实用户评论的帖子/产品页
- 行业报告或市场分析文章
- 竞品对比测评文章
- TikTok 营销案例分析

使用 `mcp__firecrawl-mcp__firecrawl_scrape`（如果未搜索到足够信息时使用 `firecrawl_search` 的 `scrapeOptions`）：
```json
{
  "scrapeOptions": {
    "formats": ["markdown"],
    "onlyMainContent": true
  }
}
```

### 数据存储

将每个维度的原始数据存入 `/tmp/market-research/`：
```
/tmp/market-research/
├── d1_market_overview.md
├── d2_competitors.md
├── d3_top_products.md
├── d4_pricing.md
├── d5_target_users.md
├── d6_pain_points.md      ← 最重要，保留原始评论
├── d7_tiktok_trends.md
├── d8_script_direction.md
└── raw_sources.md          ← 所有来源 URL 记录
```

每个文件格式：
```markdown
# D{n}: {维度名称}

## 搜索查询
- query 1: "xxx" → {结果数} 条
- query 2: "xxx" → {结果数} 条

## 关键发现
{从搜索结果中提取的结构化信息}

## 原始数据
{搜索结果的关键摘要和引用}

## 来源
- [标题](URL)
- [标题](URL)
```

---

## Step 4: 分析与报告

### 4.1 分析方法

引用 `analysis-frameworks` skill 中的以下框架：

| 报告章节 | 分析框架 | 用途 |
|---------|---------|------|
| 市场概况 | TAM-SAM-SOM | 估算市场规模 |
| 竞争格局 | 竞品矩阵 + 价值曲线 | 对比竞品定位 |
| 价格分析 | 价格带分析（参考 `pricing-strategy`） | 找甜点价位 |
| 用户洞察 | Persona + JTBD | 定义目标人群 |
| 内容策略 | 参考 `douyin-content-strategy` | TikTok 脚本框架 |

### 4.2 报告结构

输出路径：`~/AI/Research/{product_name}-印尼TikTok市场调研-{YYYY-MM-DD}.md`

```markdown
# {product_name} 印尼 TikTok 市场调研报告

> 调研日期：{date}
> 调研工具：Firecrawl + Claude Analysis
> 数据来源：{n} 个网页，{m} 条真实评论

---

## 一、执行摘要 (Executive Summary)

### 市场机会评分：{1-10}/10

| 维度 | 评分 | 说明 |
|------|------|------|
| 市场规模 | ★★★★☆ | ... |
| 竞争强度 | ★★★☆☆ | ... |
| 进入难度 | ★★☆☆☆ | ... |
| 内容机会 | ★★★★★ | ... |

### 三句话结论
1. ...
2. ...
3. ...

### Go / No-Go 建议
{明确建议，附理由}

---

## 二、市场大盘 (Market Overview)

### 2.1 市场规模
- TAM（总可触达市场）：
- SAM（可服务市场）：
- SOM（可获取市场）：

### 2.2 增长趋势
{数据支撑}

### 2.3 关键平台
| 平台 | 份额 | 特征 |
|------|------|------|
| TikTok Shop | | |
| Tokopedia | | |
| Shopee | | |

---

## 三、竞争格局 (Competitive Landscape)

### 3.1 竞品矩阵

| 品牌 | 价位 | 核心卖点 | TikTok 粉丝 | 评价 |
|------|------|---------|-------------|------|
| | | | | |

### 3.2 竞品定位图
{用文字描述二维定位：横轴=价格，纵轴=品质/功能}

### 3.3 竞品内容策略
{每个主要竞品的 TikTok 内容风格}

---

## 四、头部产品分析 (Top Products)

### 4.1 畅销单品 Top 10
| 排名 | 产品 | 品牌 | 价格 | 月销 | 核心卖点 |
|------|------|------|------|------|---------|
| | | | | | |

### 4.2 爆款共性
{总结畅销产品的共同特征}

---

## 五、价格带分析 (Pricing)

### 5.1 价格分布
| 价格带 | 占比 | 代表产品 | 竞争强度 |
|--------|------|---------|---------|
| 低端 (Rp xxx-xxx) | | | |
| 中端 (Rp xxx-xxx) | | | |
| 高端 (Rp xxx-xxx) | | | |

### 5.2 甜点价位建议
{推荐的最优价格区间及理由}

---

## 六、目标用户画像 (Target Users)

### 6.1 主要人群
{Persona 卡片格式}

**人群 A: {名称}**
- 年龄：
- 性别：
- 收入：
- 城市：
- 购买动机：
- 内容偏好：
- 决策因素：

### 6.2 次要人群
{同上格式}

---

## 七、用户痛点与真实声音 (Pain Points & Real Voice)

### 7.1 痛点排名

| 排名 | 痛点 | 频次 | 情绪强度 | 代表原话 |
|------|------|------|---------|---------|
| 1 | | | | |
| 2 | | | | |

### 7.2 用户原声（保留原文）

> "{印尼语原文}"
> —— {来源平台}, {用户标签}
> 翻译：{中文翻译}

{至少收集 10-15 条真实评论}

### 7.3 未被满足的需求
{从痛点中提炼的市场机会}

---

## 八、TikTok 内容策略 (Content Strategy)

### 8.1 内容趋势
| 内容类型 | 热度 | 适合度 | 案例 |
|---------|------|--------|------|
| 开箱评测 | | | |
| 使用前后对比 | | | |
| 教程/How-to | | | |
| 日常使用 vlog | | | |

### 8.2 高效 Hook 类型
（参考 `douyin-content-strategy` 的 Hook 框架）

| Hook 类型 | 示例 | 预期效果 |
|-----------|------|---------|
| 问题式 | "Kamu masih pakai {xxx}?" | 引发好奇 |
| 颠覆式 | "Jangan beli {xxx} sebelum..." | 阻止划走 |
| 痛点式 | "{痛点}? Ini solusinya" | 精准命中 |

### 8.3 推荐脚本模板（3 套）

**脚本 A: 痛点解决型**
```
Hook: {痛点问题}（2s）
痛点放大: {场景描述}（3s）
转折: {产品出场}（2s）
展示: {核心卖点演示}（5s）
证据: {效果/评论/数据}（3s）
CTA: {行动号召}（2s）
```

**脚本 B: 对比种草型**
```
Hook: {xxx vs xxx}（2s）
对比: {竞品痛点 vs 本品优势}（8s）
证据: {真实使用效果}（3s）
CTA: {限时优惠/链接}（2s）
```

**脚本 C: 真实体验型**
```
Hook: {使用 N 天后...}（2s）
过程: {真实使用过程}（8s）
结果: {效果展示}（3s）
CTA: {推荐理由}（2s）
```

---

## 九、可视化卖点提炼 (Visual Selling Points)

### 9.1 必拍画面清单
| 画面 | 说明 | 对应卖点 |
|------|------|---------|
| | | |

### 9.2 情绪触发点
{哪些场景能引发目标用户共鸣}

### 9.3 差异化视觉策略
{如何在视觉上区别于竞品}

---

## 十、行动建议 (Action Plan)

### 10.1 进入策略
{基于以上分析的市场进入建议}

### 10.2 首月内容计划
| 周 | 内容主题 | 脚本类型 | 数量 |
|----|---------|---------|------|
| W1 | | | |
| W2 | | | |
| W3 | | | |
| W4 | | | |

### 10.3 关键成功指标
| KPI | 目标值 | 衡量方式 |
|-----|--------|---------|
| | | |

---

## 附录

### A. 数据来源
{所有 URL 列表}

### B. 原始数据文件
{/tmp/market-research/ 目录说明}

### C. 调研局限性
{诚实说明数据覆盖不足之处}
```

### 4.3 PDF 导出

报告完成后，调用 `openai-pdf` skill 将 Markdown 转为 PDF：
- 输出路径：`~/AI/Research/{product_name}-印尼TikTok市场调研-{YYYY-MM-DD}.pdf`

---

## 异常处理

| 情况 | 处理方式 |
|------|---------|
| Firecrawl 某条查询无结果 | 换同义词重试一次，仍无则标注"数据不足" |
| 某个维度数据严重不足 | 在报告中明确标注"⚠️ 数据有限，仅供参考" |
| 产品过于小众 | 扩大品类范围搜索，提供品类级分析 |
| 电商价格数据抓不到 | 使用已有搜索结果中的价格信息，标注数据来源 |

---

## 复用的 Skills

| Skill | 复用方式 |
|-------|---------|
| `indonesia-market-context` | 印尼语关键词库、痛点词汇、数据源 |
| `indonesia-women-entrepreneur-painpoints` | 痛点分类框架（如目标人群为女性） |
| `analysis-frameworks` | TAM-SAM-SOM、竞品矩阵、Persona、JTBD |
| `pricing-strategy` | 价格带分析方法 |
| `douyin-content-strategy` | TikTok 推荐算法、脚本框架、Hook 类型 |
| `openai-pdf` | Markdown → PDF 导出 |

---

## 执行示例

```
用户: 我有一款防晒喷雾，想在印尼TikTok推广，帮我做市场调研

Claude:
1. "收到。让我先确认产品信息..."
   → 解析产品，追问缺失字段

2. "产品确认完毕，开始调研。共 8 个维度，约 30 条搜索..."
   → 执行 Firecrawl 搜索（并行）

3. "广度搜索完成，发现 {n} 条高价值页面，深度抓取中..."
   → 抓取重点页面

4. "数据收集完毕，开始分析..."
   → 结构化分析 + 报告生成

5. "调研报告已生成：
   - Markdown: ~/AI/Research/防晒喷雾-印尼TikTok市场调研-2026-02-25.md
   - PDF: ~/AI/Research/防晒喷雾-印尼TikTok市场调研-2026-02-25.pdf

   核心发现：
   1. 市场机会评分：8/10
   2. 甜点价位：Rp 89k-149k
   3. 推荐脚本方向：痛点解决型（防晒焦虑 + 使用对比）"
```
