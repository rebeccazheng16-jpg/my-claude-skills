---
name: tulandut-brand
description: Tulandut (图兰朵) 品牌视觉规范指南。应用于创建符合Tulandut品牌标准的设计物料，包括文档、演示文稿、网页、海报、包装等。当用户需要创建Tulandut品牌相关的视觉内容、需要使用Tulandut品牌色彩、字体、Logo时使用此skill。触发关键词：Tulandut、图兰朵、品牌规范、品牌设计。
---

# Tulandut 品牌视觉规范

## 品牌概述

**品牌名称**: Tulandut / 图兰朵
**品牌口号**: "微笑图兰朵，舒适生活家" / "Smiling Turandot, Comfort Living Expert"
**核心定位**: 体感舒适，内在舒心 (Physical Comfort, Inner Peace)

图兰朵Tulandut品牌源自1998年创立的服饰品牌公司，专注于基础穿搭服饰、内衣、内裤及配饰领域，融合人体工程学与设计美学，致力于打造高品质舒适服饰。

## 品牌色彩规范

### 主色调

| 颜色名称 | HEX | RGB | CMYK | 用途 |
|---------|-----|-----|------|------|
| **品牌红** | #9B212C | 155, 33, 44 | 40, 99, 90, 9 | 主品牌色，Logo、重点强调 |
| **纯白** | #FFFFFF | 255, 255, 255 | 0, 0, 0, 0 | 背景、留白 |

### 辅助色

| 颜色名称 | HEX | RGB | CMYK | 用途 |
|---------|-----|-----|------|------|
| **暖米色** | #FEF4E0 | 254, 244, 224 | 1, 6, 14, 0 | 温暖背景、柔和氛围 |
| **淡黄绿** | #EBE6B1 | 235, 230, 177 | 11, 7, 37, 0 | 自然清新感 |
| **樱花粉** | #ECB9CA | 236, 185, 202 | 6, 36, 8, 0 | 柔美女性化 |
| **深棕色** | #7F3F26 | 125, 62, 38 | 51, 81, 93, 23 | 稳重、高端感 |
| **天空蓝** | #B9E2F5 | 185, 226, 245 | 31, 0, 3, 0 | 清爽、透气感 |

### 色彩使用原则

1. **品牌红 #9B212C** 作为主识别色，用于Logo、标题、重要按钮和强调元素
2. **白色** 保持大面积留白，体现品牌简洁舒适的气质
3. **辅助色** 根据产品线和场景灵活搭配，营造不同氛围
4. 确保色彩对比度符合可读性标准

## 字体规范

### 品牌字体

**主字体**: 阿里巴巴普惠体2.0 (Alibaba PuHuiTi 2.0)

| 字重 | 用途 |
|-----|------|
| **Bold** | 主标题、Logo文字、重要信息 |
| **Regular** | 副标题、正文内容 |
| **Light** | 辅助文字、说明性内容 |

### 备选字体

- 中文: 思源黑体 (Noto Sans SC)
- 英文: Helvetica Neue, Arial

### 字体使用规则

1. 标题使用Bold字重，层级分明
2. 正文使用Regular，保证可读性
3. 中英文混排时保持视觉平衡
4. 行高建议1.5-1.8倍

## Logo使用规范

Logo资源位于 `assets/images/logo.png`

### Logo安全区域

- Logo周围需保留足够空白区域
- 最小安全距离为Logo高度的1/4

### Logo禁止行为

- 不得拉伸变形
- 不得更改颜色（除规定的单色应用）
- 不得添加阴影、描边等效果
- 不得置于复杂背景上影响识别

## 辅助图形

品牌辅助图形资源位于 `assets/images/` 目录：
- `auxiliary_graphics_1.png` - 设计端辅助图形
- `auxiliary_graphics_2.png` - 辅助图形变体
- `auxiliary_graphics_3.png` - 产品端辅助图形
- `auxiliary_graphics_4.png` - 辅助图形应用

辅助图形可用于：
- 背景装饰
- 分隔元素
- 版面点缀

## 品牌关键词

设计时可融入以下品牌核心概念：

- **COMFORT** - 舒适
- **FREE** - 自由
- **SELF** - 自我
- **HEALTH** - 健康
- **EASY LIFEIST** - 轻松生活家

## 应用示例

### 文档设计

```
标题: 品牌红 #9B212C, Bold
副标题: 深棕色 #7F3F26, Regular
正文: 黑色/深灰, Regular
背景: 白色或暖米色 #FEF4E0
```

### 网页/UI设计

```
主按钮: 品牌红 #9B212C 背景 + 白色文字
次要按钮: 白色背景 + 品牌红描边
悬停状态: 降低透明度或加深颜色
链接: 品牌红 #9B212C
```

### 演示文稿

```
封面: 品牌红背景 + 白色Logo和标题
内页: 白色背景 + 品牌红标题
强调: 使用辅助色点缀
页脚: 包含品牌口号 "微笑图兰朵，舒适生活家"
```

## 资源清单

```
assets/
└── images/
    ├── cover.png           # 品牌封面
    ├── logo.png            # Logo页面
    ├── brand_colors_primary.png  # 主色规范
    ├── color_palette.png   # 完整色板
    ├── typography.png      # 字体规范
    ├── auxiliary_graphics_1.png  # 辅助图形1
    ├── auxiliary_graphics_2.png  # 辅助图形2
    ├── auxiliary_graphics_3.png  # 辅助图形3
    └── auxiliary_graphics_4.png  # 辅助图形4
```

## CSS/代码快速参考

```css
:root {
  /* 主色 */
  --tulandut-red: #9B212C;
  --tulandut-white: #FFFFFF;

  /* 辅助色 */
  --tulandut-cream: #FEF4E0;
  --tulandut-lime: #EBE6B1;
  --tulandut-pink: #ECB9CA;
  --tulandut-brown: #7F3F26;
  --tulandut-sky: #B9E2F5;

  /* 字体 */
  --font-primary: 'Alibaba PuHuiTi 2.0', 'Noto Sans SC', sans-serif;
}
```

```python
# Python颜色常量
TULANDUT_COLORS = {
    'brand_red': '#9B212C',
    'white': '#FFFFFF',
    'cream': '#FEF4E0',
    'lime': '#EBE6B1',
    'pink': '#ECB9CA',
    'brown': '#7F3F26',
    'sky': '#B9E2F5'
}
```
