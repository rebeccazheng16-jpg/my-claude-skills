#!/bin/bash
# TikTok Fashion Video Generator 安装脚本

SKILL_DIR="$HOME/.claude/skills/tiktok-fashion-video-generator"

echo "🔧 安装 TikTok Fashion Video Generator..."

# 创建快捷命令
cat > /usr/local/bin/tiktok-fashion << 'EOF'
#!/bin/bash
python3 ~/.claude/skills/tiktok-fashion-video-generator/scripts/generate.py "$@"
EOF

chmod +x /usr/local/bin/tiktok-fashion 2>/dev/null || {
    # 如果没有权限写入 /usr/local/bin，使用 alias
    echo "alias tiktok-fashion='python3 ~/.claude/skills/tiktok-fashion-video-generator/scripts/generate.py'" >> ~/.zshrc
    echo "alias tiktok-fashion='python3 ~/.claude/skills/tiktok-fashion-video-generator/scripts/generate.py'" >> ~/.bashrc
}

echo "✅ 安装完成!"
echo ""
echo "使用方法:"
echo "  tiktok-fashion ~/path/to/image.png"
echo "  tiktok-fashion ~/path/to/image.png --duration 15 --market indonesia"
echo ""
echo "参数说明:"
echo "  --duration   视频时长: 15/20/25/30 (默认30)"
echo "  --market     目标市场: indonesia/china/global (默认indonesia)"
echo "  --gender     目标性别: female/male/unisex (默认female)"
echo "  --style      风格: casual/formal/streetwear (默认casual)"
echo "  --scene      场景: fullbody/mirror/upper (默认fullbody)"
