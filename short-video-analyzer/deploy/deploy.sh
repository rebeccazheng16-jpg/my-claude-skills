#!/bin/bash
# Short Video Analyzer - Fly.io 部署脚本

set -e

echo "=========================================="
echo "   Short Video Analyzer - Fly.io 部署"
echo "=========================================="

# 检查 flyctl 是否安装
if ! command -v flyctl &> /dev/null; then
    echo "❌ 未安装 flyctl，正在安装..."
    curl -L https://fly.io/install.sh | sh
    export FLYCTL_INSTALL="/Users/$USER/.fly"
    export PATH="$FLYCTL_INSTALL/bin:$PATH"
fi

# 检查是否登录
if ! flyctl auth whoami &> /dev/null; then
    echo "请先登录 Fly.io..."
    flyctl auth login
fi

# 创建应用（如果不存在）
APP_NAME="short-video-analyzer"
if ! flyctl apps list | grep -q "$APP_NAME"; then
    echo "创建应用: $APP_NAME"
    flyctl apps create "$APP_NAME" --org personal
fi

# 设置环境变量（Secrets）
echo ""
echo "=========================================="
echo "   配置环境变量"
echo "=========================================="
echo ""
echo "请输入以下配置（或按 Enter 跳过使用现有值）："
echo ""

read -p "FEISHU_APP_ID: " FEISHU_APP_ID
read -p "FEISHU_APP_SECRET: " FEISHU_APP_SECRET
read -p "FEISHU_VERIFICATION_TOKEN: " FEISHU_VERIFICATION_TOKEN
read -p "FEISHU_GROUP_CHAT_ID: " FEISHU_GROUP_CHAT_ID
read -p "FEISHU_BITABLE_APP_TOKEN: " FEISHU_BITABLE_APP_TOKEN
read -p "FEISHU_BITABLE_TABLE_ID: " FEISHU_BITABLE_TABLE_ID
read -p "GEMINI_API_KEY: " GEMINI_API_KEY
read -p "LARK_API_BASE (默认 https://open.larksuite.com/open-apis): " LARK_API_BASE

# 设置 secrets
if [ -n "$FEISHU_APP_ID" ]; then
    flyctl secrets set FEISHU_APP_ID="$FEISHU_APP_ID" --app "$APP_NAME"
fi
if [ -n "$FEISHU_APP_SECRET" ]; then
    flyctl secrets set FEISHU_APP_SECRET="$FEISHU_APP_SECRET" --app "$APP_NAME"
fi
if [ -n "$FEISHU_VERIFICATION_TOKEN" ]; then
    flyctl secrets set FEISHU_VERIFICATION_TOKEN="$FEISHU_VERIFICATION_TOKEN" --app "$APP_NAME"
fi
if [ -n "$FEISHU_GROUP_CHAT_ID" ]; then
    flyctl secrets set FEISHU_GROUP_CHAT_ID="$FEISHU_GROUP_CHAT_ID" --app "$APP_NAME"
fi
if [ -n "$FEISHU_BITABLE_APP_TOKEN" ]; then
    flyctl secrets set FEISHU_BITABLE_APP_TOKEN="$FEISHU_BITABLE_APP_TOKEN" --app "$APP_NAME"
fi
if [ -n "$FEISHU_BITABLE_TABLE_ID" ]; then
    flyctl secrets set FEISHU_BITABLE_TABLE_ID="$FEISHU_BITABLE_TABLE_ID" --app "$APP_NAME"
fi
if [ -n "$GEMINI_API_KEY" ]; then
    flyctl secrets set GEMINI_API_KEY="$GEMINI_API_KEY" --app "$APP_NAME"
fi
if [ -n "$LARK_API_BASE" ]; then
    flyctl secrets set LARK_API_BASE="$LARK_API_BASE" --app "$APP_NAME"
else
    flyctl secrets set LARK_API_BASE="https://open.larksuite.com/open-apis" --app "$APP_NAME"
fi

# 部署
echo ""
echo "=========================================="
echo "   开始部署"
echo "=========================================="
flyctl deploy --app "$APP_NAME"

# 获取 URL
echo ""
echo "=========================================="
echo "   部署完成！"
echo "=========================================="
APP_URL=$(flyctl info --app "$APP_NAME" -j | grep -o '"hostname":"[^"]*"' | head -1 | cut -d'"' -f4)
echo ""
echo "✅ 应用地址: https://$APP_URL"
echo "✅ Webhook URL: https://$APP_URL/webhook/feishu"
echo "✅ 健康检查: https://$APP_URL/health"
echo ""
echo "请将 Webhook URL 配置到 Lark 应用的事件订阅中。"
