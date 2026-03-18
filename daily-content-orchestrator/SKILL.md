---
name: daily-content-orchestrator
description: 每日口播稿生成器。触发词：口播稿、今日口播稿、生成口播稿、写口播稿、今日内容、每日内容、Kevin口播稿、Lina口播稿、daily content。完整流程：搜热点→匹配痛点→生成10个选题→用户选择→生成脚本→(可选)B-Roll。
---

# Daily Content Orchestrator

Execute the complete daily workflow for founder IP content creation with human-in-the-loop topic selection.

## When to Use

- Running the daily content generation process
- Generating topic options for user selection
- Creating scripts after topic approval
- Testing the end-to-end workflow

## Cost Optimization Strategy

为节省 token 成本，本流程采用**分层模型策略**：

| Phase | 步骤 | 推荐模型 | 原因 |
|-------|------|----------|------|
| Phase 0 | 创始人选择 | **Sonnet** | 简单交互，无需高级推理 |
| Phase 1 | 热点搜索+选题生成 | **Sonnet** | 结构化任务，Sonnet足够 |
| Phase 2 | **脚本生成** | **Opus** | 需要高质量创意输出 |

**预估费用对比：**
- 全程 Opus: ~$0.56/次
- 分层策略: ~$0.25/次 (节省 55%)

### 执行方式

当执行此流程时：
1. Phase 0-1 使用 `model: "sonnet"` 的 Task agent
2. Phase 2 脚本生成回到主对话（Opus）完成

## News Cache (热点缓存)

为避免同一天重复搜索，热点新闻结果缓存到本地文件：

**缓存路径:** `~/.claude/cache/daily-news-{YYYY-MM-DD}.json`

### 缓存逻辑

```
┌─────────────────────────────────────────┐
│  检查今日缓存是否存在                    │
│  ~/.claude/cache/daily-news-$(date).json │
├─────────────────────────────────────────┤
│  存在 → 直接读取缓存                     │
│  不存在 → WebSearch → 写入缓存           │
└─────────────────────────────────────────┘
```

### 缓存命令

```bash
# 检查缓存
CACHE_FILE=~/.claude/cache/daily-news-$(date +%Y-%m-%d).json
if [ -f "$CACHE_FILE" ]; then
    echo "使用缓存的热点新闻"
    cat "$CACHE_FILE"
else
    echo "缓存不存在，需要搜索新热点"
fi

# 写入缓存（搜索后）
mkdir -p ~/.claude/cache
echo '[搜索结果JSON]' > "$CACHE_FILE"

# 清理过期缓存（保留7天）
find ~/.claude/cache -name "daily-news-*.json" -mtime +7 -delete
```

### 强制刷新

用户可通过以下命令强制刷新缓存：
```
"刷新今日热点" 或 "重新搜索热点"
```

## Workflow v6 (3 Founders + Narrative Templates + B-Roll)

```
┌─────────────────────────────────────────────────────────────┐
│                    DAILY WORKFLOW v6                         │
│        (3 Founders + Narrative Templates + B-Roll)           │
├─────────────────────────────────────────────────────────────┤
│  Phase 0: FOUNDER SELECTION              [Sonnet] 💰         │
│  ├─ Step 0a: 列出可用创始人 (Lina/Kevin/Mikey)               │
│  ├─ Step 0b: 用户选择创始人                                  │
│  └─ Step 0c: (可选) 用户输入内容方向                         │
│                                                              │
│  ⏸️  WAIT FOR USER SELECTION                                 │
│                                                              │
│  Phase 1: TOPIC GENERATION               [Sonnet] 💰         │
│  ├─ Step 1: 检查缓存/搜索热点 (带缓存)                       │
│  ├─ Step 2: 查询匹配的痛点                                   │
│  ├─ Step 3: 生成10个选题                                     │
│  │    └─ Lina: 标注叙事模式 (A1/A2/A3) 📖                    │
│  └─ Step 4: 展示选题供用户选择                               │
│                                                              │
│  ⏸️  WAIT FOR TOPIC SELECTION                                │
│                                                              │
│  Phase 2: SCRIPT GENERATION              [Opus] ✨           │
│  ├─ Step 5: 加载创始人风格 Skill                             │
│  │    ├─ Lina  → lina-founder-style + narrative-templates   │
│  │    ├─ Kevin → kevin-founder-style                         │
│  │    └─ Mikey → mikey-founder-style                         │
│  ├─ Step 6: 生成口播稿 (高质量输出)                          │
│  └─ Step 7: 输出纯文案版（带时间戳）                         │
│                                                              │
│  ⏸️  ASK: 是否需要 B-Roll？(可通过触发词跳过)                │
│                                                              │
│  Phase 3: B-ROLL GENERATION (可选)       [Opus] ✨ 📹        │
│  ├─ Step 8: 调用 b-roll-generator skill                     │
│  └─ Step 9: 输出内嵌 B-Roll 的完整脚本                      │
│                                                              │
│  Phase 4: DELIVERY (可选)                                    │
│  └─ Step 10: 推送到 Lark                                     │
└─────────────────────────────────────────────────────────────┘

💰 = 使用 Sonnet 节省成本
✨ = 使用 Opus 保证质量
📹 = B-Roll 视频提示词生成
📖 = Lina 专属叙事模板
```

## Phase 0: Founder Selection

### Step 0a: List Available Founders

First, show the user all available founder personas:

```bash
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq -r '.personas[] | "- \(.id): \(.name) (\(.title))"'
```

**Output Format:**
```
📢 请选择今日内容的创始人IP：

1. **Lina Lie** - Group CEO & Co-Founder
   - 语言: Bahasa Indonesia
   - 专长: 女性创业、品牌建设、美妆行业、代理商运营
   - 目标人群: 印尼女性创业者
   - 特色: 支持3种叙事模板 (A1借势智者/A2姐姐故事/A3对比清单)

2. **Kevin Gao** - Founder & Former ByteDance Senior Director
   - 语言: Bahasa Indonesia + 英文术语
   - 专长: AI应用、电商运营、TikTok Shop、直播带货
   - 目标人群: 科技/电商创业者/传统企业CEO
   - 特色: 类比思维、排比对仗

3. **Mikey** - 连续创业者 & 出海企业家
   - 语言: 中文
   - 专长: 出海电商、品牌操盘、TikTok跨境、MCN运营
   - 目标人群: 出海创业者、追求自律的职场人
   - 特色: D数字打卡、运动+感悟、名人引用 (芒格/乔布斯/曾国藩)

请输入创始人名字或编号 (1/2/3):
```

### Step 0b: User Selects Founder

User inputs founder name or number. Load selected persona:

```bash
# Example: Load Lina's persona
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[] | select(.id == "lina-lie")'

# Example: Load Kevin's persona
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[] | select(.id == "kevin-gao")'
```

### Step 0c: (Optional) User Input Direction

Ask user if they have a specific content direction:

```
(可选) 请输入今日内容方向，或直接回车跳过：
例如：
- "koc痛点"
- "AI热点"
- "TikTok Shop新规"
- "品牌定价"
```

If user provides direction, use it to focus the news search and topic generation.

## Phase 1: Topic Generation

> **模型**: 使用 Sonnet 执行此阶段以节省成本

### Step 1: Search Trending News (with Cache)

**首先检查今日缓存：**

```bash
CACHE_FILE=~/.claude/cache/daily-news-$(date +%Y-%m-%d).json
if [ -f "$CACHE_FILE" ]; then
    echo "✅ 使用缓存的热点新闻"
    cat "$CACHE_FILE"
else
    echo "🔍 缓存不存在，开始搜索..."
fi
```

**如无缓存，使用 WebSearch 搜索热点，然后保存：**

```bash
mkdir -p ~/.claude/cache
# 将搜索结果保存到缓存
echo '{"date":"YYYY-MM-DD","founder":"kevin-gao","news":[...]}' > "$CACHE_FILE"
```

**Search Keywords by Founder:**

| Founder | Search Focus |
|---------|--------------|
| Lina Lie | 女性创业、品牌建设、美妆行业、UMKM wanita、female entrepreneur Indonesia |
| Kevin Gao | AI应用、科技趋势、电商运营、TikTok Shop、e-commerce trends |
| Mikey | 出海创业、跨境电商、东南亚市场、品牌出海、TikTok跨境、创业心态 |

If user provided content direction in Step 0c, prioritize that direction in search.

### Step 2: Query Pain Points

Use `indonesia-women-entrepreneur-painpoints` skill to get relevant pain points.

**快速查询（推荐）- 使用本地JSON：**

```bash
# 按目标受众查询痛点
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | \
  jq '.categories[] | select(.target_audiences | contains(["female-agent"])) | {id, name_zh, pain_points: [.pain_points[] | {title_zh, emotional_trigger}]}'

# 按关键词查询
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | \
  jq '.categories[] | select(.keywords | any(contains("algorithm"))) | .pain_points[]'
```

**深度查询 - 使用NotebookLM：**

如需更详细的痛点背景，可查询NotebookLM（需要额外时间）。

**Query based on:**
- Founder's `target_audience` setting
- News topics found
- User's input direction (if provided)

### Step 3: Generate 10 Topics

Use `topic-generator` skill to create 10 diverse topics:

**Important**: Topics must align with founder's `content_focus`:
- **Lina**: 女性创业、品牌建设、美妆行业、销售增长、团队管理、代理商运营
- **Kevin**: AI应用与效率、电商运营策略、TikTok Shop玩法、直播带货、平台规则解读
- **Mikey**: 出海创业、品牌操盘、TikTok跨境、创业心态、自律与坚持、长期主义

Topic distribution:
- 3-4 news-driven topics (related to founder's expertise)
- 3-4 pain point-driven topics (targeting founder's audience)
- 2-3 evergreen topics (from founder's content_focus)

**Lina 专属叙事模板**：当选题适合叙事驱动时，标注推荐的叙事模式：
- **A1 借势智者对话**：财富观、商业智慧、他人经验
- **A2 姐姐分享故事**：创业困境、成长感悟、个人经历
- **A3 对比清单框架**：行为对比、选择引导、成功/失败对比

### Step 4: Present Topics to User

Display topics in Claude for user selection (NOT push to Lark).

**Output Format:**
```
# 📋 今日选题 - [DATE]
## 创始人: [Founder Name]

### 🔥 热点驱动 (1-4)
...

### 💡 痛点驱动 (5-7)
...

### 🌟 常青内容 (8-10)
...

请选择选题编号 (1-10):
```

## Phase 2: Script Generation

> **模型**: 使用 Opus 执行此阶段以保证创意质量

### Step 6: Receive User Selection

User replies with topic number (1-10).

### Step 7: Generate Script (Opus)

Use `tiktok-script-generator` skill with:
- Selected topic details
- Relevant pain points
- Persona configuration (including content_style and core_values)

**产品关联痛点规则**：

如果选题涉及以下关键词，优先使用 `intimate-wear-health` 分类的痛点：

| 触发词 | 优先痛点 | 内容角度 |
|--------|----------|----------|
| 内衣、bra、文胸 | 压迫感、闷热、瘙痒 | 舒适与健康，避免过度强调塑形 |
| **Tulandut**、图兰朵 | 压迫感、闷热、材质安全 | 舒适、透气、安全材质（品牌调性） |
| 带货、产品推荐（内衣类） | 尺码困惑、材质安全、钢圈疼痛 | 解决选购困惑，建立信任 |

```bash
# 查询产品关联规则
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.product_pain_point_mapping.triggers'
```

**Important**: 此步骤使用 Opus 模型，确保：
- 符合创始人语言风格和人设
- 排比对仗的节奏感
- 核心价值观自然融入
- 高质量创意输出

### Step 8: (Optional) Generate B-Roll Prompts

脚本生成完成后，询问用户是否需要 B-Roll 提示词：

```
📹 脚本已生成！是否需要生成 B-Roll 视频提示词？
- 输入 "是" 或 "B-Roll" → 调用 b-roll-generator skill
- 输入 "否" 或直接回车 → 跳过
```

**触发条件（自动调用 B-Roll）：**
- 用户在流程开始时说"需要 B-Roll"、"生成分镜"、"带视频提示词"
- 用户选择选题时说"选3，带 B-Roll"

**B-Roll 生成流程：**
1. 使用脚本的"纯文案版（带时间戳）"作为输入
2. 调用 `b-roll-generator` skill
3. 自动使用内嵌模式（因为脚本已有时间戳）
4. 输出带 B-Roll 标注的完整脚本

**输出示例：**
```
📹 B-Roll [0:01-0:04] (3s)
中文：职业女性在会议室中...
EN: Professional woman in meeting room...
```

### Step 9: (Optional) Push Script to Lark

```bash
python3 ~/.claude/skills/lark-webhook-sender/scripts/send_message.py \
  --webhook "https://open.larksuite.com/open-apis/bot/v2/hook/00653044-07ab-4b45-a1aa-b8cda5c93484" \
  --title "🎬 Daily Script - $(date +%Y-%m-%d)" \
  --content "[GENERATED SCRIPT WITH B-ROLL]" \
  --card
```

## Quick Commands

### Start Daily Workflow (Full)
```
"开始今日内容流程"
"今日内容"
"每日内容"
"口播稿"
"生成口播稿"
"写口播稿"
"daily content"
```
This will:
1. Show founder selection menu
2. Ask for optional content direction
3. Generate 10 topics based on selected founder
4. Wait for topic selection
5. Generate script
6. Ask if need B-Roll
7. (Optional) Generate B-Roll prompts
8. (Optional) Push to Lark

### Start with B-Roll (Auto-include)
```
"今日内容，带B-Roll"
"口播稿+分镜"
"生成口播稿，需要视频提示词"
"Kevin口播稿，带B-Roll"
```
This will auto-generate B-Roll without asking.

### Select Founder and Generate Topics
```
"使用Lina的人设生成今日选题"
"使用Kevin的人设，方向是AI热点，生成选题"
"使用Mikey的人设，方向是出海创业，生成选题"
"Kevin口播稿"
"Lina口播稿"
"Mikey口播稿"
"Mikey的口播稿，方向是长期主义"
```

### Generate Script for Selected Topic
```
"我选择选题3，请生成口播稿"
"选题3"
"第3个"
```

### Quick Start (Skip Selection)
```
"使用默认创始人(Lina)开始今日内容"
"Kevin今日内容，方向：TikTok Shop新规"
```

### Refresh Cache
```
"刷新今日热点"
"重新搜索热点"
```

## Target Audience Reference

| ID | Name | Focus |
|----|------|-------|
| `koc` | KOC | 内容创作、变现、流量 |
| `female-agent` | 女性代理商 | 分销、团队、利润 |
| `small-brand-founder` | 小品牌创业者 | 品牌建设、供应链、定价 |
| `top-kol` | 头部KOL | 商业合作、内容创新、团队 |
| `all` | 所有女性创业者 | 通用话题 |

## Configuration

### Change Default Persona

Edit `~/.claude/skills/founder-persona-manager/data/personas.json`:
- Add new persona to `personas` array
- Set `default_persona` to new persona ID

### Change Target Audience Focus

Edit the `target_audience` field in persona config, or specify when generating topics.

## Timing & Cost Guidelines

| Phase | Step | Time | Model | Est. Cost |
|-------|------|------|-------|-----------|
| Phase 0 | Founder selection | <1 min | Sonnet | ~$0.02 |
| Phase 1 | News search (cached) | <1 min | Sonnet | ~$0.01 |
| Phase 1 | Pain points | 1-2 min | Sonnet | ~$0.02 |
| Phase 1 | Topic generation | 2-3 min | Sonnet | ~$0.05 |
| - | User selection | Variable | - | - |
| Phase 2 | Script generation | 3-5 min | **Opus** | ~$0.15 |
| Phase 2 | Push to Lark | <1 min | - | - |
| **Total** | (excluding selection) | **~10 min** | Mixed | **~$0.25** |

**对比全程 Opus**: ~$0.56/次 → 节省 55%

**月度成本估算** (每日1次):
- 优化后: ~$7.50/月
- 优化前: ~$16.80/月

## Dependencies

This skill orchestrates:
- `indonesia-trending-news` - News gathering
- `indonesia-women-entrepreneur-painpoints` - Pain point research
- `founder-persona-manager` - Persona & audience config
- `topic-generator` - Topic option generation
- `tiktok-script-generator` - Script creation
- `b-roll-generator` - B-Roll 视频提示词生成（可选，Phase 3）
- `lark-webhook-sender` - Delivery

### Persona Style References (脚本生成时必须参考)

| Founder | Style Skill | 叙事模板 | 用途 |
|---------|-------------|----------|------|
| Lina Lie | `lina-founder-style` | `lina-narrative-templates` (A1/A2/A3) | 语言风格、标志性句式、价值观表达、爆款叙事结构 |
| Kevin Gao | `kevin-founder-style` | - | 语言风格、类比思维、排比对仗、金句引用 |
| Mikey | `mikey-founder-style` | - | D数字打卡、运动+感悟、名人引用、长期主义 |

**重要**：Phase 2 脚本生成时，必须先加载对应创始人的 style skill，确保输出符合人设风格。

**Style Skill 加载命令**：
```bash
# Lina
cat ~/.claude/skills/lina-founder-style/SKILL.md
cat ~/.claude/skills/tiktok-script-generator/references/lina-narrative-templates.md  # 叙事模板

# Kevin
cat ~/.claude/skills/kevin-founder-style/SKILL.md

# Mikey
cat ~/.claude/skills/mikey-founder-style/SKILL.md
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Topics not diverse enough | Ensure all audience segments covered |
| Pain points not matching | Adjust search keywords based on news |
| Script tone off | Review persona config and guidelines |
| Lark push fails | Check webhook URL and signature secret |
