---
name: koc-video-storyboard
description: Use when creating KOC product video storyboards (25-grid or 9-grid) from product and model images. Applies to consumables (supplements, skincare, beverages, cosmetics) or apparel (T-shirts, tops, activewear). NOT for electronics, furniture, or digital services.
---

# KOC 手持消耗品视频分镜全流程

从产品图 + 模特图生成分镜图（25 宫格或 9 宫格），裁切为视频段落，配合即梦/Seedance 生成视频，最后生成口播稿。

**适用品类**：
- **消耗品**：保健品、护肤品、饮品、彩妆等可手持的消耗品 → `templates/gemini-image-prompt.md`
- **服装**：T恤、上衣、运动服等穿着类产品 → `templates/gemini-image-prompt-apparel.md`

**不适用**：电子产品、家具、数字服务等（交互动作完全不同）。

**两种格式**：

| | 25 宫格（5×5） | 9 宫格（3×3） |
|---|---|---|
| 视频段数 | 5 段 | 3 段 |
| 总时长 | 30-40s | 15-24s |
| 面板方向 | 16:9 横屏 | 9:16 竖屏 |
| 适合 | 完整展示、长视频 | 快速验证、短视频 |
| Gemini 稳定性 | 偶尔格式偏差 | 更稳定 |

## 何时用这个 skill vs 其他

| 场景 | 用哪个 |
|------|--------|
| 需要体感设计方法论（说人话翻译、价格带叙事、可拍动作） | `commerce-storyboard`（底层方法论） |
| 用 Gemini 生成分镜图（25 宫格或 9 宫格）→ 视频 | **本 skill** |
| 已有分镜图，走完整视频生成流水线（图片→视频→字幕） | `tiktok-koc-video-generator` |
| 只需要写 Seedance 单段提示词 | `commerce-storyboard` Step 5A（提示词公式 + 手部规则） |
| 只需要写口播脚本 | `tiktok-koc-video-generator` 脚本模板 |

## 核心流程

### 当前流程（部分 API + 即梦 Web）

```
产品图 + 模特图 + 卖点
       ↓
[Step 1] 分镜图生成 ─── Gemini API ✅ 或 Web Gem ✅
       ↓
[Step 2] 裁切为段落 ─── Python PIL ✅
       ↓
[Step 3] Seedance 视频 ─── 即梦 Web UI ⚠️（手动）
       ↓
[Step 4] 口播稿 + SRT ─── Claude / 手动 ✅
       ↓
[Step 5] TTS 配音 ─── fal.ai MiniMax Speech ✅
       ↓
[Step 6] Lip-sync ─── fal.ai API ✅（可选）
       ↓
[Step 7] 合成 ─── ffmpeg ✅
```

### 未来流程（Seedance 2.0 API 上线后，全自动化）

```
产品图 + 模特图 + 卖点
       ↓
[Gemini API] 分镜图 (gemini-2.5-flash-image)
       ↓
[Python PIL] 裁切为段落
       ↓
[Claude API] 口播稿 + Seedance 提示词
       ↓
[TTS API] 配音 (fal.ai MiniMax Speech)
       ↓
[Seedance 2.0 API] 每段：段落图(首帧) + 模特图 + 产品图 + 配音(音频参考)
       │                → 带原生口型的视频（音素级唇形同步）
       ↓
[ffmpeg] 合并段落 + BGM + SRT 字幕
```

**关键变化**：Seedance 2.0 支持音频参考输入（Universal Reference），可以在视频生成时直接驱动口型，跳过独立的 lip-sync 步骤。

> **Seedance 2.0 API 状态**（2026-02-12）：仅即梦 Web 端可用，API 预计 2 月底开放。`doubao-ai-media-guide` skill 有完整技术规格。

## Step 1: Gemini 分镜图生成

根据需要选择格式：

| 格式 | 提示词模板 | 输出 | 适合 |
|------|-----------|------|------|
| **25 宫格** | `templates/gemini-image-prompt.md` | 5×5 = 25 格 | 完整展示（30-40s 视频） |
| **9 宫格** | `templates/gemini-9grid-prompt.md` | 3×3 = 9 格 | 快速验证（15-24s 视频） |

**输入**：1-2 张图片（模特图 + 产品图，顺序不限）+ 产品文字信息

### 方式 A：Gemini API（推荐，可脚本化）

模型：`gemini-3-pro-image-preview`（首选，4K/14 张参考图/Thinking 模式）；fallback：`gemini-2.5-flash-image`。提示词模板中的 system instruction 和 user prompt 直接传入 API。

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)
response = client.models.generate_content(
    model='gemini-2.5-flash-image',
    contents=[USER_PROMPT, model_img, product_img],
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_modalities=['IMAGE', 'TEXT'],
        temperature=0.8,
    ),
)
```

详细代码和模型选择见 `templates/lessons-learned.md` → Gemini API 使用要点。

### 方式 B：Gemini Web Gem

将提示词模板粘贴到 Gem 系统指令中，对话时上传图片 + 产品信息。

**已知问题与对策**见 `templates/lessons-learned.md`

## Step 2: 图片裁切

按叙事段落裁切。25 宫格裁切为 5 段，9 宫格裁切为 3 段。

```python
from PIL import Image
import os

img = Image.open('storyboard.jpg')
w, h = img.size

# === 根据格式选择配置 ===

# 25 宫格（5×5）→ 5 段
SEGMENTS_25 = {
    "rows": 5,
    "segments": [
        ("segment1_hook", 0, 1),        # 第 1 行（面板 1-5）
        ("segment2_product", 1, 2),     # 第 2 行（面板 6-10）
        ("segment3_usage", 2, 3),       # 第 3 行（面板 11-15）
        ("segment4_effect", 3, 4),      # 第 4 行（面板 16-20）
        ("segment5_cta", 4, 5),         # 第 5 行（面板 21-25）
    ]
}

# 9 宫格（3×3）→ 3 段
SEGMENTS_9 = {
    "rows": 3,
    "segments": [
        ("segment1_hook", 0, 1),        # 第 1 行（面板 1-3）
        ("segment2_usage", 1, 2),       # 第 2 行（面板 4-6）
        ("segment3_cta", 2, 3),         # 第 3 行（面板 7-9）
    ]
}

# 选择配置
config = SEGMENTS_9  # 或 SEGMENTS_25
rows = config["rows"]
row_h = h / rows

output_dir = 'segments'
os.makedirs(output_dir, exist_ok=True)

for name, row_start, row_end in config["segments"]:
    top = int(row_start * row_h)
    bottom = min(int(row_end * row_h), h)
    cropped = img.crop((0, top, w, bottom))
    cropped.save(f"{output_dir}/{name}.jpg", quality=95)
    print(f"{name}: {cropped.size}")
```

## Step 3: Seedance 视频生成

使用 `templates/seedance-segment-prompts.md` 中的模板为每段生成提示词。

**即梦操作**：图生视频 → 上传裁切段落图 + 模特参考图 + 产品参考图 → 填入提示词

写提示词前必须先参考 `commerce-storyboard`（底层方法论）：体感设计三层翻译、价格带叙事逻辑、手部动作冲突规则。

## Step 4: 口播稿

根据目标市场语言生成口播稿。模板见 `templates/script-guide.md`。

印尼市场的详细口语风格指南见 `tiktok-koc-video-generator` skill 的 `templates/script-templates/default.md`。

## Step 5: TTS 配音

用 TTS API 将口播稿转为目标语言配音。

**推荐**：fal.ai MiniMax Speech（支持印尼语、中文、英语等）

```python
import fal_client

result = fal_client.subscribe(
    'fal-ai/minimax/speech-02-hd',
    arguments={
        'text': SCRIPT,           # 印尼语口播稿
        'voice_id': 'Wise_Woman', # 印尼女性推荐
        'speed': 1.3,             # 1.0-1.5
        'audio_format': 'mp3',
        'bitrate': 128000,
        'sample_rate': 44100,
    },
)
audio_url = result['audio']['url']
```

**关键**：印尼语 TTS 语速比预期慢 ~2x，10s 视频只用 ~25 词。详见 `templates/lessons-learned.md`。

音频超长时用 ffmpeg 加速（控制在 1.2x 以内）：
```bash
ffmpeg -y -i voiceover.mp3 -filter:a "atempo=1.19" -vn voiceover_fit.mp3
```

## Step 6: Lip-sync（可选）

如果 Step 3 生成的视频没有口型同步，可用 lip-sync API 后处理。

**方案选择**：

| 方案 | 输入 | 价格 | 适合 |
|------|------|------|------|
| **Kling LipSync**（fal.ai） | 视频 + 音频 | ~$0.14/10s | 短视频、性价比首选 |
| **Sync Lipsync 2.0**（fal.ai） | 视频 + 音频 | ~$0.50/min | 最高质量 |
| **LatentSync**（fal.ai） | 视频 + 音频 | ~$0.04/min | 预算方案 |
| **即梦数字人基础模式** | 视频 + 音频 | Credits | 保留原画面、只改嘴部 |

> **Seedance 2.0 API 上线后**：可以在 Step 3 中直接传入音频参考，模型原生生成带口型的视频，大多数情况下不再需要独立 lip-sync 步骤。

详细方案对比见 `doubao-ai-media-guide` skill → Part 7。

## Step 7: 最终合成

用 ffmpeg 合并视频段落 + 配音 + BGM + 字幕。

```bash
# 合并视频 + 配音音频
ffmpeg -i video_noaudio.mp4 -i voiceover_fit.mp3 \
  -c:v copy -c:a aac -shortest output_with_voice.mp4

# 叠加 BGM（BGM 音量降低）
ffmpeg -i output_with_voice.mp4 -i bgm.mp3 \
  -filter_complex "[1:a]volume=0.2[bgm];[0:a][bgm]amix=inputs=2:duration=first[aout]" \
  -map 0:v -map "[aout]" -c:v copy -c:a aac final.mp4

# 烧入字幕（可选）
ffmpeg -i final.mp4 -vf "subtitles=subtitle.srt:force_style='FontSize=24'" \
  -c:a copy final_with_subs.mp4
```

## 各步骤 API 可用性总览

| 步骤 | API | 状态 | 备注 |
|------|-----|------|------|
| Step 1 分镜图 | Gemini `gemini-3-pro-image-preview` | **可用** | `google-genai` Python SDK；fallback: `gemini-2.5-flash-image` |
| Step 2 裁切 | Python PIL | **可用** | 本地执行 |
| Step 3 视频 | Seedance 2.0 API | **未上线** | 仅即梦 Web；fal.ai 有 Seedance 1.5 |
| Step 4 口播稿 | Claude API / 手动 | **可用** | |
| Step 5 TTS | fal.ai MiniMax Speech | **可用** | `fal_client` Python SDK |
| Step 6 Lip-sync | fal.ai (Kling/Sync/LatentSync) | **可用** | Seedance 2.0 API 上线后可省略 |
| Step 7 合成 | ffmpeg | **可用** | 本地执行 |

## 关联 Skills

| Skill | 协作方式 |
|-------|---------|
| `commerce-storyboard` | **底层方法论**：体感设计三层翻译、价格带叙事逻辑、Seedance 提示词公式、手部动作规则。所有分镜和提示词生成前必须参考 |
| `tiktok-koc-video-generator` | 下游：完整视频流水线、印尼语脚本模板、本地化设置 |
| `doubao-ai-media-guide` | 参考：Seedance 2.0 技术参数、lip-sync 方案对比（Part 7） |
| `fal-ai-integration` | API 调用：视频生成、TTS、lip-sync 的统一 API 平台 |
| `camera-movement-prompts` | 参考：运镜术语速查 |
| `omnihuman-expert` | 参考：需要数字人口播时的参数指导 |
