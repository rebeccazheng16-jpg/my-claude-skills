# Nano Banana 产品植入提示词生成器

根据 Google 官方 Nano Banana 多参考图合成规范，帮助用户生成"人物手持产品合拍"的迭代编辑提示词。

## 触发方式
当用户出现以下任一意图时，使用此 skill：
- 要求在已有人物图片中**加入/植入产品**
- 要求生成**手持产品**的合照提示词
- 说"帮我加上产品"、"让她拿着产品"、"与产品合拍"等类似表达
- 提供了人物图片和产品图片，要求合成

## 官方技术基础（来源：Google DeepMind、Google AI for Developers）

### 多参考图合成能力
- Nano Banana 支持最多 **14张参考图**（6张物体高保真 + 5张人物一致性）
- 使用方式：同时上传人物图（Image 1）和产品图（Image 2），用提示词指定合成方式
- 关键语法：`Combine these two images into one photo`
- 锁定人物不变：`Keep the person's facial features, expression, outfit, skin texture, and background exactly the same as Image 1`

### 产品植入核心原则

1. **自然握持**
   - 描述手指与产品的接触方式（"gently wrapped around", "held between thumb and fingers"）
   - 指定哪只手（left hand / right hand）
   - 描述握持位置（管身中部/底部/顶部）
   - 手指不能完全遮挡logo区域

2. **产品朝向与Logo可见性**
   - 必须明确指定 logo 面朝镜头
   - 写出具体的 logo 文字和产品名称
   - 要求"clearly visible and legible"

3. **产品位置与姿势**
   - 指定产品相对于面部的位置（near cheek, at chin level, beside face）
   - 描述倾斜角度（tilted slightly toward camera）
   - 保持自拍合照的随意感，避免广告感

4. **光线一致性**
   - 产品表面的反光必须与人物图的光源方向一致
   - 金属/光面产品需描述反光效果
   - 如原图有阳光直射，产品也需体现

5. **尺寸比例（严格保真）**
   - 描述产品实际尺寸（如"approximately 15cm in length"）
   - 要求"proportionally correct to hand size"
   - **必须强调产品的宽高比与官图完全一致**：`The product must maintain the exact same width-to-height ratio and proportions as shown in Image 2. Do not stretch, compress, or distort the product in any direction.`
   - 明确描述管径/瓶宽等具体数值（如"the tube diameter is approximately 3cm"）

6. **模特表情与互动**
   - 模特应微微笑，自然不夸张（"a gentle, subtle smile — warm and effortless"）
   - 表现与产品的亲密感（"as if she genuinely loves the product"）
   - 避免僵硬的商业微笑，追求"闺蜜分享好物"的感觉

7. **氛围统一**
   - 强调"natural, authentic social media selfie"
   - 避免"staged advertisement / commercial shoot"

## 工作流程

1. **分析人物图**：识别现有的光源方向、手的位置、构图空间
2. **分析产品图**：识别产品外观（材质、颜色、形状、logo文字、尺寸）
3. **确定植入方案**：
   - 哪只手持产品（默认选择更自然/有空间的一侧）
   - 产品举在什么位置（脸旁/下巴旁/胸前）
   - logo朝向（面朝镜头）
4. **生成提示词**：按以下模板组装
5. **给出微调建议**

## 提示词模板

```
Combine these two images into one photo. Place the [产品描述（颜色+材质+形状）] product ([品牌名 + 产品全称]) from Image 2 naturally into the woman's [左/右] hand in Image 1.

She is casually holding the [材质] [形状] near her [位置：face/cheek/chin/chest], [角度：tilted slightly toward the camera], as if taking a [场景：cute selfie showing off her favorite skincare product / casual photo with her daily essential].

Her [左/右] hand grip is relaxed and natural — [握持细节：gently wrapped around the middle of the tube with fingers visible / held lightly between thumb and fingers]. The logo "[LOGO文字]" and product text "[产品文字]" are clearly legible and facing the camera.

The [产品外观细节：tube has a metallic silver finish with a silver cap at the bottom / bottle is transparent glass with a gold cap], approximately [尺寸]cm in length and [管径/瓶宽]cm in diameter, proportionally correct to her hand size. The product must maintain the exact same width-to-height ratio and proportions as shown in Image 2 — do not stretch, compress, or distort the product in any direction.

She has a gentle, subtle smile — warm and effortless, as if she genuinely loves this product and is casually sharing it with her followers. The smile should feel natural, like a candid moment between friends, not a posed commercial expression.

[光线匹配：The existing lighting should cast consistent reflections on the product surface / The direct sunlight should create warm highlights on the metallic surface].

Keep the person's facial features, expression, hair, makeup, outfit, skin texture, lighting, and background exactly the same as Image 1.

The overall feel should be a natural, authentic social media selfie — a real girl casually posing with her skincare product, not a staged commercial shoot.

Aspect ratio 9:16.
```

## 输出格式

```
【产品分析】
- 品牌：...
- 产品名：...
- 外观：...（颜色、材质、形状、尺寸）
- Logo/文字：...

【植入方案】
- 手：左手/右手
- 位置：...
- 姿势：...
- 光线匹配：...

【合成提示词（英文）】
...

【合成提示词（中文参考）】
...

【后续微调建议】
- ...
```

## 常见产品类型适配

### 管状产品（面膜/洁面/护手霜）
- 握持：手指环绕管身中部
- 朝向：管口朝上或朝斜上方，logo正面朝镜头
- 注意：手指不遮挡品牌名区域

### 瓶装产品（精华/乳液/化妆水）
- 握持：一手握住瓶身下半部，或拇指食指捏住瓶颈
- 朝向：瓶身正面logo朝镜头
- 注意：透明瓶需描述液体颜色和质感

### 盒装/罐装产品（面霜/粉底）
- 握持：掌心托住底部，或指尖捏住两侧
- 朝向：盖面或正面logo朝镜头
- 注意：小尺寸产品可放在掌心展示

### 片状面膜
- 握持：一手拎起面膜包装袋上端
- 朝向：包装正面朝镜头
- 注意：可描述另一手指向产品

## 官方资料来源
- Google DeepMind: https://deepmind.google/models/gemini-image/pro/
- Google AI for Developers: https://ai.google.dev/gemini-api/docs/image-generation
- Google Blog: https://blog.google/products/gemini/prompting-tips-nano-banana-pro/
