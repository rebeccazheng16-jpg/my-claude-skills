#!/usr/bin/env node
/**
 * TikTok Video Downloader
 * 使用 Playwright 下载 TikTok 视频
 */

const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const os = require('os');

// ============ 配置 ============
const CONFIG = {
  OUTPUT_DIR: path.join(os.homedir(), 'TikTok-Downloads'),
  HEADLESS: false,          // 是否隐藏浏览器
  TIMEOUT: 30000,           // 页面加载超时(ms)
  WAIT_TIME: 10000,         // 等待视频加载时间(ms)
  MIN_VIDEO_SIZE: 500000,   // 最小视频大小(bytes)，过滤小文件
};

// ============ 工具函数 ============

function normalizeUrl(url) {
  // 移除查询参数，保留核心 URL
  try {
    const parsed = new URL(url);
    // 保留 path，去掉多余参数
    return `${parsed.origin}${parsed.pathname}`;
  } catch {
    return url;
  }
}

function sanitizeFilename(name) {
  return name.replace(/[<>:"/\\|?*]/g, '_').substring(0, 100);
}

// ============ 主函数 ============

async function downloadTikTokVideo(videoUrl) {
  const isDouyin = videoUrl.includes('douyin.com');
  const platform = isDouyin ? '抖音' : 'TikTok';
  console.log(`=== ${platform} Video Downloader ===\n`);
  console.log('Target:', videoUrl, '\n');

  // 确保输出目录存在
  if (!fs.existsSync(CONFIG.OUTPUT_DIR)) {
    fs.mkdirSync(CONFIG.OUTPUT_DIR, { recursive: true });
  }

  const browser = await chromium.launch({
    headless: CONFIG.HEADLESS,
    slowMo: 50
  });

  const context = await browser.newContext({
    userAgent: 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    viewport: { width: 1920, height: 1080 }
  });

  const page = await context.newPage();

  // 捕获视频 URL
  const videoData = [];

  page.on('response', async (response) => {
    const url = response.url();

    // 过滤视频内容 URL（同时支持 TikTok 和抖音的 CDN 模式）
    const isTikTokVideo = url.includes('/video/tos/') &&
        (url.includes('v16-webapp') || url.includes('v19-webapp') || url.includes('v77-webapp'));
    const isDouyinVideo = url.includes('/video/tos/') ||
        (url.includes('.douyinvod.com') && url.includes('.mp4')) ||
        (url.includes('v26-web.douyinvod.com')) ||
        (url.includes('.bytevcloudcdn.com') && url.includes('video'));

    if (isTikTokVideo || (isDouyin && isDouyinVideo)) {
      const contentLength = parseInt(response.headers()['content-length'] || '0');

      if (contentLength > CONFIG.MIN_VIDEO_SIZE) {
        console.log(`📹 捕获视频: ${(contentLength / 1024 / 1024).toFixed(2)} MB`);
        videoData.push({
          url: url,
          size: contentLength
        });
      }
    }
  });

  let result = { success: false, filepath: null, metadata: null };

  try {
    // 1. 导航到页面
    console.log('1. 访问 TikTok 页面...');
    await page.goto(normalizeUrl(videoUrl), {
      waitUntil: 'domcontentloaded',
      timeout: CONFIG.TIMEOUT
    });

    // 2. 抖音：关闭登录弹窗
    if (isDouyin) {
      console.log('2. 关闭抖音登录弹窗...')
      await page.waitForTimeout(3000)

      // 方法1: 按 Escape 键关闭
      await page.keyboard.press('Escape')
      await page.waitForTimeout(500)
      await page.keyboard.press('Escape')
      await page.waitForTimeout(500)

      // 方法2: 查找并点击关闭按钮（多种策略）
      const closed = await page.evaluate(() => {
        // 策略A: 查找弹窗内的 × 关闭按钮 (通常在 dialog/modal 内)
        const dialogs = document.querySelectorAll(
          '[class*="modal"], [class*="Modal"], [class*="dialog"], [class*="Dialog"], ' +
          '[class*="login"], [class*="Login"], [class*="semi-portal"]'
        )
        for (const dialog of dialogs) {
          // 查找 dialog 内所有可能的关闭按钮
          const closeEls = dialog.querySelectorAll(
            '[class*="close"], [class*="Close"], [aria-label*="close"], [aria-label*="关闭"]'
          )
          for (const el of closeEls) {
            const rect = el.getBoundingClientRect()
            if (rect.width > 0 && rect.height > 0) {
              el.click()
              return 'dialog-close'
            }
          }
          // 查找 dialog 内的 svg（可能是 × 图标）
          const svgs = dialog.querySelectorAll('svg')
          for (const svg of svgs) {
            const rect = svg.getBoundingClientRect()
            if (rect.width >= 10 && rect.width <= 40 && rect.height >= 10 && rect.height <= 40) {
              const parent = svg.parentElement
              if (parent) {
                parent.click()
                return 'dialog-svg'
              }
            }
          }
        }

        // 策略B: 查找所有 close 相关元素
        const allClose = document.querySelectorAll(
          '[class*="close"], [class*="Close"], [class*="dy-account-close"]'
        )
        for (const el of allClose) {
          const rect = el.getBoundingClientRect()
          if (rect.width > 0 && rect.width < 60 && rect.height > 0 && rect.height < 60 &&
              rect.y > 50 && rect.y < 300) {
            el.click()
            return 'close-selector'
          }
        }
        return null
      })

      if (closed) {
        console.log(`   点击关闭按钮 (${closed})`)
      }

      await page.waitForTimeout(1000)

      // 方法3: 暴力移除弹窗 DOM + 遮罩层（确保清理干净）
      const removed = await page.evaluate(() => {
        let count = 0
        const selectors = [
          '[class*="login-guide"]', '[class*="loginGuide"]',
          '[class*="login-mask"]', '[class*="LoginMask"]',
          '[class*="account-close"]', '[class*="dy-account"]',
          '[class*="modal-mask"]', '[class*="modalMask"]',
          '[class*="semi-modal"]', '[class*="semi-portal"]',
          '[class*="login-panel"]', '[class*="LoginPanel"]',
        ]
        for (const sel of selectors) {
          document.querySelectorAll(sel).forEach(el => {
            el.remove()
            count++
          })
        }
        // 也移除固定定位的遮罩层（z-index 很高的覆盖层）
        document.querySelectorAll('div').forEach(el => {
          const style = window.getComputedStyle(el)
          if (style.position === 'fixed' && parseInt(style.zIndex) > 999 &&
              el.offsetWidth > window.innerWidth * 0.5 &&
              el.offsetHeight > window.innerHeight * 0.5) {
            el.remove()
            count++
          }
        })
        // 恢复 body 滚动
        document.body.style.overflow = ''
        document.documentElement.style.overflow = ''
        return count
      })
      console.log(`   DOM 清理: 移除 ${removed} 个元素`)

      await page.waitForTimeout(1000)

      // 点击视频区域触发播放
      try {
        const video = await page.$('video')
        if (video) {
          await video.click().catch(() => {})
        } else {
          await page.mouse.click(400, 400)
        }
      } catch {}

      await page.waitForTimeout(2000)
    }

    // 3. 等待视频加载
    console.log(`${isDouyin ? '3' : '2'}. 等待视频加载...`)
    await page.waitForTimeout(CONFIG.WAIT_TIME);

    // 4. 提取视频信息
    console.log(`${isDouyin ? '4' : '3'}. 提取视频信息...`);
    const videoInfo = await page.evaluate((isDouyinPage) => {
      // 抖音：尝试 RENDER_DATA 或 __RENDER_DATA__
      if (isDouyinPage) {
        try {
          const renderDataEl = document.getElementById('RENDER_DATA');
          if (renderDataEl) {
            const data = JSON.parse(decodeURIComponent(renderDataEl.textContent));
            const videoDetail = data?.app?.videoDetail || data?.['/video/:id']?.videoDetail || {};
            if (videoDetail.vid || videoDetail.awemeId) {
              return {
                id: videoDetail.awemeId || videoDetail.vid || Date.now().toString(),
                desc: videoDetail.desc || '',
                author: videoDetail.authorInfo?.uniqueId || videoDetail.authorInfo?.uid || 'unknown',
                nickname: videoDetail.authorInfo?.nickname || 'unknown',
                duration: videoDetail.video?.duration,
                stats: {
                  diggCount: videoDetail.stats?.diggCount,
                  commentCount: videoDetail.stats?.commentCount,
                  shareCount: videoDetail.stats?.shareCount
                }
              };
            }
          }
        } catch (e) { /* 忽略解析错误 */ }

        // 抖音备用：从 URL 提取
        const douyinMatch = window.location.pathname.match(/video\/(\d+)/);
        if (douyinMatch) {
          // 尝试从页面标题获取描述
          const title = document.title || '';
          return { id: douyinMatch[1], desc: title, author: 'douyin_user' };
        }

        return { id: Date.now().toString(), author: 'douyin_user' };
      }

      // TikTok：尝试 SIGI_STATE
      if (window['SIGI_STATE']) {
        const state = window['SIGI_STATE'];
        const itemModule = state.ItemModule || {};
        const items = Object.values(itemModule);
        if (items.length > 0) {
          const item = items[0];
          const userInfo = state.UserModule?.users?.[item.author] || {};
          return {
            id: item.id,
            desc: item.desc,
            author: item.author,
            nickname: userInfo.nickname || item.author,
            createTime: item.createTime,
            duration: item.video?.duration,
            stats: item.stats
          };
        }
      }

      // 尝试从 URL 提取 video ID
      const match = window.location.pathname.match(/video\/(\d+)/);
      if (match) {
        return { id: match[1] };
      }

      return { id: Date.now().toString() };
    }, isDouyin);

    // 显示视频信息
    if (videoInfo) {
      console.log('\n📋 视频信息:');
      console.log('   ID:', videoInfo.id);
      if (videoInfo.nickname) console.log('   作者:', videoInfo.nickname);
      if (videoInfo.desc) console.log('   描述:', videoInfo.desc.substring(0, 60) + '...');
      if (videoInfo.duration) console.log('   时长:', videoInfo.duration, '秒');
      if (videoInfo.stats) {
        console.log('   点赞:', videoInfo.stats.diggCount);
        console.log('   评论:', videoInfo.stats.commentCount);
      }
    }

    // 4. 下载视频
    console.log('\n4. 捕获到', videoData.length, '个视频 URL');

    if (videoData.length > 0) {
      // 选择最大的（最高画质）
      videoData.sort((a, b) => b.size - a.size);
      const bestVideo = videoData[0];

      console.log(`   最高画质: ${(bestVideo.size / 1024 / 1024).toFixed(2)} MB`);

      console.log('\n5. 下载视频...');

      // 使用浏览器上下文下载
      const referer = isDouyin ? 'https://www.douyin.com/' : 'https://www.tiktok.com/';
      const origin = isDouyin ? 'https://www.douyin.com' : 'https://www.tiktok.com';
      const response = await context.request.get(bestVideo.url, {
        headers: {
          'Referer': referer,
          'Origin': origin
        }
      });

      if (response.ok()) {
        const buffer = await response.body();

        // 创建作者目录
        const author = sanitizeFilename(videoInfo.author || videoInfo.nickname || 'unknown');
        const authorDir = path.join(CONFIG.OUTPUT_DIR, author);
        if (!fs.existsSync(authorDir)) {
          fs.mkdirSync(authorDir, { recursive: true });
        }

        // 保存视频
        const videoFilename = `${videoInfo.id}.mp4`;
        const videoPath = path.join(authorDir, videoFilename);
        fs.writeFileSync(videoPath, buffer);

        console.log(`\n✅ 下载成功!`);
        console.log(`   文件: ${videoPath}`);
        console.log(`   大小: ${(buffer.length / 1024 / 1024).toFixed(2)} MB`);

        // 保存元数据
        const metadata = {
          ...videoInfo,
          sourceUrl: videoUrl,
          downloadTime: new Date().toISOString(),
          fileSize: buffer.length
        };
        const metaPath = path.join(authorDir, `${videoInfo.id}.json`);
        fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
        console.log(`   元数据: ${metaPath}`);

        result = { success: true, filepath: videoPath, metadata };
      } else {
        console.log('❌ 下载失败:', response.status());
      }
    } else if (isDouyin) {
      // 抖音 fallback: 从 RENDER_DATA 提取 CDN URL
      console.log('\n   网络拦截未捕获，尝试从 RENDER_DATA 提取...')
      const cdnUrl = await page.evaluate(() => {
        const el = document.getElementById('RENDER_DATA')
        if (!el) return null
        try {
          const text = decodeURIComponent(el.textContent)
          const patterns = [
            /https?:\/\/v[0-9.-]*douyinvod\.com\/[^"\\]+/g,
            /https?:\/\/[^"\\]+tos-cn-ve[^"\\]+/g,
          ]
          const all = []
          for (const p of patterns) {
            const m = text.match(p)
            if (m) all.push(...m)
          }
          const video = [...new Set(all)].filter(u => !u.includes('audio'))
          return video[0] || null
        } catch { return null }
      }).catch(() => null)

      if (cdnUrl) {
        console.log('   找到 CDN URL，下载中...')
        const dlPage = await context.newPage()
        try {
          const resp = await dlPage.goto(cdnUrl.replace(/\\u002F/g, '/'), {
            timeout: 60000
          })
          if (resp) {
            const buffer = await resp.body()
            if (buffer.length > CONFIG.MIN_VIDEO_SIZE) {
              const author = sanitizeFilename(
                videoInfo.author || videoInfo.nickname || 'douyin_user'
              )
              const authorDir = path.join(CONFIG.OUTPUT_DIR, author)
              if (!fs.existsSync(authorDir)) {
                fs.mkdirSync(authorDir, { recursive: true })
              }
              const videoPath = path.join(authorDir, `${videoInfo.id}.mp4`)
              fs.writeFileSync(videoPath, buffer)
              console.log(`\n✅ 下载成功!`)
              console.log(`   文件: ${videoPath}`)
              console.log(`   大小: ${(buffer.length / 1024 / 1024).toFixed(2)} MB`)
              const metadata = {
                ...videoInfo,
                sourceUrl: videoUrl,
                downloadTime: new Date().toISOString(),
                fileSize: buffer.length
              }
              const metaPath = path.join(authorDir, `${videoInfo.id}.json`)
              fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2))
              result = { success: true, filepath: videoPath, metadata }
            } else {
              console.log(`   文件太小 (${buffer.length} bytes)，可能不是完整视频`)
            }
          }
        } catch (e) {
          console.log('   CDN 下载失败:', e.message.substring(0, 80))
        }
        await dlPage.close()
      }

      if (!result.success) {
        console.log('\n❌ 未能下载视频')
        await page.screenshot({ path: '/tmp/tiktok-debug.png' })
        console.log('   调试截图: /tmp/tiktok-debug.png')
      }
    } else {
      console.log('\n❌ 未捕获到视频 URL');
      await page.screenshot({ path: '/tmp/tiktok-debug.png' });
      console.log('   调试截图: /tmp/tiktok-debug.png');
    }

  } catch (error) {
    console.error('\n❌ 错误:', error.message);
    await page.screenshot({ path: '/tmp/tiktok-error.png' }).catch(() => {});
  } finally {
    await browser.close();
    console.log('\n浏览器已关闭');
  }

  return result;
}

// ============ CLI 入口 ============

async function main() {
  const args = process.argv.slice(2);

  // 解析参数
  let videoUrl = null;
  let shouldAnalyze = false;

  for (const arg of args) {
    if (arg === '--analyze' || arg === '-a') {
      shouldAnalyze = true;
    } else if (!arg.startsWith('-')) {
      videoUrl = arg;
    }
  }

  if (!videoUrl) {
    console.log('用法: node download.js [选项] <TikTok视频链接>');
    console.log('');
    console.log('选项:');
    console.log('  --analyze, -a    下载后使用 Gemini 分析视频内容');
    console.log('');
    console.log('示例:');
    console.log('  node download.js "https://www.tiktok.com/@user/video/123456"');
    console.log('  node download.js --analyze "https://www.tiktok.com/@user/video/123456"');
    process.exit(1);
  }

  // 验证 URL
  if (!videoUrl.includes('tiktok.com') && !videoUrl.includes('douyin.com')) {
    console.error('错误: 请提供有效的 TikTok 或抖音链接');
    process.exit(1);
  }

  const result = await downloadTikTokVideo(videoUrl);

  if (result.success) {
    // 如果需要分析
    if (shouldAnalyze) {
      console.log('\n' + '='.repeat(50));
      console.log('📊 开始 Gemini 视频分析...');
      console.log('='.repeat(50) + '\n');

      try {
        const { analyzeVideo } = require('./analyze.js');
        const analysis = await analyzeVideo(result.filepath);

        if (analysis) {
          // 保存分析结果
          const analysisPath = result.filepath.replace('.mp4', '_analysis.json');
          fs.writeFileSync(analysisPath, JSON.stringify(analysis, null, 2), 'utf-8');

          console.log('\n✅ 分析完成!');
          console.log('📄 分析结果:', analysisPath);

          // 打印摘要
          if (analysis.basic_info) {
            console.log('\n📋 内容摘要:');
            if (analysis.basic_info.product_name) {
              console.log('   产品:', analysis.basic_info.product_name);
            }
            if (analysis.basic_info.product_type) {
              console.log('   类型:', analysis.basic_info.product_type);
            }
            if (analysis.basic_info.target_audience) {
              console.log('   受众:', analysis.basic_info.target_audience);
            }
          }
          if (analysis.overall_analysis) {
            if (analysis.overall_analysis.viral_reason) {
              console.log('   爆款原因:', analysis.overall_analysis.viral_reason);
            }
            if (analysis.overall_analysis.success_factors) {
              console.log('   成功要素:', analysis.overall_analysis.success_factors.join(', '));
            }
          }
        }
      } catch (error) {
        console.error('❌ 分析失败:', error.message);
      }
    }

    console.log('\n🎉 完成!');
    process.exit(0);
  } else {
    process.exit(1);
  }
}

// 支持作为模块导入
module.exports = { downloadTikTokVideo, CONFIG };

// CLI 模式
if (require.main === module) {
  main();
}
