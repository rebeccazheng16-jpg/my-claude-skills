# Seedance / 即梦 视频分段提示词模板

本文件只包含 Seedance 特有的操作流程和分段模板。

**底层方法论**见 `commerce-storyboard`：体感设计三层翻译（参数→说人话→可拍动作）、价格带叙事逻辑、手部动作冲突规则（Step 5A）。写提示词前必须先参考。
Seedance 2.0 完整技术规格见 `doubao-ai-media-guide` skill。

## 操作流程

### 方式 A：即梦 Web UI（当前可用）

1. 进入即梦（jimeng.jianying.com）→ 图生视频
2. 上传裁切后的分镜段落图作为「首帧参考」
3. 额外上传模特原图 + 产品原图作为「参考图」
4. 填入英文提示词
5. 设置：时长 6-8s，分辨率 720p+，宽高比 9:16

### 方式 B：Seedance 2.0 API（预计 2026 年 2 月底开放）

API 上线后，每段视频可通过以下方式自动化生成：

```python
# 伪代码 — API 接口以官方发布为准
payload = {
    "model": "seedance-2.0-pro",  # Model ID 待确认
    "content": [
        {"type": "text", "text": SEGMENT_PROMPT},
        {"type": "image_url", "image_url": {"url": segment_img_url}, "role": "first_frame"},
        {"type": "image_url", "image_url": {"url": model_img_url}, "role": "reference_image"},
        {"type": "image_url", "image_url": {"url": product_img_url}, "role": "reference_image"},
        {"type": "audio_url", "audio_url": {"url": voiceover_url}, "role": "audio_reference"},
    ],
    "duration": 8,
    "resolution": "720p",
    "ratio": "9:16",
    "generate_audio": True,  # 原生音频同步
}
```

**关键优势**：
- **音频参考**（`audio_reference`）使模型原生生成带口型同步的视频，跳过独立 lip-sync 步骤
- **多图参考**：首帧 + 人物参考 + 产品参考，保持角色和产品一致性
- **批量化**：可脚本循环所有段落，一次性生成全部视频

> **注意**：Seedance 2.0 输出时长必须与输入音频时长匹配（见 `doubao-ai-media-guide` → 时长匹配规则）。如果配音 8s，视频也设为 8s。

## 提示词结构

每段遵循：Subject + Action + Camera + Style + @References

## 关键规则

1. **每段 ≤ 60 英文词**（不含 @references）
2. **只写物理动作**（❌ "radiating confidence" → ✅ "stands tall, smiles wide"）
3. **不用否定句**（模型会忽略否定）
4. **动作序列 2-3 步**，不超过 3 步
5. **产品标签特写建议用真实产品混剪**，AI 无法准确渲染文字

## 中价品模板（5 段 × 6-8s ≈ 36s）

### Segment 1: Hook（6s）

```
A young woman in [outfit] sits at a table, looking uncomfortable,
hand on stomach with a slight frown. She notices a [product] on the table,
reaches for it, picks it up, and her expression shifts to curiosity.
Medium shot, slight push-in, warm indoor lighting, natural color tone.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 2: Product Showcase（8s）

```
Shot 1: Medium close-up, she holds [product] up to camera, turns it slowly
to show the label, smiles proudly.
Shot Switch.
Shot 2: Close-up of her hands holding the [product], fingers pointing at
key text on label, gentle tilt.
Soft key light from left, clean background, product colors pop.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 3: Usage（8s）

```
Shot 1: Medium close-up, she opens the [product container], takes out
[one unit], places it [usage action].
Shot Switch.
Shot 2: Close-up of [usage detail], then she picks up a glass of water,
drinks, and sets the glass down with a satisfied nod.
Natural lighting, warm tone, smooth continuous motion.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 4: Effect + Price Surprise（8s）

```
Shot 1: Medium shot, she stretches comfortably, touches her [relevant body part],
smiles with relief, gives a thumbs up to camera.
Shot Switch.
Shot 2: Medium close-up, she looks at [price/phone screen], eyes widen in surprise,
shakes head in disbelief, breaks into a big smile.
Bright warm lighting, slight lens flare, energetic mood.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 5: CTA（6s）

```
Medium shot, she holds [product] next to her face, points directly at camera
with other hand, mouths words enthusiastically, then waves goodbye with
a bright smile. Product stays visible throughout.
Eye-level angle, warm golden light, friendly inviting mood.
@Image1 as character reference. @Image2 as product reference.
```

## 产品类型 → 使用动作替换

| 产品类型 | Segment 3 的 [usage action] 替换为 |
|---------|----------------------------------|
| 胶囊/药片 | opens cap → pours one capsule into palm → swallows with water |
| 身体乳 | squeezes onto palm → rubs on forearm → spreads evenly |
| 面膜 | unfolds mask → places on face → smooths edges |
| 饮品 | opens bottle → pours into glass → takes a sip |
| 服装 | holds up garment → puts it on → turns to show fit |
| 彩妆 | opens compact → applies with brush/finger → checks mirror |

## 9 宫格模板（3 段 × 6-8s ≈ 20s）

9 宫格裁切为 3 段，每段对应 1 行（3 格）。节奏更快，适合短视频。

### Segment 1: Hook + Discovery（8s）

```
Shot 1: Medium shot, a young woman in [outfit] sits looking uncomfortable,
hand on stomach with a slight frown.
Shot Switch.
Shot 2: Medium close-up, she notices a [product] on the table, picks it up,
examines it with growing curiosity, holds it up to see the label.
Warm indoor lighting, natural color tone, slight push-in.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 2: Usage + Effect（8s）

```
Shot 1: Medium close-up, she opens the [product container], takes out
[one unit], [usage action], drinks water, sets glass down.
Shot Switch.
Shot 2: Medium shot, she stretches comfortably, touches her [relevant body part],
smiles with relief, nods approvingly at the product.
Natural lighting, warm tone, smooth continuous motion.
@Image1 as character reference. @Image2 as product reference.
```

### Segment 3: Price Surprise + CTA（6s）

```
Shot 1: Medium close-up, she looks at [price/phone screen], eyes widen
in surprise, shakes head in disbelief, breaks into a big smile.
Shot Switch.
Shot 2: She holds [product] next to her face, points directly at camera,
mouths words enthusiastically, waves goodbye with a bright smile.
Eye-level angle, warm golden light, friendly inviting mood.
@Image1 as character reference. @Image2 as product reference.
```

## 低价品和高价品模板

低价品（冲动型）和高价品（信任型）的叙事结构和面板分配见 `commerce-storyboard`（底层方法论）的 `templates/commerce-templates.md`。

**25 宫格（5 段）**：
- **低价品**：Seg1 视觉冲击 → Seg2-3 逐品体感循环 → Seg4 多角度享受 → Seg5 价格+CTA
- **高价品**：Seg1 效果先行 → Seg2 个人故事 → Seg3 产品仪式感 → Seg4 社交证明 → Seg5 值得+CTA

**9 宫格（3 段）**：
- **低价品**：Seg1 视觉冲击+产品 → Seg2 使用体感循环 → Seg3 价格+CTA
- **高价品**：Seg1 效果先行+故事 → Seg2 产品仪式感 → Seg3 值得+CTA
