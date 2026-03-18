---
name: indonesia-women-entrepreneur-painpoints
description: 印尼女性创业者痛点知识库。触发词：女性创业、女性痛点、印尼痛点、KOC痛点、代理痛点、主播痛点、微商痛点、MLM痛点、创业者挑战。提供12大痛点分类、6种用户画像、720+数据点，用于口播稿选题和内容创作。
---

# Indonesia Women Entrepreneur Painpoints

印尼女性创业者/KOC/KOL痛点研究知识库，基于2024.07-2025.01期间720+数据点的调研分析。

## 触发场景

当用户：
- 需要了解印尼女性创业者的痛点
- 创作面向女性创业者的TikTok内容
- 为口播稿寻找痛点切入角度
- 研究特定群体（MLM代理、带货主播、微商代理）的挑战
- 提到关键词：女性创业、痛点、印尼、KOC、代理、主播

## 数据源

**本地 JSON 文件（推荐，零延迟）：**
```
~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json
```

## 痛点分类总览

| # | 类别 | 聚合度 | 情绪 | 核心问题 |
|---|------|--------|------|----------|
| 1 | 资金获取 | 95% | 强负面 | 女性仅获2.8%VC投资 |
| 2 | 心理健康 | 92% | 强负面 | 78%创作者倦怠 |
| 3 | 收入付款 | 90% | 强负面 | 付款延迟达5个月 |
| 4 | 算法平台 | 88% | 负面 | Shadowban无预警 |
| 5 | 家庭负担 | 88% | 负面 | 三明治一代压力 |
| 6 | 数字技能 | 85% | 负面 | 37%仅基础操作 |
| 7 | 性别偏见 | 82% | 负面 | 自信心差距20% |
| 8 | MLM特有 | 90% | 强负面 | 95%招募失败 |
| 9 | 主播特有 | 88% | 强负面 | 日均6小时直播 |
| 10 | 微商特有 | 85% | 负面 | 利润双重挤压 |

## 用户画像

| 画像 | 年龄 | 粉丝量 | 主要痛点 |
|------|------|--------|----------|
| 微型电商创业者 | 25-40 | 10K-50K | 佣金高、COD拒收、价格战 |
| 内容创作者/KOC | 20-35 | 10K-100K | 倦怠、算法波动、付款延迟 |
| 中型KOL | 25-40 | 100K-500K | 预算削减、以物易物、互动下降 |
| 传统MSME | 35-55 | <10K | 数字技能、融资困难、认证复杂 |
| MLM代理 | 25-45 | N/A | 招不到人、社交破裂、囤货 |
| 带货主播 | 20-35 | 10K-500K | 直播压力、收入不稳、Agency剥削 |

## 快速查询

### 按分类查询痛点

```bash
# 查看所有分类
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | {id, name_zh, aggregation}'

# 查询特定分类（如：心理健康）
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.id == "mental-health") | .pain_points[]'

# 查询高聚合度痛点（>90%）
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.aggregation >= 90) | {name_zh, aggregation, pain_points: [.pain_points[].title_zh]}'
```

### 按用户画像查询

```bash
# 查看所有画像
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.personas[] | {id, name_zh, top_pain_points}'

# 查询特定画像（如：带货主播）
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.personas[] | select(.id == "live-host")'

# 查询适合某画像的痛点分类
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.target_audiences | contains(["live-host"])) | {name_zh, pain_points: [.pain_points[].title_zh]}'
```

### 按关键词搜索

```bash
# 搜索包含特定关键词的分类
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.keywords | any(contains("burnout"))) | {name_zh, pain_points}'

# 搜索情绪触发词
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.emotional_keywords'
```

### 获取关键统计

```bash
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.key_stats'
```

## 输出格式

查询痛点时，结构化输出：

```
## 痛点摘要
- **分类**: [分类名称]
- **聚合度**: [百分比]
- **核心问题**: [一句话描述]
- **情绪触发**: [目标受众的感受]

## 内容角度
- **Hook 潜力**: [如何作为视频开头]
- **解决方向**: [可以提供什么建议/洞察]
- **适合画像**: [哪些用户画像最相关]
```

## 与其他 Skill 集成

此 skill 为以下 skill 提供数据支持：

| Skill | 用途 |
|-------|------|
| `daily-content-orchestrator` | 热点匹配痛点，生成选题 |
| `tiktok-script-generator` | 痛点驱动 Hook 和内容角度 |
| `topic-generator` | 基于痛点生成选题选项 |

## 常用组合查询

### 为 Lina（女性创业方向）获取痛点

```bash
# 适合 Lina 的痛点（女性创业、代理、品牌）
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.target_audiences | any(. == "all" or . == "female-agent" or . == "small-brand-founder")) | {name_zh, pain_points: [.pain_points[] | {title_zh, emotional_trigger}]}'
```

### 为 Kevin（科技/电商方向）获取痛点

```bash
# 适合 Kevin 的痛点（电商、主播、算法）
cat ~/.claude/skills/indonesia-women-entrepreneur-painpoints/data/pain-points.json | jq '.categories[] | select(.target_audiences | any(. == "live-host" or . == "reseller" or . == "koc")) | {name_zh, pain_points: [.pain_points[] | {title_zh, emotional_trigger}]}'
```

## 参考文档

完整调研报告存放在 `references/` 目录：

- `Indonesia_Women_Entrepreneur_Pain_Point_Analysis_Report.md` - 主报告（35KB）
- `印尼MLM代理痛点调研报告_2025-01-14.md` - MLM专题
- `印尼带货主播痛点调研报告_2025-01-14.md` - 主播专题
- `印尼微商代理痛点调研报告_2025-01-14.md` - 微商专题

## 数据更新

- **版本**: 2.0.0
- **最后更新**: 2025-01-19
- **数据点**: 720+
- **调研周期**: 2024.07 - 2025.01
- **来源**: TikTok, YouTube, Instagram, Media Reports, Industry Reports
