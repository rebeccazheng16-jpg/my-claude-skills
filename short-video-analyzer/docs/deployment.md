# 部署指南

## 快速开始

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`

### 2. 配置应用权限

在「权限管理」中开启：

| 权限 | 说明 |
|------|------|
| `im:message:send` | 发送消息到群/私聊 |
| `im:message` | 接收消息事件 |
| `bitable:app` | 多维表格读写 |

### 3. 配置事件订阅

在「事件订阅」页面：

1. 获取 `Encrypt Key` 和 `Verification Token`
2. 订阅事件：`im.message.receive_v1`
3. 请求地址稍后配置（需要先部署服务）

### 4. 创建多维表格

创建表格并添加以下字段：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| 视频链接 | URL | 原始链接 |
| 平台 | 单选 | TikTok / 小红书 / 其他 |
| 分析时间 | 日期 | 自动填充 |
| 视频时长 | 数字 | 秒 |
| 类型 | 单选 | 带货/教程/娱乐 |
| 产品 | 文本 | 产品名称 |
| 综合评分 | 数字 | 1-10 |
| 核心卖点 | 文本 | USP |
| 爆款原因 | 文本 | 分析结论 |

从表格 URL 获取 `App Token` 和 `Table ID`：
```
https://xxx.feishu.cn/base/{app_token}?table={table_id}
```

---

## 方案 A: Railway 部署（推荐）

### 步骤

1. Fork 或上传代码到 GitHub

2. 登录 [Railway](https://railway.app) 并创建新项目

3. 连接 GitHub 仓库

4. 配置环境变量：
   ```
   FEISHU_APP_ID=cli_xxxxx
   FEISHU_APP_SECRET=xxxxx
   FEISHU_ENCRYPT_KEY=xxxxx
   FEISHU_VERIFICATION_TOKEN=xxxxx
   FEISHU_GROUP_CHAT_ID=oc_xxxxx
   FEISHU_BITABLE_APP_TOKEN=xxxxx
   FEISHU_BITABLE_TABLE_ID=tblxxxxx
   GEMINI_API_KEY=xxxxx
   ```

5. 部署后获取域名（如 `https://xxx.up.railway.app`）

6. 回到飞书应用，配置事件订阅地址：
   ```
   https://xxx.up.railway.app/webhook/feishu
   ```

7. 发布应用版本

---

## 方案 B: Docker 本地部署

### 步骤

1. 复制环境变量文件：
   ```bash
   cp server/.env.example .env
   ```

2. 编辑 `.env` 填入实际配置

3. 启动服务：
   ```bash
   docker-compose up -d
   ```

4. 使用 ngrok 暴露本地服务：
   ```bash
   ngrok http 3000
   ```

5. 配置飞书事件订阅地址为 ngrok URL

---

## 方案 C: VPS 部署

### 步骤

```bash
# 1. SSH 到服务器
ssh user@your-server

# 2. 安装依赖
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs ffmpeg python3-pip
pip3 install yt-dlp

# 3. 克隆代码
git clone <your-repo> short-video-analyzer
cd short-video-analyzer

# 4. 安装依赖
npm install
cd server && npm install && cd ..

# 5. 配置环境变量
cp server/.env.example .env
vim .env

# 6. 使用 PM2 启动
npm install -g pm2
pm2 start server/index.js --name video-analyzer
pm2 save
pm2 startup

# 7. 配置 Nginx 反向代理（可选）
sudo apt install nginx
```

Nginx 配置示例：
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 测试

### 健康检查

```bash
curl https://your-server/health
# 返回: {"status":"ok","timestamp":"..."}
```

### 发送测试消息

1. 在飞书中找到机器人
2. 私聊发送一个 TikTok 或小红书链接
3. 等待分析结果推送到群

---

## 常见问题

### Q: Webhook 验证失败

确保：
- `FEISHU_VERIFICATION_TOKEN` 正确
- 服务器可公网访问
- URL 包含 `/webhook/feishu` 路径

### Q: 下载视频失败

检查：
- `yt-dlp` 是否安装并可执行
- 视频链接是否有效
- 服务器网络是否可访问目标平台

### Q: Gemini 分析超时

- 大视频可能需要较长处理时间
- 考虑增加超时时间或使用更短的视频

### Q: 多维表格写入失败

检查：
- 应用是否有 `bitable:app` 权限
- `App Token` 和 `Table ID` 是否正确
- 表格字段名是否完全匹配
