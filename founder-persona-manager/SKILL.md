---
name: founder-persona-manager
description: Manage founder IP personas and target audiences for content creation. This skill should be used when creating content for specific founder personas, configuring target audience segments, retrieving persona configurations, or setting up new founder profiles for TikTok/social media content generation.
---

# Founder Persona Manager

Manage and configure founder IP personas and target audience segments for content creation workflows.

## When to Use

- Creating TikTok scripts for a specific founder persona
- Configuring target audience segments for content
- Adding or updating founder profiles
- Switching between different target audiences
- Generating content tailored to specific audience segments

## Data Location

All configurations are stored in:
```
~/.claude/skills/founder-persona-manager/data/personas.json
```

## Target Audience Segments

### Available Audiences

| ID | Name (EN) | Name (ID) | Description |
|----|-----------|-----------|-------------|
| `koc` | KOC | KOC | 小型内容创作者，粉丝1万-10万 |
| `female-agent` | Female Agent/Reseller | Agen Wanita/Reseller | 女性代理商，代理品牌分销 |
| `small-brand-founder` | Small Brand Founder | Founder Brand Kecil | 小品牌创业者，自有品牌 |
| `top-kol` | Top KOL | KOL Besar | 头部KOL，粉丝50万以上 |
| `all` | All Female Entrepreneurs | Semua Wanita Wirausaha | 所有女性创业者（默认） |

### Get Target Audience Info

```bash
# List all available audiences
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.target_audiences.available'

# Get specific audience pain keywords
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.target_audiences.available[] | select(.id == "koc")'
```

### Pain Keywords by Audience

- **KOC**: 变现, 流量, 算法, 佣金, 转化
- **Female Agent**: 库存, 利润, 招商, 团队管理, 品牌选择
- **Small Brand Founder**: 品牌建设, 供应链, 资金, 定价, 差异化
- **Top KOL**: 商务谈判, 内容创新, 团队, 个人品牌, 多平台
- **All**: 变现, 平衡, 成长, 资金, 心理健康

## Persona Management

### Persona Structure

Each persona contains:

| Field | Description |
|-------|-------------|
| `id` | Unique identifier |
| `name` | Display name |
| `title` | Professional title |
| `mbti` | Personality type |
| `background` | Experience, achievements, expertise |
| `target_audience` | Default audience segment ID |
| `content_style` | Language, tone, approach |
| `content_guidelines` | Metrics, avoid/embrace lists |
| `signature_phrases` | Characteristic expressions |

### Get Persona

```bash
# Get default persona
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[] | select(.id == .default_persona)'

# Get specific persona
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[] | select(.id == "lina-lie")'

# List all persona IDs
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[].id'
```

## Quick Founder Selection

When starting daily content workflow, display this selection menu:

```
📢 请选择今日内容的创始人IP：

1. Lina Lie - Group CEO & Co-Founder
   语言: Bahasa Indonesia | 专长: 女性创业、品牌建设、美妆行业

2. Kevin Gao - Founder & Former ByteDance Senior Director
   语言: 中文 | 专长: AI应用、电商运营、TikTok Shop

3. Mikey - 连续创业者、品牌操盘手、出海企业家
   语言: 中文 | 专长: 出海电商、品牌操盘、TikTok跨境、自律成长

请输入编号 (1/2/3):
```

### List All Founders Command

```bash
# Quick list all founders
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq -r '.personas[] | "\(.id): \(.name) - \(.title)"'

# Get founder summary
cat ~/.claude/skills/founder-persona-manager/data/personas.json | jq '.personas[] | {id, name, title, language: .content_style.language, focus: .content_focus[0:3]}'
```

## Available Personas

### Lina Lie (Default)

- **Title**: Group CEO & Co-Founder
- **MBTI**: ENTJ
- **Background**: Former brand director; co-founded BIOAQUA ($50M in 2 years)
- **Default Audience**: All female entrepreneurs
- **Language**: Bahasa Indonesia (conversational)
- **Tone**: Inspiring, professional, authentic
- **Content Focus**: 女性创业、品牌建设、美妆行业、销售增长、团队管理、代理商运营

**Signature Phrases:**
- "Jadi gini..."
- "Yang paling penting itu..."
- "Aku pribadi sih..."
- "Dari pengalaman aku..."

### Kevin Gao

- **Title**: Founder & Former ByteDance Senior Director
- **MBTI**: INTJ
- **Background**: 20+ years at Google, Facebook, ByteDance; Led TikTok Shop global operations
- **Default Audience**: Tech entrepreneurs, E-commerce operators
- **Language**: 中文 (专业但通俗易懂)
- **Tone**: 理性、专业、数据驱动、洞察分享
- **Content Focus**: AI应用与效率、电商运营策略、TikTok Shop玩法、直播带货、平台规则解读、出海业务

**Signature Phrases:**
- "这个问题的本质是..."
- "给大家一个可执行的建议..."
- "很多人不知道的是..."

### Mikey

- **Title**: 连续创业者、品牌操盘手、出海企业家、Tulandut合伙人
- **MBTI**: ENFJ
- **Background**: 草根逆袭型创业者，从负债五千万到营收十亿；新三板上市经历；2025年TikTok越南跨境赛道夺冠
- **Default Audience**: All entrepreneurs
- **Language**: 中文 (口语化、接地气)
- **Tone**: 真诚、务实、正能量、有深度
- **Content Focus**: 出海创业实战、东南亚电商市场、品牌运营策略、自律与成长、商业案例复盘

**Core Values:**
- 长期主义、复利思维、定力优先、保持在场、真诚表达

**Signature Phrases:**
- "慢慢跑，不着急不着急～要学骆驼，沉得住气的动物"
- "世界上有一种英雄主义，那就是吃了无数次生活的苦后仍然热爱生活"
- "Keep it up!"
- "以史为鉴"
- "simple but not easy"

## Configuration Guide

### Add New Persona

Edit `data/personas.json` and add to the `personas` array:

```json
{
  "id": "new-founder",
  "name": "Founder Name",
  "title": "Title",
  "mbti": "XXXX",
  "background": {
    "experience": "...",
    "achievements": "...",
    "expertise": ["..."]
  },
  "target_audience": "all",
  "content_style": {
    "language": "...",
    "tone": "...",
    "approach": "..."
  },
  "content_guidelines": {
    "priority_metrics": ["..."],
    "avoid": ["..."],
    "embrace": ["..."]
  },
  "signature_phrases": ["..."]
}
```

### Add New Target Audience

Edit `data/personas.json` and add to `target_audiences.available`:

```json
{
  "id": "new-audience",
  "name": "English Name",
  "name_id": "Indonesian Name",
  "description": "Description",
  "pain_keywords": ["keyword1", "keyword2"]
}
```

### Change Default Settings

```bash
# Change default persona (edit JSON)
jq '.default_persona = "new-founder-id"' personas.json > tmp.json && mv tmp.json personas.json

# Change default target audience (edit JSON)
jq '.target_audiences.default = "koc"' personas.json > tmp.json && mv tmp.json personas.json
```

## Integration with Other Skills

This skill provides configuration for:
- `topic-generator`: Target audience determines topic angles
- `tiktok-script-generator`: Persona defines voice and style
- `daily-content-orchestrator`: Orchestrates content for configured persona/audience
