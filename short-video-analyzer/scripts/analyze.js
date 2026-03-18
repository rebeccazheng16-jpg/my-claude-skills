#!/usr/bin/env node
/**
 * TikTok Video Analyzer
 * 使用 Gemini 2.5 Flash 全面分析短视频内容
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// ============ 完整分析提示词 ============

const ANALYSIS_PROMPT = `# 短视频深度分析报告

你是一位专业的短视频内容分析师，精通内容策略、视频制作、产品营销和数据运营。请仔细观看这个视频，进行全方位深度分析。

## 核心要求
1. **口播文案必须完整逐字提取**，用「」包裹原文，不要省略
2. 如果视频是外语，同时提供原文和中文翻译
3. 所有分析要具体、可执行，避免泛泛而谈
4. 时间精确到秒

## 输出 JSON 格式

{
  "basic_info": {
    "title_suggestion": "为这个视频起3个吸引人的标题",
    "duration": "视频总时长",
    "video_type": "视频类型（带货/种草/教程/娱乐/剧情/vlog/测评）",
    "content_theme": "内容主题概述",
    "target_audience": {
      "demographics": "人口统计（年龄、性别、地域）",
      "psychographics": "心理特征（兴趣、需求、痛点）",
      "consumption_scenario": "消费场景"
    }
  },

  "full_transcript": {
    "original": "完整口播稿原文（逐字记录，包括语气词、停顿）",
    "chinese": "中文翻译（如果原文非中文）",
    "language": "原视频语言",
    "word_count": "字数统计",
    "speaking_rate": "语速（字/分钟）"
  },

  "storyboard": [
    {
      "segment": 1,
      "name": "Hook（开场钩子）",
      "time_range": "0:00 - 0:XX",
      "duration_seconds": "本段时长（秒）",
      "shot_type": "景别（特写/中近景/中景/全景/多景别切换）",
      "camera_angle": "机位角度（平视/俯拍/仰拍/侧面）",
      "camera_movement": "运镜（固定/推/拉/摇/移/跟/手持晃动）",
      "script": "「完整口播文案原文」",
      "script_chinese": "「中文翻译」",
      "visual_description": "详细画面描述：人物表情、动作、手势、产品位置、背景环境、道具",
      "text_overlay": "画面文字/字幕内容",
      "tone_and_pace": {
        "speed": "语速（快/中/慢）",
        "emotion": "情绪（兴奋/惊讶/平静/急切/真诚/幽默）",
        "volume": "音量变化"
      },
      "hook_type": "Hook类型（问题式/惊喜式/数字式/对比式/痛点式/悬念式/反转式）",
      "hook_technique": "Hook技巧分析：为什么能在3秒内抓住注意力",
      "retention_prediction": "本段留存预测（高/中/低）及原因"
    },
    {
      "segment": 2,
      "name": "Pain Point（痛点共鸣）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "tone_and_pace": {},
      "pain_point_analysis": {
        "pain_points_mentioned": ["痛点1", "痛点2"],
        "resonance_technique": "共鸣技巧：如何让观众产生'说的就是我'的感觉",
        "emotion_triggered": "触发的情绪（焦虑/不满/渴望/认同）"
      }
    },
    {
      "segment": 3,
      "name": "Product Intro（产品介绍）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "product_presentation": {
        "reveal_method": "产品出场方式（直接展示/悬念揭晓/对比引出）",
        "display_technique": "展示技巧（手持/特写/使用中/包装展示）",
        "first_impression": "产品第一印象设计"
      }
    },
    {
      "segment": 4,
      "name": "Selling Points（卖点展示）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "selling_points_breakdown": [
        {
          "claim": "卖点宣称",
          "proof_method": "证明方式（演示/对比/数据/证言）",
          "visual_proof": "视觉化呈现方式"
        }
      ]
    },
    {
      "segment": 5,
      "name": "Demonstration（使用演示）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "demo_analysis": {
        "demo_steps": ["步骤1", "步骤2", "步骤3"],
        "demo_highlights": "演示亮点",
        "believability": "可信度设计"
      }
    },
    {
      "segment": 6,
      "name": "Benefits（效果利益）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "benefits_analysis": {
        "functional_benefits": ["功能利益"],
        "emotional_benefits": ["情感利益"],
        "social_benefits": ["社交利益"],
        "effect_visualization": "效果可视化方式"
      }
    },
    {
      "segment": 7,
      "name": "CTA（行动号召）",
      "time_range": "",
      "duration_seconds": "",
      "shot_type": "",
      "camera_angle": "",
      "camera_movement": "",
      "script": "「完整口播文案」",
      "script_chinese": "",
      "visual_description": "",
      "text_overlay": "",
      "cta_analysis": {
        "cta_type": "CTA类型（购买/关注/评论/收藏/私信）",
        "cta_strength": "强度（软性引导/中等推动/强势逼单）",
        "urgency_tactics": ["紧迫感策略"],
        "incentive_offered": "提供的激励（优惠/赠品/福利）"
      }
    }
  ],

  "product_analysis": {
    "product_info": {
      "name": "产品名称",
      "brand": "品牌",
      "category": "品类",
      "price_mentioned": "提及的价格",
      "price_anchor": "价格锚点（原价vs现价）",
      "positioning": "产品定位（高端/中端/性价比）"
    },
    "selling_points_system": {
      "core_usp": "核心差异化卖点（一句话）",
      "functional_points": ["功能卖点1", "功能卖点2"],
      "emotional_points": ["情感卖点1", "情感卖点2"],
      "visual_proofs": [
        {
          "point": "卖点",
          "proof_type": "证明类型（对比/演示/数据/权威）",
          "timestamp": "出现时间",
          "effectiveness": "有效性评估"
        }
      ],
      "points_presentation_order": "卖点呈现顺序及逻辑"
    },
    "benefits_matrix": {
      "functional": "功能利益：产品能做什么",
      "emotional": "情感利益：用户感受如何",
      "social": "社交利益：他人如何看待",
      "economic": "经济利益：省钱/划算/值得",
      "time": "时间利益：省时/方便/高效"
    },
    "trust_building": {
      "brand_authority": "品牌背书",
      "creator_credibility": "达人可信度塑造",
      "social_proof": "社会认同（销量/评价/回购）",
      "expert_endorsement": "专家/权威背书",
      "risk_reversal": "风险消除（退换/保障/试用）"
    },
    "cta_strategy": {
      "primary_cta": "主要行动号召",
      "cta_timing": "CTA出现时机",
      "cta_script": "「CTA具体话术」",
      "urgency_elements": {
        "time_limit": "限时策略",
        "quantity_limit": "限量策略",
        "price_limit": "限价策略",
        "bonus_limit": "赠品策略"
      },
      "friction_reduction": "降低行动摩擦的设计"
    },
    "persuasion_techniques": ["说服技巧1", "说服技巧2", "说服技巧3"]
  },

  "audio_analysis": {
    "bgm": {
      "music_type": "音乐类型（流行/电子/古典/民谣/无BGM）",
      "music_mood": "音乐情绪（欢快/激昂/温馨/紧张/治愈）",
      "tempo": "节奏（快/中/慢，估算BPM）",
      "volume_level": "音量层级（背景/中等/突出）",
      "music_function": "音乐功能（烘托氛围/卡点/情绪引导）"
    },
    "sound_effects": {
      "effects_used": ["音效1", "音效2"],
      "effect_timing": "音效出现时机",
      "effect_purpose": "音效作用"
    },
    "voice_analysis": {
      "voice_character": "声音特质（温柔/有力/亲切/专业）",
      "speaking_style": "说话风格",
      "pace_variation": "语速变化节奏",
      "emphasis_points": "重音强调位置"
    },
    "audio_video_sync": {
      "beat_matching": "卡点情况",
      "mood_alignment": "音画情绪一致性",
      "transition_audio": "转场音效设计"
    }
  },

  "visual_style_analysis": {
    "shooting_style": {
      "environment": "拍摄环境详细描述",
      "scene_setup": "场景布置",
      "props_used": ["道具1", "道具2"],
      "lighting": {
        "type": "光线类型（自然光/打光/混合）",
        "direction": "光线方向",
        "mood": "光线营造的氛围",
        "quality": "光线质量（柔和/硬朗）"
      }
    },
    "color_analysis": {
      "dominant_colors": ["主色调1", "主色调2"],
      "color_temperature": "色温（暖/冷/中性）",
      "saturation": "饱和度（高/中/低）",
      "color_psychology": "色彩心理学分析：颜色如何影响观众情绪",
      "brand_color_consistency": "品牌色一致性"
    },
    "composition": {
      "framing_style": "构图风格",
      "subject_placement": "主体位置",
      "background_treatment": "背景处理",
      "visual_hierarchy": "视觉层次"
    },
    "editing_style": {
      "cutting_rhythm": "剪辑节奏（快切/慢切/混合）",
      "average_shot_length": "平均镜头时长",
      "transition_types": ["转场类型1", "转场类型2"],
      "text_graphics": {
        "style": "字幕/贴纸风格",
        "animation": "文字动效",
        "placement": "文字位置"
      },
      "effects_filters": "特效/滤镜使用"
    }
  },

  "content_strategy_analysis": {
    "hook_analysis": {
      "hook_duration": "Hook时长（秒）",
      "hook_effectiveness": "Hook有效性评分（1-10）",
      "attention_grabbers": ["抓注意力的元素"],
      "first_3_seconds": "前3秒具体内容及策略"
    },
    "narrative_structure": {
      "story_arc": "叙事弧线",
      "pacing": "节奏把控",
      "tension_points": "张力点设计",
      "climax_moment": "高潮时刻"
    },
    "engagement_triggers": {
      "comment_triggers": "引发评论的设计",
      "share_triggers": "引发分享的设计",
      "save_triggers": "引发收藏的设计",
      "follow_triggers": "引发关注的设计"
    },
    "voiceover_style": {
      "persona": "人设定位（闺蜜/专家/搞笑/真诚分享者）",
      "language_features": "语言特点（用词、口头禅、句式）",
      "catchphrases": ["金句/口头禅"],
      "emotion_curve": "情绪曲线（开场→发展→高潮→收尾）"
    }
  },

  "performance_prediction": {
    "completion_rate": {
      "prediction": "完播率预测（高>60%/中40-60%/低<40%）",
      "factors": "影响因素分析",
      "drop_off_risks": ["可能的流失点"]
    },
    "engagement_prediction": {
      "like_potential": "点赞潜力及原因",
      "comment_potential": "评论潜力及原因",
      "share_potential": "分享潜力及原因",
      "save_potential": "收藏潜力及原因"
    },
    "conversion_prediction": {
      "click_through_potential": "点击率潜力",
      "purchase_intent_trigger": "购买意向触发点"
    },
    "platform_fit": {
      "tiktok": "TikTok适配度及建议",
      "douyin": "抖音适配度及建议",
      "xiaohongshu": "小红书适配度及建议",
      "kuaishou": "快手适配度及建议"
    }
  },

  "operation_suggestions": {
    "title_suggestions": [
      "标题建议1（带数字）",
      "标题建议2（带疑问）",
      "标题建议3（带痛点）"
    ],
    "cover_frame": {
      "recommended_timestamp": "推荐封面时间点",
      "cover_elements": "封面应包含的元素",
      "text_overlay_suggestion": "封面文字建议"
    },
    "hashtag_suggestions": {
      "primary_tags": ["核心标签"],
      "trending_tags": ["热门标签"],
      "niche_tags": ["垂直标签"]
    },
    "posting_strategy": {
      "best_time": "最佳发布时间",
      "frequency": "发布频率建议",
      "series_potential": "系列化潜力"
    },
    "comment_section_strategy": {
      "pinned_comment": "置顶评论建议",
      "engagement_questions": ["引导互动的问题"]
    }
  },

  "replication_guide": {
    "difficulty_assessment": {
      "overall_difficulty": "整体难度（简单/中等/困难）",
      "skill_requirements": ["所需技能"],
      "equipment_needed": ["所需设备"],
      "budget_estimate": "预算估算"
    },
    "essential_elements": {
      "must_have": ["必须保留的核心元素"],
      "can_adapt": ["可以调整的元素"],
      "avoid": ["应该避免的做法"]
    },
    "step_by_step_guide": [
      "复刻步骤1",
      "复刻步骤2",
      "复刻步骤3"
    ],
    "ai_video_prompts": {
      "seedance_prompt_cn": "Seedance中文提示词",
      "seedance_prompt_en": "Seedance English prompt",
      "scene_by_scene": [
        {
          "scene": "场景描述",
          "prompt": "该场景的AI生成提示词"
        }
      ],
      "b_roll_suggestions": ["B-Roll素材建议"]
    },
    "variation_ideas": ["变体创意1", "变体创意2"]
  },

  "overall_assessment": {
    "strengths": ["优势1", "优势2", "优势3"],
    "weaknesses": ["不足1", "不足2"],
    "viral_factors": {
      "primary_reason": "核心爆款原因（一句话）",
      "detailed_analysis": "爆款原因详细分析（100字以上）",
      "replicable_elements": ["可复制的爆款元素"]
    },
    "success_score": {
      "hook_score": "开场分数（1-10）",
      "content_score": "内容分数（1-10）",
      "production_score": "制作分数（1-10）",
      "conversion_score": "转化分数（1-10）",
      "overall_score": "综合分数（1-10）"
    },
    "key_learnings": ["关键学习点1", "关键学习点2", "关键学习点3"]
  }
}

## 重要提醒
1. script 字段最重要，必须完整提取每一句口播，用「」包裹
2. 如果某些分镜合并或不存在，可以调整，但需说明
3. 非带货视频也按此结构分析，product_analysis 可简化
4. 时间要精确，分析要具体可执行
5. 只输出 JSON，不要输出其他内容`;

// ============ Gemini API 调用 ============

// 配置
const GEMINI_CONFIG = {
  MODEL: 'gemini-2.5-flash',           // 升级到 2.5 Flash（2.0 将于 2026.3.31 退役）
  INLINE_THRESHOLD_MB: 100,             // inline 阈值提升到 100MB（官方支持）
  MAX_RETRIES: 3,                       // 最大重试次数
  INITIAL_RETRY_DELAY_MS: 1000,         // 初始重试延迟
};

// 带重试的 API 调用
async function callWithRetry(fn, maxRetries = GEMINI_CONFIG.MAX_RETRIES) {
  let lastError;
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error;
      const isRetryable = error.status === 500 || error.status === 503 ||
                          error.message?.includes('500') || error.message?.includes('503');

      if (!isRetryable || attempt === maxRetries) {
        throw error;
      }

      const delay = GEMINI_CONFIG.INITIAL_RETRY_DELAY_MS * Math.pow(2, attempt - 1);
      console.log(`   ⚠️ 请求失败 (${error.message})，${delay/1000}秒后重试 (${attempt}/${maxRetries})...`);
      await new Promise(resolve => setTimeout(resolve, delay));
    }
  }
  throw lastError;
}

async function analyzeVideoWithGemini(videoPath, apiKey) {
  // 使用新版 SDK: @google/genai
  const { GoogleGenAI } = require('@google/genai');

  console.log('📊 正在进行深度分析（这可能需要1-2分钟）...');
  console.log(`   使用模型: ${GEMINI_CONFIG.MODEL}`);

  // 读取视频文件
  const videoData = fs.readFileSync(videoPath);
  const base64Video = videoData.toString('base64');
  const fileSizeMB = videoData.length / (1024 * 1024);

  console.log(`   视频大小: ${fileSizeMB.toFixed(2)} MB`);

  const ai = new GoogleGenAI({ apiKey });

  // 对于超大文件（>100MB），使用 File API
  if (fileSizeMB > GEMINI_CONFIG.INLINE_THRESHOLD_MB) {
    console.log('   文件较大，使用 File API 上传...');

    return await callWithRetry(async () => {
      // 上传文件
      const uploadResult = await ai.files.upload({
        file: videoPath,
        config: { mimeType: 'video/mp4' }
      });

      // 等待处理完成
      let file = uploadResult;
      let retries = 0;
      while (file.state === 'PROCESSING' && retries < 24) {
        console.log('   等待视频处理...');
        await new Promise(resolve => setTimeout(resolve, 5000));
        file = await ai.files.get({ name: file.name });
        retries++;
      }

      if (file.state === 'FAILED') {
        throw new Error('视频处理失败');
      }

      // 生成内容
      const response = await ai.models.generateContent({
        model: GEMINI_CONFIG.MODEL,
        contents: [
          { fileData: { mimeType: file.mimeType, fileUri: file.uri } },
          { text: ANALYSIS_PROMPT }
        ]
      });

      return parseGeminiResponse(response.text);
    });
  }

  // 对于小文件（≤100MB），使用 inline base64（更稳定，避免 File API 500 错误）
  console.log('   使用 inline 方式发送视频（推荐）...');

  return await callWithRetry(async () => {
    const response = await ai.models.generateContent({
      model: GEMINI_CONFIG.MODEL,
      contents: [
        {
          inlineData: {
            mimeType: 'video/mp4',
            data: base64Video
          }
        },
        { text: ANALYSIS_PROMPT }
      ]
    });

    return parseGeminiResponse(response.text);
  });
}

// 解析 Gemini 响应
function parseGeminiResponse(text) {
  let jsonStr = text;

  // 尝试从 markdown 代码块中提取
  const jsonMatch = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (jsonMatch) {
    jsonStr = jsonMatch[1].trim();
  }

  // 解析 JSON
  try {
    return JSON.parse(jsonStr);
  } catch (e) {
    console.log('⚠️  JSON 解析失败，返回原始文本');
    return { raw_response: text };
  }
}

// ============ 获取 API Key ============

function getGeminiApiKey() {
  // 1. 环境变量
  if (process.env.GEMINI_API_KEY) {
    return process.env.GEMINI_API_KEY;
  }
  if (process.env.GOOGLE_API_KEY) {
    return process.env.GOOGLE_API_KEY;
  }

  // 2. 从 api-keys-manager 获取
  try {
    const result = execSync(
      'python3 ~/.claude/skills/api-keys-manager/scripts/api_keys.py get GOOGLE_AI',
      { encoding: 'utf-8', stdio: ['pipe', 'pipe', 'pipe'] }
    ).trim();
    if (result && !result.includes('not found')) {
      return result;
    }
  } catch (e) {
    // 忽略错误
  }

  return null;
}

// ============ 打印分析摘要 ============

function printSummary(analysis) {
  console.log('\n' + '='.repeat(60));
  console.log('📊 分析报告摘要');
  console.log('='.repeat(60));

  // 基础信息
  if (analysis.basic_info) {
    console.log('\n【基础信息】');
    if (analysis.basic_info.duration) console.log(`  时长: ${analysis.basic_info.duration}`);
    if (analysis.basic_info.video_type) console.log(`  类型: ${analysis.basic_info.video_type}`);
    if (analysis.basic_info.title_suggestion) {
      const titles = Array.isArray(analysis.basic_info.title_suggestion)
        ? analysis.basic_info.title_suggestion
        : [analysis.basic_info.title_suggestion];
      console.log(`  标题建议: ${titles[0]}`);
    }
  }

  // 产品信息
  if (analysis.product_analysis?.product_info) {
    console.log('\n【产品信息】');
    const p = analysis.product_analysis.product_info;
    if (p.name) console.log(`  产品: ${p.name}`);
    if (p.brand) console.log(`  品牌: ${p.brand}`);
    if (analysis.product_analysis.selling_points_system?.core_usp) {
      console.log(`  核心卖点: ${analysis.product_analysis.selling_points_system.core_usp}`);
    }
  }

  // 口播稿
  if (analysis.full_transcript?.original) {
    console.log('\n【口播稿】');
    const transcript = analysis.full_transcript.original;
    console.log(`  ${transcript.substring(0, 100)}...`);
    if (analysis.full_transcript.chinese) {
      console.log(`  [译] ${analysis.full_transcript.chinese.substring(0, 100)}...`);
    }
  }

  // 爆款分析
  if (analysis.overall_assessment?.viral_factors) {
    console.log('\n【爆款分析】');
    if (analysis.overall_assessment.viral_factors.primary_reason) {
      console.log(`  核心原因: ${analysis.overall_assessment.viral_factors.primary_reason}`);
    }
  }

  // 评分
  if (analysis.overall_assessment?.success_score) {
    console.log('\n【评分】');
    const s = analysis.overall_assessment.success_score;
    if (s.overall_score) console.log(`  综合评分: ${s.overall_score}/10`);
    if (s.hook_score) console.log(`  开场: ${s.hook_score}/10 | 内容: ${s.content_score}/10 | 制作: ${s.production_score}/10`);
  }

  // 关键学习点
  if (analysis.overall_assessment?.key_learnings) {
    console.log('\n【关键学习点】');
    analysis.overall_assessment.key_learnings.forEach((point, i) => {
      console.log(`  ${i + 1}. ${point}`);
    });
  }

  console.log('\n' + '='.repeat(60));
}

// ============ 主函数 ============

async function analyzeVideo(videoPath) {
  // 检查文件存在
  if (!fs.existsSync(videoPath)) {
    console.error('❌ 视频文件不存在:', videoPath);
    return null;
  }

  // 获取 API Key
  const apiKey = getGeminiApiKey();
  if (!apiKey) {
    console.error('❌ 未找到 Gemini API Key');
    console.log('   请设置环境变量 GEMINI_API_KEY 或 GOOGLE_API_KEY');
    console.log('   或使用 api-keys-manager 配置 GOOGLE_AI');
    return null;
  }

  console.log('🎬 视频文件:', videoPath);
  console.log('📏 文件大小:', (fs.statSync(videoPath).size / 1024 / 1024).toFixed(2), 'MB');

  try {
    const analysis = await analyzeVideoWithGemini(videoPath, apiKey);
    return analysis;
  } catch (error) {
    console.error('❌ 分析失败:', error.message);
    return null;
  }
}

// ============ CLI 入口 ============

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0) {
    console.log('用法: node analyze.js <视频文件路径>');
    console.log('');
    console.log('示例:');
    console.log('  node analyze.js ~/TikTok-Downloads/user/123456.mp4');
    console.log('');
    console.log('分析内容包括:');
    console.log('  - 完整口播稿（原文+翻译）');
    console.log('  - 分镜脚本（时间+景别+文案+画面）');
    console.log('  - 产品分析（卖点+利益点+CTA）');
    console.log('  - 音频分析（BGM+音效+音画配合）');
    console.log('  - 视觉风格（拍摄+色彩+剪辑）');
    console.log('  - 数据预测（完播率+互动率）');
    console.log('  - 运营建议（标题+封面+标签）');
    console.log('  - 复刻指南（步骤+AI提示词）');
    process.exit(1);
  }

  const videoPath = args[0].replace(/^~/, process.env.HOME);

  const analysis = await analyzeVideo(videoPath);

  if (analysis) {
    // 保存分析结果（修复：使用不区分大小写的替换，避免覆盖原视频）
    const ext = path.extname(videoPath);  // 获取实际扩展名（可能是 .mp4 或 .MP4）
    const outputPath = videoPath.slice(0, -ext.length) + '_analysis.json';
    fs.writeFileSync(outputPath, JSON.stringify(analysis, null, 2), 'utf-8');

    console.log('\n✅ 分析完成!');
    console.log('📄 完整报告:', outputPath);

    // 打印摘要
    printSummary(analysis);
  }
}

// 导出模块
module.exports = { analyzeVideo, ANALYSIS_PROMPT };

// CLI 模式
if (require.main === module) {
  main();
}
