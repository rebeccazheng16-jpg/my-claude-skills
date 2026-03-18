# Tulandut Green Label 内裤视频首尾帧生成规范

## 产品信息
- **品牌**：Tulandut Green Label
- **颜色**：鼠尾草绿 / 樱花粉 / 天空蓝（奶油腰边）
- **核心卖点**：海藻纤维、7A抗菌、无痕零感、冰感降温、轻薄垂感
- **Obsidian**：`10-Products/Tulandut Green Label 女款内裤.md`

## 素材路径
| 素材 | 路径 |
|------|------|
| 三色挂杆图 | `/Users/zhengrebecca/Desktop/ASSETS WOMEN/RESELLER CONTENT (1).png` |
| 绿色平铺正面 | `/Users/zhengrebecca/Desktop/ASSETS WOMEN/women tp b.png` |
| 面料细节 | `/Users/zhengrebecca/Desktop/ASSETS WOMEN/详情-拷贝1-拷贝_02.png` |
| 透光演示 | `/Users/zhengrebecca/Desktop/ASSETS WOMEN/_DSC1632.png` |
| 腰边背面 Logo | `/Users/zhengrebecca/Desktop/ASSETS WOMEN/8.70102.jpg` |
| 包装盒（多角度） | `~/Desktop/包装照片/1-10.jpg` |
| 手模参考 | `~/Desktop/model/手部模特/hands_v1.png` |
| 圆桌背景 | `~/Desktop/tulandut_table_bg_v1.png`（手持/平铺场景）|
| 床单背景 | `~/Desktop/tulandut_bg_v1.png`（Kirana 出镜场景）|

---

## ✅ 正确的展示手法

### 托举展示（展示垂感/轻薄）
> 手掌穿过腰口从下向上托举

```
"palm facing upward, hand inserted through the waist opening from below,
gently cradling and lifting the fabric with an open flat palm.
The unsupported portions of the ultra-lightweight fabric drape and fall
naturally downward due to gravity, creating soft organic folds.
The fabric looks airy, weightless, and has a beautiful natural drape."
```

### 三色平铺（展示颜色系列）
> 扇形重叠摆放，包装盒放一侧

```
"Three seamless briefs in EXACTLY these colors from the reference photo —
muted sage olive green, soft dusty blush rose, and pale periwinkle sky blue —
all with identical cream ivory waistbands. Arranged in overlapping fan spread."
```
⚠️ 必须传 `RESELLER CONTENT (1).png` 作为 `-r` 参考锁定颜色

### 腰边展示（展示无痕）
> 拇指沿腰边缓缓滑过

```
"thumb gently tracing along the seamless waistband,
no elastic marks, no pressure lines, smooth and flat against the skin."
```

### 面料捻拉（展示弹性/质感）
> 指尖捻住面料，微微拉伸后回弹

```
"fingertips gently pinching the fabric,
slightly stretching to reveal elasticity, then releasing —
fabric snaps back smoothly showing premium stretch recovery."
```

---

## 面料材质描述（区分光线条件）

> ⚠️ 必须根据镜头光线条件使用不同描述，参考图也要对应切换

### 正常光线镜头（S2 捻料 / S3 腰边 / S4 展开）
**参考图**：`women tp.png`（白底平铺，正常光线）

```
ultra-fine dense weave that appears smooth and silky in normal light —
surface texture nearly invisible to the naked eye, clean and refined.
Subtle silk-like sheen that catches light softly.
Completely weightless, drapes like flowing water with zero structure.
```
Negative 追加：`visible mesh, grid texture, coarse weave, visible perforations, net-like pattern, open weave`

### 透光特写（需要展示薄透卖点时）
**参考图**：`_DSC1632.png`（强背光透光演示）

```
ultra-sheer translucent fabric — so thin that a hand held behind it
casts a visible silhouette through the material. Micro-mesh structure
becomes visible when backlit.
```
> ⚠️ `_DSC1632.png` 仅限透光演示镜头，其他普通场景**不要**传入此图

---

## 🔄 图片迭代规则

> 当生成结果不满意，需要重做时：

| | 操作 |
|---|---|
| ❌ 错误 | 把上一版生成图作为 `-r` 传入继续迭代 |
| ✅ 正确 | 回到**原始参考图 + 原始提示词**，只修改导致问题的1处描述，或替换对应的1张原始参考图 |

**原因**：链式使用生成图会累积误差，且无法判断是哪个变量出了问题。每次迭代只改1个变量。

---

## ❌ 错误手法 / 避坑

| 错误 | 原因 | 替代方案 |
|------|------|---------|
| 手捏住腰边或两侧角竖直提起 | 面料变硬变板，失去垂感，像纸板 | 改用手掌托举穿过腰口 |
| 书本封面有文字 | 生成后文字变形穿帮 | 提示词写 "plain blank hardcover notebook, NO text NO title on cover" |
| 颜色未锁定 | AI 自由发挥颜色，偏蓝/偏紫/偏灰 | 必须传 RESELLER CONTENT 参考图 + 提示词写 "Do NOT change the colors from the reference image" |
| 打开盒子/从包装取出 | 盒子变形、文字扭曲、动作复杂 | 展示封好的盒子 + 产品已放在桌面 |

---

## 固定 Negative Prompt

```
stiff fabric, rigid underwear, cardboard-like texture, flat lighting,
text on books, distorted logo, wrong colors, extra limbs, deformed hands,
extra fingers, floating objects
```

---

## 颜色锁定提示词模板

```
"EXACTLY these colors from the reference photo —
muted sage olive green, soft dusty blush rose, and pale periwinkle sky blue,
all with identical cream ivory waistbands.
Do NOT change the colors of the underwear from the reference image."
```

---

## ⚠️ 提示词复杂度规则

- **参考图最多 3 张**：手模 + 产品 + 背景。超过 3 张会互相干扰，图像质量下降
- **手法描述要简单**："open upturned palm, fabric drapes naturally" 比 "insert hand through waist opening from below" 更有效
- **每次只改一个变量**：别同时改背景+手法+颜色，改乱了就回最简版本重来

## 生成参数

- **模型**：`gemini-3-pro-image-preview`
- **分辨率**：`4K`（-s 4K）
- **比例**：`9:16`（-a 9:16）
- **参考图**：最多传 3 张（手模 + 产品 + 背景）

## 首尾帧输出目录

- V2 手持版：`~/Desktop/Tulandut_v2_frames/`
- 命名：`S[编号]_first_v[版本].jpg` / `S[编号]_last_v[版本].jpg`
