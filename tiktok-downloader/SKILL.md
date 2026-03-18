---
name: tiktok-downloader
description: TikTok 视频下载工具。输入视频链接自动下载无水印视频和元数据。使用 Playwright 浏览器自动化绕过防护机制。触发词：下载TikTok、TikTok下载、抖音国际版下载。
---

# TikTok 视频下载工具

**一键下载 TikTok 视频**：无水印视频 + 元数据，保存到本地。

## 功能特性

| 功能 | 说明 |
|------|------|
| 📹 视频下载 | 自动选择最高画质，无水印 |
| 📝 元数据保存 | 作者、描述、点赞数等存入 JSON |
| 🎭 浏览器自动化 | 使用 Playwright 绕过防护 |
| 📁 分类存储 | 按作者自动分类 |
| 🤖 AI 视频分析 | Gemini 2.5 Flash 分析视频内容 |
| 📊 分镜脚本 | 6段式结构拆解（Hook/痛点/产品/演示/效果/CTA） |
| 💡 爆款分析 | 成功要素、复刻建议、AI 视频提示词 |

## 快速开始

### 首次使用

```bash
# 1. 运行环境设置
bash ~/.claude/skills/tiktok-downloader/scripts/setup.sh

# 2. 下载视频
tiktok-download "视频链接"

# 3. 下载并分析（需要 Gemini API Key）
tiktok-download --analyze "视频链接"
```

### 日常使用

```bash
# 仅下载
tiktok-download "https://www.tiktok.com/@user/video/123456"

# 下载 + Gemini 分析（推荐）
tiktok-download --analyze "https://www.tiktok.com/@user/video/123456"

# 短链接也支持
tiktok-download "https://vm.tiktok.com/xxx"

# 单独分析已下载的视频
node ~/.claude/skills/tiktok-downloader/scripts/analyze.js ~/TikTok-Downloads/user/123.mp4
```

## 工作流程

```
输入视频链接
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Playwright 打开浏览器            │
│    ├─ 访问视频页面                  │
│    └─ 等待视频加载                  │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 2. 捕获网络请求                     │
│    ├─ 监听 /video/tos/ 请求         │
│    └─ 选择最大文件（最高画质）      │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 3. 下载并保存                       │
│    ├─ 使用浏览器上下文下载          │
│    ├─ 提取视频元数据                │
│    └─ 保存到输出目录                │
└─────────────────────────────────────┘
     │
     ▼
输出保存到 ~/TikTok-Downloads/
```

## 输出结构

```
~/TikTok-Downloads/
├── alice321441/                      # 按作者分类
│   ├── 7498701296262843655.mp4       # 视频文件
│   ├── 7498701296262843655.json      # 元数据
│   └── 7498701296262843656.mp4
└── another_user/
    └── ...
```

### metadata.json 结构

```json
{
  "id": "7498701296262843655",
  "author": "alice321441",
  "nickname": "Alice",
  "desc": "视频描述...",
  "duration": 15,
  "createTime": 1705123456,
  "stats": {
    "diggCount": 12345,
    "commentCount": 234,
    "shareCount": 56
  },
  "sourceUrl": "https://www.tiktok.com/@alice321441/video/...",
  "downloadTime": "2025-01-24T10:15:00.000Z"
}
```

### analysis.json 结构（Gemini 分析结果）

使用 `--analyze` 参数后会生成分析文件：

```json
{
  "basic_info": {
    "duration": "15秒",
    "product_type": "护肤",
    "product_name": "XX精华液",
    "target_audience": "25-35岁女性"
  },
  "storyboard": [
    {
      "segment": 1,
      "name": "Hook（开场钩子）",
      "time_range": "0:00 - 0:03",
      "shot_type": "中近景",
      "script": "姐妹们！这瓶精华真的绝了...",
      "hook_type": "惊喜式"
    },
    // ... 6段式分镜
  ],
  "overall_analysis": {
    "voiceover_style": {
      "persona": "闺蜜种草型",
      "emotion_curve": "兴奋→共鸣→信任→紧迫"
    },
    "visual_style": {
      "environment": "家居浴室",
      "lighting": "自然光",
      "camera_movement": "手持微晃"
    },
    "success_factors": ["强共鸣开场", "真实使用场景", "限时优惠刺激"],
    "viral_reason": "痛点精准+效果可视化"
  },
  "ai_video_prompt": {
    "seedance_prompt": "用于复刻的 AI 视频提示词",
    "b_roll_suggestions": ["产品特写", "使用过程"]
  }
}
```

## 目录结构

```
~/.claude/skills/tiktok-downloader/
├── SKILL.md              # 使用文档
├── package.json          # Node.js 依赖
├── scripts/
│   ├── tiktok-download   # 快捷命令入口
│   ├── download.js       # 核心下载脚本
│   └── setup.sh          # 环境设置
└── data/                 # 临时数据
```

## 配置

### 下载配置

编辑 `scripts/download.js` 顶部的配置：

```javascript
const CONFIG = {
  OUTPUT_DIR: '~/TikTok-Downloads',  // 输出目录
  HEADLESS: false,                    // 是否隐藏浏览器
  TIMEOUT: 30000,                     // 页面加载超时(ms)
  WAIT_TIME: 10000,                   // 等待视频加载时间(ms)
};
```

### Gemini API Key 配置（视频分析功能）

使用 `--analyze` 功能需要配置 Gemini API Key：

**方式 1：环境变量（推荐）**
```bash
export GEMINI_API_KEY="your-api-key"
# 或
export GOOGLE_API_KEY="your-api-key"
```

**方式 2：使用 api-keys-manager**
```bash
python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py set GOOGLE_AI "your-api-key"
```

获取 API Key：https://aistudio.google.com/app/apikey

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 命令找不到 | 运行 `setup.sh` 或添加 `~/bin` 到 PATH |
| Playwright 错误 | 运行 `npx playwright install chromium` |
| 下载失败 403 | 确保使用浏览器上下文下载，不要直接 HTTP 请求 |
| 视频加载慢 | 增加 WAIT_TIME 配置 |
| 元数据缺失 | TikTok 页面结构可能变化，需更新提取逻辑 |

## 技术原理

### 为什么需要 Playwright？

TikTok 有以下防护机制：
1. **直接下载返回 403** - 需要正确的 Cookies 和 Headers
2. **视频使用 blob URL** - 无法直接从页面提取
3. **动态加载** - 需要等待 JavaScript 执行

### 解决方案

1. 使用 Playwright 打开真实浏览器
2. 监听网络请求捕获真实视频 URL（`/video/tos/`）
3. 使用 `context.request.get()` 下载，自动带上 Cookies

## 依赖

- Node.js 18+
- Playwright
- Chromium (自动安装)

## 注意事项

1. **合规使用**: 仅用于个人学习研究
2. **频率控制**: 避免短时间大量下载
3. **浏览器窗口**: 下载过程中会打开浏览器，请勿关闭（除非配置 headless）

## 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2025-01-24 | 初始版本，支持单视频下载 |
