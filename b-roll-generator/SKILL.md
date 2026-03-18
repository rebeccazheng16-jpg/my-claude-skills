---
name: b-roll-generator
description: 根据口播稿自动生成 B-Roll 提示词。分析口播脚本的语义和上下文，智能识别需要 B-Roll 的位置，生成中英双语 AI 视频提示词并标注建议时长。适用于 Runway、Pika、可灵等 AI 视频生成工具。支持两种输出模式：带时间戳脚本自动使用内嵌模式（直接在脚本中插入 B-Roll 标注），无时间戳脚本使用表格模式。当用户提供口播稿/脚本并需要生成 B-Roll、分镜、视频提示词时触发此 skill。
---

# B-Roll 提示词生成器

## 概述

根据口播稿自动分析上下文语义，在需要视觉增强的位置生成 B-Roll 提示词，用于 AI 视频生成工具（Runway/Pika/可灵等）。

## 工作流程

```
口播稿输入 → 语义分析 → 确定统一风格 → 识别插入点 → 生成提示词 → 输出表格
```

### 第一步：语义分析

分析口播稿的整体内容，识别：

1. **内容主题** - 商业、科技、教育、生活方式等
2. **情感基调** - 激励、严肃、轻松、紧迫等
3. **叙事结构** - 问题-解决、故事线、列举、对比等

### 第二步：确定统一风格（风格锚定）

**这是确保视觉连贯性的关键步骤。** 在生成任何 B-Roll 提示词之前，必须先确定整个视频的统一风格锚点。

根据语义分析结果，确定以下风格要素：

| 风格要素 | 说明 | 示例 |
|---------|------|-----|
| **主色调** | 整体画面的色彩倾向 | warm tones / cool tones / neutral |
| **光线风格** | 统一的光线处理 | soft natural lighting / dramatic lighting / golden hour |
| **质感** | 画面的视觉质感 | cinematic film grain / clean digital / vintage 8mm |
| **镜头风格** | 主要的镜头运动方式 | smooth dolly / handheld / static |
| **整体氛围** | 贯穿始终的情绪基调 | hopeful / tense / professional / intimate |

**风格锚点模板：**
```
色调: [主色调]
光线: [光线风格]
质感: [质感]
镜头: [镜头风格]
氛围: [整体氛围]
```

**内容类型与风格对应参考：**
- 商业/创业 → warm tones, soft professional lighting, clean cinematic, smooth dolly, confident
- 科技/产品 → cool blue tones, sleek lighting, digital clean, smooth tracking, futuristic
- 教育/知识 → neutral bright tones, natural soft lighting, clean minimal, steady shots, clear
- 情感/故事 → warm golden tones, cinematic lighting, film grain, handheld subtle, intimate
- 数据/分析 → cool tones, dramatic accent lighting, clean digital, smooth motion, authoritative

### 第三步：识别 B-Roll 插入点

扫描每个段落，识别以下触发场景：

| 触发类型 | 识别特征 | B-Roll 方向 |
|---------|---------|------------|
| **数据/数字** | 百分比、增长率、金额、数量 | 数据可视化、图表动画、数字跳动 |
| **抽象概念** | 战略、创新、效率、价值 | 视觉隐喻、象征性画面 |
| **场景描述** | 地点、环境、情境描写 | 对应实景或风格化场景 |
| **动作/过程** | 做、建立、实现、转变 | 过程展示、动态画面 |
| **情感表达** | 痛点、焦虑、兴奋、期待 | 情绪化画面、人物表情 |
| **举例/故事** | 比如、例如、有一次 | 叙事性画面、情景再现 |
| **对比/转折** | 但是、然而、相反 | 对比蒙太奇、转场画面 |
| **时间线** | 过去、现在、未来、阶段 | 时间流逝、时代变迁 |

### 第四步：生成提示词

为每个识别的插入点生成提示词，**每个提示词必须包含统一的风格后缀**。

**提示词结构：**
```
[主体] + [动作/状态] + [环境/背景] + [统一风格后缀]
```

**统一风格后缀** = 第二步确定的风格锚点关键词组合，确保所有 B-Roll 视觉一致。

**示例：** 如果风格锚点是 `warm tones, soft professional lighting, cinematic, smooth dolly`，则每个提示词结尾都应包含这些关键词。

**镜头语言参考（详见 references/camera-movements.md）：**
- 静态：wide shot, close-up, medium shot
- 运动：dolly in, tracking shot, crane shot
- 特效：time-lapse, slow motion, hyperlapse

**风格关键词库：**
- 电影感：cinematic, film grain, anamorphic lens flare
- 商务：corporate, professional, clean
- 科技：futuristic, digital, holographic
- 温暖：warm tones, golden hour, soft lighting
- 冷峻：cool tones, blue hour, dramatic lighting

### 第五步：输出格式

根据输入脚本的格式，自动选择输出模式：

| 脚本特征 | 输出模式 |
|---------|---------|
| 带时间戳（如 `[0:00-0:08]`、`[HOOK - 0:00]`） | **内嵌模式** - 直接在脚本中插入 B-Roll 标注 |
| 无时间戳的纯文本/分段脚本 | **表格模式** - 输出独立的 B-Roll 表格 |

---

#### 模式一：内嵌模式（带时间戳脚本）

当脚本已包含时间戳时，直接在原脚本中插入 B-Roll 标注。

**时间戳自动计算规则：**
1. 解析脚本中的时间段（如 `[HOOK - 0:00-0:08]`）
2. 根据该段内的句子位置，按比例分配 B-Roll 的起止时间
3. B-Roll 时长根据内容复杂度自动调整（2-5秒）

**内嵌标注格式：**
```
📹 B-Roll [起始时间-结束时间] (时长)
中文：[中文提示词]
EN: [English prompt with style suffix]
```

**输出结构：**
```
## 🎬 视频风格设定
[风格声明，同表格模式]

---

## 📝 带 B-Roll 标注的完整脚本

[原脚本段落标题]
原脚本文字...

📹 B-Roll [0:02-0:05] (3s)
中文：[中文提示词]
EN: [English prompt + style suffix]

原脚本文字继续...

📹 B-Roll [0:06-0:08] (2s)
中文：[中文提示词]
EN: [English prompt + style suffix]

[下一段落...]
```

**内嵌位置选择原则：**
- 在触发内容（数据、场景、情感等）**之后**立即插入
- 一个时间段内可以有多个 B-Roll，但避免过于密集
- B-Roll 时间段不应超出所属段落的时间范围

---

#### 模式二：表格模式（无时间戳脚本）

当脚本没有时间戳时，输出独立的 B-Roll 表格。

**风格声明（输出在表格之前）：**
```
## 🎬 视频风格设定

**内容类型：** [识别的内容类型]
**情感基调：** [识别的情感基调]

**统一风格锚点：**
- 色调: [主色调]
- 光线: [光线风格]
- 质感: [质感]
- 镜头: [镜头风格]
- 氛围: [整体氛围]

**风格后缀（每个提示词结尾统一添加）：**
`[英文风格关键词组合]`
```

**B-Roll 表格：**

| 段落 | 口播内容摘要 | B-Roll 提示词 (中文) | B-Roll Prompt (English) | 建议时长 |
|-----|-------------|---------------------|------------------------|---------|
| 1 | [20字内摘要] | [中文提示词] | [英文提示词 + 统一风格后缀] | [X秒] |

---

**时长建议规则（两种模式通用）：**
- 简单概念/数据展示：2-3秒
- 场景/动作展示：3-5秒
- 复杂过程/情感表达：5-8秒
- 故事/叙事片段：8-10秒

## 示例

### 示例一：表格模式（无时间戳脚本）

**输入口播稿：**
```
【段落1】
去年我们公司的收入增长了300%，但我却越来越焦虑。

【段落2】
因为我发现，增长的背后是团队的疲惫和流程的混乱。

【段落3】
直到我开始用系统化的方法重新梳理业务，一切才开始改变。
```

**输出：**

## 🎬 视频风格设定

**内容类型：** 商业/创业分享
**情感基调：** 反思 → 转折 → 希望

**统一风格锚点：**
- 色调: warm to neutral tones（温暖到中性，随叙事变化但保持统一质感）
- 光线: soft cinematic lighting（柔和电影光）
- 质感: cinematic with subtle film grain（电影感，轻微胶片颗粒）
- 镜头: smooth dolly movements（平滑推拉镜头）
- 氛围: reflective, professional（反思、专业）

**风格后缀（每个提示词结尾统一添加）：**
`cinematic, soft lighting, subtle film grain, smooth camera movement, professional atmosphere`

---

| 段落 | 口播内容摘要 | B-Roll 提示词 (中文) | B-Roll Prompt (English) | 建议时长 |
|-----|-------------|---------------------|------------------------|---------|
| 1 | 收入增长300%但焦虑 | 数字快速跳动的数据面板，绿色增长曲线急剧上升，商务人士在办公室窗前若有所思 | Data dashboard with rapidly changing numbers, green growth curve rising sharply, businessman standing pensively by office window, **cinematic, soft lighting, subtle film grain, smooth camera movement, professional atmosphere** | 4秒 |
| 2 | 增长背后是疲惫混乱 | 深夜办公室灯火通明，疲惫的团队成员揉眼睛，桌面堆满文件，镜头缓慢后拉揭示全景 | Late night office with warm lamp light, tired team member rubbing eyes, desk cluttered with papers, slow dolly out revealing the scene, **cinematic, soft lighting, subtle film grain, smooth camera movement, professional atmosphere** | 5秒 |
| 3 | 系统化方法带来改变 | 清晨阳光照进整洁的办公室，有序的白板流程图，团队轻松交流，镜头缓慢推进，暖色调 | Morning sunlight streaming into organized office, neat flowchart on whiteboard, team collaborating with ease, slow dolly in, warm tones, **cinematic, soft lighting, subtle film grain, smooth camera movement, professional atmosphere** | 5秒 |

---

### 示例二：内嵌模式（带时间戳脚本）

**输入口播稿：**
```
[HOOK - 0:00-0:08] 🎯
Kamu pernah nggak, lagi meeting penting... tiba-tiba dapat telepon dari rumah sakit soal orang tua?
Atau lagi urus anak yang sakit, tapi orderan numpuk harus diproses?

[PROBLEM - 0:08-0:20] 💭
Jadi gini... Ini namanya "Generasi Sandwich."
Kita yang di tengah. Urus orang tua yang makin tua, urus anak yang masih kecil, sambil bangun bisnis supaya keluarga bisa hidup layak.
Capek? Pasti. Kadang pengen nangis? Wajar banget.

[CTA - 0:50-0:60] 🔥
Kalau kamu juga generasi sandwich, comment "SAMA" — aku mau tahu cerita kamu. 💪
```

**输出：**

## 🎬 视频风格设定

**内容类型：** 女性创业/生活分享
**情感基调：** 共情 → 理解 → 鼓励

**统一风格锚点：**
- 色调: warm earthy tones（温暖大地色调）
- 光线: soft natural lighting（柔和自然光）
- 质感: cinematic, authentic feel（电影感，真实质感）
- 镜头: gentle handheld, intimate（轻柔手持，亲密感）
- 氛围: empathetic, supportive（共情、支持）

**风格后缀：**
`cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere`

---

## 📝 带 B-Roll 标注的完整脚本

**[HOOK - 0:00-0:08] 🎯**

Kamu pernah nggak, lagi meeting penting... tiba-tiba dapat telepon dari rumah sakit soal orang tua?

📹 B-Roll [0:01-0:04] (3s)
中文：职业女性在会议室中突然看到手机来电，表情从专注变为担忧，镜头特写手机屏幕显示"医院"
EN: Professional woman in meeting room suddenly looking at phone, expression shifting from focused to worried, close-up of phone screen showing hospital caller ID, **cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere**

Atau lagi urus anak yang sakit, tapi orderan numpuk harus diproses?

📹 B-Roll [0:05-0:08] (3s)
中文：母亲一手抱着生病的孩子，一手在笔记本电脑上处理订单，桌上堆满包裹，疲惫但坚持
EN: Mother holding sick child with one arm while typing on laptop with the other, packages piled on desk, tired but persevering, **cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere**

---

**[PROBLEM - 0:08-0:20] 💭**

Jadi gini... Ini namanya "Generasi Sandwich."

Kita yang di tengah. Urus orang tua yang makin tua, urus anak yang masih kecil, sambil bangun bisnis supaya keluarga bisa hidup layak.

📹 B-Roll [0:10-0:14] (4s)
中文：三代同堂画面：年迈的父母坐在沙发上，孩子在地上玩耍，女性在中间忙碌照顾两边，镜头缓慢后拉展示全景
EN: Three-generation scene: elderly parents sitting on sofa, child playing on floor, woman in the middle busy caring for both sides, slow dolly out revealing the full picture, **cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere**

Capek? Pasti. Kadang pengen nangis? Wajar banget.

📹 B-Roll [0:16-0:19] (3s)
中文：深夜，女性独自坐在窗边，疲惫地揉太阳穴，窗外城市灯光闪烁，情绪化的特写镜头
EN: Late night, woman sitting alone by window, tiredly rubbing temples, city lights twinkling outside, emotional close-up shot, **cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere**

---

**[CTA - 0:50-0:60] 🔥**

Kalau kamu juga generasi sandwich, comment "SAMA" — aku mau tahu cerita kamu. 💪

📹 B-Roll [0:52-0:56] (4s)
中文：女性对着镜头温暖微笑，伸出手做出邀请姿态，背景虚化温馨的家庭环境，传递支持与连接
EN: Woman smiling warmly at camera, reaching out with inviting gesture, soft bokeh background of cozy home environment, conveying support and connection, **cinematic, warm earthy tones, soft natural lighting, gentle handheld, empathetic atmosphere**

---

**注意：** 内嵌模式下，所有 B-Roll 标注都包含精确的时间戳，且风格后缀保持统一，确保剪辑时视觉连贯。

## 注意事项

1. **风格统一优先** - 每个提示词必须包含统一的风格后缀，这是视觉连贯性的保障
2. **避免过度插入** - 不是每句话都需要 B-Roll，只在能增强表达的地方插入
3. **服务于内容** - B-Roll 是为了增强口播表达，不能喧宾夺主
4. **考虑可生成性** - 提示词要符合当前 AI 视频工具的能力范围
5. **情绪可以变化，风格保持统一** - 不同段落的情绪可以不同（紧张→希望），但光线、质感、镜头风格应保持一致

## 资源

### references/
- `camera-movements.md` - 镜头语言参考库，包含各类镜头运动的英文术语和使用场景
