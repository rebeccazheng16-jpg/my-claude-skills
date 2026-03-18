#!/usr/bin/env python3
"""
小红书账号内容全量下载工具 v5.0
直接从页面提取下载地址，完全自主下载

v5.0 优化：
- 跳过已下载文件（断点续传）
- httpx 连接池复用
- 并行 CDN 下载（3并发）
- 随机 UA 轮换
- 两阶段下载：先收集URL，再并行下载

功能：
- 下载账号所有视频（无水印）
- 下载账号所有图片（PNG格式）
- 保存所有文案到 JSON 文件
- 按作者/作品分类存储
"""

import asyncio
import sys
import re
import json
import random
import time
import httpx
from pathlib import Path
from typing import Optional, List, Dict, Tuple
from datetime import datetime

# ============== 配置 ==============
SKILL_DIR = Path(__file__).parent.parent
COOKIE_CACHE_FILE = SKILL_DIR / "data" / "cookies.json"
OUTPUT_DIR = Path.home() / "XHS-Downloads"

MAX_SCROLL_ATTEMPTS = 50
SCROLL_DELAY = 1.5
DOWNLOAD_DELAY = 0.3  # 减少延迟（因为有并行下载）
LOGIN_TIMEOUT = 300
MAX_CONCURRENT_DOWNLOADS = 3  # CDN 并发下载数

# ============== UA 池 ==============
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
]

def get_random_ua() -> str:
    return random.choice(USER_AGENTS)

# ============== 工具函数 ==============

def print_banner():
    """打印横幅"""
    print("\n" + "=" * 60)
    print("   🎬 小红书内容全量下载工具 v5.0")
    print("   📦 视频 + 图片 + 文案 一键下载")
    print("   ⚡ 并行下载 | 断点续传 | 连接复用")
    print("=" * 60)


def print_progress(current: int, total: int, success: int, failed: int, skipped: int, title: str = ""):
    """打印进度条"""
    width = 30
    filled = int(width * current / total) if total > 0 else 0
    bar = "█" * filled + "░" * (width - filled)

    status = f"\r[{bar}] {current}/{total} | ✅{success} ⏭️{skipped} ❌{failed}"
    if title:
        title = title[:20] + "..." if len(title) > 20 else title
        status += f" | {title}"

    print(status, end="", flush=True)


def extract_user_id(input_str: str) -> str:
    """从输入中提取用户 ID"""
    input_str = input_str.strip()

    if re.match(r'^[a-f0-9]{24}$', input_str):
        return input_str

    match = re.search(r'/user/profile/([a-f0-9]{24})', input_str)
    if match:
        return match.group(1)

    if 'xhslink.com' in input_str:
        return input_str

    raise ValueError(f"无法识别的输入格式: {input_str}")


def sanitize_filename(name: str) -> str:
    """清理文件名"""
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', name)
    name = re.sub(r'[^\w\s\u4e00-\u9fff\-.]', '', name)
    return name[:50].strip() or "untitled"


def get_note_dir(note: Dict, output_dir: Path) -> Path:
    """获取笔记的保存目录"""
    note_time = note.get('time', '')
    if note_time:
        try:
            timestamp = int(note_time) / 1000
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')
        except:
            date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        date_str = datetime.now().strftime('%Y-%m-%d')

    title = sanitize_filename(note.get('title', '') or 'untitled')
    user = note.get('user', {})
    nickname = sanitize_filename(user.get('nickname', '') or 'unknown')
    user_id = user.get('userId', 'unknown')

    author_dir = output_dir / f"{user_id}_{nickname}"
    note_dir = author_dir / f"{date_str}_{title}"
    return note_dir


def is_note_downloaded(note_dir: Path) -> bool:
    """检查笔记是否已下载"""
    metadata_file = note_dir / "metadata.json"
    return metadata_file.exists()


# ============== Cookie 管理 ==============

class CookieManager:
    """Cookie 管理器"""

    def __init__(self):
        self.cookies = []
        self.source = None

    def load_from_chrome(self) -> bool:
        try:
            import rookiepy
            cookies = rookiepy.chrome(domains=[".xiaohongshu.com"])
            if cookies:
                self.cookies = [
                    {
                        "name": c["name"],
                        "value": c["value"],
                        "domain": c["domain"],
                        "path": c.get("path", "/"),
                    }
                    for c in cookies
                ]
                self.source = "Chrome 浏览器"
                return True
        except Exception:
            pass
        return False

    def load_from_cache(self) -> bool:
        if not COOKIE_CACHE_FILE.exists():
            return False
        try:
            with open(COOKIE_CACHE_FILE, 'r') as f:
                data = json.load(f)
            self.cookies = data.get("cookies", [])
            if self.cookies:
                self.source = "本地缓存"
                return True
        except Exception:
            pass
        return False

    def save_to_cache(self, cookies: List[Dict]):
        COOKIE_CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COOKIE_CACHE_FILE, 'w') as f:
            json.dump({"cookies": cookies, "time": time.time()}, f)

    def try_load_all(self) -> bool:
        if self.load_from_cache():
            return True
        if self.load_from_chrome():
            return True
        return False

    def get_cookie_string(self) -> str:
        return "; ".join([f"{c['name']}={c['value']}" for c in self.cookies])

    def has_valid_cookies(self) -> bool:
        if not self.cookies:
            return False
        cookie_names = {c["name"] for c in self.cookies}
        required = {"a1", "web_session", "webId"}
        return required.issubset(cookie_names)


# ============== 数据提取 ==============

JS_EXTRACT_USER_NOTES = """
() => {
    try {
        const state = window.__INITIAL_STATE__;
        if (!state || !state.user || !state.user.notes) return [];

        const result = [];
        const notesObj = state.user.notes._rawValue || state.user.notes;

        for (const key in notesObj) {
            const noteList = notesObj[key];
            if (Array.isArray(noteList)) {
                noteList.forEach(item => {
                    if (item && item.id && item.xsecToken) {
                        result.push({
                            id: item.id,
                            token: item.xsecToken,
                            title: item.noteCard ? item.noteCard.displayTitle : '',
                            type: item.noteCard ? item.noteCard.type : 'normal'
                        });
                    }
                });
            }
        }
        return result;
    } catch (e) {
        return [];
    }
}
"""

JS_EXTRACT_NOTE_DETAIL = """
() => {
    try {
        const state = window.__INITIAL_STATE__;
        if (!state) return {error: 'no __INITIAL_STATE__'};
        if (!state.note) return {error: 'no state.note'};

        const noteDetailMap = state.note.noteDetailMap;
        if (!noteDetailMap) return {error: 'no noteDetailMap'};

        const keys = Object.keys(noteDetailMap);
        if (keys.length === 0) return {error: 'empty noteDetailMap'};

        const noteData = noteDetailMap[keys[0]];
        if (!noteData) return {error: 'noteData is null'};
        if (!noteData.note) return {error: 'noteData.note is null'};

        const note = noteData.note;

        let videoUrls = [];
        try {
            if (note.video && note.video.media && note.video.media.stream) {
                const stream = note.video.media.stream;
                const formats = ['h265', 'h264'];
                for (const fmt of formats) {
                    if (stream[fmt] && Array.isArray(stream[fmt]) && stream[fmt].length > 0) {
                        const best = stream[fmt].reduce((a, b) =>
                            (a.height || 0) > (b.height || 0) ? a : b
                        );
                        if (best && best.masterUrl) {
                            videoUrls.push(best.masterUrl);
                        }
                        if (best && best.backupUrls && Array.isArray(best.backupUrls)) {
                            videoUrls = videoUrls.concat(best.backupUrls);
                        }
                        break;
                    }
                }
            }
        } catch (videoErr) {}

        let imageUrls = [];
        try {
            if (note.imageList && Array.isArray(note.imageList) && note.imageList.length > 0) {
                imageUrls = note.imageList.map(img => {
                    if (!img) return null;
                    if (img.urlDefault) {
                        return img.urlDefault.replace(/!.*$/, '');
                    }
                    if (img.url) {
                        return img.url.replace(/!.*$/, '');
                    }
                    return null;
                }).filter(url => url);
            }
        } catch (imgErr) {}

        return {
            id: note.noteId || '',
            title: note.title || '',
            desc: note.desc || '',
            type: note.type || 'normal',
            time: note.time || 0,
            videoUrls: videoUrls,
            imageUrls: imageUrls,
            hasContent: videoUrls.length > 0 || imageUrls.length > 0,
            user: note.user ? {
                userId: note.user.userId || '',
                nickname: note.user.nickname || ''
            } : {userId: '', nickname: ''},
            interactInfo: note.interactInfo ? {
                likedCount: note.interactInfo.likedCount || '0',
                collectedCount: note.interactInfo.collectedCount || '0',
                commentCount: note.interactInfo.commentCount || '0',
                shareCount: note.interactInfo.shareCount || '0'
            } : null
        };
    } catch (e) {
        return {error: e.message || 'unknown error'};
    }
}
"""


# ============== 下载器（优化版）==============

class Downloader:
    """优化的下载器：连接池复用 + 并行下载"""

    def __init__(self, cookie_str: str, max_concurrent: int = MAX_CONCURRENT_DOWNLOADS):
        self.cookie_str = cookie_str
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.client = httpx.AsyncClient(
            follow_redirects=True,
            timeout=httpx.Timeout(60.0, connect=10.0),
            limits=httpx.Limits(max_connections=10, max_keepalive_connections=5)
        )

    async def close(self):
        await self.client.aclose()

    def _get_headers(self) -> Dict:
        return {
            "User-Agent": get_random_ua(),
            "Referer": "https://www.xiaohongshu.com/",
            "Cookie": self.cookie_str,
        }

    async def download_file(self, url: str, filepath: Path) -> bool:
        """下载单个文件（带信号量限制）"""
        async with self.semaphore:
            try:
                response = await self.client.get(url, headers=self._get_headers())
                if response.status_code == 200:
                    filepath.parent.mkdir(parents=True, exist_ok=True)
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    return True
            except Exception:
                pass
            return False

    async def download_files_parallel(self, tasks: List[Tuple[str, Path]]) -> Tuple[int, int]:
        """并行下载多个文件"""
        if not tasks:
            return 0, 0

        results = await asyncio.gather(
            *[self.download_file(url, path) for url, path in tasks],
            return_exceptions=True
        )

        success = sum(1 for r in results if r is True)
        failed = len(results) - success
        return success, failed


async def download_note_content(
    note: Dict,
    output_dir: Path,
    downloader: Downloader
) -> Tuple[bool, str, bool]:
    """
    下载单个笔记的所有内容
    返回: (是否成功, 消息, 是否跳过)
    """
    note_dir = get_note_dir(note, output_dir)
    title = sanitize_filename(note.get('title', '') or 'untitled')

    # 检查是否已下载
    if is_note_downloaded(note_dir):
        return (True, f"⏭️ {title}", True)  # skipped=True

    note_dir.mkdir(parents=True, exist_ok=True)

    # 收集下载任务
    download_tasks = []

    # 视频下载任务
    video_urls = note.get('videoUrls', [])
    if video_urls:
        video_path = note_dir / "video_1.mp4"
        if not video_path.exists():
            download_tasks.append((video_urls[0], video_path))

    # 图片下载任务
    image_urls = note.get('imageUrls', [])
    for i, url in enumerate(image_urls):
        img_path = note_dir / f"image_{i + 1}.png"
        if not img_path.exists():
            download_tasks.append((url, img_path))

    # 并行下载
    success, failed = await downloader.download_files_parallel(download_tasks)

    # 保存元数据（即使没有媒体文件也保存）
    metadata = {
        "id": note.get('id'),
        "title": note.get('title'),
        "desc": note.get('desc'),
        "type": note.get('type'),
        "time": note.get('time'),
        "user": note.get('user'),
        "interactInfo": note.get('interactInfo'),
        "downloadTime": datetime.now().isoformat(),
    }
    with open(note_dir / "metadata.json", 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    if success > 0:
        return (True, title, False)
    elif failed == 0:
        return (True, f"{title} (仅文案)", False)
    else:
        return (False, f"下载失败 ({failed})", False)


# ============== 主流程 ==============

async def main(account_input: str, limit: int = None):
    """主函数"""
    print_banner()

    try:
        user_id = extract_user_id(account_input)
    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)

    print("\n🔑 检查登录状态...")
    cookie_manager = CookieManager()

    if cookie_manager.try_load_all():
        if cookie_manager.has_valid_cookies():
            print(f"   ✅ 找到有效 Cookie（来源: {cookie_manager.source}）")
        else:
            print(f"   ⚠️ Cookie 不完整，可能需要重新登录")
    else:
        print("   ℹ️ 未找到已保存的登录状态，需要扫码登录")

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌ Playwright 未安装")
        sys.exit(1)

    if user_id.startswith("http"):
        profile_url = user_id
    else:
        profile_url = f"https://www.xiaohongshu.com/user/profile/{user_id}"

    print(f"\n🔗 目标: {profile_url}")

    async with async_playwright() as p:
        print("\n🌐 启动浏览器...")
        browser = await p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-first-run',
                '--no-default-browser-check',
            ]
        )

        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent=get_random_ua()
        )

        if cookie_manager.cookies:
            print(f"   📦 使用 {cookie_manager.source} 的 Cookie")
            await context.add_cookies(cookie_manager.cookies)

        page = await context.new_page()

        print("   🔍 检查登录状态...")
        try:
            await page.goto("https://www.xiaohongshu.com", wait_until='domcontentloaded', timeout=45000)
        except Exception:
            pass
        await asyncio.sleep(3)

        logged_in = False
        try:
            avatar = await page.query_selector('.user-avatar, [class*="avatar"], .side-bar-avatar')
            if avatar:
                logged_in = True
            else:
                login_btn = await page.query_selector('text=登录')
                logged_in = login_btn is None
                if 'login' in page.url.lower():
                    logged_in = False
        except:
            pass

        if not logged_in:
            print("\n" + "=" * 50)
            print("⚠️  需要登录小红书")
            print("=" * 50)
            print("\n请在浏览器中扫码登录（5分钟内）\n")

            for i in range(LOGIN_TIMEOUT):
                await asyncio.sleep(1)
                try:
                    login_btn = await page.query_selector('text=登录')
                    if login_btn is None:
                        logged_in = True
                        break
                except:
                    pass
                if i > 0 and i % 30 == 0:
                    print(f"   ⏳ 等待登录... ({i}秒)")

            if not logged_in:
                print("\n❌ 登录超时")
                await browser.close()
                return

            print("✅ 登录成功！")
            cookies = await context.cookies()
            cookie_manager.save_to_cache(cookies)
            cookie_manager.cookies = cookies
        else:
            print("   ✅ 已登录")

        print(f"\n📂 访问账号主页...")
        try:
            await page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
        except Exception:
            pass
        await asyncio.sleep(5)

        if '/login' in page.url:
            print("   ⚠️ Cookie 失效，请重新登录...")
            for i in range(LOGIN_TIMEOUT):
                await asyncio.sleep(1)
                if '/login' not in page.url:
                    break
                if i > 0 and i % 30 == 0:
                    print(f"   ⏳ 等待登录... ({i}秒)")

            if '/login' in page.url:
                await browser.close()
                return

            cookies = await context.cookies()
            cookie_manager.save_to_cache(cookies)
            await page.goto(profile_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)

        nickname = "未知"
        try:
            el = await page.query_selector('.user-nickname, .nickname, [class*="nickname"]')
            if el:
                nickname = await el.inner_text()
                print(f"   👤 账号: {nickname}")
        except:
            pass

        # Phase 1: 收集笔记列表
        print(f"\n📜 滚动加载笔记...")
        all_notes = []
        last_count = 0
        no_new_count = 0

        for attempt in range(MAX_SCROLL_ATTEMPTS):
            try:
                notes_data = await page.evaluate(JS_EXTRACT_USER_NOTES)
                seen_ids = {n['id'] for n in all_notes}
                for note in notes_data:
                    if note['id'] not in seen_ids:
                        all_notes.append(note)
                        seen_ids.add(note['id'])
            except Exception:
                pass

            current = len(all_notes)
            print(f"   滚动 {attempt + 1}/{MAX_SCROLL_ATTEMPTS}，发现 {current} 个笔记", end='\r')

            if current == last_count:
                no_new_count += 1
                if no_new_count >= 5:
                    break
            else:
                no_new_count = 0
                last_count = current

            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(SCROLL_DELAY)

        print(f"\n   ✅ 共发现 {len(all_notes)} 个笔记")

        if not all_notes:
            print("\n❌ 未找到任何笔记")
            await browser.close()
            return

        if limit and limit > 0:
            all_notes = all_notes[:limit]
            print(f"   📌 限制下载前 {limit} 个")

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        print(f"\n📁 保存位置: {OUTPUT_DIR}")

        # Phase 2: 逐个访问详情页提取数据
        print(f"\n🔍 提取详情信息...")
        print("-" * 50)

        notes_to_download = []
        success = 0
        failed = 0
        skipped = 0

        # 创建下载器（连接池复用）
        downloader = Downloader(cookie_manager.get_cookie_string())

        for i, note_info in enumerate(all_notes, 1):
            note_id = note_info['id']
            token = note_info['token']

            # 先检查是否已下载（不需要访问详情页）
            temp_note = {'time': 0, 'title': note_info.get('title', ''), 'user': {'userId': '', 'nickname': ''}}

            detail_url = f"https://www.xiaohongshu.com/explore/{note_id}?xsec_token={token}"

            try:
                await page.goto(detail_url, wait_until='domcontentloaded', timeout=30000)
                await asyncio.sleep(2)

                note_detail = None
                for retry in range(3):
                    note_detail = await page.evaluate(JS_EXTRACT_NOTE_DETAIL)
                    if note_detail and 'error' not in note_detail:
                        break
                    await asyncio.sleep(1.5)

                if not note_detail:
                    failed += 1
                    print_progress(i, len(all_notes), success, failed, skipped, "页面数据为空")
                elif 'error' in note_detail:
                    failed += 1
                    print_progress(i, len(all_notes), success, failed, skipped, f"提取失败")
                else:
                    # 下载内容（包含跳过检查）
                    ok, msg, was_skipped = await download_note_content(note_detail, OUTPUT_DIR, downloader)
                    if was_skipped:
                        skipped += 1
                    elif ok:
                        success += 1
                    else:
                        failed += 1
                    print_progress(i, len(all_notes), success, failed, skipped, msg)

            except Exception as e:
                failed += 1
                print_progress(i, len(all_notes), success, failed, skipped, f"错误: {str(e)[:15]}")

            await asyncio.sleep(DOWNLOAD_DELAY)

        # 关闭下载器
        await downloader.close()
        await browser.close()

    # 输出统计
    print("\n\n" + "=" * 50)
    print("📊 下载完成")
    print("=" * 50)
    print(f"   ✅ 新下载: {success}")
    print(f"   ⏭️ 已跳过: {skipped}")
    print(f"   ❌ 失败: {failed}")
    print(f"   📁 总计: {len(all_notes)}")
    print(f"\n   📂 文件位置: {OUTPUT_DIR}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print_banner()
        print("\n用法: python auto_download.py <账号链接或ID> [--limit N]")
        print("\n示例:")
        print("  python auto_download.py 5675e19782ec397e4a6835d3")
        print("  python auto_download.py 5675e19782ec397e4a6835d3 --limit 20")
        print("\n输出:")
        print(f"  📁 文件位置: {OUTPUT_DIR}")
        sys.exit(1)

    account = sys.argv[1]
    limit = None
    if '--limit' in sys.argv:
        idx = sys.argv.index('--limit')
        if idx + 1 < len(sys.argv):
            limit = int(sys.argv[idx + 1])

    asyncio.run(main(account, limit))
