---
name: creator-matrix-manager
description: |
  创作者矩阵管理器。管理 Person（人）→ Account（账号）→ Persona（人设）三层结构。
  此skill应在以下场景触发：(1)获取或配置人设信息 (2)查询某人设的知识范围 (3)为内容生成选择人设
  (4)管理创作者账号矩阵 (5)配置目标受众。
  触发词：人设、persona、账号矩阵、创作者管理、获取人设、知识范围、content creator、matrix。
  与 content-knowledge-hub 协作：提供人设配置，用于知识过滤和内容生成。
---

# Creator Matrix Manager - 创作者矩阵管理器

## 概述

管理创作者的多层级结构：Person（人）→ Account（账号）→ Persona（人设），支持内容生成时的人设选择和知识范围过滤。

## 数据模型

```
Person (人)
├── id: "lina"
├── name: "Lina Lie"
├── type: founder | KOL | KOC | virtual
├── style_ref: "lina-founder-style"  ← 关联风格 skill
│
└── Account[] (账号)
    ├── id: "lina-tiktok-id"
    ├── platform: TikTok | Instagram | 小红书 | WeChat
    ├── handle: "@linalie91"
    ├── region: "Indonesia"
    │
    └── Persona[] (人设)
        ├── id: "lina-fashion-expert"
        ├── name: "时尚面料专家"
        ├── knowledge_scope: ["面料/*", "服装/*"]  ← 可访问的知识范围
        ├── target_audience: "female-agent"
        └── content_style: {tone, topics, hashtags}
```

## 数据位置

```
~/.claude/skills/creator-matrix-manager/data/matrix.json
```

---

## 核心操作

### 1. 获取人设配置

**场景**：内容生成前获取人设信息

```bash
# 获取指定人设
cat data/matrix.json | jq '.personas[] | select(.id == "lina-fashion-expert")'

# 获取人设的知识范围
cat data/matrix.json | jq '.personas[] | select(.id == "lina-fashion-expert") | .knowledge_scope'
```

**输出示例**：
```json
{
  "id": "lina-fashion-expert",
  "name": "时尚面料专家",
  "knowledge_scope": ["面料/*", "服装/*", "穿搭/女装"],
  "target_audience": "female-agent",
  "content_style": {
    "tone": "专业、亲和、有深度",
    "topics": ["面料知识", "穿搭技巧", "服装品质鉴别"],
    "hashtags": ["#fashiontips", "#fabricexpert"]
  }
}
```

### 2. 列出所有人设

```bash
# 列出所有人设（简要）
cat data/matrix.json | jq '.personas[] | {id, name, knowledge_scope}'

# 按账号分组列出
cat data/matrix.json | jq '.accounts[] | {platform, handle, personas}'
```

### 3. 获取人员信息

```bash
# 获取指定人员及其所有账号
cat data/matrix.json | jq '.persons[] | select(.id == "lina")'

# 获取人员的风格引用
cat data/matrix.json | jq '.persons[] | select(.id == "lina") | .style_ref'
```

### 4. 查询知识范围

**用于 content-knowledge-hub 过滤知识**：

```bash
# 获取人设的知识范围（用于知识查询）
SCOPE=$(cat data/matrix.json | jq -r '.personas[] | select(.id == "lina-fashion-expert") | .knowledge_scope[]')
echo $SCOPE
# 输出: 面料/* 服装/* 穿搭/女装
```

---

## 当前创作者矩阵

### Lina Lie (李丽娜)

| 账号 | 平台 | 人设 | 知识范围 |
|------|------|------|----------|
| @linalie91 | TikTok ID | 时尚面料专家 | 面料/*, 服装/* |
| @linalie91 | TikTok ID | 美妆创业导师 | 美妆/*, 创业/* |
| @linalie91 | TikTok ID | 女性创业教练 | 创业/*, 团队管理/* |
| @linalie91 | Instagram | 生活方式分享者 | 生活/*, 健康/* |
| Lina李丽娜 | 小红书 | 海外创业者 | 出海/*, 印尼市场/* |

### Kevin Gao (高冉)

| 账号 | 平台 | 人设 | 知识范围 |
|------|------|------|----------|
| @kevingao_id | TikTok ID | AI应用专家 | AI/*, 效率/* |
| @kevingao_id | TikTok ID | 电商策略师 | 电商/*, TikTok/* |
| kevingao | WeChat | 科技领袖 | 科技/*, 创业/* |

### Mikey

| 账号 | 平台 | 人设 | 知识范围 |
|------|------|------|----------|
| @mikey_tulandut | TikTok ID | 品牌操盘手 | 品牌/*, 电商/* |
| @mikey_tulandut | TikTok ID | 自律成长者 | 成长/*, 自律/* |
| mikey | WeChat | 连续创业者 | 创业/*, 商业/* |

---

## 与其他 Skill 的协作

### 与 content-knowledge-hub 协作

内容生成时的完整流程：

```
1. 获取人设配置
   creator-matrix-manager → persona 配置

2. 获取知识范围
   persona.knowledge_scope → ["面料/*", "服装/*"]

3. 过滤知识
   content-knowledge-hub.query(scope=knowledge_scope)

4. 获取写作风格
   person.style_ref → 调用 lina-founder-style skill

5. 生成内容
   founder-style + persona + knowledge → 最终内容
```

### 与 *-founder-style 协作

```bash
# 获取人员的风格引用
STYLE_REF=$(cat data/matrix.json | jq -r '.persons[] | select(.id == "lina") | .style_ref')
# 输出: lina-founder-style

# 然后调用对应的 skill 获取风格指南
```

---

## 目标受众

### 可用受众类型

| ID | 名称 | 痛点关键词 |
|----|------|-----------|
| `koc` | KOC | 变现, 流量, 算法 |
| `female-agent` | 女性代理商 | 库存, 利润, 招商 |
| `small-brand-founder` | 小品牌创业者 | 品牌建设, 供应链 |
| `top-kol` | 头部KOL | 商务谈判, 内容创新 |
| `ecommerce-operator` | 电商运营 | ROI, 转化率 |
| `tech-entrepreneur` | 科技创业者 | AI应用, 效率提升 |
| `all` | 所有创业者 | 变现, 成长, 平衡 |

### 获取受众信息

```bash
# 获取指定受众的痛点关键词
cat data/matrix.json | jq '.target_audiences.available[] | select(.id == "female-agent") | .pain_keywords'
```

---

## 管理操作

### 添加新人设

编辑 `data/matrix.json`，在 `personas` 数组中添加：

```json
{
  "id": "new-persona-id",
  "account_id": "关联的账号ID",
  "name": "人设名称",
  "description": "人设描述",
  "knowledge_scope": ["主题1/*", "主题2/*"],
  "target_audience": "目标受众ID",
  "content_style": {
    "tone": "语气特点",
    "topics": ["话题1", "话题2"],
    "hashtags": ["#标签1", "#标签2"]
  }
}
```

### 添加新账号

在 `accounts` 数组中添加：

```json
{
  "id": "new-account-id",
  "person_id": "关联的人员ID",
  "platform": "平台名称",
  "handle": "@账号名",
  "region": "地区",
  "language": "语言代码",
  "personas": ["人设ID1", "人设ID2"]
}
```

### 添加新人员

在 `persons` 数组中添加：

```json
{
  "id": "new-person-id",
  "name": "姓名",
  "type": "founder",
  "style_ref": "xxx-founder-style",
  "bio": "简介",
  "accounts": ["账号ID1", "账号ID2"]
}
```

---

## 触发场景示例

| 用户说 | 执行操作 |
|--------|----------|
| "用 Lina 的面料专家人设写内容" | 获取 lina-fashion-expert 配置 |
| "这个人设可以用哪些知识" | 返回 knowledge_scope |
| "列出 Lina 的所有人设" | 查询 Lina 关联的所有 personas |
| "为电商运营者生成内容" | 匹配 target_audience=ecommerce-operator 的人设 |

---

## 数据结构参考

详细数据结构定义见 `references/data-structures.md`
