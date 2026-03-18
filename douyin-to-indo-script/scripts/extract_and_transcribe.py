#!/usr/bin/env python3
"""
extract_and_transcribe.py
从视频文件中提取音频并使用 OpenAI Whisper API 进行中文语音识别。
Usage: python3 extract_and_transcribe.py <video_path_or_url> [--output transcript.txt]
"""

import os
import sys
import argparse
import subprocess
import tempfile
from pathlib import Path


def check_dependencies():
    """检查必要依赖是否安装"""
    missing = []
    try:
        import openai  # noqa: F401
    except ImportError:
        missing.append("openai (pip install openai)")
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True)
    if result.returncode != 0:
        missing.append("ffmpeg (brew install ffmpeg)")
    if missing:
        print("❌ 缺少以下依赖，请先安装：")
        for dep in missing:
            print(f"   - {dep}")
        sys.exit(1)


def extract_audio(video_path: str, output_path: str) -> bool:
    """使用 ffmpeg 从视频中提取 MP3 音频"""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                  # 不要视频流
        "-acodec", "libmp3lame",
        "-ar", "16000",         # Whisper 推荐采样率
        "-ac", "1",             # 单声道
        "-q:a", "5",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ 音频提取失败:\n{result.stderr}")
        return False
    print(f"✅ 音频已提取: {output_path}")
    return True


def transcribe_audio(audio_path: str) -> str:
    """调用 OpenAI Whisper API 进行中文语音识别"""
    from openai import OpenAI

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("❌ 未找到 OPENAI_API_KEY 环境变量")
        print("   请设置: export OPENAI_API_KEY='your-key-here'")
        sys.exit(1)

    client = OpenAI(api_key=api_key)

    print("🎙️  正在调用 Whisper API 识别语音...")
    with open(audio_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file,
            language="zh",          # 强制指定中文
            response_format="text"
        )
    return response.strip()


def main():
    parser = argparse.ArgumentParser(description="从视频提取中文口播稿")
    parser.add_argument("video", help="视频文件路径（本地路径）")
    parser.add_argument("--output", "-o", default=None,
                        help="输出文字稿文件路径（可选，默认打印到终端）")
    args = parser.parse_args()

    check_dependencies()

    video_path = args.video
    if not os.path.exists(video_path):
        print(f"❌ 文件不存在: {video_path}")
        sys.exit(1)

    # 创建临时音频文件
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        audio_path = tmp.name

    try:
        print(f"📹 处理视频: {video_path}")
        if not extract_audio(video_path, audio_path):
            sys.exit(1)

        transcript = transcribe_audio(audio_path)

        if args.output:
            Path(args.output).write_text(transcript, encoding="utf-8")
            print(f"✅ 文字稿已保存: {args.output}")
        else:
            print("\n===== 口播稿原文 =====")
            print(transcript)
            print("======================\n")

        return transcript

    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)


if __name__ == "__main__":
    main()
