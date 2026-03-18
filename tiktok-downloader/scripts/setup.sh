#!/bin/bash
# TikTok Downloader 环境设置脚本

set -e

SKILL_DIR="$HOME/.claude/skills/tiktok-downloader"
BIN_DIR="$HOME/bin"

echo "=== TikTok Downloader Setup ==="
echo ""

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "   请先安装 Node.js: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "⚠️  Node.js 版本过低 (需要 v18+)"
    echo "   当前版本: $(node -v)"
fi

echo "✅ Node.js $(node -v)"

# 进入 skill 目录
cd "$SKILL_DIR"

# 安装依赖
echo ""
echo "📦 安装依赖..."

if [ ! -f "package.json" ]; then
    npm init -y > /dev/null
fi

npm install playwright --save

# 安装 Chromium
echo ""
echo "🌐 安装 Chromium 浏览器..."
npx playwright install chromium

# 创建快捷命令
echo ""
echo "🔧 创建快捷命令..."

mkdir -p "$BIN_DIR"

cat > "$BIN_DIR/tiktok-download" << 'EOF'
#!/bin/bash
SKILL_DIR="$HOME/.claude/skills/tiktok-downloader"
cd "$SKILL_DIR" && node scripts/download.js "$@"
EOF

chmod +x "$BIN_DIR/tiktok-download"

# 检查 PATH
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo ""
    echo "⚠️  请将 ~/bin 添加到 PATH:"
    echo "   echo 'export PATH=\"\$HOME/bin:\$PATH\"' >> ~/.zshrc"
    echo "   source ~/.zshrc"
fi

# 创建输出目录
mkdir -p "$HOME/TikTok-Downloads"

echo ""
echo "=== 设置完成 ==="
echo ""
echo "使用方法:"
echo "  tiktok-download \"https://www.tiktok.com/@user/video/123456\""
echo ""
echo "输出目录: ~/TikTok-Downloads/"
