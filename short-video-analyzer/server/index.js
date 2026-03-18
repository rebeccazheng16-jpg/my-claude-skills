/**
 * Short Video Analyzer - 飞书机器人服务器
 *
 * 功能：
 * 1. 接收飞书私聊消息
 * 2. 下载视频 + Gemini 分析
 * 3. 发送群消息 + 写入多维表格
 */

const express = require('express');
const crypto = require('crypto');
const path = require('path');
const fs = require('fs');
const { analyzeVideo } = require('../scripts/analyze.js');

// ============ 配置 ============

const CONFIG = {
  PORT: process.env.PORT || 3000,

  // 飞书应用配置
  FEISHU_APP_ID: process.env.FEISHU_APP_ID,
  FEISHU_APP_SECRET: process.env.FEISHU_APP_SECRET,
  FEISHU_ENCRYPT_KEY: process.env.FEISHU_ENCRYPT_KEY,
  FEISHU_VERIFICATION_TOKEN: process.env.FEISHU_VERIFICATION_TOKEN,

  // 飞书目标配置
  FEISHU_GROUP_CHAT_ID: process.env.FEISHU_GROUP_CHAT_ID,
  FEISHU_BITABLE_APP_TOKEN: process.env.FEISHU_BITABLE_APP_TOKEN,
  FEISHU_BITABLE_TABLE_ID: process.env.FEISHU_BITABLE_TABLE_ID,

  // Gemini
  GEMINI_API_KEY: process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY,

  // 临时文件目录
  TEMP_DIR: process.env.TEMP_DIR || '/tmp/video-analyzer',

  // 支持的平台
  SUPPORTED_PLATFORMS: {
    'tiktok.com': 'tiktok',
    'vm.tiktok.com': 'tiktok',
    'xiaohongshu.com': 'xiaohongshu',
    'xhslink.com': 'xiaohongshu',
  }
};

// ============ 飞书 API 客户端 ============

class FeishuClient {
  constructor(appId, appSecret, baseUrl) {
    this.appId = appId;
    this.appSecret = appSecret;
    // 支持 Lark Suite 国际版
    this.baseUrl = baseUrl || process.env.LARK_API_BASE || 'https://open.feishu.cn/open-apis';
    this.token = null;
    this.tokenExpiry = 0;
    console.log(`使用 API: ${this.baseUrl}`);
  }

  async getToken() {
    if (this.token && Date.now() < this.tokenExpiry) {
      return this.token;
    }

    const response = await fetch(`${this.baseUrl}/auth/v3/tenant_access_token/internal/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        app_id: this.appId,
        app_secret: this.appSecret,
      }),
    });

    const data = await response.json();
    if (data.code !== 0) {
      throw new Error(`获取 token 失败: ${data.msg}`);
    }

    this.token = data.tenant_access_token;
    this.tokenExpiry = Date.now() + (data.expire - 300) * 1000; // 提前5分钟过期

    return this.token;
  }

  async sendGroupMessage(chatId, content, msgType = 'interactive') {
    const token = await this.getToken();

    const response = await fetch(`${this.baseUrl}/im/v1/messages?receive_id_type=chat_id`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        receive_id: chatId,
        msg_type: msgType,
        content: typeof content === 'string' ? content : JSON.stringify(content),
      }),
    });

    return response.json();
  }

  async createBitableRecord(appToken, tableId, fields) {
    const token = await this.getToken();

    const response = await fetch(
      `${this.baseUrl}/bitable/v1/apps/${appToken}/tables/${tableId}/records`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fields }),
      }
    );

    return response.json();
  }

  async replyMessage(messageId, content, msgType = 'text') {
    const token = await this.getToken();

    const response = await fetch(`${this.baseUrl}/im/v1/messages/${messageId}/reply`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        msg_type: msgType,
        content: typeof content === 'string' ? content : JSON.stringify(content),
      }),
    });

    return response.json();
  }
}

// ============ 视频处理器 ============

class VideoProcessor {
  constructor(tempDir) {
    this.tempDir = tempDir;
    if (!fs.existsSync(tempDir)) {
      fs.mkdirSync(tempDir, { recursive: true });
    }
  }

  detectPlatform(url) {
    try {
      const parsed = new URL(url);
      for (const [domain, platform] of Object.entries(CONFIG.SUPPORTED_PLATFORMS)) {
        if (parsed.hostname.includes(domain)) {
          return platform;
        }
      }
      return 'unknown';
    } catch {
      return 'invalid';
    }
  }

  async downloadVideo(url, platform) {
    try {
      if (platform === 'tiktok') {
        // 使用 tiktok-downloader skill
        const result = await this.downloadWithTikTokDownloader(url);
        if (result.success) {
          return { success: true, path: result.path };
        }
        throw new Error(result.error || '下载失败');

      } else if (platform === 'xiaohongshu') {
        // 小红书使用 yt-dlp
        const videoId = Date.now().toString();
        const videoPath = path.join(this.tempDir, `${videoId}.mp4`);
        const { execSync } = require('child_process');
        const ytdlp = process.env.YTDLP_PATH || '/Users/kevingao/Library/Python/3.9/bin/yt-dlp';
        execSync(`${ytdlp} -f best -o "${videoPath}" "${url}"`, { stdio: 'pipe' });

        if (fs.existsSync(videoPath)) {
          return { success: true, path: videoPath };
        }
        throw new Error('下载失败');
      } else {
        throw new Error(`不支持的平台: ${platform}`);
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // 使用 tiktok-downloader skill 下载
  async downloadWithTikTokDownloader(url) {
    // 直接调用 tiktok-downloader 的下载函数
    const tiktokDownloaderPath = path.join(__dirname, '../../tiktok-downloader/scripts/download.js');
    const { downloadTikTokVideo, CONFIG } = require(tiktokDownloaderPath);

    console.log('使用 tiktok-downloader 下载视频...');

    // 调用下载函数
    const result = await downloadTikTokVideo(url);

    if (result.success && result.filepath) {
      // 复制到临时目录（可选，或直接使用原路径）
      return { success: true, path: result.filepath };
    }

    return { success: false, error: '下载失败，未捕获到视频' };
  }

  async analyze(videoPath) {
    return analyzeVideo(videoPath);
  }

  cleanup(videoPath) {
    try {
      if (fs.existsSync(videoPath)) {
        fs.unlinkSync(videoPath);
      }
    } catch (e) {
      console.error('清理失败:', e);
    }
  }
}

// ============ 消息格式化 ============

function formatAnalysisCard(analysis, sourceUrl) {
  const basicInfo = analysis.basic_info || {};
  const scores = analysis.overall_assessment?.success_score || {};
  const viral = analysis.overall_assessment?.viral_factors || {};

  return {
    config: { wide_screen_mode: true },
    header: {
      title: { tag: 'plain_text', content: '📊 视频分析完成' },
      template: 'blue',
    },
    elements: [
      {
        tag: 'div',
        fields: [
          { is_short: true, text: { tag: 'lark_md', content: `**时长**: ${basicInfo.duration || 'N/A'}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**类型**: ${basicInfo.video_type || 'N/A'}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**评分**: ${scores.overall_score || 'N/A'}/10` } },
        ],
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**标题建议**\n${(basicInfo.title_suggestion || []).slice(0, 2).map((t, i) => `${i + 1}. ${t}`).join('\n')}`,
        },
      },
      { tag: 'hr' },
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**爆款原因**\n${viral.primary_reason || '分析中...'}`,
        },
      },
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**关键学习点**\n${(analysis.overall_assessment?.key_learnings || []).map((l, i) => `• ${l}`).join('\n')}`,
        },
      },
      { tag: 'hr' },
      {
        tag: 'action',
        actions: [
          {
            tag: 'button',
            text: { tag: 'plain_text', content: '查看原视频' },
            type: 'primary',
            url: sourceUrl,
          },
        ],
      },
    ],
  };
}

function formatBitableRecord(analysis, sourceUrl, platform, userId) {
  const basicInfo = analysis.basic_info || {};
  const scores = analysis.overall_assessment?.success_score || {};
  const product = analysis.product_analysis?.product_info || {};
  const viral = analysis.overall_assessment?.viral_factors || {};

  return {
    '视频链接': { link: sourceUrl, text: sourceUrl },
    '平台': platform === 'tiktok' ? 'TikTok' : platform === 'xiaohongshu' ? '小红书' : '其他',
    '分析时间': Date.now(),
    '视频时长': parseInt(basicInfo.duration) || 0,
    '类型': basicInfo.video_type || '',
    '产品': product.name || '',
    '综合评分': parseInt(scores.overall_score) || 0,
    '核心卖点': analysis.product_analysis?.selling_points_system?.core_usp || '',
    '爆款原因': viral.primary_reason || '',
    // '提交人': [{ id: userId }], // 需要用户 open_id
  };
}

// ============ Express 服务器 ============

const app = express();
app.use(express.json());

const feishu = new FeishuClient(CONFIG.FEISHU_APP_ID, CONFIG.FEISHU_APP_SECRET);
const processor = new VideoProcessor(CONFIG.TEMP_DIR);

// 健康检查
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 飞书事件订阅回调
app.post('/webhook/feishu', async (req, res) => {
  const body = req.body;

  console.log('收到 Webhook 请求:', JSON.stringify(body, null, 2));

  // 1. URL 验证（首次配置）
  if (body.type === 'url_verification') {
    console.log('URL 验证请求');
    return res.json({ challenge: body.challenge });
  }

  // 2. 支持 v1 和 v2 事件格式
  // v1: body.token, body.event
  // v2: body.header.token, body.event
  const token = body.token || body.header?.token;
  const event = body.event;

  // 验证 token（如果配置了的话）
  if (CONFIG.FEISHU_VERIFICATION_TOKEN && token !== CONFIG.FEISHU_VERIFICATION_TOKEN) {
    console.error('Token 验证失败, 收到:', token, '期望:', CONFIG.FEISHU_VERIFICATION_TOKEN);
    return res.status(401).json({ error: 'Invalid token' });
  }

  // 3. 处理事件
  if (!event) {
    console.log('没有 event 字段');
    return res.json({ ok: true });
  }

  // 立即返回，避免超时
  res.json({ ok: true });

  // 4. 异步处理消息 (支持 v1 和 v2 格式)
  const messageType = event.message?.message_type || event.message_type;
  console.log('消息类型:', messageType);

  if (messageType === 'text') {
    processMessage(event).catch(console.error);
  }
});

// 异步处理消息
async function processMessage(event) {
  const message = event.message;
  const sender = event.sender;
  const messageId = message.message_id;

  // 解析消息内容
  let text;
  try {
    const content = JSON.parse(message.content);
    text = content.text || '';
  } catch {
    text = message.content || '';
  }

  console.log(`收到消息: ${text}`);

  // 提取链接
  const urlMatch = text.match(/https?:\/\/[^\s]+/);
  if (!urlMatch) {
    await feishu.replyMessage(messageId, JSON.stringify({ text: '请发送视频链接（TikTok/小红书）' }));
    return;
  }

  const url = urlMatch[0];
  const platform = processor.detectPlatform(url);

  if (platform === 'unknown' || platform === 'invalid') {
    await feishu.replyMessage(messageId, JSON.stringify({ text: '暂不支持此平台，目前支持 TikTok 和小红书' }));
    return;
  }

  // 回复处理中
  await feishu.replyMessage(messageId, JSON.stringify({ text: '⏳ 正在下载并分析视频，请稍候...' }));

  try {
    // 1. 下载视频
    console.log(`下载视频: ${url}`);
    const downloadResult = await processor.downloadVideo(url, platform);
    if (!downloadResult.success) {
      throw new Error(`下载失败: ${downloadResult.error}`);
    }

    // 2. 分析视频
    console.log(`分析视频: ${downloadResult.path}`);
    const analysis = await processor.analyze(downloadResult.path);
    if (!analysis) {
      throw new Error('分析失败');
    }

    // 3. 发送群消息
    if (CONFIG.FEISHU_GROUP_CHAT_ID) {
      const card = formatAnalysisCard(analysis, url);
      await feishu.sendGroupMessage(CONFIG.FEISHU_GROUP_CHAT_ID, card);
      console.log('群消息已发送');
    }

    // 4. 写入多维表格
    if (CONFIG.FEISHU_BITABLE_APP_TOKEN && CONFIG.FEISHU_BITABLE_TABLE_ID) {
      const record = formatBitableRecord(analysis, url, platform, sender.sender_id?.user_id);
      await feishu.createBitableRecord(
        CONFIG.FEISHU_BITABLE_APP_TOKEN,
        CONFIG.FEISHU_BITABLE_TABLE_ID,
        record
      );
      console.log('多维表格记录已创建');
    }

    // 5. 回复完成
    await feishu.replyMessage(messageId, JSON.stringify({ text: '✅ 分析完成！结果已发送到群里并保存到表格。' }));

    // 6. 清理临时文件
    processor.cleanup(downloadResult.path);

  } catch (error) {
    console.error('处理失败:', error);
    await feishu.replyMessage(messageId, JSON.stringify({ text: `❌ 处理失败: ${error.message}` }));
  }
}

// ============ 启动服务器 ============

app.listen(CONFIG.PORT, () => {
  console.log(`
╔════════════════════════════════════════════════════════╗
║     Short Video Analyzer - Feishu Bot Server           ║
╠════════════════════════════════════════════════════════╣
║  端口: ${CONFIG.PORT}                                          ║
║  Webhook: http://localhost:${CONFIG.PORT}/webhook/feishu       ║
║  健康检查: http://localhost:${CONFIG.PORT}/health              ║
╚════════════════════════════════════════════════════════╝
  `);
});
