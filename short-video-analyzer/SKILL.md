---
name: short-video-analyzer
description: |
  短视频深度分析工具。使用 Gemini 2.5 Flash 多模态 AI 对视频进行全方位分析。
  支持飞书机器人集成：私聊发链接 → 自动下载分析 → 群消息通知 + 多维表格存储。
  输出包括：完整口播稿、分镜脚本、产品营销分析、音频分析（BGM/音效）、
  视觉风格（拍摄/色彩/剪辑）、数据预测、运营建议、复刻指南（含 AI 视频提示词）。
  触发场景：(1)分析短视频内容 (2)拆解爆款视频 (3)提取视频脚本 (4)学习视频制作技巧
  (5)获取 AI 视频复刻提示词 (6)评估视频数据潜力 (7)飞书机器人自动化分析。
  触发词：分析视频、拆解视频、视频分析、爆款分析、脚本提取、Gemini分析、视频拆解。
---

# Short Video Analyzer - 短视频深度分析

## 飞书机器人集成（推荐使用方式）

```
┌─────────────────────────────────────────────────────────────────────┐
│                         飞书生态                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌───────────┐                              ┌───────────────────┐  │
│  │   用户    │  ①私聊发送链接               │   飞书群          │  │
│  │           │─────────────────┐            │                   │  │
│  └───────────┘                 │            │  ⑤ 分析结果卡片   │  │
│                                │            └───────────────────┘  │
│                                ▼                      ▲            │
│                       ┌───────────────┐               │            │
│                       │  飞书机器人   │───────────────┘            │
│                       └───────┬───────┘                            │
│                               │ ② 事件订阅                         │
│                               ▼                                    │
└───────────────────────────────┼─────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      云服务器 (Webhook Server)                       │
│                                                                     │
│  ③ 下载视频 ──→ ④ Gemini 分析 ──→ 发送群消息 + 写入多维表格        │
└─────────────────────────────────────────────────────────────────────┘
```

### 快速部署

```bash
# 1. 进入目录
cd ~/.claude/skills/short-video-analyzer

# 2. 配置环境变量
cp server/.env.example .env
# 编辑 .env 填入飞书应用和 Gemini API 配置

# 3. 部署到 Railway（推荐）
# 详见 docs/deployment.md
```

详细部署指南：[docs/deployment.md](docs/deployment.md)

---

## 本地使用（命令行模式）

```
┌─────────────────────────────────────────────────────────────────┐
│                   Short Video Pipeline                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  输入层              处理层                    输出层           │
│  ──────              ──────                    ──────           │
│                                                                 │
│  ┌─────────┐    ┌─────────────────┐    ┌──────────────────┐    │
│  │ TikTok  │    │                 │    │ 分析报告         │    │
│  │ 链接    │───→│                 │───→│ (JSON + MD)      │    │
│  └─────────┘    │                 │    └──────────────────┘    │
│                 │  Gemini 2.5     │                             │
│  ┌─────────┐    │  Flash          │    ┌──────────────────┐    │
│  │ 小红书  │───→│  多模态分析     │───→│ 切片素材         │    │
│  │ 链接    │    │                 │    │ (可选)           │    │
│  └─────────┘    │                 │    └──────────────────┘    │
│                 │                 │                             │
│  ┌─────────┐    │                 │    ┌──────────────────┐    │
│  │ 本地    │───→│                 │───→│ 飞书同步         │    │
│  │ 视频    │    └─────────────────┘    │ (可选)           │    │
│  └─────────┘                           └──────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## 快速开始

```bash
# 1. 首次使用：运行环境设置
bash ~/.claude/skills/short-video-analyzer/scripts/setup.sh

# 2. 分析视频
video-analyze ~/path/to/video.mp4

# 3. 全链路处理（下载 + 分析）
video-pipeline "https://www.tiktok.com/@user/video/123"
```

---

使用 Gemini 2.5 Flash 多模态 AI 对短视频进行全方位深度分析。

## 功能特性

| 分析维度 | 输出内容 |
|----------|----------|
| **基础信息** | 标题建议(3个)、时长、类型、目标受众画像 |
| **完整口播稿** | 逐字转录 + 多语言翻译 + 语速统计 |
| **分镜脚本** | 7段式结构，含时间、景别、机位、运镜、口播、画面描述 |
| **产品分析** | 卖点系统、利益矩阵、信任建立、CTA策略、说服技巧 |
| **音频分析** | BGM(类型/情绪/节奏)、音效、人声特质、音画同步 |
| **视觉风格** | 拍摄环境、灯光、色彩心理学、构图、剪辑节奏 |
| **内容策略** | Hook分析、叙事结构、互动触发点、人设定位 |
| **数据预测** | 完播率、互动率、转化率、各平台适配度 |
| **运营建议** | 标题、封面、标签、发布策略、评论区策略 |
| **复刻指南** | 难度评估、必备元素、步骤、AI视频提示词(Seedance) |
| **整体评估** | 综合评分(1-10)、爆款因素、关键学习点 |

## 快速使用

### 方式一：命令行

```bash
# 分析本地视频
node ~/.claude/skills/short-video-analyzer/scripts/analyze.js /path/to/video.mp4

# 分析后保存到同目录
# 输出：/path/to/video_analysis.json
```

### 方式二：在 Claude Code 中

```
分析这个视频 /path/to/video.mp4
```

### 方式三：与 tiktok-downloader 联动

```bash
# 下载 + 分析一条龙
tiktok-download --analyze "https://www.tiktok.com/@user/video/123"
```

## 输出示例

```json
{
  "basic_info": {
    "title_suggestion": ["标题1", "标题2", "标题3"],
    "duration": "0:58",
    "video_type": "教程",
    "target_audience": {
      "demographics": "18-35岁，男性",
      "psychographics": "追求时尚，注重形象",
      "consumption_scenario": "日常造型"
    }
  },
  "full_transcript": {
    "original": "完整口播稿原文...",
    "chinese": "中文翻译...",
    "language": "印尼语",
    "word_count": "147",
    "speaking_rate": "151"
  },
  "storyboard": [
    {
      "segment": 1,
      "name": "Hook（开场钩子）",
      "time_range": "0:00 - 0:04",
      "shot_type": "中近景",
      "camera_angle": "平视",
      "script": "「口播文案」",
      "visual_description": "画面描述...",
      "hook_type": "问题式",
      "retention_prediction": "中"
    }
  ],
  "product_analysis": {
    "selling_points_system": {
      "core_usp": "核心卖点一句话",
      "functional_points": ["功能卖点"],
      "emotional_points": ["情感卖点"]
    },
    "benefits_matrix": {
      "functional": "功能利益",
      "emotional": "情感利益",
      "social": "社交利益"
    },
    "cta_strategy": {
      "primary_cta": "主要行动号召",
      "urgency_elements": {}
    }
  },
  "audio_analysis": {
    "bgm": {
      "music_type": "电子",
      "music_mood": "欢快",
      "tempo": "快"
    },
    "sound_effects": {
      "effects_used": ["音效列表"]
    }
  },
  "visual_style_analysis": {
    "color_analysis": {
      "dominant_colors": ["黑", "灰"],
      "color_psychology": "专业感"
    },
    "editing_style": {
      "cutting_rhythm": "适中",
      "average_shot_length": "3秒"
    }
  },
  "performance_prediction": {
    "completion_rate": {
      "prediction": "中",
      "factors": "影响因素分析"
    },
    "platform_fit": {
      "tiktok": "高",
      "douyin": "高",
      "xiaohongshu": "高"
    }
  },
  "operation_suggestions": {
    "title_suggestions": ["标题1", "标题2"],
    "cover_frame": {
      "recommended_timestamp": "0:50"
    },
    "hashtag_suggestions": {
      "primary_tags": ["核心标签"]
    }
  },
  "replication_guide": {
    "difficulty_assessment": {
      "overall_difficulty": "中等"
    },
    "ai_video_prompts": {
      "seedance_prompt_cn": "Seedance中文提示词",
      "seedance_prompt_en": "Seedance English prompt"
    }
  },
  "overall_assessment": {
    "success_score": {
      "hook_score": "7",
      "content_score": "8",
      "overall_score": "6"
    },
    "viral_factors": {
      "primary_reason": "核心爆款原因"
    },
    "key_learnings": ["学习点1", "学习点2"]
  }
}
```

## 分镜脚本结构

采用 7 段式标准结构（可根据视频内容调整）：

| 段落 | 名称 | 典型时长 | 核心作用 |
|------|------|----------|----------|
| 1 | Hook（开场钩子） | 0-3秒 | 抓住注意力 |
| 2 | Pain Point（痛点共鸣） | 3-10秒 | 建立共鸣 |
| 3 | Product Intro（产品介绍） | 10-15秒 | 引出解决方案 |
| 4 | Selling Points（卖点展示） | 15-25秒 | 核心价值传递 |
| 5 | Demonstration（使用演示） | 25-40秒 | 证明有效性 |
| 6 | Benefits（效果利益） | 40-50秒 | 强化价值感知 |
| 7 | CTA（行动号召） | 50-60秒 | 引导转化 |

## 配置

### Gemini API Key

**方式 1：环境变量（推荐）**
```bash
export GEMINI_API_KEY="your-api-key"
# 或
export GOOGLE_API_KEY="your-api-key"
```

**方式 2：使用 api-keys-manager**
```bash
python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py set GOOGLE_AI "your-api-key"
```

获取 API Key：https://aistudio.google.com/app/apikey

## 依赖

```bash
# 安装依赖
cd ~/.claude/skills/short-video-analyzer
npm install

# 需要 Node.js 18+
```

### package.json

```json
{
  "name": "short-video-analyzer",
  "version": "1.0.0",
  "dependencies": {
    "@google/generative-ai": "^0.24.0"
  }
}
```

## 关联 Skills

| Skill | 关系 |
|-------|------|
| `commerce-storyboard` | **底层方法论**：分析结果可对照体感设计方法论评估视频的体感密度和叙事结构 |
| `tiktok-downloader` | 下载视频后调用分析 |
| `douyin-content-strategy` | 提供平台算法知识支持 |
| `video-content-atomizer` | 分析后可切割为素材 |
| `seedream-seedance-prompting` | 复刻指南中的 AI 提示词参考 |
| `b-roll-generator` | 基于分析结果生成 B-Roll 提示词 |

## 使用场景

1. **爆款拆解**：分析竞品/对标账号的爆款视频，学习成功要素
2. **脚本提取**：从视频中提取完整口播稿，用于二创或改编
3. **数据预测**：发布前评估视频的数据潜力
4. **复刻指南**：获取 AI 视频生成提示词，用于内容复刻
5. **运营优化**：获取标题、封面、标签等运营建议

## 技术原理

1. 使用 Google AI File API 上传视频文件
2. 调用 Gemini 2.5 Flash 多模态模型分析视频
3. 模型直接观看视频，提取画面、音频、文字信息
4. 按结构化提示词输出 JSON 格式分析报告

## 成本参考

| 视频时长 | 预计 Token | Gemini Flash 成本 |
|----------|------------|-------------------|
| 15秒 | ~10K | ~$0.01 |
| 30秒 | ~15K | ~$0.02 |
| 60秒 | ~25K | ~$0.03 |
| 120秒 | ~40K | ~$0.05 |

## 工作流模式

### 模式 1: 单视频分析

```bash
video-analyze ~/Videos/sample.mp4
```

输出：
- `sample_analysis.json` - 完整分析数据
- 终端显示分析摘要

### 模式 2: 全链路处理

```bash
# TikTok 视频
video-pipeline "https://www.tiktok.com/@user/video/123"

# 小红书视频
video-pipeline "https://www.xiaohongshu.com/explore/xxx"

# 本地视频
video-pipeline ~/Videos/sample.mp4
```

输出：
- 视频文件（如果是下载）
- `*_analysis.json` - 分析数据
- `report.md` - Markdown 报告

### 模式 3: 分析 + 切片

```bash
video-pipeline "视频链接" --atomize
```

输出：
- 分析报告
- 按分镜切割的视频片段
- 素材归档到分类文件夹

### 模式 4: 分析 + 飞书同步

```bash
video-pipeline "视频链接" --sync-lark
```

输出：
- 分析报告
- 自动同步到飞书多维表格

---

## 使用场景

### 场景 1: 竞品分析 / 爆款拆解

```bash
# 批量分析对标账号视频
for url in "${URLS[@]}"; do
  video-pipeline "$url"
done

# 输出：每个视频的详细分析报告，包含成功要素、可复制元素
```

### 场景 2: 内容复刻 / 二创

```bash
# 分析后获取 AI 视频提示词
video-analyze ~/爆款视频.mp4

# 查看复刻指南
cat ~/爆款视频_analysis.json | jq '.replication_guide'
# 输出：Seedance 提示词、场景分镜、B-Roll 建议
```

### 场景 3: 素材库建设

```bash
# 分析并切片归档
video-pipeline "视频链接" --atomize

# 输出目录结构：
# VideoCut/
# ├── 01_Hook/
# ├── 02_PainPoint/
# ├── 03_ProductDemo/
# └── ...
```

### 场景 4: 全流程内容生产

```
1. 采集爆款视频    → tiktok-downloader / media-crawler
2. 分析视频内容    → short-video-analyzer (本 skill)
3. 提取脚本框架    → 分析报告中的 storyboard
4. 生成新脚本      → tiktok-script-generator
5. 生成 B-Roll     → b-roll-generator
6. 合成视频        → video-composer / Seedance
7. 发布分发        → 各平台工具
```

---

## 与其他 Skills 的协作

```
                    ┌─────────────────────────┐
                    │   tiktok-downloader     │
                    │   xhs-video-downloader  │
                    │   media-crawler         │
                    └───────────┬─────────────┘
                                │ 下载视频
                                ▼
┌───────────────────────────────────────────────────────────────┐
│                   short-video-analyzer                        │
│                   (Gemini 2.5 Flash)                          │
│                                                               │
│  输入: 视频文件                                                │
│  输出: 分析报告 (JSON)                                         │
│        - 口播稿、分镜、产品分析、音频、视觉、预测、建议         │
└───────────────────────────────────────────────────────────────┘
          │                    │                    │
          ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ video-content-  │  │ tiktok-script-  │  │ b-roll-         │
│ atomizer        │  │ generator       │  │ generator       │
│                 │  │                 │  │                 │
│ 切片归档        │  │ 生成新脚本      │  │ 生成B-Roll      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   video-composer    │
                    │   Seedance API      │
                    │                     │
                    │   合成新视频        │
                    └─────────────────────┘
```

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1 | 2025-01-24 | 添加 Pipeline 全链路处理 |
| v1.0 | 2025-01-24 | 初始版本，完整分析功能 |
