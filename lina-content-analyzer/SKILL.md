---
name: lina-content-analyzer
description: |
  Lina TikTok/Instagram 内容表现分析工具。
  自动从飞书多维表格提取数据，一次性生成 3 种报告：
  1. Markdown 分析报告
  2. 交互式 HTML 图表 (artifacts-builder)
  3. 设计感信息图 PNG (canvas-design)
triggers:
  - 分析Lina内容
  - 分析口播稿
  - Lina内容分析
  - 内容表现分析
  - 口播稿数据分析
---

# Lina Content Analyzer

内容表现分析引擎，一次调用生成 3 种可视化报告。

---

## 执行指令

**当用户触发此 skill 时，必须按顺序完成以下所有步骤：**

```
┌─────────────────────────────────────────────────────────────┐
│                    执行流程（必须全部完成）                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Step 1: 数据获取                                           │
│  └─→ python3 scripts/fetch_data.py                         │
│                                                             │
│  Step 2: 数据分析                                           │
│  └─→ python3 scripts/analyze.py                            │
│                                                             │
│  Step 3: 生成 Markdown 报告                                 │
│  └─→ 输出到 ~/AI/Lina IP/Lina-口播稿数据分析报告.md        │
│                                                             │
│  Step 4: 生成交互式图表                                     │
│  └─→ 调用 artifacts-builder skill                          │
│  └─→ 输出 HTML 仪表板                                      │
│                                                             │
│  Step 5: 生成设计感信息图                                   │
│  └─→ 调用 canvas-design skill                              │
│  └─→ 输出 PNG 信息图                                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: 数据获取

```bash
python3 ~/.claude/skills/lina-content-analyzer/scripts/fetch_data.py
```

**数据源配置**:
```python
FEISHU_CONFIG = {
    "app_id": "cli_a9fbcb802e789ed2",
    "app_secret": "6DluFaAcL0klYLDhQk5W7bLO4yRRhotN",
    "api_base": "https://open.larksuite.com/open-apis",
    "app_token": "APIhbAcq9aLJQxskyPIl6fxRgnd",
    "table_id": "tblGmzYquULXY3oX"
}
```

**输出**: `/tmp/lina_raw_data.json`

---

## Step 2: 数据分析

```bash
python3 ~/.claude/skills/lina-content-analyzer/scripts/analyze.py
```

**分析维度**:
- 主题分析（经济独立/关系/心态/成长/美丽）
- 开头风格分析（问题式/颠覆式/女性定位/借势式/陈述式）
- 平台对比（TikTok vs Instagram）
- 内容特征对比（TOP 5 vs BOTTOM 5）

**输出**: `/tmp/lina_analysis.json`

---

## Step 3: 生成 Markdown 报告

读取 `/tmp/lina_analysis.json`，生成完整 Markdown 报告。

**输出路径**: `/Users/kevingao/AI/Lina IP/Lina-口播稿数据分析报告.md`

**报告结构**:
1. 执行摘要（关键指标 + 核心发现）
2. 可视化分析（ASCII 图表）
3. TOP 5 / BOTTOM 5 详情
4. 洞察与建议
5. 行动计划

---

## Step 4: 生成交互式图表

**调用 artifacts-builder skill**，创建 React + Recharts 仪表板。

### 图表数据准备

从 `/tmp/lina_analysis.json` 提取以下数据：

```javascript
// 主题数据
const topicData = [
  { name: '经济独立', avgViews: 99265, count: 15 },
  { name: '关系婚姻', avgViews: 104493, count: 1 },
  { name: '美丽形象', avgViews: 21716, count: 6 },
  { name: '心态能量', avgViews: 21278, count: 7 },
  { name: '成长提升', avgViews: 2813, count: 6 },
];

// 开头效果数据
const hookData = [
  { name: '问题式', avgViews: 92884, count: 5 },
  { name: '颠覆式', avgViews: 83666, count: 7 },
  { name: '女性定位', avgViews: 53906, count: 13 },
  { name: '个人故事', avgViews: 24322, count: 2 },
  { name: '陈述式', avgViews: 16378, count: 17 },
];

// 平台对比数据
const platformData = [
  { name: 'Instagram', views: 782160, count: 25 },
  { name: 'TikTok', views: 1295755, count: 23 },
];
```

### 仪表板组件

创建包含以下组件的 React 应用：

```tsx
// 1. 概览卡片
<StatsCard title="总播放" value="2,077,915" />
<StatsCard title="内容数" value="44" />
<StatsCard title="平均播放" value="47,225" />

// 2. 主题表现柱状图 (Horizontal Bar)
<TopicChart data={topicData} />

// 3. 开头效果柱状图
<HookChart data={hookData} />

// 4. 平台对比
<PlatformChart data={platformData} />

// 5. TOP 5 排名表
<TopContentTable data={top5Data} />

// 6. 播放量分布饼图
<DistributionPieChart data={distributionData} />
```

### 执行命令

```bash
# 初始化项目
bash ~/.claude/skills/artifacts-builder/scripts/init-artifact.sh lina-dashboard
cd /tmp/lina-dashboard

# 编辑 src/App.tsx (添加上述组件)

# 打包
bash ~/.claude/skills/artifacts-builder/scripts/bundle-artifact.sh

# 输出: /tmp/lina-dashboard/bundle.html
```

**输出**: 交互式 HTML 文件，展示给用户

---

## Step 5: 生成设计感信息图

**调用 canvas-design skill**，生成 PNG 信息图。

### 设计哲学

```markdown
## "Data Clarity" 设计哲学

这是一种将数据转化为视觉叙事的设计语言。追求让数字本身成为设计元素——
通过精确的排版、克制的色彩和充分的留白，让关键洞察如诗句般跃然纸上。

### 色彩系统
- 主色: 深蓝 (#1e3a5f) - 信任与专业
- 强调: 翠绿 (#22c55e) - 增长与成功
- 警示: 珊瑚红 (#ef4444) - 需要关注
- 背景: 米白 (#faf9f7) - 温和优雅

### 排版原则
- 大数字作为视觉锚点
- 小字注释提供上下文
- 大量留白创造呼吸感
- 中英双语并存
```

### 信息图内容

生成 1 张 PNG 信息图，包含：

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   LINA CONTENT PERFORMANCE INSIGHTS                        │
│   内容表现分析报告                                          │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐  │
│   │         2.08M              44            47K        │  │
│   │        总播放            内容数         平均播放     │  │
│   └─────────────────────────────────────────────────────┘  │
│                                                             │
│   🔥 爆款公式                                              │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│   "钱" + "女性定位" + "问题开头" = 高播放                   │
│                                                             │
│   📊 主题表现                                              │
│   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 经济独立 99k      │
│   ━━━━━━━━━━━━━━━━━━━━━━━━ 关系婚姻 104k                   │
│   ━━━━━━━━━━━━ 美丽形象 22k                                │
│   ━━ 成长提升 3k ⚠️                                        │
│                                                             │
│   ✅ DO                    ❌ DON'T                        │
│   经济独立话题              纯成长鸡汤                      │
│   问题式开头                陈述式开头                      │
│   1000-1200字              1500+字                         │
│                                                             │
│   📱 平台策略: TikTok 优先 (65% 表现更好)                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**输出**: `/Users/kevingao/AI/Lina IP/Lina-内容分析-信息图.png`

---

## 输出清单

执行完成后，应生成以下 3 个文件：

| # | 类型 | 输出路径 | 工具 |
|:-:|------|---------|------|
| 1 | Markdown 报告 | `~/AI/Lina IP/Lina-口播稿数据分析报告.md` | 内置 |
| 2 | 交互式图表 | 展示给用户 (HTML artifact) | artifacts-builder |
| 3 | 设计感信息图 | `~/AI/Lina IP/Lina-内容分析-信息图.png` | canvas-design |

---

## 完整执行示例

当用户说 "分析Lina内容" 时，Claude 应该：

```
用户: 分析Lina内容

Claude:
1. "正在获取飞书数据..."
   → 运行 fetch_data.py

2. "正在分析内容表现..."
   → 运行 analyze.py

3. "生成 Markdown 报告..."
   → 写入 Lina-口播稿数据分析报告.md

4. "生成交互式图表..."
   → 调用 artifacts-builder
   → 展示 HTML 仪表板给用户

5. "生成设计感信息图..."
   → 调用 canvas-design
   → 保存 PNG 并展示给用户

6. 输出总结:
   "✅ 分析完成，已生成 3 种报告：
    - Markdown: ~/AI/Lina IP/Lina-口播稿数据分析报告.md
    - 交互式图表: [上方展示]
    - 信息图: ~/AI/Lina IP/Lina-内容分析-信息图.png

    核心发现：
    1. 经济独立主题表现最佳 (平均99k播放)
    2. 问题式开头效果最好 (是陈述式的6倍)
    3. TikTok优先发布 (65%内容表现更好)"
```

---

## 数据更新

如果飞书表格配置发生变化，更新以下文件中的配置：

```
~/.claude/skills/lina-content-analyzer/scripts/fetch_data.py

FEISHU_CONFIG = {
    "app_token": "新的app_token",
    "table_id": "新的table_id"
}
```

---

## 相关 Skills

| Skill | 用途 |
|-------|------|
| **artifacts-builder** | Step 4 生成交互式图表 |
| **canvas-design** | Step 5 生成设计感信息图 |
| **super-analyst-core** | 分析框架参考 |
| **feishu-developer** | 飞书 API 参考 |
