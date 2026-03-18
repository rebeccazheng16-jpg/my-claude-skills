# Creator Matrix 数据结构

## 完整 JSON Schema

### Person (人)

```json
{
  "id": "string",           // 唯一标识，如 "lina"
  "name": "string",         // 显示名称，如 "Lina Lie (李丽娜)"
  "type": "string",         // founder | KOL | KOC | virtual
  "style_ref": "string",    // 关联的风格 skill，如 "lina-founder-style"
  "bio": "string",          // 简介
  "accounts": ["string"]    // 关联的账号 ID 列表
}
```

**type 说明**：
| 类型 | 说明 |
|------|------|
| `founder` | 创始人，有对应的 *-founder-style skill |
| `KOL` | 头部达人，粉丝量大 |
| `KOC` | 素人种草，真实分享 |
| `virtual` | 虚拟人设，非真人 |

### Account (账号)

```json
{
  "id": "string",           // 唯一标识，如 "lina-tiktok-id"
  "person_id": "string",    // 关联的人员 ID
  "platform": "string",     // 平台：TikTok | Instagram | 小红书 | WeChat | YouTube
  "handle": "string",       // 账号名，如 "@linalie91"
  "region": "string",       // 地区：Indonesia | China | Global
  "language": "string",     // 主要语言：id | zh | en
  "personas": ["string"]    // 关联的人设 ID 列表
}
```

### Persona (人设)

```json
{
  "id": "string",           // 唯一标识，如 "lina-fashion-expert"
  "account_id": "string",   // 关联的账号 ID
  "name": "string",         // 人设名称（中文）
  "name_local": "string",   // 人设名称（本地语言，可选）
  "description": "string",  // 人设描述
  "knowledge_scope": ["string"],  // 知识范围，支持通配符
  "target_audience": "string",    // 目标受众 ID
  "content_style": {
    "tone": "string",       // 语气特点
    "topics": ["string"],   // 常见话题
    "hashtags": ["string"]  // 常用标签
  }
}
```

### knowledge_scope 格式

使用路径通配符匹配知识主题：

| 格式 | 说明 | 示例 |
|------|------|------|
| `主题/*` | 匹配主题下所有子主题 | `面料/*` 匹配 面料/羊绒, 面料/丝绸 等 |
| `主题/子主题` | 精确匹配 | `服装/内衣` 只匹配这一个主题 |
| `*` | 匹配所有 | 无限制 |

### Target Audience (目标受众)

```json
{
  "id": "string",           // 唯一标识
  "name": "string",         // 英文名称
  "name_id": "string",      // 印尼语名称
  "description": "string",  // 描述
  "pain_keywords": ["string"]  // 痛点关键词
}
```

---

## 完整数据示例

```json
{
  "version": "1.0",
  "updated_at": "2025-01-22T12:00:00Z",

  "persons": [
    {
      "id": "lina",
      "name": "Lina Lie (李丽娜)",
      "type": "founder",
      "style_ref": "lina-founder-style",
      "bio": "Tulandut联合创始人",
      "accounts": ["lina-tiktok-id", "lina-instagram"]
    }
  ],

  "accounts": [
    {
      "id": "lina-tiktok-id",
      "person_id": "lina",
      "platform": "TikTok",
      "handle": "@linalie91",
      "region": "Indonesia",
      "language": "id",
      "personas": ["lina-fashion-expert", "lina-beauty-mentor"]
    }
  ],

  "personas": [
    {
      "id": "lina-fashion-expert",
      "account_id": "lina-tiktok-id",
      "name": "时尚面料专家",
      "name_local": "Ahli Kain Fashion",
      "description": "专注于高端面料知识分享",
      "knowledge_scope": ["面料/*", "服装/*"],
      "target_audience": "female-agent",
      "content_style": {
        "tone": "专业、亲和、有深度",
        "topics": ["面料知识", "穿搭技巧"],
        "hashtags": ["#fashiontips", "#tulandut"]
      }
    }
  ],

  "target_audiences": {
    "default": "all",
    "available": [
      {
        "id": "female-agent",
        "name": "Female Agent / Reseller",
        "name_id": "Agen Wanita / Reseller",
        "description": "女性代理商",
        "pain_keywords": ["库存", "利润", "招商"]
      }
    ]
  }
}
```

---

## 关系图

```
Person (1) ──┬──▶ Account (N)
             │
             └──▶ style_ref ──▶ *-founder-style skill

Account (1) ──┬──▶ Persona (N)
              │
              └──▶ platform/region/language

Persona (1) ──┬──▶ knowledge_scope ──▶ 知识过滤
              │
              └──▶ target_audience ──▶ Target Audience
```

---

## 查询示例

### 获取某人的所有人设

```bash
# 1. 获取人员的账号列表
ACCOUNTS=$(cat matrix.json | jq -r '.persons[] | select(.id == "lina") | .accounts[]')

# 2. 获取这些账号的所有人设
cat matrix.json | jq --argjson accounts "$ACCOUNTS" \
  '.personas[] | select(.account_id as $aid | $accounts | index($aid))'
```

### 按知识范围筛选人设

```bash
# 查找能访问"面料"知识的人设
cat matrix.json | jq '.personas[] | select(.knowledge_scope[] | startswith("面料"))'
```

### 获取完整的人设上下文

```bash
# 获取人设 + 账号 + 人员 + 风格引用
PERSONA_ID="lina-fashion-expert"

# 人设
PERSONA=$(cat matrix.json | jq ".personas[] | select(.id == \"$PERSONA_ID\")")

# 账号
ACCOUNT_ID=$(echo $PERSONA | jq -r '.account_id')
ACCOUNT=$(cat matrix.json | jq ".accounts[] | select(.id == \"$ACCOUNT_ID\")")

# 人员
PERSON_ID=$(echo $ACCOUNT | jq -r '.person_id')
PERSON=$(cat matrix.json | jq ".persons[] | select(.id == \"$PERSON_ID\")")

# 风格引用
STYLE_REF=$(echo $PERSON | jq -r '.style_ref')
```
