#!/bin/bash
# 小红书视频下载工具 - 环境设置脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
VENV_DIR="$SKILL_DIR/.venv"

# 颜色
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}  小红书视频下载工具 - 环境设置${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# 检查 uv
if ! command -v uv &> /dev/null; then
    echo -e "${YELLOW}安装 uv...${NC}"
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi
echo -e "${GREEN}✓${NC} uv 已安装"

# 创建虚拟环境
if [ ! -d "$VENV_DIR" ]; then
    echo -e "${YELLOW}创建虚拟环境...${NC}"
    cd "$SKILL_DIR"
    uv venv
fi
echo -e "${GREEN}✓${NC} 虚拟环境已创建"

# 安装依赖
echo -e "${YELLOW}安装依赖...${NC}"
cd "$SKILL_DIR"
uv pip install playwright httpx rookiepy qrcode 2>/dev/null

# 检查 Playwright
$VENV_DIR/bin/python -c "from playwright.async_api import async_playwright" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}安装 Playwright...${NC}"
    uv pip install playwright
fi
echo -e "${GREEN}✓${NC} Python 依赖已安装"

# 检查 Chromium
CHROMIUM_EXISTS=false
for dir in ~/Library/Caches/ms-playwright/chromium-*; do
    if [ -d "$dir" ]; then
        CHROMIUM_EXISTS=true
        break
    fi
done

if [ "$CHROMIUM_EXISTS" = false ]; then
    echo -e "${YELLOW}安装 Chromium 浏览器...${NC}"
    $VENV_DIR/bin/playwright install chromium 2>/dev/null || true

    # 如果下载失败，尝试使用 MediaCrawler 的
    if [ ! -d ~/Library/Caches/ms-playwright/chromium-* ]; then
        echo -e "${YELLOW}尝试使用 MediaCrawler 的 Chromium...${NC}"
        MEDIA_CRAWLER_VENV="/Users/kevingao/AI/Github/BettaFish/MindSpider/DeepSentimentCrawling/MediaCrawler/.venv"
        if [ -f "$MEDIA_CRAWLER_VENV/bin/playwright" ]; then
            $MEDIA_CRAWLER_VENV/bin/playwright install chromium 2>/dev/null || true
        fi
    fi
fi

# 再次检查
for dir in ~/Library/Caches/ms-playwright/chromium-*; do
    if [ -d "$dir" ]; then
        echo -e "${GREEN}✓${NC} Chromium 浏览器已安装"
        CHROMIUM_EXISTS=true
        break
    fi
done

if [ "$CHROMIUM_EXISTS" = false ]; then
    echo -e "${YELLOW}⚠ Chromium 安装失败，将尝试使用系统 Chrome${NC}"
fi

# 创建数据目录
mkdir -p "$SKILL_DIR/data"
echo -e "${GREEN}✓${NC} 数据目录已创建"

# 创建快捷命令
mkdir -p ~/bin
ln -sf "$SCRIPT_DIR/xhs-download" ~/bin/xhs-download 2>/dev/null
chmod +x "$SCRIPT_DIR/xhs-download"
chmod +x "$SCRIPT_DIR/auto_download.py"
echo -e "${GREEN}✓${NC} 快捷命令已创建"

# 检查 PATH
if [[ ":$PATH:" != *":$HOME/bin:"* ]]; then
    echo ""
    echo -e "${YELLOW}提示: 请将 ~/bin 添加到 PATH${NC}"
    echo "在 ~/.zshrc 或 ~/.bashrc 中添加:"
    echo '  export PATH="$HOME/bin:$PATH"'
    echo ""
fi

echo ""
echo -e "${GREEN}=====================================${NC}"
echo -e "${GREEN}  环境设置完成！${NC}"
echo -e "${GREEN}=====================================${NC}"
echo ""
echo "使用方法:"
echo -e "  ${BLUE}xhs-download${NC} <账号链接或ID>"
echo ""
echo "示例:"
echo "  xhs-download 5675e19782ec397e4a6835d3"
echo "  xhs-download 'https://www.xiaohongshu.com/user/profile/xxx'"
echo ""
