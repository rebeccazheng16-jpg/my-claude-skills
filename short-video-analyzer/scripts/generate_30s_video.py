#!/usr/bin/env python3
"""
30秒视频生成脚本 - 使用豆包 Seedance 1.5 Pro
"""

import os
import sys
import json
import time
import httpx
import subprocess
from pathlib import Path
from datetime import datetime

# 配置
API_KEY = os.getenv("DOUBAO_ARK", "32bdf7d3-f544-4e3a-bd46-4e17983031f3")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 输出目录
OUTPUT_DIR = Path.home() / "Downloads" / "video_30s"
OUTPUT_DIR.mkdir(exist_ok=True)


def upload_image(image_path: str) -> str:
    """上传图片到临时存储获取公网URL"""
    print(f"📤 上传图片...")

    with open(image_path, "rb") as f:
        response = httpx.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": f},
            timeout=60
        )

    if response.status_code == 200:
        url = response.json()["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
        print(f"✅ 上传成功")
        return url
    else:
        raise Exception(f"上传失败: {response.text}")


def create_video_task(image_url: str, prompt: str, duration: int = 5) -> str:
    """创建视频生成任务"""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "doubao-seedance-1-5-pro-251215",
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}, "role": "first_frame"}
        ],
        "duration": duration,
        "resolution": "720p",
        "ratio": "9:16",
        "generate_audio": False,  # 不生成音频
        "watermark": False,
        "return_last_frame": True
    }

    response = httpx.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        raise Exception(f"创建任务失败: {response.text}")

    return response.json().get("id")


def poll_task(task_id: str) -> dict:
    """轮询任务状态"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    start_time = time.time()

    while True:
        response = httpx.get(
            f"{BASE_URL}/contents/generations/tasks/{task_id}",
            headers=headers,
            timeout=30
        )

        data = response.json()
        status = data.get("status")
        elapsed = int(time.time() - start_time)

        if status == "succeeded":
            print(f"   ✅ 完成 ({elapsed}秒)")
            return data
        elif status == "failed":
            raise Exception(f"生成失败: {data.get('error')}")
        else:
            print(f"   ⏳ {status} ({elapsed}秒)...")
            time.sleep(5)


def download_video(url: str, output_path: Path) -> Path:
    """下载视频"""
    response = httpx.get(url, timeout=120, follow_redirects=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    """拼接视频"""
    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(list_file), "-c", "copy", str(output_path)
    ], capture_output=True)

    list_file.unlink()
    return output_path


def main(image_path: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("🎬 30秒视频生成（镜子自拍场景）")
    print("=" * 60)

    # 上传图片
    image_url = upload_image(image_path)

    # 针对镜子自拍场景的提示词（手持手机，动作受限）
    segments = [
        # 第1段：微微调整姿势
        "模特保持手机自拍姿势，身体轻微左右摆动，目光看向镜头，嘴角微扬。镜头固定。",

        # 第2段：整理头发
        "模特左手缓缓抬起轻触发丝，头微微侧向一边，随后手放下。镜头固定。",

        # 第3段：换个角度
        "模特身体缓慢向右侧转约20度，展示侧面轮廓，目光依然看向镜头。镜头固定。",

        # 第4段：回正+表情变化
        "模特身体缓缓转回正面，嘴唇微张后闭合，眼神略带俏皮。镜头固定。",

        # 第5段：自信定格
        "模特微微挺胸调整站姿，下巴轻抬，目光自信看向镜头。镜头固定。",

        # 第6段：最终微笑
        "模特保持姿势，嘴角缓缓上扬露出微笑，轻轻点头后静止。镜头固定。",
    ]

    video_paths = []
    last_frame_url = image_url

    for i, prompt in enumerate(segments, 1):
        print(f"\n📹 生成第 {i}/6 段")
        print(f"   提示词: {prompt[:40]}...")

        try:
            task_id = create_video_task(last_frame_url, prompt, duration=5)
            print(f"   任务ID: {task_id}")

            result = poll_task(task_id)

            video_url = result.get("content", {}).get("video_url")
            if video_url:
                video_path = OUTPUT_DIR / f"segment_{timestamp}_{i}.mp4"
                download_video(video_url, video_path)
                video_paths.append(video_path)
                print(f"   📁 已保存: {video_path.name}")

            # 获取尾帧用于下一段
            last_frame = result.get("content", {}).get("last_frame_url")
            if last_frame:
                last_frame_url = last_frame

        except Exception as e:
            print(f"   ❌ 失败: {e}")
            continue

    if not video_paths:
        print("❌ 没有成功生成任何视频")
        return

    # 拼接视频
    print(f"\n🔗 拼接 {len(video_paths)} 段视频...")
    final_path = OUTPUT_DIR / f"final_{timestamp}.mp4"
    concatenate_videos(video_paths, final_path)

    print(f"\n{'=' * 60}")
    print("🎉 完成!")
    print(f"{'=' * 60}")
    print(f"📁 输出目录: {OUTPUT_DIR}")
    print(f"🎬 最终视频: {final_path}")
    print(f"⏱️  总时长: {len(video_paths) * 5} 秒")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_30s_video.py <图片路径>")
        sys.exit(1)

    main(sys.argv[1])
