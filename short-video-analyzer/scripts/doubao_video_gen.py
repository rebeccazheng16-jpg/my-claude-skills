#!/usr/bin/env python3
"""
使用豆包 Seedance 1.5 Pro 从图片生成视频
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
OUTPUT_DIR = Path.home() / "Downloads" / "fal_generated"
OUTPUT_DIR.mkdir(exist_ok=True)


def upload_image_to_url(image_path: str) -> str:
    """
    由于豆包需要公网可访问的 URL，我们需要先上传图片
    这里使用 tmpfiles.org 临时文件服务
    """
    print(f"📤 上传图片到临时存储...")

    with open(image_path, "rb") as f:
        response = httpx.post(
            "https://tmpfiles.org/api/v1/upload",
            files={"file": f},
            timeout=60
        )

    if response.status_code == 200:
        data = response.json()
        # tmpfiles.org 返回的 URL 需要转换
        url = data["data"]["url"].replace("tmpfiles.org/", "tmpfiles.org/dl/")
        print(f"✅ 上传成功: {url}")
        return url
    else:
        raise Exception(f"上传失败: {response.text}")


def create_video_task(
    image_url: str,
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    ratio: str = "9:16",
    generate_audio: bool = False
) -> str:
    """创建视频生成任务"""
    print(f"\n🎬 创建视频生成任务...")
    print(f"   提示词: {prompt[:80]}...")
    print(f"   时长: {duration}秒")
    print(f"   分辨率: {resolution}")
    print(f"   宽高比: {ratio}")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}"
    }

    payload = {
        "model": "doubao-seedance-1-5-pro-251215",  # 使用 1.5 Pro
        "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": image_url}, "role": "first_frame"}
        ],
        "duration": duration,
        "resolution": resolution,
        "ratio": ratio,
        "watermark": False,
        "return_last_frame": True  # 返回尾帧，用于连续生成
    }

    # Seedance 1.5 Pro 才支持 generate_audio
    # if generate_audio:
    #     payload["generate_audio"] = True

    response = httpx.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers=headers,
        json=payload,
        timeout=30
    )

    if response.status_code != 200:
        print(f"❌ 创建任务失败: {response.status_code}")
        print(f"   响应: {response.text}")
        raise Exception(f"创建任务失败: {response.text}")

    data = response.json()
    task_id = data.get("id")
    print(f"✅ 任务创建成功: {task_id}")
    return task_id


def poll_task_status(task_id: str) -> dict:
    """轮询任务状态直到完成"""
    print(f"\n⏳ 等待视频生成...")

    headers = {
        "Authorization": f"Bearer {API_KEY}"
    }

    start_time = time.time()

    while True:
        response = httpx.get(
            f"{BASE_URL}/contents/generations/tasks/{task_id}",
            headers=headers,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ 查询状态失败: {response.text}")
            time.sleep(5)
            continue

        data = response.json()
        status = data.get("status")
        elapsed = int(time.time() - start_time)

        if status == "succeeded":
            print(f"✅ 视频生成成功！({elapsed}秒)")
            return data
        elif status == "failed":
            error = data.get("error", {})
            print(f"❌ 视频生成失败: {error}")
            raise Exception(f"视频生成失败: {error}")
        elif status in ["queued", "running"]:
            print(f"   状态: {status} ({elapsed}秒)...")
            time.sleep(5)
        else:
            print(f"   未知状态: {status}")
            time.sleep(5)


def download_video(url: str, output_path: Path) -> Path:
    """下载视频到本地"""
    print(f"\n📥 下载视频: {output_path.name}")

    response = httpx.get(url, timeout=120, follow_redirects=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ 已保存: {output_path} ({size_mb:.2f} MB)")
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    """使用 ffmpeg 拼接视频"""
    print(f"\n🔗 拼接 {len(video_paths)} 个视频...")

    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"⚠️ ffmpeg 警告: {result.stderr}")

    list_file.unlink()
    print(f"✅ 拼接完成: {output_path}")
    return output_path


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("🚀 豆包 Seedance 视频生成")
    print("=" * 60)

    # 使用之前生成的图片
    image_path = OUTPUT_DIR / "fashion_model_20260127_224004.png"

    if not image_path.exists():
        # 查找最新的图片
        images = list(OUTPUT_DIR.glob("fashion_model_*.png"))
        if images:
            image_path = max(images, key=lambda p: p.stat().st_mtime)
        else:
            print("❌ 找不到图片文件")
            sys.exit(1)

    print(f"📸 使用图片: {image_path}")

    # 上传图片获取公网 URL
    image_url = upload_image_to_url(str(image_path))

    # 生成多个视频片段
    motion_prompts = [
        "模特向前缓步走动，裤子布料随着步伐自然摆动，姿态自信从容。镜头固定。",
        "模特缓慢转身180度展示裤子背面，转动流畅自然。镜头固定。",
    ]

    video_paths = []
    last_frame_url = image_url  # 用于连续生成

    for i, prompt in enumerate(motion_prompts, 1):
        print(f"\n{'='*50}")
        print(f"生成视频片段 {i}/{len(motion_prompts)}")
        print(f"{'='*50}")

        try:
            task_id = create_video_task(
                image_url=last_frame_url,
                prompt=prompt,
                duration=5,  # 每段 5 秒
                resolution="720p",
                ratio="9:16",
                generate_audio=False
            )

            result = poll_task_status(task_id)

            # 获取视频 URL
            video_url = result.get("content", {}).get("video_url")
            if not video_url:
                print(f"❌ 未找到视频 URL")
                continue

            # 下载视频
            video_path = OUTPUT_DIR / f"fashion_clip_{timestamp}_{i}.mp4"
            download_video(video_url, video_path)
            video_paths.append(video_path)

            # 获取尾帧用于下一段
            last_frame = result.get("content", {}).get("last_frame_url")
            if last_frame:
                last_frame_url = last_frame
                print(f"   获取尾帧用于下一段")

        except Exception as e:
            print(f"❌ 片段 {i} 生成失败: {e}")
            continue

    if not video_paths:
        print("❌ 没有成功生成任何视频片段")
        sys.exit(1)

    # 拼接视频
    if len(video_paths) > 1:
        final_path = OUTPUT_DIR / f"fashion_video_{timestamp}_final.mp4"
        concatenate_videos(video_paths, final_path)
    else:
        final_path = video_paths[0]

    # 完成
    print(f"\n{'='*60}")
    print("🎉 生成完成!")
    print(f"{'='*60}")
    print(f"📸 图片: {image_path}")
    print(f"🎬 最终视频: {final_path}")
    print(f"📁 输出目录: {OUTPUT_DIR}")

    return {
        "image_path": str(image_path),
        "video_path": str(final_path),
        "video_segments": [str(p) for p in video_paths],
    }


if __name__ == "__main__":
    result = main()
    print(f"\n{json.dumps(result, indent=2, ensure_ascii=False)}")
