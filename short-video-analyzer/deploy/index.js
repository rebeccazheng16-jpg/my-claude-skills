/**
 * Short Video Analyzer - 云端部署版
 *
 * 功能：
 * 1. 接收 Lark 私聊消息（TikTok 链接）
 * 2. Playwright 下载视频
 * 3. Gemini 分析视频
 * 4. 发送群消息 + 写入多维表格
 */

const express = require('express');
const { chromium } = require('playwright');
const { google } = require('googleapis');
const fs = require('fs');
const path = require('path');

// ============ 配置 ============

const CONFIG = {
  PORT: process.env.PORT || 3000,

  // Lark 应用配置
  FEISHU_APP_ID: process.env.FEISHU_APP_ID,
  FEISHU_APP_SECRET: process.env.FEISHU_APP_SECRET,
  FEISHU_VERIFICATION_TOKEN: process.env.FEISHU_VERIFICATION_TOKEN,

  // Lark 目标配置
  FEISHU_GROUP_CHAT_ID: process.env.FEISHU_GROUP_CHAT_ID,
  FEISHU_BITABLE_APP_TOKEN: process.env.FEISHU_BITABLE_APP_TOKEN,
  FEISHU_BITABLE_TABLE_ID: process.env.FEISHU_BITABLE_TABLE_ID,

  // API Base
  LARK_API_BASE: process.env.LARK_API_BASE || 'https://open.larksuite.com/open-apis',

  // Gemini
  GEMINI_API_KEY: process.env.GEMINI_API_KEY,

  // Google Drive
  GOOGLE_DRIVE_CREDENTIALS: process.env.GOOGLE_DRIVE_CREDENTIALS,
  GOOGLE_DRIVE_FOLDER_ID: process.env.GOOGLE_DRIVE_FOLDER_ID, // 可选：指定文件夹

  // 临时目录
  TEMP_DIR: process.env.TEMP_DIR || '/tmp/video-analyzer',

  // Playwright
  HEADLESS: process.env.PLAYWRIGHT_HEADLESS !== 'false',

  // 支持的平台
  SUPPORTED_PLATFORMS: {
    'tiktok.com': 'tiktok',
    'vm.tiktok.com': 'tiktok',
  }
};

// 确保临时目录存在
if (!fs.existsSync(CONFIG.TEMP_DIR)) {
  fs.mkdirSync(CONFIG.TEMP_DIR, { recursive: true });
}

console.log('配置:', {
  PORT: CONFIG.PORT,
  LARK_API_BASE: CONFIG.LARK_API_BASE,
  HEADLESS: CONFIG.HEADLESS,
  TEMP_DIR: CONFIG.TEMP_DIR,
});

// ============ Gemini 分析提示词 ============

const ANALYSIS_PROMPT = `# 短视频深度分析

你是专业的短视频内容分析师。请仔细观看视频的每一帧画面，聆听所有音频内容，输出完整的 JSON 格式分析报告。

## 输出 JSON 结构

{
  "basic_info": {
    "title_suggestion": ["爆款标题1", "爆款标题2", "爆款标题3"],
    "duration": "0:58",
    "video_type": "教程/测评/种草/剧情/Vlog等",
    "target_audience": {
      "demographics": "年龄性别等人口统计特征",
      "psychographics": "心理特征、兴趣爱好",
      "consumption_scenario": "使用场景"
    }
  },
  "full_transcript": {
    "original": "【最重要】完整逐字口播稿原文，一字不漏地转录视频中所有说话内容，包括语气词、重复、停顿。这是最核心的输出，必须完整准确。",
    "chinese": "如原文非中文，提供完整中文翻译",
    "language": "原视频语言",
    "word_count": "总字数",
    "speaking_rate": "每分钟字数"
  },
  "storyboard": [
    {
      "segment": 1,
      "name": "Hook（开场钩子）",
      "time_range": "0:00 - 0:04",
      "shot_type": "特写/中景/全景等",
      "camera_angle": "平视/俯视/仰视",
      "camera_movement": "固定/推/拉/摇/移/跟",
      "script": "这个片段的口播文案原文",
      "visual_description": "详细的画面描述：人物动作、表情、场景、道具、服装等",
      "text_overlay": "画面上出现的文字",
      "hook_type": "问题式/悬念式/利益式/共鸣式",
      "retention_prediction": "高/中/低"
    },
    {
      "segment": 2,
      "name": "Pain Point（痛点共鸣）",
      "time_range": "0:04 - 0:10",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "",
      "visual_description": "",
      "text_overlay": ""
    },
    {
      "segment": 3,
      "name": "Product Intro（产品介绍）",
      "time_range": "",
      "shot_type": "",
      "script": "",
      "visual_description": ""
    },
    {
      "segment": 4,
      "name": "Selling Points（卖点展示）",
      "time_range": "",
      "script": "",
      "visual_description": ""
    },
    {
      "segment": 5,
      "name": "Demonstration（使用演示）",
      "time_range": "",
      "script": "",
      "visual_description": ""
    },
    {
      "segment": 6,
      "name": "Benefits（效果利益）",
      "time_range": "",
      "script": "",
      "visual_description": ""
    },
    {
      "segment": 7,
      "name": "CTA（行动号召）",
      "time_range": "",
      "script": "",
      "visual_description": ""
    }
  ],
  "product_analysis": {
    "product_info": {
      "name": "产品名称",
      "category": "品类",
      "brand": "品牌",
      "price_point": "价格定位"
    },
    "selling_points_system": {
      "core_usp": "核心卖点一句话总结",
      "functional_points": ["功能卖点1", "功能卖点2"],
      "emotional_points": ["情感卖点1", "情感卖点2"]
    },
    "benefits_matrix": {
      "functional": "功能利益",
      "emotional": "情感利益",
      "social": "社交利益"
    },
    "cta_strategy": {
      "primary_cta": "主要行动号召",
      "urgency_elements": "紧迫感元素",
      "trust_elements": "信任元素"
    }
  },
  "audio_analysis": {
    "bgm": {
      "music_type": "电子/流行/古典等",
      "music_mood": "欢快/紧张/温馨等",
      "tempo": "快/中/慢",
      "music_video_sync": "音乐与画面的配合分析"
    },
    "sound_effects": {
      "effects_used": ["音效1", "音效2"],
      "effect_purpose": "音效的作用"
    },
    "voice_characteristics": {
      "tone": "语调特点",
      "energy_level": "能量等级",
      "speaking_style": "说话风格"
    }
  },
  "visual_style_analysis": {
    "shooting_environment": "拍摄环境描述",
    "lighting": "灯光分析",
    "color_analysis": {
      "dominant_colors": ["主色1", "主色2"],
      "color_psychology": "色彩心理学分析"
    },
    "composition": "构图特点",
    "editing_style": {
      "cutting_rhythm": "剪辑节奏",
      "average_shot_length": "平均镜头时长",
      "transitions": "转场方式"
    }
  },
  "performance_prediction": {
    "completion_rate": {
      "prediction": "高/中/低",
      "factors": "影响因素"
    },
    "engagement_rate": {
      "prediction": "高/中/低",
      "triggers": "互动触发点"
    },
    "platform_fit": {
      "tiktok": "高/中/低",
      "douyin": "高/中/低",
      "xiaohongshu": "高/中/低"
    }
  },
  "operation_suggestions": {
    "title_suggestions": ["优化标题1", "优化标题2"],
    "cover_frame": {
      "recommended_timestamp": "推荐封面时间点",
      "reason": "原因"
    },
    "hashtag_suggestions": {
      "primary_tags": ["核心标签"],
      "trending_tags": ["热门标签"],
      "niche_tags": ["细分标签"]
    },
    "posting_strategy": {
      "best_time": "最佳发布时间",
      "frequency": "发布频率建议"
    }
  },
  "replication_guide": {
    "difficulty_assessment": {
      "overall_difficulty": "简单/中等/困难",
      "required_equipment": ["设备1", "设备2"],
      "required_skills": ["技能1", "技能2"]
    },
    "essential_elements": ["必备元素1", "必备元素2", "必备元素3"],
    "script_template": "可直接套用的脚本模板，用[产品名]等占位符",
    "step_by_step": ["步骤1", "步骤2", "步骤3"],
    "ai_video_prompts": {
      "seedance_prompt_cn": "详细的 Seedance AI 视频生成提示词（中文），包含画面、动作、镜头运动描述",
      "seedance_prompt_en": "Detailed Seedance AI video generation prompt (English)"
    }
  },
  "overall_assessment": {
    "success_score": {
      "hook_score": 8,
      "content_score": 8,
      "cta_score": 8,
      "overall_score": 8
    },
    "viral_factors": {
      "primary_reason": "爆款核心原因详细分析",
      "secondary_reasons": ["次要原因1", "次要原因2"]
    },
    "key_learnings": ["关键学习点1", "关键学习点2", "关键学习点3"],
    "improvement_suggestions": ["改进建议1", "改进建议2"]
  }
}

## 重要要求

1. **full_transcript.original 是最重要的输出**：必须完整逐字转录视频中所有口播内容，一字不漏
2. **storyboard 分镜脚本**：按7段式结构分析，每段都要有具体的时间、口播、画面描述
3. **所有分析要具体**：不要泛泛而谈，要有具体的细节和数据
4. **如果某些段落不适用**：可以合并或调整，但要保持结构完整

只输出 JSON，不要任何其他内容。`;

// ============ Lark API 客户端 ============

class LarkClient {
  constructor(appId, appSecret, baseUrl) {
    this.appId = appId;
    this.appSecret = appSecret;
    this.baseUrl = baseUrl;
    this.token = null;
    this.tokenExpiry = 0;
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
    this.tokenExpiry = Date.now() + (data.expire - 300) * 1000;
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

// ============ Google Drive 上传器 ============

class GoogleDriveUploader {
  constructor() {
    this.drive = null;
    this.initialized = false;
  }

  async init() {
    if (this.initialized) return true;

    if (!CONFIG.GOOGLE_DRIVE_CREDENTIALS) {
      console.log('⚠️ Google Drive 未配置，跳过视频上传');
      return false;
    }

    try {
      const credentials = JSON.parse(CONFIG.GOOGLE_DRIVE_CREDENTIALS);
      const auth = new google.auth.GoogleAuth({
        credentials,
        scopes: ['https://www.googleapis.com/auth/drive.file']
      });

      this.drive = google.drive({ version: 'v3', auth });
      this.initialized = true;
      console.log('✓ Google Drive 初始化成功');
      return true;
    } catch (error) {
      console.error('Google Drive 初始化失败:', error.message);
      return false;
    }
  }

  async uploadFile(filePath, fileName) {
    if (!await this.init()) {
      return { success: false, error: 'Google Drive 未初始化' };
    }

    const fileSize = fs.statSync(filePath).size;
    const fileSizeMB = (fileSize / 1024 / 1024).toFixed(2);
    console.log(`📤 上传文件到 Google Drive: ${fileName} (${fileSizeMB} MB)`);

    try {
      // 上传文件
      const fileMetadata = {
        name: fileName,
      };

      // 如果配置了文件夹 ID，则上传到指定文件夹
      if (CONFIG.GOOGLE_DRIVE_FOLDER_ID) {
        fileMetadata.parents = [CONFIG.GOOGLE_DRIVE_FOLDER_ID];
      }

      const media = {
        mimeType: 'video/mp4',
        body: fs.createReadStream(filePath),
      };

      const response = await this.drive.files.create({
        requestBody: fileMetadata,
        media: media,
        fields: 'id, name, webViewLink',
      });

      const fileId = response.data.id;
      console.log(`   文件已上传，ID: ${fileId}`);

      // 设置公开访问权限
      await this.drive.permissions.create({
        fileId: fileId,
        requestBody: {
          role: 'reader',
          type: 'anyone',
        },
      });

      const shareUrl = `https://drive.google.com/file/d/${fileId}/view`;
      console.log(`   ✓ 分享链接: ${shareUrl}`);

      return {
        success: true,
        fileId: fileId,
        shareUrl: shareUrl,
      };
    } catch (error) {
      console.error('Google Drive 上传失败:', error.message);
      return { success: false, error: error.message };
    }
  }
}

// ============ TikTok 下载器 ============

async function downloadTikTokVideo(videoUrl) {
  console.log('📥 开始下载 TikTok 视频...');
  console.log('   URL:', videoUrl);
  console.log('   Headless:', CONFIG.HEADLESS);

  const browser = await chromium.launch({
    headless: CONFIG.HEADLESS,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
    ]
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();
  const videoData = [];
  let firstValidVideo = null;

  // 从 URL 提取视频 ID
  const videoIdMatch = videoUrl.match(/video\/(\d+)/);
  const targetVideoId = videoIdMatch ? videoIdMatch[1] : null;
  console.log(`   目标视频 ID: ${targetVideoId || '未知'}`);

  // 捕获视频 URL
  page.on('response', async (response) => {
    const url = response.url();
    if (url.includes('/video/tos/') &&
        (url.includes('v16-webapp') || url.includes('v19-webapp') || url.includes('v77-webapp'))) {
      const contentLength = parseInt(response.headers()['content-length'] || '0');
      if (contentLength > 500000) {
        console.log(`   📹 捕获视频: ${(contentLength / 1024 / 1024).toFixed(2)} MB`);
        videoData.push({ url, size: contentLength });
        // 记录第一个捕获的有效视频（通常是主视频）
        if (!firstValidVideo) {
          firstValidVideo = { url, size: contentLength };
          console.log(`   📍 标记为主视频候选`);
        }
      }
    }
  });

  let result = { success: false, path: null };

  try {
    // 规范化 URL
    const normalizedUrl = new URL(videoUrl);
    const cleanUrl = `${normalizedUrl.origin}${normalizedUrl.pathname}`;

    console.log('   1. 访问页面...');
    await page.goto(cleanUrl, {
      waitUntil: 'domcontentloaded',
      timeout: 30000
    });

    // 只等待 5 秒，减少捕获其他视频的机会
    console.log('   2. 等待主视频加载...');
    await page.waitForTimeout(5000);

    console.log(`   3. 捕获到 ${videoData.length} 个视频 URL`);

    if (videoData.length > 0) {
      // 使用第一个捕获的视频（主视频）而不是最大的
      const bestVideo = firstValidVideo || videoData[0];
      console.log(`   选择视频: ${(bestVideo.size / 1024 / 1024).toFixed(2)} MB (第一个捕获)`);

      console.log('   4. 下载主视频...');
      const response = await context.request.get(bestVideo.url, {
        headers: {
          'Referer': 'https://www.tiktok.com/',
          'Origin': 'https://www.tiktok.com'
        }
      });

      if (response.ok()) {
        const buffer = await response.body();
        const videoPath = path.join(CONFIG.TEMP_DIR, `${Date.now()}.mp4`);
        fs.writeFileSync(videoPath, buffer);

        console.log(`   ✅ 下载成功: ${(buffer.length / 1024 / 1024).toFixed(2)} MB`);
        result = { success: true, path: videoPath };
      }
    } else {
      console.log('   ❌ 未捕获到视频 URL');
    }
  } catch (error) {
    console.error('   ❌ 下载错误:', error.message);
  } finally {
    await browser.close();
  }

  return result;
}

// ============ Gemini 分析 ============

async function analyzeVideo(videoPath) {
  const { GoogleGenAI } = require('@google/genai');

  console.log('📊 开始 Gemini 分析...');

  const videoData = fs.readFileSync(videoPath);
  const base64Video = videoData.toString('base64');
  const fileSizeMB = videoData.length / (1024 * 1024);

  console.log(`   视频大小: ${fileSizeMB.toFixed(2)} MB`);

  const ai = new GoogleGenAI({ apiKey: CONFIG.GEMINI_API_KEY });

  // 带重试的调用
  for (let attempt = 1; attempt <= 3; attempt++) {
    try {
      const response = await ai.models.generateContent({
        model: 'gemini-2.5-flash',
        contents: [
          { inlineData: { mimeType: 'video/mp4', data: base64Video } },
          { text: ANALYSIS_PROMPT }
        ]
      });

      // 解析 JSON
      let text = response.text;
      const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
      if (jsonMatch) {
        text = jsonMatch[1].trim();
      }

      return JSON.parse(text);
    } catch (error) {
      console.log(`   ⚠️ 尝试 ${attempt}/3 失败: ${error.message}`);
      if (attempt < 3) {
        await new Promise(r => setTimeout(r, 2000 * attempt));
      } else {
        throw error;
      }
    }
  }
}

// ============ 消息格式化 ============

function formatAnalysisCard(analysis, sourceUrl) {
  const basicInfo = analysis.basic_info || {};
  const scores = analysis.overall_assessment?.success_score || {};
  const viral = analysis.overall_assessment?.viral_factors || {};
  const transcript = analysis.full_transcript || {};
  const product = analysis.product_analysis?.product_info || {};
  const replication = analysis.replication_guide || {};

  // 截取口播稿摘要（前200字）
  const transcriptPreview = (transcript.original || '').slice(0, 200);
  const hasMoreTranscript = (transcript.original || '').length > 200;

  return {
    config: { wide_screen_mode: true },
    header: {
      title: { tag: 'plain_text', content: '📊 视频深度分析完成' },
      template: 'blue',
    },
    elements: [
      // 基础信息
      {
        tag: 'div',
        fields: [
          { is_short: true, text: { tag: 'lark_md', content: `**时长**: ${basicInfo.duration || 'N/A'}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**类型**: ${basicInfo.video_type || 'N/A'}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**产品**: ${product.name || 'N/A'}` } },
          { is_short: true, text: { tag: 'lark_md', content: `**评分**: ${scores.overall_score || 'N/A'}/10` } },
        ],
      },
      { tag: 'hr' },
      // 口播稿摘要
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**📝 口播稿**\n${transcriptPreview}${hasMoreTranscript ? '...' : ''}\n\n*完整口播稿请查看多维表格*`,
        },
      },
      { tag: 'hr' },
      // 核心卖点
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**💡 核心卖点**\n${analysis.product_analysis?.selling_points_system?.core_usp || 'N/A'}`,
        },
      },
      { tag: 'hr' },
      // 爆款原因
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**🔥 爆款原因**\n${viral.primary_reason || '分析中...'}`,
        },
      },
      // 关键学习点
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**📚 关键学习点**\n${(analysis.overall_assessment?.key_learnings || []).map(l => `• ${l}`).join('\n')}`,
        },
      },
      { tag: 'hr' },
      // AI 复刻提示词预览
      {
        tag: 'div',
        text: {
          tag: 'lark_md',
          content: `**🤖 AI视频提示词**\n${(replication.ai_video_prompts?.seedance_prompt_cn || '').slice(0, 150)}${(replication.ai_video_prompts?.seedance_prompt_cn || '').length > 150 ? '...' : ''}\n\n*完整提示词请查看多维表格*`,
        },
      },
      { tag: 'hr' },
      // 按钮
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

function formatBitableRecord(analysis, sourceUrl, platform, videoFileUrl = null) {
  const basicInfo = analysis.basic_info || {};
  const scores = analysis.overall_assessment?.success_score || {};
  const product = analysis.product_analysis?.product_info || {};
  const viral = analysis.overall_assessment?.viral_factors || {};
  const transcript = analysis.full_transcript || {};
  const storyboard = analysis.storyboard || [];
  const replication = analysis.replication_guide || {};

  // 格式化分镜脚本为文本
  const storyboardText = storyboard.map(s =>
    `【${s.name}】${s.time_range || ''}\n${s.script || ''}\n画面：${s.visual_description || ''}`
  ).join('\n\n');

  // 格式化学习点
  const learnings = analysis.overall_assessment?.key_learnings || [];
  const learningsText = learnings.map((l, i) => `${i + 1}. ${l}`).join('\n');

  const record = {
    '视频链接': { link: sourceUrl, text: '查看视频' },
    '平台': platform === 'tiktok' ? 'TikTok' : '其他',
    '分析时间': Date.now(),
    '视频时长': basicInfo.duration || '',
    '类型': basicInfo.video_type || '',
    '产品': product.name || '',
    '综合评分': parseInt(scores.overall_score) || 0,
    '核心卖点': analysis.product_analysis?.selling_points_system?.core_usp || '',
    '爆款原因': viral.primary_reason || '',
    // 新增字段
    '口播稿原文': transcript.original || '',
    '口播稿中文': transcript.chinese || '',
    '分镜脚本': storyboardText || '',
    '关键学习点': learningsText || '',
    '脚本模板': replication.script_template || '',
    'AI视频提示词': replication.ai_video_prompts?.seedance_prompt_cn || '',
  };

  // 如果有视频文件链接，添加到记录
  if (videoFileUrl) {
    record['视频文件'] = { link: videoFileUrl, text: '下载视频' };
  }

  return record;
}

// ============ Express 服务器 ============

const app = express();
app.use(express.json());

const lark = new LarkClient(CONFIG.FEISHU_APP_ID, CONFIG.FEISHU_APP_SECRET, CONFIG.LARK_API_BASE);
const googleDrive = new GoogleDriveUploader();

// 健康检查
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    timestamp: new Date().toISOString(),
    config: {
      headless: CONFIG.HEADLESS,
      tempDir: CONFIG.TEMP_DIR,
    }
  });
});

// Lark Webhook
app.post('/webhook/feishu', async (req, res) => {
  const body = req.body;
  console.log('收到 Webhook:', JSON.stringify(body, null, 2));

  // URL 验证
  if (body.type === 'url_verification') {
    return res.json({ challenge: body.challenge });
  }

  // Token 验证
  const token = body.token || body.header?.token;
  if (CONFIG.FEISHU_VERIFICATION_TOKEN && token !== CONFIG.FEISHU_VERIFICATION_TOKEN) {
    console.error('Token 验证失败');
    return res.status(401).json({ error: 'Invalid token' });
  }

  const event = body.event;
  if (!event) {
    return res.json({ ok: true });
  }

  // 立即返回
  res.json({ ok: true });

  // 异步处理
  const messageType = event.message?.message_type;
  if (messageType === 'text') {
    processMessage(event).catch(console.error);
  }
});

// 处理消息
async function processMessage(event) {
  const message = event.message;
  const messageId = message.message_id;

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
    await lark.replyMessage(messageId, JSON.stringify({ text: '请发送 TikTok 视频链接' }));
    return;
  }

  const url = urlMatch[0];

  // 检测平台
  let platform = 'unknown';
  try {
    const parsed = new URL(url);
    for (const [domain, p] of Object.entries(CONFIG.SUPPORTED_PLATFORMS)) {
      if (parsed.hostname.includes(domain)) {
        platform = p;
        break;
      }
    }
  } catch {}

  if (platform === 'unknown') {
    await lark.replyMessage(messageId, JSON.stringify({ text: '目前只支持 TikTok 链接' }));
    return;
  }

  // 回复处理中
  await lark.replyMessage(messageId, JSON.stringify({ text: '⏳ 正在下载并分析视频，请稍候...' }));

  try {
    // 1. 下载
    console.log('开始下载...');
    const downloadResult = await downloadTikTokVideo(url);
    if (!downloadResult.success) {
      throw new Error('下载失败');
    }

    // 2. 分析
    console.log('开始分析...');
    const analysis = await analyzeVideo(downloadResult.path);
    if (!analysis) {
      throw new Error('分析失败');
    }

    // 3. 发送群消息
    if (CONFIG.FEISHU_GROUP_CHAT_ID) {
      const card = formatAnalysisCard(analysis, url);
      const msgResult = await lark.sendGroupMessage(CONFIG.FEISHU_GROUP_CHAT_ID, card);
      console.log('群消息 API 响应:', JSON.stringify(msgResult, null, 2));
      if (msgResult.code !== 0) {
        console.error('群消息发送失败:', msgResult.msg);
      } else {
        console.log('群消息已发送');
      }
    }

    // 4. 上传视频到 Google Drive
    let videoFileUrl = null;
    try {
      const videoId = url.match(/video\/(\d+)/)?.[1] || Date.now();
      const fileName = `tiktok_${videoId}.mp4`;
      const uploadResult = await googleDrive.uploadFile(downloadResult.path, fileName);
      if (uploadResult.success) {
        videoFileUrl = uploadResult.shareUrl;
        console.log('视频上传成功:', videoFileUrl);
      } else {
        console.log('视频上传跳过:', uploadResult.error);
      }
    } catch (uploadError) {
      console.error('视频上传异常:', uploadError.message);
    }

    // 5. 写入多维表格
    if (CONFIG.FEISHU_BITABLE_APP_TOKEN && CONFIG.FEISHU_BITABLE_TABLE_ID) {
      const record = formatBitableRecord(analysis, url, platform, videoFileUrl);
      console.log('写入多维表格，字段:', JSON.stringify(record, null, 2));
      const bitableResult = await lark.createBitableRecord(
        CONFIG.FEISHU_BITABLE_APP_TOKEN,
        CONFIG.FEISHU_BITABLE_TABLE_ID,
        record
      );
      console.log('多维表格 API 响应:', JSON.stringify(bitableResult, null, 2));
      if (bitableResult.code !== 0) {
        console.error('多维表格写入失败:', bitableResult.msg);
      } else {
        console.log('多维表格已写入');
      }
    }

    // 6. 回复完成
    const replyText = videoFileUrl
      ? '✅ 分析完成！结果已发送到群里，视频和数据已保存到表格。'
      : '✅ 分析完成！结果已发送到群里并保存到表格。';
    await lark.replyMessage(messageId, JSON.stringify({ text: replyText }));

    // 7. 清理本地文件
    try {
      fs.unlinkSync(downloadResult.path);
    } catch {}

  } catch (error) {
    console.error('处理失败:', error);
    await lark.replyMessage(messageId, JSON.stringify({ text: `❌ 处理失败: ${error.message}` }));
  }
}

// 启动服务器
app.listen(CONFIG.PORT, '0.0.0.0', () => {
  console.log(`
╔════════════════════════════════════════════════════════╗
║     Short Video Analyzer - Cloud Edition               ║
╠════════════════════════════════════════════════════════╣
║  端口: ${CONFIG.PORT}                                          ║
║  Webhook: /webhook/feishu                              ║
║  健康检查: /health                                     ║
╚════════════════════════════════════════════════════════╝
  `);
});
