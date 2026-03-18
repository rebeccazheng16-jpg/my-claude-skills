# Nano Banana 提示词优化器

根据 Google 官方 Nano Banana / Nano Banana Pro 提示词规范，优化用户的图像生成提示词。

## 触发方式
当用户出现以下任一意图时，使用此 skill：
- 要求优化 Nano Banana 提示词
- 提供了需要改进的图像生成提示词
- 要求**反推图片提示词**（如"帮我反推这张图片的提示词"、"这张图是怎么生成的"、"帮我写出这张图的prompt"等）
- 要求根据图片写出可复现的提示词

## 官方提示词规范（来源：Google Blog、Google DeepMind、Google AI for Developers）

### 黄金法则

1. **用自然语言描述场景，不要堆砌关键词**
   - 错误示范：`dog, park, 4k, realistic, beautiful`
   - 正确示范：`A golden retriever playing fetch in a sun-drenched park, with warm afternoon light casting long shadows across the grass`
   - 要像给一位人类创意总监做简报一样写提示词

2. **编辑优化，而非重新生成**
   - Nano Banana 擅长理解对话式编辑指令
   - 在已有结果上微调比重新生成更高效
   - 示例：`That's great, but can you make the lighting warmer?`

3. **具体且描述性强**
   - 不要写 `woman`，而要写 `sophisticated elderly woman wearing vintage Chanel-style suit`
   - 明确描述材质、纹理、氛围

4. **提供上下文**
   - 说明图片用途或受众，帮助模型做出更好的构图和风格决策

### 五大核心提示词结构

#### 结构公式
```
[主体 + 形容词] 正在 [动作] 在 [场景/地点], [构图/镜头角度], [光线/氛围], [风格/媒介]
```

#### 1. 写实场景（Photorealistic）
要素：
- 具体的镜头类型和角度（wide-angle, close-up, low-angle）
- 镜头参数（85mm portrait lens, macro lens）
- 光线描述（golden hour lighting, soft diffused window light）
- 情绪和氛围（moody, cheerful, dramatic）
- 材质纹理细节
- 宽高比（16:9, 9:16, 1:1）

示例模板：
```
A photorealistic [镜头类型] of [主体], [动作], set in [环境].
Illuminated by [光线描述], creating [情绪] atmosphere.
Captured with [相机/镜头细节], emphasizing [纹理细节].
```

#### 2. 风格化插画 / 贴纸（Stylized）
要素：
- 艺术风格（kawaii, cel-shading, minimalist, watercolor）
- 线条和阴影风格
- 配色方案
- 背景要求（transparent, white, gradient）
- 设计特征（bold outlines, clean lines）

#### 3. 精准文字渲染（Text Rendering）
要素：
- 明确引用要渲染的文字内容（用引号框起来）
- 描述字体风格（sans-serif, serif, bold, handwritten）
- 整体设计美学
- 配色方案
- 文字位置和层级关系

#### 4. 产品模型 / 商业摄影（Product Mockup）
要素：
- 详细的产品描述
- 表面和背景规格
- 三点布光描述
- 相机角度和仰角
- 聚焦重点特征
- 超写实渲染要求

#### 5. 风格迁移（Style Transfer）
要素：
- 组合多种艺术风格
- 在单一构图中分层不同视觉媒介
- 明确指定不同风格元素之间的交互方式

### 高级功能

- **高分辨率输出**：明确指定 1K / 2K / 4K（必须大写）
- **多参考图组合**：最多 14 张参考图（6张物体高保真 + 5张人物一致性）
- **角色一致性**：使用 `Keep the person's facial features exactly the same as Image 1`
- **宽高比**：支持 1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9（**默认使用 9:16**，除非用户另有指定）
- **批量生成**：可一次请求生成多个变体
- **本地化翻译**：支持图内文字多语言翻译
- **Google Search 实时数据**：可生成基于实时信息的可视化
- **迭代编辑**：多轮对话持续优化，优于重新生成

### 常见问题与语义替代

- 不要用否定词（"no cars"），而要用正面描述（"An empty, desolate street with no signs of traffic"）
- 复杂场景分步描述：先背景，再前景，再细节
- 指定数量时要明确（"Make 8 minimalistic logos"）
- 角色锁定时加上："The character remains exactly locked in its current position"

---

## 工作流程

### 流程A：优化用户提供的提示词

1. **诊断问题**：检查原始提示词缺少哪些核心要素（主体/动作/场景/构图/光线/风格）
2. **去关键词化**：将关键词堆砌改为自然语言完整句子
3. **补充细节**：添加缺失的镜头、光线、材质、氛围描述
4. **结构化**：按官方推荐的公式重组提示词
5. **输出优化版**：同时给出中文说明和英文提示词（Nano Banana 对英文提示词效果更好）
6. **给出编辑建议**：提示用户后续可以如何迭代微调

#### 输出格式A
```
【原始提示词分析】
- 优点：...
- 不足：...

【优化后提示词（英文）】
...

【优化后提示词（中文参考）】
...

【后续微调建议】
- 建议1：...
- 建议2：...
```

### 流程B：根据图片反推提示词

当用户提供一张图片并要求反推/还原/写出提示词时：

1. **仔细观察图片**：分析图片中的所有视觉要素
2. **拆解要素**：按官方结构公式逐一提取
   - **主体**：谁/什么（外貌、服装、表情、姿势等细节）
   - **动作**：正在做什么
   - **场景/地点**：在哪里（环境、背景元素）
   - **构图/镜头**：镜头类型（特写/中景/全景）、角度（俯拍/平拍/仰拍）、景深
   - **光线/氛围**：光源方向、色温、明暗对比、整体情绪
   - **风格/媒介**：写实摄影/插画/3D渲染/水彩等、色彩风格
   - **文字元素**：图中是否有文字、字体风格
   - **特殊细节**：材质纹理、配色方案、画面比例等
3. **组装提示词**：用自然语言将所有要素组织成完整的描述性段落，严格遵循官方规范
4. **输出双语版本**：英文提示词 + 中文参考

#### 输出格式B
```
【图片要素分析】
- 主体：...
- 动作：...
- 场景：...
- 构图/镜头：...
- 光线/氛围：...
- 风格：...
- 特殊细节：...

【反推提示词（英文）】
...

【反推提示词（中文参考）】
...

【复现建议】
- 建议1：...
- 建议2：...
```

## 官方资料来源
- Google Blog: https://blog.google/products/gemini/prompting-tips-nano-banana-pro/
- Google Blog: https://blog.google/products/gemini/nano-banana-tips/
- Google DeepMind: https://deepmind.google/models/gemini-image/pro/
- Google AI for Developers: https://ai.google.dev/gemini-api/docs/image-generation
- Google Blog: https://blog.google/technology/ai/nano-banana-pro/
