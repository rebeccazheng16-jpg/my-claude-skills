#!/usr/bin/env node
/**
 * Short Video Pipeline - 短视频全链路自动化
 *
 * 功能：下载 → 分析 → 切片 → 归档
 *
 * 使用方式：
 *   video-pipeline <视频链接或本地路径> [选项]
 *
 * 选项：
 *   --analyze     仅分析，不切片（默认）
 *   --atomize     分析后切片归档
 *   --sync-lark   同步到飞书多维表格
 *   --output-dir  指定输出目录
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');

// ============ 配置 ============

const CONFIG = {
  SKILLS_DIR: path.join(process.env.HOME, '.claude/skills'),
  OUTPUT_DIR: path.join(process.env.HOME, 'VideoAnalysis'),
  SUPPORTED_PLATFORMS: {
    'tiktok.com': 'tiktok',
    'vm.tiktok.com': 'tiktok',
    'xiaohongshu.com': 'xiaohongshu',
    'xhslink.com': 'xiaohongshu',
  }
};

// ============ 工具函数 ============

function log(emoji, message) {
  console.log(`${emoji} ${message}`);
}

function detectPlatform(input) {
  // 本地文件
  if (fs.existsSync(input)) {
    return { type: 'local', path: input };
  }

  // URL
  try {
    const url = new URL(input);
    for (const [domain, platform] of Object.entries(CONFIG.SUPPORTED_PLATFORMS)) {
      if (url.hostname.includes(domain)) {
        return { type: platform, url: input };
      }
    }
    return { type: 'unknown', url: input };
  } catch {
    return { type: 'invalid', input };
  }
}

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
  return dir;
}

// ============ 下载模块 ============

async function downloadVideo(source) {
  log('📥', `下载视频 (${source.type})...`);

  let downloadScript;
  let args;

  switch (source.type) {
    case 'tiktok':
      downloadScript = path.join(CONFIG.SKILLS_DIR, 'tiktok-downloader/scripts/download.js');
      args = [source.url];
      break;

    case 'xiaohongshu':
      downloadScript = path.join(CONFIG.SKILLS_DIR, 'xhs-video-downloader/scripts/download.js');
      args = [source.url];
      break;

    case 'local':
      log('✅', `使用本地文件: ${source.path}`);
      return { success: true, filepath: source.path };

    default:
      log('❌', `不支持的平台: ${source.type}`);
      return { success: false };
  }

  // 检查脚本是否存在
  if (!fs.existsSync(downloadScript)) {
    log('❌', `下载脚本不存在: ${downloadScript}`);
    log('💡', `请先安装对应的下载器 skill`);
    return { success: false };
  }

  try {
    const result = execSync(`node "${downloadScript}" "${source.url}"`, {
      encoding: 'utf-8',
      stdio: ['pipe', 'pipe', 'pipe']
    });

    // 从输出中提取文件路径
    const fileMatch = result.match(/文件: (.+\.mp4)/);
    if (fileMatch) {
      const filepath = fileMatch[1];
      log('✅', `下载完成: ${filepath}`);
      return { success: true, filepath };
    }

    log('⚠️', '下载完成但未找到文件路径');
    return { success: false };

  } catch (error) {
    log('❌', `下载失败: ${error.message}`);
    return { success: false };
  }
}

// ============ 分析模块 ============

async function analyzeVideo(videoPath) {
  log('🔍', '分析视频内容...');

  const analyzeScript = path.join(CONFIG.SKILLS_DIR, 'short-video-analyzer/scripts/analyze.js');

  if (!fs.existsSync(analyzeScript)) {
    log('❌', '分析脚本不存在');
    return { success: false };
  }

  try {
    // 动态导入分析模块
    const { analyzeVideo: analyze } = require(analyzeScript);
    const analysis = await analyze(videoPath);

    if (analysis) {
      // 保存分析结果
      const analysisPath = videoPath.replace('.mp4', '_analysis.json');
      fs.writeFileSync(analysisPath, JSON.stringify(analysis, null, 2), 'utf-8');

      log('✅', `分析完成: ${analysisPath}`);
      return { success: true, analysis, analysisPath };
    }

    return { success: false };

  } catch (error) {
    log('❌', `分析失败: ${error.message}`);
    return { success: false };
  }
}

// ============ 切片模块 ============

async function atomizeVideo(videoPath, analysis) {
  log('✂️', '切片视频...');

  // TODO: 集成 video-content-atomizer
  log('⚠️', '切片功能开发中...');

  return { success: false, message: 'Not implemented' };
}

// ============ 同步模块 ============

async function syncToLark(analysisPath) {
  log('📤', '同步到飞书...');

  const syncScript = path.join(CONFIG.SKILLS_DIR, 'feishu-developer/scripts/sync_to_bitable.py');

  if (!fs.existsSync(syncScript)) {
    log('⚠️', '飞书同步脚本不存在，跳过');
    return { success: false };
  }

  try {
    execSync(`python3 "${syncScript}" "${analysisPath}"`, {
      encoding: 'utf-8',
      stdio: 'inherit'
    });

    log('✅', '同步完成');
    return { success: true };

  } catch (error) {
    log('❌', `同步失败: ${error.message}`);
    return { success: false };
  }
}

// ============ 报告生成 ============

function generateReport(analysis, outputDir) {
  if (!analysis) return;

  const reportPath = path.join(outputDir, 'report.md');

  let report = `# 视频分析报告\n\n`;
  report += `生成时间: ${new Date().toLocaleString()}\n\n`;

  // 基础信息
  if (analysis.basic_info) {
    report += `## 基础信息\n\n`;
    report += `- **时长**: ${analysis.basic_info.duration || 'N/A'}\n`;
    report += `- **类型**: ${analysis.basic_info.video_type || 'N/A'}\n`;

    if (analysis.basic_info.title_suggestion) {
      report += `\n### 标题建议\n\n`;
      const titles = Array.isArray(analysis.basic_info.title_suggestion)
        ? analysis.basic_info.title_suggestion
        : [analysis.basic_info.title_suggestion];
      titles.forEach((t, i) => {
        report += `${i + 1}. ${t}\n`;
      });
    }
  }

  // 口播稿
  if (analysis.full_transcript) {
    report += `\n## 完整口播稿\n\n`;
    if (analysis.full_transcript.original) {
      report += `### 原文\n\n${analysis.full_transcript.original}\n\n`;
    }
    if (analysis.full_transcript.chinese) {
      report += `### 中文翻译\n\n${analysis.full_transcript.chinese}\n\n`;
    }
  }

  // 分镜
  if (analysis.storyboard && analysis.storyboard.length > 0) {
    report += `\n## 分镜脚本\n\n`;
    report += `| 段落 | 时间 | 景别 | 内容 |\n`;
    report += `|------|------|------|------|\n`;
    analysis.storyboard.forEach(seg => {
      const script = seg.script_chinese || seg.script || '';
      const shortScript = script.length > 30 ? script.substring(0, 30) + '...' : script;
      report += `| ${seg.name} | ${seg.time_range} | ${seg.shot_type || 'N/A'} | ${shortScript} |\n`;
    });
  }

  // 评分
  if (analysis.overall_assessment?.success_score) {
    report += `\n## 评分\n\n`;
    const scores = analysis.overall_assessment.success_score;
    report += `| 维度 | 分数 |\n`;
    report += `|------|------|\n`;
    if (scores.hook_score) report += `| 开场 | ${scores.hook_score}/10 |\n`;
    if (scores.content_score) report += `| 内容 | ${scores.content_score}/10 |\n`;
    if (scores.production_score) report += `| 制作 | ${scores.production_score}/10 |\n`;
    if (scores.overall_score) report += `| **综合** | **${scores.overall_score}/10** |\n`;
  }

  // 爆款分析
  if (analysis.overall_assessment?.viral_factors) {
    report += `\n## 爆款分析\n\n`;
    const vf = analysis.overall_assessment.viral_factors;
    if (vf.primary_reason) {
      report += `**核心原因**: ${vf.primary_reason}\n\n`;
    }
    if (vf.detailed_analysis) {
      report += `${vf.detailed_analysis}\n\n`;
    }
  }

  // 关键学习点
  if (analysis.overall_assessment?.key_learnings) {
    report += `\n## 关键学习点\n\n`;
    analysis.overall_assessment.key_learnings.forEach((point, i) => {
      report += `${i + 1}. ${point}\n`;
    });
  }

  fs.writeFileSync(reportPath, report, 'utf-8');
  log('📄', `Markdown 报告: ${reportPath}`);

  return reportPath;
}

// ============ 主流程 ============

async function runPipeline(input, options = {}) {
  console.log('\n' + '='.repeat(60));
  console.log('🎬 Short Video Pipeline - 短视频全链路分析');
  console.log('='.repeat(60) + '\n');

  const startTime = Date.now();

  // 1. 检测输入类型
  const source = detectPlatform(input);
  log('🔍', `输入类型: ${source.type}`);

  if (source.type === 'invalid') {
    log('❌', '无效的输入');
    process.exit(1);
  }

  // 2. 下载视频（如果是链接）
  let videoPath;
  if (source.type === 'local') {
    videoPath = source.path;
  } else {
    const downloadResult = await downloadVideo(source);
    if (!downloadResult.success) {
      log('❌', '下载失败，流程终止');
      process.exit(1);
    }
    videoPath = downloadResult.filepath;
  }

  // 3. 分析视频
  const analyzeResult = await analyzeVideo(videoPath);
  if (!analyzeResult.success) {
    log('❌', '分析失败，流程终止');
    process.exit(1);
  }

  // 4. 生成 Markdown 报告
  const outputDir = options.outputDir || path.dirname(videoPath);
  generateReport(analyzeResult.analysis, outputDir);

  // 5. 切片（可选）
  if (options.atomize) {
    await atomizeVideo(videoPath, analyzeResult.analysis);
  }

  // 6. 同步到飞书（可选）
  if (options.syncLark) {
    await syncToLark(analyzeResult.analysisPath);
  }

  // 完成
  const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
  console.log('\n' + '='.repeat(60));
  log('🎉', `流程完成！耗时 ${elapsed} 秒`);
  console.log('='.repeat(60));

  console.log('\n📁 输出文件:');
  console.log(`   视频: ${videoPath}`);
  console.log(`   分析: ${analyzeResult.analysisPath}`);
  console.log(`   报告: ${path.join(outputDir, 'report.md')}`);

  return {
    success: true,
    videoPath,
    analysisPath: analyzeResult.analysisPath,
    analysis: analyzeResult.analysis
  };
}

// ============ CLI 入口 ============

function printUsage() {
  console.log(`
Short Video Pipeline - 短视频全链路自动化

用法:
  node pipeline.js <视频链接或本地路径> [选项]

支持的平台:
  - TikTok (tiktok.com, vm.tiktok.com)
  - 小红书 (xiaohongshu.com, xhslink.com)
  - 本地视频文件 (.mp4)

选项:
  --atomize      分析后切片归档
  --sync-lark    同步到飞书多维表格
  --output-dir   指定输出目录

示例:
  # 分析 TikTok 视频
  node pipeline.js "https://www.tiktok.com/@user/video/123"

  # 分析本地视频
  node pipeline.js ~/Videos/sample.mp4

  # 分析并切片
  node pipeline.js "https://vm.tiktok.com/xxx" --atomize

  # 分析并同步到飞书
  node pipeline.js ~/Videos/sample.mp4 --sync-lark
`);
}

async function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    printUsage();
    process.exit(0);
  }

  // 解析参数
  let input = null;
  const options = {
    atomize: false,
    syncLark: false,
    outputDir: null
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];

    if (arg === '--atomize') {
      options.atomize = true;
    } else if (arg === '--sync-lark') {
      options.syncLark = true;
    } else if (arg === '--output-dir' && args[i + 1]) {
      options.outputDir = args[++i];
    } else if (!arg.startsWith('-')) {
      input = arg;
    }
  }

  if (!input) {
    console.error('错误: 请提供视频链接或本地路径');
    printUsage();
    process.exit(1);
  }

  await runPipeline(input, options);
}

// 导出模块
module.exports = { runPipeline, detectPlatform, CONFIG };

// CLI 模式
if (require.main === module) {
  main().catch(error => {
    console.error('Pipeline 错误:', error.message);
    process.exit(1);
  });
}
