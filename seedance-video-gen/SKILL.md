# Seedance 1.5 Pro 视频生成 Skill

## 概述

通过火山引擎 Ark API 调用豆包 Seedance 1.5 Pro 模型生成视频。
异步模式：提交任务 → 轮询状态 → 下载视频。

## 脚本路径

`~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py`

## 调用方式

```bash
# 不需要 venv，使用系统 Python3 即可
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py [参数] "提示词"
```

## 参数速查

| 参数 | 说明 | 默认值 | 可选值 |
|------|------|--------|--------|
| `prompt` | 提示词（位置参数） | 必填 | 中文或英文 |
| `-n` | 输出文件名（不含.mp4） | 自动时间戳 | |
| `-o` | 输出目录 | ~/Desktop | |
| `-d` | 时长（秒） | 5 | 4-12 或 -1(自动) |
| `-a` | 宽高比 | 9:16 | 9:16/16:9/4:3/3:4/1:1/21:9/adaptive |
| `-r` | 分辨率 | 720p | 480p/720p/1080p |
| `--audio` | 开启音频 | 默认开启 | |
| `--no-audio` | 关闭音频（静音） | | |
| `--camera-fixed` | 固定镜头 | 关 | |
| `--watermark` | 加水印 | 关 | |
| `-i` | 首帧图片（路径或URL） | | 图生视频 |
| `--last-frame` | 尾帧图片 | | 首尾帧模式 |
| `--draft` | 草稿预览（480p低消耗） | 关 | |
| `--seed` | 随机种子 | -1(随机) | |
| `--return-last-frame` | 返回最后一帧PNG | 关 | 用于视频衔接 |

## 示例

### 文生视频（带音频）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 1080p -a '9:16' -d 8 -n test_video \
  '写实风格，一个印尼女生对着手机镜头说："你的面膜敢查BPOM吗？"，自然室内光，TikTok自拍角度'
```

### 静音视频（产品展示类）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 1080p -a '9:16' -d 5 --no-audio -n product_demo \
  '特写镜头，手持银色管状面膜产品，桌面自然光'
```

### 图生视频（首帧）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  -r 720p -a adaptive -d 5 \
  -i ~/Desktop/first_frame.jpg \
  -n img2vid_test \
  '女孩微笑着转头看向镜头'
```

### 草稿预览（低消耗试看）
```bash
python3 ~/.claude/skills/seedance-video-gen/scripts/seedance_video_gen.py \
  --draft -d 5 -n draft_preview \
  '测试提示词内容'
```

## 与 Veo 的对比

| 特性 | Seedance 1.5 Pro | Veo 3.1 |
|------|-----------------|---------|
| 时长 | 4-12秒（任意整数） | 4/6/8秒 |
| 音频 | 原生支持（语音+音效+BGM） | 有语音但不可精确控制 |
| 提示词语言 | 中文+英文 | 仅英文 |
| 分辨率 | 480p/720p/1080p | 720p/1080p/4K |
| 宽高比 | 7种+adaptive | 2种（9:16/16:9） |
| 图生视频 | 首帧/尾帧/首尾帧 | 仅首帧 |
| 草稿模式 | 有（480p低消耗） | 无 |
| 镜头固定 | camera_fixed 参数 | 仅靠 negative prompt |
| 台词控制 | 双引号对话，支持多语种 | 无法精确控制 |
| 视频衔接 | return_last_frame | 无 |
| 输出 | MP4 24fps | MP4 24fps |

## 适用场景建议

- **口播视频**（有台词）→ Seedance（原生音频+台词控制更强）
- **产品展示**（静物/手持）→ 即梦 或 Seedance（--no-audio）
- **人物场景**（无特定台词）→ Veo 或 Seedance
- **需要超高分辨率（4K）**→ Veo（Seedance 最高 1080p）

## API 限制

- 视频 URL **24小时内有效**，必须及时下载
- 任务记录保留 **7天**
- 图片输入：jpeg/png/webp/bmp/tiff/gif/heic，最大 30MB，宽高 300-6000px
- 真人面部图片可能触发隐私安全检测
- 提示词建议：中文 <500字，英文 <1000词
- 台词写法：用双引号包裹，如 `女孩说："你好"`
- 多人对话需明确标注每人特征（性别/年龄/服装）

## 提示词技巧（官方推荐）

公式：**主体 + 动作 + 环境 + 镜头运动 + 画风 + 声音**

```
写实风格，在温暖的室内自然光下，一个20岁印尼女生坐在镜头前，
快节奏地说："Habis maskeran muka gatal, jerawatan — itu maskernya yang bermasalah!"
表情从愤怒转为共情，手势自然，TikTok自拍角度，固定机位。
```
