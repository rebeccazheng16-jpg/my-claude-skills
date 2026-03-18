#!/usr/bin/env python3
"""
图片到视频生成管道
使用 fal.ai API: Seedream V4 (图片) + Kling 2.6 (视频)
"""

import os
import sys
import json
import requests
import subprocess
from pathlib import Path
from datetime import datetime

# 设置 fal API key
FAL_KEY = os.getenv("FAL_KEY", "9b85b92f-f62f-4e69-a82f-2ebe7edfbc83:ec4f3e9f3c49a67ef24c3f0c2a78f3cb")
os.environ["FAL_KEY"] = FAL_KEY

import fal_client

# 输出目录
OUTPUT_DIR = Path.home() / "Downloads" / "fal_generated"
OUTPUT_DIR.mkdir(exist_ok=True)


def generate_image(prompt: str, width: int = 720, height: int = 1280) -> dict:
    """使用 Seedream V4 生成图片"""
    print(f"\n🎨 正在生成图片...")
    print(f"   提示词: {prompt[:80]}...")
    print(f"   尺寸: {width}x{height}")

    try:
        result = fal_client.subscribe(
            "fal-ai/seedream-v4",
            arguments={
                "prompt": prompt,
                "image_size": {"width": width, "height": height},
                "num_images": 1,
            },
            with_logs=True,
            on_queue_update=lambda update: print(f"   状态: {update}") if hasattr(update, 'status') else None,
        )

        if result and "images" in result and len(result["images"]) > 0:
            image_url = result["images"][0]["url"]
            print(f"✅ 图片生成成功: {image_url}")
            return {"status": "completed", "image_url": image_url}
        else:
            print(f"❌ 图片生成失败: {result}")
            return {"status": "failed", "error": str(result)}

    except Exception as e:
        print(f"❌ 图片生成出错: {e}")
        return {"status": "failed", "error": str(e)}


def generate_video_from_image(
    image_url: str,
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "9:16",
) -> dict:
    """使用 Kling 2.6 从图片生成视频"""
    print(f"\n🎬 正在生成视频...")
    print(f"   运动提示词: {prompt}")
    print(f"   时长: {duration}秒")

    try:
        # 使用 Kling 2.6，支持最大 10 秒
        result = fal_client.subscribe(
            "fal-ai/kling-video/v2.6/pro/image-to-video",
            arguments={
                "prompt": prompt,
                "image_url": image_url,
                "duration": str(duration),  # Kling 需要字符串
                "aspect_ratio": aspect_ratio,
            },
            with_logs=True,
            on_queue_update=lambda update: print(f"   状态: {update}") if hasattr(update, 'status') else None,
        )

        if result and "video" in result:
            video_url = result["video"]["url"]
            print(f"✅ 视频生成成功: {video_url}")
            return {"status": "completed", "video_url": video_url}
        else:
            print(f"❌ 视频生成失败: {result}")
            return {"status": "failed", "error": str(result)}

    except Exception as e:
        print(f"❌ 视频生成出错: {e}")
        return {"status": "failed", "error": str(e)}


def download_file(url: str, output_path: Path) -> Path:
    """下载文件到本地"""
    print(f"\n📥 正在下载: {output_path.name}")
    response = requests.get(url, stream=True)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    size_mb = output_path.stat().st_size / (1024 * 1024)
    print(f"✅ 已保存: {output_path} ({size_mb:.2f} MB)")
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    """使用 ffmpeg 拼接视频"""
    print(f"\n🔗 正在拼接 {len(video_paths)} 个视频...")

    # 创建临时文件列表
    list_file = OUTPUT_DIR / "concat_list.txt"
    with open(list_file, "w") as f:
        for vp in video_paths:
            f.write(f"file '{vp}'\n")

    # 使用 ffmpeg 拼接
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
        print(f"❌ ffmpeg 错误: {result.stderr}")
        raise Exception(f"ffmpeg failed: {result.stderr}")

    # 清理临时文件
    list_file.unlink()

    print(f"✅ 拼接完成: {output_path}")
    return output_path


def main():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    print("=" * 60)
    print("🚀 fal.ai 图片到视频生成管道")
    print("=" * 60)

    # ===== 步骤 1: 生成图片 =====
    image_prompt = """A young Southeast Asian male model, early 20s, slim athletic build, standing confidently in a minimalist indoor setting. He is wearing beige/khaki straight-leg casual trousers paired with a simple dark t-shirt. The pants have a relaxed, slightly wide-leg fit that drapes naturally. Clean white or neutral gray background. Soft natural lighting from the side. Full body shot, fashion photography style. The model has a cool, effortless expression. High quality, sharp details, modern streetwear aesthetic."""

    image_result = generate_image(image_prompt, width=720, height=1280)  # 9:16 竖屏

    if image_result["status"] != "completed":
        print("❌ 图片生成失败，退出")
        sys.exit(1)

    image_url = image_result["image_url"]

    # 下载图片
    image_path = OUTPUT_DIR / f"fashion_model_{timestamp}.png"
    download_file(image_url, image_path)

    # ===== 步骤 2: 生成视频片段 =====
    # Kling 2.6 支持最大 10 秒，生成 2 个片段共 20 秒
    motion_prompts = [
        "The model walks forward slowly with confidence, the pants fabric moves naturally with each step. Slight body movement, casual walking pose. Camera remains static.",
        "The model slowly turns around 180 degrees to show the back of the pants, then turns back. Smooth natural rotation. Camera remains static.",
    ]

    video_paths = []

    for i, motion_prompt in enumerate(motion_prompts, 1):
        print(f"\n{'='*50}")
        print(f"生成视频片段 {i}/{len(motion_prompts)}")
        print(f"{'='*50}")

        video_result = generate_video_from_image(
            image_url=image_url,
            prompt=motion_prompt,
            duration=10,  # Kling 2.6 最大 10 秒
            aspect_ratio="9:16",
        )

        if video_result["status"] != "completed":
            print(f"❌ 视频片段 {i} 生成失败，跳过")
            continue

        # 下载视频片段
        video_path = OUTPUT_DIR / f"fashion_clip_{timestamp}_{i}.mp4"
        download_file(video_result["video_url"], video_path)
        video_paths.append(video_path)

    if not video_paths:
        print("❌ 没有成功生成任何视频片段")
        sys.exit(1)

    # ===== 步骤 3: 拼接视频 =====
    if len(video_paths) > 1:
        final_path = OUTPUT_DIR / f"fashion_video_{timestamp}_final.mp4"
        concatenate_videos(video_paths, final_path)
    else:
        final_path = video_paths[0]

    # ===== 完成 =====
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
