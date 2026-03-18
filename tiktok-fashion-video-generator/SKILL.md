---
name: tiktok-fashion-video-generator
description: 从参考图一键生成 TikTok 穿搭展示视频，包含分段动作、自动拼接、多语言文案生成。适用于服装电商、穿搭博主、KOC 带货场景。
triggers:
  - 生成穿搭视频
  - TikTok视频
  - 服装展示视频
  - 图生视频
  - 穿搭展示
  - fashion video
  - OOTD视频
---

# TikTok Fashion Video Generator

从一张参考图自动生成 TikTok 穿搭展示视频，并提供多语言标题和文案。

## 工作流程

```
┌─────────────────────────────────────────────────────────────────────┐
│                         完整工作流                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📸 参考图片                                                         │
│      ↓                                                              │
│  📤 上传到临时存储 (获取公网 URL)                                     │
│      ↓                                                              │
│  🎬 分段视频生成 (Seedance 1.5 Pro)                                  │
│      ├── 第1段: 站立微动                                             │
│      ├── 第2段: 展示动作                                             │
│      ├── 第3段: 转身侧面                                             │
│      ├── 第4段: 背面回眸                                             │
│      ├── 第5段: 转回正面                                             │
│      └── 第6段: 最终定格                                             │
│      ↓                                                              │
│  🔗 ffmpeg 拼接                                                      │
│      ↓                                                              │
│  📝 生成标题 + 文案 + 标签                                           │
│      ↓                                                              │
│  ✅ 输出: 视频文件 + 文案文档                                         │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## 交互式模式（推荐）

当用户需要预览并选择保留哪些段落时，使用交互式模式：

```
┌─────────────────────────────────────────────────────────────────────┐
│                    交互式视频生成流程                                 │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ① 用户提供参考图                                                    │
│      ↓                                                              │
│  ② 运行 generate_interactive.py 生成所有段落                         │
│      ↓                                                              │
│  ③ 输出: segments/ (视频) + thumbnails/ (缩略图)                     │
│      ↓                                                              │
│  ④ Claude 读取缩略图，用 AskUserQuestion 让用户选择                   │
│      ↓                                                              │
│  ⑤ 根据用户选择拼接最终视频                                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Claude Code 交互式工作流

**步骤 1**: 生成所有段落
```bash
python3 ~/.claude/skills/tiktok-fashion-video-generator/scripts/generate_interactive.py ~/path/to/image.png
```

**步骤 2**: 读取段落信息
```python
# 输出目录: ~/Downloads/tiktok_fashion_YYYYMMDD_HHMMSS/
# 包含:
#   segments/segment_1.mp4 ~ segment_6.mp4  # 视频片段
#   thumbnails/thumb_1.jpg ~ thumb_6.jpg    # 缩略图
#   segments_info.json                       # 段落元数据
```

**步骤 3**: 展示缩略图让用户选择
```
Claude 使用 AskUserQuestion 工具:

questions:
  - question: "请选择要保留的视频段落（可多选）"
    header: "段落选择"
    multiSelect: true
    options:
      - label: "1. 站立微动"
        description: "模特自然站立，身体轻微摆动"
      - label: "2. 展示上衣"
        description: "双手抬起展示上衣"
      - label: "3. 转身侧面"
        description: "转身90度展示侧面"
      - label: "4. 背面回眸"
        description: "背对镜头后回头"
```

**步骤 4**: 拼接选中段落
```bash
# 假设用户选择了 1, 3, 4, 6
ffmpeg -y -f concat -safe 0 -i concat_list.txt -c copy final_video.mp4
```

### 输出目录结构（交互式模式）

```
~/Downloads/tiktok_fashion_YYYYMMDD_HHMMSS/
├── segments/
│   ├── segment_1.mp4
│   ├── segment_2.mp4
│   └── ...
├── thumbnails/
│   ├── thumb_1.jpg      # 用于预览
│   ├── thumb_2.jpg
│   └── ...
├── segments_info.json   # 段落元数据
└── final_video.mp4      # 用户选择后的最终视频
```

---

## 快速使用

### 方式1：命令行

```bash
# 生成30秒视频（6段）
tiktok-fashion ~/path/to/image.png

# 生成15秒视频（3段）
tiktok-fashion ~/path/to/image.png --duration 15

# 指定目标市场
tiktok-fashion ~/path/to/image.png --market indonesia --gender female
```

### 方式2：在 Claude Code 中

```
用这张图片生成一个TikTok穿搭视频，面向印尼女性用户
```

## 参数说明

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--duration` | 30 | 视频时长(秒): 15/20/25/30 |
| `--market` | indonesia | 目标市场: indonesia/china/global |
| `--gender` | female | 目标性别: female/male/unisex |
| `--style` | casual | 风格: casual/formal/streetwear |
| `--no-audio` | true | 不生成音频（后期配音） |

## 视频动作模板

### 全身穿搭展示（默认）

```python
SEGMENTS_FULLBODY = [
    "模特自然站立面向镜头，双手插在裤兜，身体轻微左右摆动后站定。镜头固定。",
    "模特双手从裤兜抽出，缓缓抬起双臂微微张开展示上衣，随后手臂放下。镜头固定。",
    "模特缓慢向右转身约90度展示侧面轮廓，站定后左手轻搭腰间。镜头固定。",
    "模特继续向右转身至背对镜头，停顿展示背面，随后微微回头看向镜头。镜头固定。",
    "模特从背面缓缓转回正面，双手自然下垂，站定后调整站姿。镜头固定。",
    "模特面向镜头站定，双手重新插入裤兜，嘴角微扬，轻轻点头后静止。镜头固定。",
]
```

### 镜子自拍场景

```python
SEGMENTS_MIRROR_SELFIE = [
    "模特保持手机自拍姿势，身体轻微左右摆动，目光看向镜头，嘴角微扬。镜头固定。",
    "模特左手缓缓抬起轻触发丝，头微微侧向一边，随后手放下。镜头固定。",
    "模特身体缓慢向右侧转约20度，展示侧面轮廓，目光依然看向镜头。镜头固定。",
    "模特身体缓缓转回正面，嘴唇微张后闭合，眼神略带俏皮。镜头固定。",
    "模特微微挺胸调整站姿，下巴轻抬，目光自信看向镜头。镜头固定。",
    "模特保持姿势，嘴角缓缓上扬露出微笑，轻轻点头后静止。镜头固定。",
]
```

### 上半身/坐姿场景

```python
SEGMENTS_UPPER_BODY = [
    "模特面向镜头自然微笑，头部轻微左右摆动后正视镜头。镜头固定。",
    "模特右手抬起整理衣领或发丝，目光短暂下移后抬头。镜头固定。",
    "模特身体略微向右侧倾斜，展示侧面轮廓，随后回正。镜头固定。",
    "模特面向镜头，嘴角上扬露出微笑，轻轻点头后静止。镜头固定。",
]
```

## 文案模板

### 印尼语 (Indonesia)

```python
COPY_TEMPLATES_ID = {
    "casual": [
        {
            "title": "Outfit ke kantor tapi tetap santai ✨",
            "caption": "Siapa bilang ke kantor harus ribet? 🤭\n\n{product_desc}\n\nSave dulu biar nggak lupa! 📌",
            "hashtags": "#ootdindonesia #outfitkantor #fashiontiktok #workoutfit #styleinspo #fyp"
        },
        {
            "title": "1 celana, bisa dipake kemana aja 👀",
            "caption": "Celana ini literally jadi bestie aku sekarang 😍\n\n✅ Ke kantor - bisa\n✅ Hangout - bisa\n✅ Kondangan - bisa juga!\n\n{product_desc}",
            "hashtags": "#celanakulot #outfitideas #ootdindokece #capsulewardrobe #viral"
        },
    ],
    "formal": [...],
    "streetwear": [...],
}
```

### 中文 (China)

```python
COPY_TEMPLATES_CN = {
    "casual": [
        {
            "title": "通勤穿搭 | 简约不简单 ✨",
            "caption": "每天早上不知道穿什么？\n\n这套look闭眼入！\n{product_desc}\n\n点赞收藏不迷路～",
            "hashtags": "#穿搭分享 #通勤穿搭 #ootd #显瘦穿搭 #抖音穿搭"
        },
    ],
}
```

## API 配置

### 环境变量

```bash
# 豆包 Seedance API (必需)
export DOUBAO_ARK="your-api-key"

# 或使用 api-keys-manager
python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py set DOUBAO_ARK "your-key"
```

### API 参数

| 参数 | 值 | 说明 |
|------|-----|------|
| `model` | `doubao-seedance-1-5-pro-251215` | Seedance 1.5 Pro |
| `duration` | 5 | 每段5秒 |
| `resolution` | `720p` | 分辨率 |
| `ratio` | `9:16` | 竖屏比例 |
| `generate_audio` | `false` | 不生成音频 |
| `return_last_frame` | `true` | 返回尾帧用于连续生成 |

## 输出文件

```
~/Downloads/tiktok_fashion_YYYYMMDD_HHMMSS/
├── segments/
│   ├── segment_1.mp4      # 第1段
│   ├── segment_2.mp4      # 第2段
│   └── ...
├── final_video.mp4        # 最终拼接视频
├── copy.json              # 文案数据
└── copy.txt               # 文案文本（可直接复制）
```

## 成本估算

| 时长 | 段数 | Seedance 成本 |
|------|------|---------------|
| 15秒 | 3段 | ~$0.75 |
| 20秒 | 4段 | ~$1.00 |
| 30秒 | 6段 | ~$1.50 |

计算公式: `段数 × 5秒 × $0.05/秒`

## 最佳实践

### 1. 图片要求

| 要求 | 说明 |
|------|------|
| **比例** | 9:16 竖屏最佳 |
| **清晰度** | 720p 以上 |
| **主体** | 人物居中，全身或半身 |
| **背景** | 简洁，无杂乱元素 |

### 2. 提高衔接流畅度

- 每段结尾设计"自然停顿点"
- 使用 `return_last_frame` 确保连续性
- 后期添加叠化转场（0.3-0.5秒）

### 3. 文案优化

- 根据目标市场选择语言
- 前3秒文案要有 Hook
- 标签混合热门+垂直

## 关联 Skills

| Skill | 关系 |
|-------|------|
| `commerce-storyboard` | **底层方法论**：体感设计三层翻译、价格带叙事逻辑、手部动作规则。生成提示词前应参考 |
| `short-video-analyzer` | 分析竞品视频获取灵感 |
| `doubao-ai-media-guide` | Seedance API 详细文档 |
| `tiktok-script-generator` | 生成口播脚本 |
| `b-roll-generator` | 生成 B-Roll 提示词 |

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.1 | 2025-01-28 | 添加交互式段落选择模式 |
| v1.0 | 2025-01-27 | 初始版本，支持全身穿搭、镜子自拍场景 |
