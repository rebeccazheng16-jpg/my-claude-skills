---
name: broll-pipeline
description: B-Roll 全流程工具。三个阶段：build（从 Pexels/Pixabay 批量下载素材库）→ match（分析口播稿自动匹配 B-Roll 生成 storyboard）→ assemble（将主视频与 B-Roll 按 storyboard 时间线自动拼接输出成品）。触发词：B-Roll、stock footage、素材库、补充画面、匹配分镜、storyboard、拼接视频、插入B-Roll、组装视频、口播稿视频合成。
---

# B-Roll Pipeline

口播视频 B-Roll 全流程：素材下载 → 脚本匹配 → 视频拼接。

## 工具位置

```
/Users/kevingao/AI/Lina IP/broll-stock-finder/
```

## 三阶段工作流

```
build（预下载素材库）
  ↓
match（口播稿 → LLM 分析 → 本地匹配 → API 兜底 → storyboard.json）
  ↓
assemble（主视频 + B-Roll + storyboard → FFmpeg 拼接 → 成品视频）
```

## 使用方式

### 1. Build 模式（批量下载素材库）

```bash
TOOL="/Users/kevingao/AI/Lina IP/broll-stock-finder/broll_finder.py"

# 下载所有预设关键词
python3 "$TOOL" build

# 下载指定主题
python3 "$TOOL" build --theme entrepreneurship

# 仅下载高优先级
python3 "$TOOL" build --priority high

# 下载指定关键词
python3 "$TOOL" build --keyword "woman entrepreneur"
```

### 2. Match 模式（脚本匹配 B-Roll）

```bash
# 从文件读取脚本，指定视频时长
python3 "$TOOL" match --file script.txt --duration 60 -o storyboard.json

# 直接传入脚本文本
python3 "$TOOL" match --script "口播稿内容..."

# 仅匹配本地库（不调用 API）
python3 "$TOOL" match --file script.txt --local-only
```

### 3. Assemble 模式（视频拼接）

```bash
# 将主视频与 B-Roll 按 storyboard 拼接
python3 "$TOOL" assemble --video lina_heygen.mp4 --storyboard storyboard.json -o final.mp4

# 使用淡入淡出转场
python3 "$TOOL" assemble --video main.mp4 --storyboard storyboard.json --transition fade -o final.mp4
```

### 辅助命令

```bash
# 查看素材库统计
python3 "$TOOL" stats

# 搜索本地库
python3 "$TOOL" search --keyword "coffee,business"
```

## 前置条件

### API Keys

```bash
# 素材下载（至少一个）
export PIXABAY_API_KEY="your_key"   # https://pixabay.com/api/docs/
export PEXELS_API_KEY="your_key"    # https://www.pexels.com/api/

# LLM 脚本分析（match 模式）
export GOOGLE_API_KEY="your_key"    # Gemini（默认）
# 或 export ANTHROPIC_API_KEY="your_key"

# 视频拼接（assemble 模式）
# 需要 FFmpeg: brew install ffmpeg
```

## 配置文件

| 文件 | 用途 |
|------|------|
| `config.yaml` | API Keys、下载参数、LLM 模型选择 |
| `keywords.yaml` | 60 个关键词，4 大主题 13 分类 |

## 素材库现状

- 293 个视频，4.3 GB
- 来源：Pixabay
- 覆盖：创业商业、个人成长、日常生活、印尼市场、电商、社交媒体
