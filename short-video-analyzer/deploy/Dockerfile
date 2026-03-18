# 使用 Playwright 官方镜像（包含浏览器）
FROM mcr.microsoft.com/playwright:v1.58.0-noble

# 设置工作目录
WORKDIR /app

# 复制 package.json
COPY package.json ./

# 安装依赖
RUN npm install --production

# 复制应用代码
COPY . .

# 创建临时目录
RUN mkdir -p /tmp/video-analyzer

# 设置环境变量
ENV NODE_ENV=production
ENV PLAYWRIGHT_HEADLESS=true
ENV TEMP_DIR=/tmp/video-analyzer

# 暴露端口
EXPOSE 3000

# 启动命令
CMD ["node", "index.js"]
