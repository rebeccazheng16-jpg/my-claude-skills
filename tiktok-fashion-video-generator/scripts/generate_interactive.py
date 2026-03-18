#!/usr/bin/env python3
"""
TikTok Fashion Video Generator - 交互式版本
生成后让用户选择保留哪些段落
"""

import os
import sys
import json
import time
import httpx
import subprocess
from pathlib import Path
from datetime import datetime

# ============ 配置 ============

API_KEY = os.getenv("DOUBAO_ARK", "")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

if not API_KEY:
    try:
        from subprocess import run
        result = run(
            ["python3", str(Path.home() / ".claude/skills/api-keys-manager/scripts/api_keys.py"), "get", "DOUBAO_ARK"],
            capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout.strip():
            API_KEY = result.stdout.strip()
    except:
        pass

# ============ 动作模板 ============

SEGMENTS_FULLBODY = [
    {"name": "站立微动", "prompt": "模特自然站立面向镜头，双手插在裤兜或自然下垂，身体轻微左右摆动后站定。镜头固定。"},
    {"name": "展示上衣", "prompt": "模特双手缓缓抬起微微张开展示上衣，随后手臂放下。镜头固定。"},
    {"name": "转身侧面", "prompt": "模特缓慢向右转身约90度展示侧面轮廓，站定后左手轻搭腰间。镜头固定。"},
    {"name": "背面回眸", "prompt": "模特继续向右转身至背对镜头，停顿展示背面，随后微微回头看向镜头。镜头固定。"},
    {"name": "转回正面", "prompt": "模特从背面缓缓转回正面，双手自然下垂，站定后调整站姿。镜头固定。"},
    {"name": "最终定格", "prompt": "模特面向镜头站定，恢复初始姿势，嘴角微扬，轻轻点头后静止。镜头固定。"},
]

# ============ API 函数 ============

def upload_image(image_path: str) -> str:
    print(f"📤 上传图片...")
    with open(image_path, "rb") as f:
        response = httpx.post("https://tmpfiles.org/api/v1/upload", files={"file": f}, timeout=60)
    url = response.json()["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
    print(f"✅ 上传成功")
    return url


def create_video_task(image_url: str, prompt: str, duration: int = 5) -> str:
    response = httpx.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"},
        json={
            "model": "doubao-seedance-1-5-pro-251215",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": image_url}, "role": "first_frame"}
            ],
            "duration": duration, "resolution": "720p", "ratio": "9:16",
            "generate_audio": False, "watermark": False, "return_last_frame": True
        },
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"创建任务失败: {response.text}")
    return response.json().get("id")


def poll_task(task_id: str) -> dict:
    start_time = time.time()
    while True:
        response = httpx.get(
            f"{BASE_URL}/contents/generations/tasks/{task_id}",
            headers={"Authorization": f"Bearer {API_KEY}"}, timeout=30
        )
        data = response.json()
        status = data.get("status")
        elapsed = int(time.time() - start_time)
        if status == "succeeded":
            print(f"   ✅ 完成 ({elapsed}秒)")
            return data
        elif status == "failed":
            raise Exception(f"生成失败: {data.get('error')}")
        print(f"   ⏳ {status} ({elapsed}秒)...")
        time.sleep(5)


def download_video(url: str, output_path: Path) -> Path:
    response = httpx.get(url, timeout=120, follow_redirects=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def extract_thumbnail(video_path: Path, output_path: Path) -> Path:
    """提取视频中间帧作为缩略图"""
    subprocess.run([
        "ffmpeg", "-y", "-i", str(video_path),
        "-vf", "select=eq(n\\,50),scale=360:-1",  # 取第50帧
        "-vframes", "1", str(output_path)
    ], capture_output=True)
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    list_file = output_path.parent / "concat_list.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(output_path)
    ], capture_output=True)
    list_file.unlink()
    return output_path


# ============ 主函数 ============

def generate_all_segments(image_path: str, output_dir: Path) -> list:
    """生成所有段落，返回段落信息列表"""

    segments_dir = output_dir / "segments"
    segments_dir.mkdir(exist_ok=True)
    thumbs_dir = output_dir / "thumbnails"
    thumbs_dir.mkdir(exist_ok=True)

    image_url = upload_image(image_path)

    results = []
    last_frame_url = image_url

    for i, seg in enumerate(SEGMENTS_FULLBODY, 1):
        print(f"\n📹 生成第 {i}/6 段: {seg['name']}")

        try:
            task_id = create_video_task(last_frame_url, seg['prompt'], duration=5)
            print(f"   任务ID: {task_id}")

            result = poll_task(task_id)

            video_url = result.get("content", {}).get("video_url")
            if video_url:
                video_path = segments_dir / f"segment_{i}.mp4"
                download_video(video_url, video_path)

                # 提取缩略图
                thumb_path = thumbs_dir / f"thumb_{i}.jpg"
                extract_thumbnail(video_path, thumb_path)

                results.append({
                    "index": i,
                    "name": seg["name"],
                    "video_path": str(video_path),
                    "thumb_path": str(thumb_path),
                    "prompt": seg["prompt"]
                })
                print(f"   📁 已保存: {video_path.name}")

            last_frame = result.get("content", {}).get("last_frame_url")
            if last_frame:
                last_frame_url = last_frame

        except Exception as e:
            print(f"   ❌ 失败: {e}")
            results.append({
                "index": i,
                "name": seg["name"],
                "video_path": None,
                "error": str(e)
            })

    return results


def concat_selected_segments(segments: list, selected_indices: list, output_path: Path) -> Path:
    """拼接选中的段落"""
    video_paths = []
    for idx in selected_indices:
        for seg in segments:
            if seg["index"] == idx and seg.get("video_path"):
                video_paths.append(Path(seg["video_path"]))
                break

    if not video_paths:
        raise Exception("没有有效的视频段落")

    return concatenate_videos(video_paths, output_path)


# ============ CLI 入口 ============

def print_usage():
    print("""
用法:
  生成段落:  python generate_interactive.py <图片路径>
  拼接视频:  python generate_interactive.py --concat <输出目录> <段落序号...>

示例:
  python generate_interactive.py ~/photo.png
  python generate_interactive.py --concat ~/Downloads/tiktok_fashion_20260128_120000 1 3 4 6
""")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    # 拼接模式
    if sys.argv[1] == "--concat":
        if len(sys.argv) < 4:
            print("错误: 请提供输出目录和至少一个段落序号")
            print_usage()
            sys.exit(1)

        output_dir = Path(sys.argv[2])
        selected = [int(x) for x in sys.argv[3:]]

        # 读取段落信息
        info_path = output_dir / "segments_info.json"
        if not info_path.exists():
            print(f"错误: 找不到 {info_path}")
            sys.exit(1)

        with open(info_path, "r", encoding="utf-8") as f:
            segments = json.load(f)

        print(f"🔗 拼接段落: {selected}")
        final_path = output_dir / "final_video.mp4"
        concat_selected_segments(segments, selected, final_path)
        print(f"✅ 最终视频: {final_path}")

    # 生成模式
    else:
        image_path = sys.argv[1]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path.home() / "Downloads" / f"tiktok_fashion_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)

        print("=" * 60)
        print("🎬 TikTok Fashion Video Generator (交互式)")
        print("=" * 60)

        # 生成所有段落
        segments = generate_all_segments(image_path, output_dir)

        # 保存段落信息供 Claude 读取
        info_path = output_dir / "segments_info.json"
        with open(info_path, "w", encoding="utf-8") as f:
            json.dump(segments, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 所有段落生成完成!")
        print(f"📁 输出目录: {output_dir}")
        print(f"📋 段落信息: {info_path}")
        print(f"\n下一步: 查看缩略图后运行拼接命令")
        print(f"示例: python generate_interactive.py --concat {output_dir} 1 3 4 6")
