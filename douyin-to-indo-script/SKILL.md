---
name: douyin-to-indo-script
description: This skill should be used when the user wants to extract a voiceover script from a downloaded Douyin/TikTok product promotion video, supplement missing Hook or CTA using AI, and translate the complete script into colloquial Indonesian (bahasa gaul) suitable for TikTok. Supports local video file paths, video URLs, or directly pasted Chinese text scripts.
---

# 抖音带货视频 → 印尼语口播稿转化工具

## 工作流程

根据用户提供的输入类型，按以下流程处理：

```
[视频文件/URL] → 提取音频 → Whisper转文字 → 分析结构 → 补充Hook/CTA → 翻译印尼语
[直接粘贴文字稿]                            → 分析结构 → 补充Hook/CTA → 翻译印尼语
```

## 第一步：获取口播稿原文

### 情况A：用户提供本地视频文件路径

运行提取脚本：

```bash
python3 ~/.claude/skills/douyin-to-indo-script/scripts/extract_and_transcribe.py \
  "/path/to/video.mp4" \
  --output transcript.txt
```

前置条件检查：
- 需要 `ffmpeg`：`brew install ffmpeg`
- 需要 `openai` Python包：`pip install openai`
- 需要设置环境变量：`export OPENAI_API_KEY="your-key"`

若用户没有 OpenAI API Key，提供备选方案：
> "没有 Whisper API Key 也没关系！可以用以下免费工具先转文字：
> - **剪映**（PC版）：导入视频 → 字幕 → 自动识别 → 导出文字
> - **飞书妙记**：上传视频自动识别
> 把识别结果直接粘贴给我，我来处理后续步骤。"

### 情况B：用户提供视频URL

若是抖音/TikTok链接，不能直接处理语音，告知用户：
> "抖音视频链接需要先下载到本地才能处理语音识别。推荐工具：
> - SnapTik（网页）或抖音下载类APP
> - 下载后提供本地文件路径即可
> 如果你已有文字稿，也可以直接粘贴！"

### 情况C：用户直接提供文字稿

直接进入第二步，无需提取。

## 第二步：分析口播稿结构

拿到中文口播稿后进行分析（内部判断，不输出分析过程）：

**识别产品类型：** 参考 `references/indo_tiktok_language.md` 中"产品类型对应词汇"部分

**识别脚本结构，判断是否存在：**
1. **Hook（开场钩子句）** — 前1-2句是否立即抓住注意力、提出痛点或制造悬念？
2. **产品卖点** — 核心功能/效果描述
3. **CTA（行动号召）** — 末尾是否有明确的购买/互动引导？

## 第三步：AI补充缺失的Hook和CTA

**读取 `references/indo_tiktok_language.md`**，根据产品类型选择对应Hook模板：
- 美妆/护肤 → 痛点共鸣型
- 食品零食 → 悬念/口感描述型
- 日用品/家居 → 数字/效果型或反转型
- 限时促销 → 紧迫感型

AI补充的内容用 `【AI补充】` 标注，原有内容标注 `✅ 原稿已有`。

## 第四步：翻译为印尼语口语版

**翻译前必须读取 `references/indo_tiktok_language.md`** 作为参考。

翻译核心原则：
1. 本地化优先，不直译 — 像印尼TikTok达人在说话
2. 语气轻松活泼 — 加入口语助词：loh, dong, sih, deh, nih, yuk
3. 句子简短有力 — 节奏快，每句不超过15词
4. 保留TikTok平台用语 — klik keranjang kuning, stok terbatas, worth banget 等
5. 称观众为 "guys/kalian"，自称 "aku"

禁忌：
- 不用 "Anda"（太正式）→ 用 "kamu/kalian"
- 不直译 "点击购物车" → 用 "klik keranjang kuning di bawah"
- 不用书面语 "sangat baik" → 用 "works banget / bagus banget sih"

## 第五步：输出格式

严格按以下格式输出：

```
## 📝 中文口播稿（含AI补充）

**产品类型：** [识别的产品类型]

---

【AI补充】**Hook：**
[补充的开场钩子句]

**产品卖点：**
[原稿中的产品介绍和卖点内容]

【AI补充】**CTA：**
[补充的行动号召]

---

## 🇮🇩 印尼语口播稿（TikTok口语版）

[完整印尼语版本，直接可以使用]

---

💡 **使用提示：**
- 建议录制时语速适中，情绪饱满
- Hook部分要有停顿感，吸引观众继续看
- CTA时配合手势指向购物车区域效果更好
```

若原稿 Hook 和 CTA 都完整，则对应标注改为 `✅ 原稿已有` 并保留原文，不修改。
