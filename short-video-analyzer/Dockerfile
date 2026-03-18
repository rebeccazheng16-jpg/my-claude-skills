# Short Video Analyzer - 飞书机器人服务
FROM node:20-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    ffmpeg \
    chromium \
    && rm -rf /var/lib/apt/lists/*

# 安装 yt-dlp
RUN pip3 install --break-system-packages yt-dlp

# 安装 Playwright
ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright
RUN npx playwright install chromium --with-deps

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY package*.json ./
COPY server/package*.json ./server/

# 安装依赖
RUN npm install
RUN cd server && npm install

# 复制代码
COPY . .

# 创建临时目录
RUN mkdir -p /tmp/video-analyzer

# 暴露端口
EXPOSE 3000

# 启动服务
CMD ["node", "server/index.js"]
