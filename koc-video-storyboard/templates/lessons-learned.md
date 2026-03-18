# 经验教训

实测总结。

## 问题 → 解法速查

### Gemini 图像生成（Web Gem + API 通用）——消耗品（测试产品：Life-Space Probiotic 益生菌）

| 问题 | 根因 | 解法 |
|------|------|------|
| 不是 5×5 格式 | 未强制指定 | 明确写 "5 columns × 5 rows = 25 panels"，列出每行编号 |
| 编号乱跳/重复 | Gemini 图内文字不稳定 | 列出 Row 1: 1,2,3,4,5 ... Row 5: 21-25 |
| 面板内有乱码文字 | 默认加描述文字 | "NO TEXT inside panels except the panel number" |
| 产品出镜太少（5/25） | 未量化要求 | "At least 12/25 panels" + 列出 8 种必须动作 |
| 出现裸露/不雅 | 未设安全规则 | 专门的 Content Safety Rules 章节 |
| 动作重复（同姿势×4） | 未限制重复 | "No single pose repeats more than TWICE" + 禁止列表 |
| 服装颜色漂移 | 特写时忘记一致性 | "SAME outfit in ALL 25 panels, even in close-ups" |
| 只输出文字不出图 | 长文字耗尽响应 | 只要求图片输出，文字 <20 词；或分两个 Gem |
| 3 列而非 5 列 | Gemini 随机行为 | 重新生成；或接受两种格式各有优势 |
| 产品标签文字变形 | AI 模型能力限制 | 无法修复，用真实产品特写混剪 |
| **价格/文字被渲染到图片中** | 提示词含 "Mid-Price"/"price tier" 等文字 | 提示词中**绝对不写任何价格数字、价格带名称**；"price surprise" 改为 "thumbs up with big smile" |
| **面板 8 出现产品名+价格文字** | Narrative Flow 章节写了 "Mid Price (needs a reason)" | 叙事逻辑描述中也不能出现具体价格/品牌关键词 |

### Gemini 图像生成——服装类（测试产品：Seamless Brown T-shirt，2026-02-14）

| 问题 | 根因 | 解法 |
|------|------|------|
| **叙事标签被渲染到面板中**（如 "Morning Good & Top"） | Narrative Flow 章节用了大写英文概念标签（MORNING, FABRIC DISCOVERY, ACTIVE MOVEMENT） | 叙事结构**只用动作描述**，不用概念标签。如 "character wakes up, reaches for clothing" 而非 "MORNING ROUTINE" |
| **面板出现无人产品图**（衣服独立展示） | 极端特写描述写了 "seamless seam, texture" 未指定穿在人身上 | 服装类**所有面板必须有模特穿着**，特写也要写 "close-up of fabric on character's shoulder" |
| **Feeling-First 表格中的英文被渲染** | 表格左列写了 "Butter-soft fabric"、"Four-way stretch" 等英文术语 | Feeling-First 表格**两列都只写视觉动作描述**，不写产品参数原文 |
| 产品交互规则不适用 | 消耗品模板要求 "hand-held product in 12/25 panels"，服装是穿在身上的 | 服装类用 **Clothing Interaction** 规则替代 Product Interaction：产品 = 模特穿着的衣服，交互 = 穿/脱/拉/展示动作 |

**服装类核心教训**：
1. 服装 ≠ 手持产品。产品就是模特身上的衣服，不存在"拿起产品"的动作
2. 提示词中**每一个英文单词都可能被渲染**——包括叙事逻辑章节、表格标题、章节名
3. 所有特写必须是"穿在身上的面料特写"，不是"衣服平铺特写"
4. 服装适用的交互动作：拉衣角展示弹性、转身展示版型、抬手展示无束缚感、摸面料展示质感
5. **user prompt 也必须清洗**：system instruction 修好了但 user prompt 写 "daily wear" "light exercise" → 照样被渲染成文字和图标（v2 教训）
6. **user prompt 不能写 "recommends it to the viewer"**：Gemini 会自动加对话气泡 "So comfy!" "Try it!"。改为纯动作 "points at camera, waves goodbye"（v3 教训）
7. **中价服装叙事关键**：必须有「痛点对比」— 先穿旧衣服不舒服，再换新衣服。视觉上用不同颜色的衣服区分前后（如白色旧 T → 棕色新 T），观众一眼看出变化（v4 验证）
8. **服装核心卖点是材质/面料/工艺**，不是消耗品的成分/功效。名人效应（如"和 Skims 同款面料"）走口播脚本，不进分镜图（会被渲染）

### Gemini API 专有问题

| 问题 | 根因 | 解法 |
|------|------|------|
| `gemini-2.0-flash-exp` 返回 404 | 模型已下线 | 用 `gemini-3-pro-image-preview`（2026-02-12 实测可用） |
| `gemini-2.0-flash-exp-image-generation` 不支持 system_instruction | 模型限制 | 换 `gemini-3-pro-image-preview`（支持 system_instruction） |

### TTS 配音

| 问题 | 根因 | 解法 |
|------|------|------|
| 印尼语 TTS 40 词生成 21s（目标 10s） | MiniMax Speech 印尼语语速比预期慢 ~2x | 10s 视频用 **~25 词**，不超过 30 词 |
| fal.ai REST 轮询 JSON 解析失败 | 状态端点返回格式不稳定 | 用 `fal_client` Python SDK 代替原生 REST |
| 加速 >1.5x 后语音不自然 | atempo 算法限制 | 控制原始音频在目标时长 ×1.2 以内，加速不超过 1.2x |

### 视频后处理

| 问题 | 根因 | 解法 |
|------|------|------|
| Seedance 2.0 Web 生成的视频带中文字幕 | 即梦 Web 端自动加字幕 | 用于印尼市场时需重新生成（不加字幕），或后期叠加覆盖 |

## 提示词优化的关键转折点

### V1 → V2：加入量化约束
- 从「描述性要求」升级为「可验证的数字规则」
- "show the product often" → "at least 12 of 25 panels must show the product"
- 效果：产品出镜从 5/25 → 16/25

### V2 → V3：去掉文字输出要求
- 去掉文字表格需求，只要求图片输出
- 效果：Gemini 100% 生成图片，不再卡在纯文字响应

### V3 → V4：内容质量 vs 格式精度的平衡
- V3（5×5）：格式完美，内容 8.5/10
- V4（3 列）：格式偏离，内容 9/10（更好的叙事、更清晰的标签）
- 结论：同一提示词可能产生不同布局，两种都可用

## Gemini 图像生成的通用规律

1. **量化 > 描述**：数字规则比形容词有效 10 倍
2. **禁止列表有效**：明确说「不要做 X」比「要做 Y」更能避免问题
3. **文字+图片互斥**：要长文字就别要图片，要图片就压缩文字
4. **一致性需反复强调**：服装、发型、体型一致性要在多处重复提及
5. **安全规则必须显式声明**：不写 = 不保证
6. **重新生成是合理策略**：格式不对就重新生成，不必改提示词
7. **提示词中的任何英文单词都可能被渲染**：Gemini 会把提示词中的关键词（价格、品牌名、价格带标签）当作需要渲染到图片中的文字。提示词中**不要出现任何你不想在图片中看到的文字**
8. **服装类产品 ≠ 手持产品**：产品 = 模特穿着的衣服，不能套用"拿起产品、展示标签"的消耗品模板。必须用服装专用模板 `gemini-image-prompt-apparel.md`

## Gemini API 使用要点（2026-02-12 实测）

### 可用模型（按优先级，2026-02-12 实测）

1. **`gemini-3-pro-image-preview`**（推荐）：Nano Banana Pro，支持 system_instruction + 多图输入 + 图片生成，4K 分辨率，最多 14 张参考图，Thinking 模式，文字渲染更好
2. `gemini-2.5-flash-image`：Nano Banana，稳定可用，作为 fallback
3. `gemini-2.0-flash-exp-image-generation`：图片生成可用但**不支持 system_instruction**，作为最后 fallback

### gemini-3-pro-image-preview vs gemini-2.5-flash-image

| 维度 | gemini-3-pro-image-preview | gemini-2.5-flash-image |
|------|---------------------------|----------------------|
| 代号 | Nano Banana Pro | Nano Banana |
| 最大分辨率 | **4K** | 2K |
| 参考图数量 | **最多 14 张** | 最多 5 张 |
| Thinking 模式 | **支持** | 不支持 |
| 文字渲染 | **更准确** | 一般 |
| system_instruction | 支持 | 支持 |
| 速度 | 较慢（Pro 级） | 较快（Flash 级） |
| 适合 | 高质量分镜、复杂场景 | 快速迭代、批量生成 |

### 分辨率限制（2026-02-13 实测）

| 方法 | 结果 |
|------|------|
| `generate_content` + `ImageConfig` | **固定 1024x1024**，`ImageConfig` 仅支持 `aspectRatio`，不支持 `image_size` |
| `generate_images` + `GenerateImagesConfig.imageSize="4K"` | 支持 4K，但是纯文生图 API，**不支持多图输入和 system_instruction** |
| `upscale_image` + `upscale_factor="x4"` | **仅 Vertex AI**，Google AI API key 不可用 |

**结论**：用 `generate_content`（多图输入 + system_instruction）生成分镜图时，输出固定 1024x1024。如需更高分辨率，需要后期用外部工具放大（如 Real-ESRGAN、fal.ai upscaler 等）。

**SDK 版本**：`google-genai==1.47.0`（2026-02-13 最新）

### API vs Web Gem 对比

| 维度 | Gemini API | Web Gem |
|------|-----------|---------|
| 自动化 | 可脚本化 | 手动操作 |
| system_instruction | 支持 | 支持 |
| 多图输入 | 支持 | 支持 |
| 稳定性 | 同等 | 同等 |
| 适合 | 批量生成、流水线集成 | 单次交互、快速实验 |

### API 调用代码片段

```python
from google import genai
from google.genai import types

client = genai.Client(api_key=API_KEY)

# 读取图片
def load_image(path):
    with open(path, 'rb') as f:
        data = f.read()
    mime = 'image/png' if str(path).endswith('.png') else 'image/jpeg'
    return types.Part.from_bytes(data=data, mime_type=mime)

response = client.models.generate_content(
    model='gemini-3-pro-image-preview',  # 首选；fallback: gemini-2.5-flash-image
    contents=[USER_PROMPT, model_img, product_img],
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_INSTRUCTION,
        response_modalities=['IMAGE', 'TEXT'],
        temperature=0.8,
    ),
)

# 提取图片
for part in response.candidates[0].content.parts:
    if part.inline_data and part.inline_data.mime_type.startswith('image/'):
        with open('output.png', 'wb') as f:
            f.write(part.inline_data.data)
```

## TTS 配音经验（fal.ai MiniMax Speech）

### 印尼语词数 vs 时长参考

| 视频时长 | 推荐词数 | TTS speed 参数 | 实际音频时长 |
|---------|---------|--------------|------------|
| 10s | ~25 词 | 1.3 | ~12s（加速 1.2x 后自然） |
| 20s | ~50 词 | 1.2 | ~24s |
| 30s | ~75 词 | 1.1 | ~34s |

### 关键参数

```python
result = fal_client.subscribe(
    'fal-ai/minimax/speech-02-hd',
    arguments={
        'text': SCRIPT,
        'voice_id': 'Wise_Woman',  # 印尼女性推荐
        'speed': 1.3,              # 1.0-1.5，越高越快
        'audio_format': 'mp3',
        'bitrate': 128000,
        'sample_rate': 44100,
    },
)
```

### 时长适配

音频超过视频时长时，用 ffmpeg atempo 加速（控制在 1.2x 以内）：
```bash
ffmpeg -y -i voiceover.mp3 -filter:a "atempo=1.19" -vn voiceover_fit.mp3
```

## 两步工作流（当需要文字+图片时）

Gemini 无法在一次响应中同时输出长文字和图片。解决方案：

**方案 A：两个 Gem**
- Gem 1（文字规划器）：输出分镜文字描述表格
- Gem 2（图片生成器）：用上面的提示词只生成图片

**方案 B：两步对话**
- 第一轮：发送产品信息 → 获得图片
- 第二轮：发送「根据上面的分镜图，输出每格的文字描述」→ 获得表格
