#!/usr/bin/env python3
"""下载单篇小红书笔记的视频/图片/文案"""

import asyncio
import sys
import json
import random
import httpx
from pathlib import Path
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
COOKIE_CACHE_FILE = SKILL_DIR / "data" / "cookies.json"
OUTPUT_DIR = Path.home() / "XHS-Downloads"
LOGIN_TIMEOUT = 300

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

JS_EXTRACT_NOTE_DETAIL = """
() => {
    try {
        const state = window.__INITIAL_STATE__;
        if (!state || !state.note) return {error: 'no state.note'};
        const noteDetailMap = state.note.noteDetailMap;
        if (!noteDetailMap) return {error: 'no noteDetailMap'};
        const keys = Object.keys(noteDetailMap);
        if (keys.length === 0) return {error: 'empty noteDetailMap'};
        const noteData = noteDetailMap[keys[0]];
        if (!noteData || !noteData.note) return {error: 'noteData.note is null'};
        const note = noteData.note;

        let videoUrls = [];
        try {
            if (note.video && note.video.media && note.video.media.stream) {
                const stream = note.video.media.stream;
                for (const fmt of ['h265', 'h264']) {
                    if (stream[fmt] && Array.isArray(stream[fmt]) && stream[fmt].length > 0) {
                        const best = stream[fmt].reduce((a, b) => (a.height || 0) > (b.height || 0) ? a : b);
                        if (best && best.masterUrl) videoUrls.push(best.masterUrl);
                        if (best && best.backupUrls) videoUrls = videoUrls.concat(best.backupUrls);
                        break;
                    }
                }
            }
        } catch (e) {}

        let imageUrls = [];
        try {
            if (note.imageList && Array.isArray(note.imageList)) {
                imageUrls = note.imageList.map(img => {
                    if (!img) return null;
                    return (img.urlDefault || img.url || '').replace(/!.*$/, '');
                }).filter(url => url);
            }
        } catch (e) {}

        return {
            id: note.noteId || '',
            title: note.title || '',
            desc: note.desc || '',
            type: note.type || 'normal',
            time: note.time || 0,
            videoUrls: videoUrls,
            imageUrls: imageUrls,
            user: note.user ? { userId: note.user.userId || '', nickname: note.user.nickname || '' } : {},
            interactInfo: note.interactInfo ? {
                likedCount: note.interactInfo.likedCount || '0',
                collectedCount: note.interactInfo.collectedCount || '0',
                commentCount: note.interactInfo.commentCount || '0',
                shareCount: note.interactInfo.shareCount || '0'
            } : null
        };
    } catch (e) { return {error: e.message}; }
}
"""


def load_cookies():
    if COOKIE_CACHE_FILE.exists():
        try:
            with open(COOKIE_CACHE_FILE) as f:
                data = json.load(f)
            cookies = data.get("cookies", [])
            if cookies:
                return cookies
        except Exception:
            pass
    try:
        import rookiepy
        chrome_cookies = rookiepy.chrome(domains=[".xiaohongshu.com"])
        if chrome_cookies:
            return [{"name": c["name"], "value": c["value"], "domain": c["domain"], "path": c.get("path", "/")} for c in chrome_cookies]
    except Exception:
        pass
    return []


def sanitize(name):
    import re
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    name = re.sub(r'[^\w\s\u4e00-\u9fff\-.]', '', name)
    return name[:80].strip() or "untitled"


async def main(url: str):
    from playwright.async_api import async_playwright

    print(f"\n{'='*50}")
    print(f"  小红书单篇笔记下载")
    print(f"{'='*50}")
    print(f"\n链接: {url}")

    cookies = load_cookies()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent=random.choice(USER_AGENTS)
        )

        if cookies:
            await context.add_cookies(cookies)
            print("已加载 Cookie")

        page = await context.new_page()

        # 先访问首页检查登录
        print("检查登录状态...")
        try:
            await page.goto("https://www.xiaohongshu.com", wait_until='domcontentloaded', timeout=30000)
        except Exception:
            pass
        await asyncio.sleep(3)

        logged_in = False
        try:
            # 多种方式检测登录状态
            if '/login' not in page.url.lower():
                # 检查是否有用户相关元素
                avatar = await page.query_selector('.user-avatar, [class*="avatar"], .side-bar-avatar, [class*="user-info"], [class*="sidebar"] img')
                if avatar:
                    logged_in = True
                else:
                    # 检查 cookie 中是否有 web_session
                    page_cookies = await context.cookies()
                    cookie_names = {c['name'] for c in page_cookies}
                    if 'web_session' in cookie_names:
                        logged_in = True
                    else:
                        login_btn = await page.query_selector('text=登录')
                        logged_in = login_btn is None
        except:
            pass

        if not logged_in:
            print("\n请在浏览器中扫码登录（5分钟内）...")
            for i in range(LOGIN_TIMEOUT):
                await asyncio.sleep(1)
                try:
                    if '/login' not in page.url.lower():
                        page_cookies = await context.cookies()
                        cookie_names = {c['name'] for c in page_cookies}
                        if 'web_session' in cookie_names:
                            logged_in = True
                            break
                        login_btn = await page.query_selector('text=登录')
                        if login_btn is None:
                            logged_in = True
                            break
                except:
                    pass
                if i > 0 and i % 30 == 0:
                    print(f"  等待登录... ({i}秒)")

            if not logged_in:
                print("登录超时")
                await browser.close()
                return None

            # 保存 cookies
            new_cookies = await context.cookies()
            COOKIE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(COOKIE_CACHE_FILE, 'w') as f:
                json.dump({"cookies": new_cookies}, f)
            print("登录成功，Cookie 已保存")
        else:
            print("已登录")

        # 访问笔记页面
        print(f"\n访问笔记页面...")
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
        except Exception:
            pass
        await asyncio.sleep(5)

        # 如果是短链接被重定向了，记录最终 URL
        final_url = page.url
        print(f"最终 URL: {final_url}")

        # 提取笔记数据
        print("提取笔记数据...")
        note = None
        for retry in range(5):
            note = await page.evaluate(JS_EXTRACT_NOTE_DETAIL)
            if note and 'error' not in note:
                break
            await asyncio.sleep(2)

        if not note or 'error' in note:
            print(f"提取失败: {note}")
            await browser.close()
            return None

        print(f"\n标题: {note.get('title', '无标题')}")
        print(f"作者: {note.get('user', {}).get('nickname', '未知')}")
        print(f"类型: {note.get('type', '未知')}")
        print(f"描述: {(note.get('desc', '') or '')[:100]}...")

        if note.get('interactInfo'):
            info = note['interactInfo']
            print(f"互动: 赞{info.get('likedCount',0)} 藏{info.get('collectedCount',0)} 评{info.get('commentCount',0)} 转{info.get('shareCount',0)}")

        # 创建输出目录
        user = note.get('user', {})
        nickname = sanitize(user.get('nickname', 'unknown'))
        user_id = user.get('userId', 'unknown')
        title = sanitize(note.get('title', 'untitled'))

        timestamp = note.get('time', 0)
        if timestamp:
            try:
                date_str = datetime.fromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d')
            except:
                date_str = datetime.now().strftime('%Y-%m-%d')
        else:
            date_str = datetime.now().strftime('%Y-%m-%d')

        note_dir = OUTPUT_DIR / f"{user_id}_{nickname}" / f"{date_str}_{title}"
        note_dir.mkdir(parents=True, exist_ok=True)

        cookie_str = "; ".join([f"{c['name']}={c['value']}" for c in (await context.cookies())])

        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            headers = {
                "User-Agent": random.choice(USER_AGENTS),
                "Referer": "https://www.xiaohongshu.com/",
                "Cookie": cookie_str,
            }

            # 下载视频
            video_urls = note.get('videoUrls', [])
            video_path = None
            if video_urls:
                print(f"\n下载视频... ({len(video_urls)} 个源)")
                for i, vurl in enumerate(video_urls):
                    try:
                        resp = await client.get(vurl, headers=headers)
                        if resp.status_code == 200 and len(resp.content) > 1000:
                            video_path = note_dir / "video_1.mp4"
                            with open(video_path, 'wb') as f:
                                f.write(resp.content)
                            size_mb = len(resp.content) / 1024 / 1024
                            print(f"  视频已下载: {video_path} ({size_mb:.1f}MB)")
                            break
                    except Exception as e:
                        print(f"  源 {i+1} 失败: {e}")

            # 下载图片
            image_urls = note.get('imageUrls', [])
            if image_urls:
                print(f"\n下载图片... ({len(image_urls)} 张)")
                for i, iurl in enumerate(image_urls):
                    try:
                        resp = await client.get(iurl, headers=headers)
                        if resp.status_code == 200:
                            img_path = note_dir / f"image_{i+1}.png"
                            with open(img_path, 'wb') as f:
                                f.write(resp.content)
                            print(f"  图片 {i+1} 已下载")
                    except Exception as e:
                        print(f"  图片 {i+1} 失败: {e}")

        # 保存元数据
        metadata = {
            "id": note.get('id'),
            "title": note.get('title'),
            "desc": note.get('desc'),
            "type": note.get('type'),
            "time": note.get('time'),
            "user": note.get('user'),
            "interactInfo": note.get('interactInfo'),
            "sourceUrl": final_url,
            "downloadTime": datetime.now().isoformat(),
        }
        metadata_path = note_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        print(f"\n元数据已保存: {metadata_path}")

        await browser.close()

    print(f"\n{'='*50}")
    print(f"下载完成！")
    print(f"文件位置: {note_dir}")
    print(f"{'='*50}\n")

    return str(note_dir)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("用法: python download_single.py <笔记链接>")
        sys.exit(1)
    result = asyncio.run(main(sys.argv[1]))
    if result:
        print(f"OUTPUT_DIR={result}")
