---
name: xhs-video-downloader
description: 小红书内容全量下载工具 v5.0。输入账号链接自动下载所有内容（视频+图片+文案）。完全自主下载，不依赖第三方工具。支持并行下载、断点续传、连接复用、Cookie 复用、进度显示、按作者分类存储。触发词：下载小红书、批量下载、无水印下载。
---

# 小红书内容全量下载工具 v5.0

**一键下载账号所有内容**：视频、图片、文案，全部保存到本地。

## 功能特性

| 功能 | 说明 |
|------|------|
| 📹 视频下载 | 无水印高清视频（自动选择最高画质） |
| 🖼️ 图片下载 | 原图质量，支持多图笔记 |
| 📝 文案保存 | 标题、描述、标签存入 JSON |
| 📊 元数据 | 点赞、收藏、评论数等 |
| 📁 分类存储 | 按作者/日期/标题自动分类 |
| 🔑 Cookie 复用 | 登录一次，后续免登录 |
| ⚡ 并行下载 | CDN 文件 3 并发下载，大幅提速 |
| 🔄 断点续传 | 自动跳过已下载内容，支持中断后继续 |
| 🌐 连接复用 | httpx 连接池，减少连接开销 |
| 🎭 随机 UA | User-Agent 池轮换，降低被识别风险 |

## 快速开始

### 首次使用

```bash
# 1. 运行环境设置
bash ~/.claude/skills/xhs-video-downloader/scripts/setup.sh

# 2. 下载内容
xhs-download "账号链接或ID"
```

### 日常使用

```bash
xhs-download "5675e19782ec397e4a6835d3"
xhs-download "https://www.xiaohongshu.com/user/profile/xxx"
xhs-download "https://xhslink.com/xxx"
```

## 工作流程

```
输入账号链接
     │
     ▼
┌─────────────────────────────────────┐
│ 1. Cookie 检查（2个来源）            │
│    ├─ 本地缓存（优先）               │
│    └─ Chrome 浏览器                 │
└─────────────────────────────────────┘
     │
     ▼ (有 Cookie 则跳过登录)
┌─────────────────────────────────────┐
│ 2. 浏览器自动化                      │
│    ├─ 访问账号主页                   │
│    ├─ 滚动加载所有笔记               │
│    └─ 从 __INITIAL_STATE__ 提取数据  │
└─────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────┐
│ 3. 逐个访问详情页下载                │
│    ├─ 提取视频/图片下载地址          │
│    ├─ 下载视频（选择最高画质）       │
│    ├─ 下载图片（原图质量）           │
│    └─ 保存文案（JSON格式）           │
└─────────────────────────────────────┘
     │
     ▼
输出保存到 ~/XHS-Downloads/
```

## 输出结构

```
~/XHS-Downloads/
├── 作者ID_作者昵称/                    # 按作者分类
│   ├── 2025-01-21_作品标题/           # 每个作品一个文件夹
│   │   ├── video_1.mp4                # 视频文件
│   │   ├── image_1.png                # 图片文件
│   │   ├── image_2.png
│   │   └── metadata.json              # 文案和元数据
│   └── 2025-01-20_另一作品/
│       └── ...
```

### metadata.json 结构

```json
{
  "id": "笔记ID",
  "title": "标题",
  "desc": "完整描述和标签",
  "type": "video/normal",
  "time": 1725615750000,
  "user": {
    "userId": "作者ID",
    "nickname": "作者昵称"
  },
  "interactInfo": {
    "likedCount": "5155",
    "collectedCount": "1890",
    "commentCount": "201",
    "shareCount": "690"
  },
  "downloadTime": "2025-01-21T20:19:18"
}
```

## 目录结构

```
~/.claude/skills/xhs-video-downloader/
├── SKILL.md              # 使用文档
├── data/
│   └── cookies.json      # Cookie 缓存
├── scripts/
│   ├── xhs-download      # 快捷命令入口
│   ├── auto_download.py  # 核心脚本 v4.0
│   └── setup.sh          # 环境设置
└── .venv/                # 独立 Python 环境
```

## 配置

编辑 `scripts/auto_download.py` 顶部的配置：

```python
OUTPUT_DIR = Path.home() / "XHS-Downloads"  # 输出目录
MAX_SCROLL_ATTEMPTS = 50   # 最大滚动次数（更多=更多笔记）
SCROLL_DELAY = 1.5         # 滚动间隔（秒）
DOWNLOAD_DELAY = 0.3       # 下载间隔（秒）
LOGIN_TIMEOUT = 300        # 登录超时（秒）
MAX_CONCURRENT_DOWNLOADS = 3  # CDN 并发下载数（建议 3-5）
```

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| 命令找不到 | 运行 `setup.sh` 或添加 `~/bin` 到 PATH |
| Playwright 错误 | 运行 `setup.sh` 重新安装 |
| 登录超时 | 确保在 5 分钟内完成扫码 |
| Cookie 失效 | 删除 `data/cookies.json`，重新登录 |
| 下载失败 | 检查网络，或增加 timeout 配置 |
| 视频下载不完整 | 网络问题，重新运行会跳过已下载 |

## 依赖

- Python 3.9+
- Playwright (自动安装)
- httpx (自动安装)
- rookiepy (读取 Chrome Cookie)

## 版本历史

| 功能 | v3.0 | v4.0 | v4.1 | v5.0 |
|------|------|------|------|------|
| 下载方式 | XHS-Downloader | 自主下载 | 自主下载 | 自主下载 |
| 依赖项 | 需要 XHS-Downloader | 完全独立 | 完全独立 | 完全独立 |
| 可靠性 | 受第三方限制 | 较稳定 | 更稳定 | 最稳定 |
| 视频下载 | ❌ (token失效) | ✅ | ✅ | ✅ |
| 图片下载 | ❌ (token失效) | ✅ | ✅ | ✅ |
| 文案保存 | SQLite | JSON | JSON | JSON |
| 空值处理 | - | ❌ | ✅ | ✅ |
| 重试机制 | - | ❌ | ✅ (3次) | ✅ (3次) |
| 断点续传 | - | - | - | ✅ |
| 并行下载 | - | - | - | ✅ (3并发) |
| 连接复用 | - | - | - | ✅ |
| 随机 UA | - | - | - | ✅ |

## 注意事项

1. **合规使用**: 仅用于个人学习研究
2. **频率控制**: 页面访问保持间隔，CDN 下载并行但有限流
3. **Cookie 安全**: Cookie 仅保存在本地，不上传
4. **首次登录**: 需要手动扫码，之后自动复用
5. **存储空间**: 视频和图片可能占用较大空间，请确保磁盘充足
6. **浏览器窗口**: 下载过程中会打开浏览器，请勿关闭
7. **断点续传**: 如果下载中断，重新运行会自动跳过已下载内容
