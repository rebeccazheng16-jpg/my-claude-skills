#!/usr/bin/env python3
"""
30秒穿搭展示视频生成脚本
"""

import os
import sys
import time
import httpx
import subprocess
from pathlib import Path
from datetime import datetime

API_KEY = os.getenv("DOUBAO_ARK", "32bdf7d3-f544-4e3a-bd46-4e17983031f3")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
OUTPUT_DIR = Path.home() / "Downloads" / "fashion_video"
OUTPUT_DIR.mkdir(exist_ok=True)


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
            "duration": duration,
            "resolution": "720p",
            "ratio": "9:16",
            "generate_audio": False,
            "watermark": False,
            "return_last_frame": True
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
            headers={"Authorization": f"Bearer {API_KEY}"},
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
        print(f"   ⏳ {status} ({elapsed}秒)...")
        time.sleep(5)


def download_video(url: str, output_path: Path) -> Path:
    response = httpx.get(url, timeout=120, follow_redirects=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(list_file), "-c", "copy", str(output_path)], capture_output=True)
    list_file.unlink()
    return output_path


def main(image_path: str):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print("=" * 60)
    print("🎬 30秒穿搭展示视频生成")
    print("=" * 60)

    image_url = upload_image(image_path)

    # 全身穿搭展示场景的提示词
    segments = [
        # 第1段：站立微动
        "模特自然站立面向镜头，双手插在裤兜，身体轻微左右摆动后站定。镜头固定。",

        # 第2段：抬手展示
        "模特双手从裤兜抽出，缓缓抬起双臂微微张开展示上衣，随后手臂放下。镜头固定。",

        # 第3段：转身侧面
        "模特缓慢向右转身约90度展示侧面轮廓，站定后左手轻搭腰间。镜头固定。",

        # 第4段：转至背面
        "模特继续向右转身至背对镜头，停顿展示背面，随后微微回头看向镜头。镜头固定。",

        # 第5段：转回正面
        "模特从背面缓缓转回正面，双手自然下垂，站定后调整站姿。镜头固定。",

        # 第6段：最终定格
        "模特面向镜头站定，双手重新插入裤兜，嘴角微扬，轻轻点头后静止。镜头固定。",
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
            last_frame = result.get("content", {}).get("last_frame_url")
            if last_frame:
                last_frame_url = last_frame
        except Exception as e:
            print(f"   ❌ 失败: {e}")

    if not video_paths:
        print("❌ 没有成功生成任何视频")
        return

    print(f"\n🔗 拼接 {len(video_paths)} 段视频...")
    final_path = OUTPUT_DIR / f"fashion_{timestamp}.mp4"
    concatenate_videos(video_paths, final_path)

    print(f"\n{'=' * 60}")
    print("🎉 完成!")
    print(f"{'=' * 60}")
    print(f"🎬 最终视频: {final_path}")
    print(f"⏱️  总时长: {len(video_paths) * 5} 秒")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python generate_fashion_video.py <图片路径>")
        sys.exit(1)
    main(sys.argv[1])
