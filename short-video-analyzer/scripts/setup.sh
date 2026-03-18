#!/bin/bash
# Short Video Analyzer - 环境设置脚本

set -e

SKILL_DIR="$HOME/.claude/skills/short-video-analyzer"
BIN_DIR="$HOME/bin"

echo "=== Short Video Analyzer 环境设置 ==="
echo ""

# 1. 检查 Node.js
echo "1. 检查 Node.js..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js 未安装"
    echo "   请安装 Node.js 18+: https://nodejs.org/"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js 版本过低: $(node -v)"
    echo "   需要 Node.js 18+"
    exit 1
fi
echo "✅ Node.js $(node -v)"

# 2. 安装依赖
echo ""
echo "2. 安装依赖..."
cd "$SKILL_DIR"
npm install --silent
echo "✅ 依赖安装完成"

# 3. 创建命令行入口
echo ""
echo "3. 创建命令行入口..."
mkdir -p "$BIN_DIR"

# video-analyze 命令
cat > "$BIN_DIR/video-analyze" << 'EOF'
#!/bin/bash
node ~/.claude/skills/short-video-analyzer/scripts/analyze.js "$@"
EOF
chmod +x "$BIN_DIR/video-analyze"

# video-pipeline 命令
cat > "$BIN_DIR/video-pipeline" << 'EOF'
#!/bin/bash
node ~/.claude/skills/short-video-analyzer/scripts/pipeline.js "$@"
EOF
chmod +x "$BIN_DIR/video-pipeline"

echo "✅ 命令创建完成"
echo "   - video-analyze: 分析单个视频"
echo "   - video-pipeline: 全链路处理"

# 4. 检查 PATH
echo ""
echo "4. 检查 PATH..."
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    echo "⚠️  $BIN_DIR 不在 PATH 中"
    echo "   请添加以下行到 ~/.zshrc 或 ~/.bashrc:"
    echo ""
    echo "   export PATH=\"\$HOME/bin:\$PATH\""
    echo ""
else
    echo "✅ PATH 已配置"
fi

# 5. 检查 Gemini API Key
echo ""
echo "5. 检查 Gemini API Key..."
if [ -n "$GEMINI_API_KEY" ] || [ -n "$GOOGLE_API_KEY" ]; then
    echo "✅ API Key 已配置"
else
    # 尝试从 api-keys-manager 获取
    API_KEY=$(python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py get GOOGLE_AI 2>/dev/null || echo "")
    if [ -n "$API_KEY" ] && [[ "$API_KEY" != *"not found"* ]]; then
        echo "✅ API Key 已配置 (via api-keys-manager)"
    else
        echo "⚠️  Gemini API Key 未配置"
        echo "   请设置环境变量:"
        echo ""
        echo "   export GEMINI_API_KEY=\"your-api-key\""
        echo ""
        echo "   或使用 api-keys-manager:"
        echo "   python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py set GOOGLE_AI \"your-key\""
        echo ""
        echo "   获取 API Key: https://aistudio.google.com/app/apikey"
    fi
fi

echo ""
echo "=== 设置完成 ==="
echo ""
echo "快速开始:"
echo "  video-analyze ~/path/to/video.mp4"
echo "  video-pipeline \"https://www.tiktok.com/@user/video/123\""
echo ""
