# 口播稿生成指南

配合 25 宫格分镜使用，为每个视频段落生成目标市场语言的 KOC 风格口播稿。

各市场的详细口语风格指南见 `tiktok-koc-video-generator` skill 的 `templates/script-templates/`。

## 段落对应关系

### 25 宫格（5 段，中价品结构）

| 视频段落 | 分镜面板 | 时长 | 口播内容 |
|---------|---------|------|---------|
| Seg1 Hook | 1-5 | 6s | 痛点提问 + 自我代入 |
| Seg2 产品介绍 | 6-10 | 8s | 产品名 + 2-3 个核心数据（说人话） |
| Seg3 使用过程 | 11-15 | 8s | 步骤演示（超简单感） |
| Seg4 效果感受 | 16-20 | 8s | 个人体验 + 价格惊喜 |
| Seg5 CTA | 21-25 | 6s | 总结推荐 + 购买引导 |

### 9 宫格（3 段，中价品结构）

| 视频段落 | 分镜面板 | 时长 | 口播内容 |
|---------|---------|------|---------|
| Seg1 Hook + 产品 | 1-3 | 8s | 痛点提问 + 产品名 + 核心数据 |
| Seg2 使用 + 效果 | 4-6 | 8s | 步骤演示 + 个人体验 |
| Seg3 价格 + CTA | 7-9 | 6s | 价格惊喜 + 购买引导 |

## 通用口播稿原则

1. **念出来像聊天**，不像念广告
2. **每段有体感动词**，不是纯信息罗列
3. **痛点部分建立共情**：「我以前也这样」
4. **数据用说人话方式**：技术参数 → 惊叹反应（如「32 miliar CFU → Gila sih!」）
5. **CTA 有紧迫感或利益点**

## SRT 字幕格式

```srt
1
00:00:00,000 --> 00:00:03,000
第一句台词

2
00:00:03,000 --> 00:00:06,000
第二句台词
```

规则：
- 每条字幕 2-3 秒，不超过 2 行
- 按语义断句，不要在词中间断
- 时间戳与视频段落对齐

## 示例：印尼语（Life-Space 益生菌）

```
Seg1 (0-6s):
"Eh sis, siapa yang sering perut kembung abis makan?
Gue dulu juga gitu, makan dikit aja udah begah. Sampe gue nemu INI..."

Seg2 (6-14s):
"Life-Space Probiotic dari Australia!
15 jenis bakteri baik, 32 miliar CFU per kapsul. Gila sih!
Plus gluten free, dairy free — perutnya sensitif, aman banget."

Seg3 (14-22s):
"Cara minumnya gampang banget. Buka, keluarin satu kapsul,
telan pake air putih. Sehari cuma satu kali.
Pagi-pagi sebelum makan. Udah gitu doang!"

Seg4 (22-30s):
"Gue udah minum dua minggu. Perut berasa enteng,
gak kembung lagi abis makan. Bangun badan fresh!
Terus gue cek harganya... loh kok segini doang?!"

Seg5 (30-36s):
"30 kapsul cukup sebulan, worth it parah!
Cobain deh, perut lo bakal makasih. Link di keranjang kuning ya!"
```

## 质量检查

- [ ] 念出来像聊天，不像念广告
- [ ] 每段有体感动词（不是纯信息）
- [ ] 痛点部分有共情句式
- [ ] 数据用「说人话」方式呈现
- [ ] CTA 有紧迫感或利益点
- [ ] SRT 时间戳与视频段落对齐
