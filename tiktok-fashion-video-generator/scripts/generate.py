#!/usr/bin/env python3
"""
TikTok Fashion Video Generator
从参考图生成穿搭展示视频 + 文案
"""

import os
import sys
import json
import time
import httpx
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

# ============ 配置 ============

API_KEY = os.getenv("DOUBAO_ARK", "")
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"

# 尝试从 api-keys-manager 获取
if not API_KEY:
    try:
        from subprocess import run, PIPE
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
    "模特自然站立面向镜头，双手插在裤兜或自然下垂，身体轻微左右摆动后站定。镜头固定。",
    "模特双手缓缓抬起微微张开展示上衣，随后手臂放下。镜头固定。",
    "模特缓慢向右转身约90度展示侧面轮廓，站定后左手轻搭腰间。镜头固定。",
    "模特继续向右转身至背对镜头，停顿展示背面，随后微微回头看向镜头。镜头固定。",
    "模特从背面缓缓转回正面，双手自然下垂，站定后调整站姿。镜头固定。",
    "模特面向镜头站定，恢复初始姿势，嘴角微扬，轻轻点头后静止。镜头固定。",
]

SEGMENTS_MIRROR_SELFIE = [
    "模特保持手机自拍姿势，身体轻微左右摆动，目光看向镜头，嘴角微扬。镜头固定。",
    "模特左手缓缓抬起轻触发丝，头微微侧向一边，随后手放下。镜头固定。",
    "模特身体缓慢向右侧转约20度，展示侧面轮廓，目光依然看向镜头。镜头固定。",
    "模特身体缓缓转回正面，嘴唇微张后闭合，眼神略带俏皮。镜头固定。",
    "模特微微挺胸调整站姿，下巴轻抬，目光自信看向镜头。镜头固定。",
    "模特保持姿势，嘴角缓缓上扬露出微笑，轻轻点头后静止。镜头固定。",
]

SEGMENTS_UPPER_BODY = [
    "模特面向镜头自然微笑，头部轻微左右摆动后正视镜头。镜头固定。",
    "模特右手抬起整理衣领或发丝，目光短暂下移后抬头。镜头固定。",
    "模特身体略微向右侧倾斜，展示侧面轮廓，随后回正。镜头固定。",
    "模特面向镜头，嘴角上扬露出微笑，轻轻点头后静止。镜头固定。",
]

# ============ 文案模板 ============

COPY_TEMPLATES = {
    "indonesia": {
        "female": {
            "casual": [
                {
                    "title": "Outfit ke kantor tapi tetap santai ✨",
                    "caption": "Siapa bilang ke kantor harus ribet? 🤭\n\nSimple tapi tetap stylish!\n\nCocok buat kamu yang mau tampil rapi tanpa effort lebih 💅\n\nSave dulu biar nggak lupa! 📌",
                    "hashtags": ["#ootdindonesia", "#outfitkantor", "#fashiontiktok", "#workoutfit", "#styleinspo", "#ootdindo", "#fyp"]
                },
                {
                    "title": "Basic items tapi hasil WOW 🔥",
                    "caption": "Nggak perlu baju mahal buat tampil kece ✨\n\nKuncinya? Pilih warna yang matching!\n\nKalian suka outfit yang mana? Comment ya! 👇",
                    "hashtags": ["#ootdmurah", "#mixmatch", "#fashionmurah", "#outfitinspo", "#dailyoutfit", "#tiktokviral", "#racunshopee"]
                },
                {
                    "title": "1 outfit, bisa dipake kemana aja 👀",
                    "caption": "Outfit ini literally jadi bestie aku sekarang 😍\n\n✅ Ke kantor - bisa\n✅ Hangout - bisa\n✅ Kondangan - bisa juga!\n\nYang setuju angkat tangan! 🙋‍♀️",
                    "hashtags": ["#outfitideas", "#ootdindokece", "#capsulewardrobe", "#mixandmatch", "#tiktokindonesia", "#viral"]
                },
            ],
            "formal": [
                {
                    "title": "Meeting look yang bikin auto pede 💼",
                    "caption": "First impression itu penting banget!\n\nOutfit formal tapi nggak kaku ✨\n\nPerfect buat meeting atau interview~",
                    "hashtags": ["#formaloutfit", "#meetinglook", "#officewear", "#workstyle", "#professionalook", "#fyp"]
                },
            ],
        },
        "male": {
            "casual": [
                {
                    "title": "Outfit cowok simple tapi kece 🔥",
                    "caption": "Buat kalian yang bingung mau pake apa...\n\nINI JAWABANNYA! 🙌\n\nSimple, nyaman, dan nggak perlu mikir lama~",
                    "hashtags": ["#ootdcowok", "#outfitpria", "#fashionpria", "#menswear", "#casualstyle", "#fyp"]
                },
            ],
        },
    },
    "china": {
        "female": {
            "casual": [
                {
                    "title": "通勤穿搭 | 简约不简单 ✨",
                    "caption": "每天早上不知道穿什么？\n\n这套look闭眼入！简单百搭不出错～\n\n点赞收藏不迷路！",
                    "hashtags": ["#穿搭分享", "#通勤穿搭", "#ootd", "#显瘦穿搭", "#抖音穿搭", "#每日穿搭"]
                },
                {
                    "title": "一衣多穿 | 这件单品太能打了 🔥",
                    "caption": "姐妹们！这件真的绝了！\n\n上班、约会、逛街都能穿～\n\n评论区告诉我你们喜欢哪套？",
                    "hashtags": ["#一衣多穿", "#胶囊衣橱", "#穿搭模板", "#时尚穿搭", "#显瘦神器"]
                },
            ],
        },
        "male": {
            "casual": [
                {
                    "title": "男生穿搭 | 简约风永不过时 👔",
                    "caption": "不会穿搭的兄弟看过来！\n\n这套直接抄作业就行～\n\n简单干净 不费脑子",
                    "hashtags": ["#男生穿搭", "#男装推荐", "#简约风", "#型男穿搭", "#ootd男"]
                },
            ],
        },
    },
    "global": {
        "female": {
            "casual": [
                {
                    "title": "Outfit inspo for you ✨",
                    "caption": "Simple but make it fashion! 💅\n\nPerfect for work or casual hangouts~\n\nSave for later! 📌",
                    "hashtags": ["#ootd", "#outfitinspo", "#fashiontiktok", "#styleinspo", "#whatiwore", "#fyp"]
                },
            ],
        },
        "male": {
            "casual": [
                {
                    "title": "Easy outfit for guys 🔥",
                    "caption": "Keeping it simple today!\n\nThis combo never fails 👌\n\nWhat do you think?",
                    "hashtags": ["#mensoutfit", "#mensfashion", "#ootdmen", "#casualstyle", "#menswear", "#fyp"]
                },
            ],
        },
    },
}


# ============ API 函数 ============

def upload_image(image_path: str) -> str:
    """上传图片到临时存储"""
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
    raise Exception(f"上传失败: {response.text}")


def create_video_task(image_url: str, prompt: str, duration: int = 5) -> str:
    """创建视频生成任务"""
    response = httpx.post(
        f"{BASE_URL}/contents/generations/tasks",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"
        },
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
    """轮询任务状态"""
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
    """下载视频"""
    response = httpx.get(url, timeout=120, follow_redirects=True)
    with open(output_path, "wb") as f:
        f.write(response.content)
    return output_path


def concatenate_videos(video_paths: list, output_path: Path) -> Path:
    """拼接视频"""
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


# ============ 文案生成 ============

def generate_copy(market: str, gender: str, style: str) -> dict:
    """生成文案"""
    import random

    templates = COPY_TEMPLATES.get(market, COPY_TEMPLATES["global"])
    gender_templates = templates.get(gender, templates.get("female", {}))
    style_templates = gender_templates.get(style, gender_templates.get("casual", []))

    if not style_templates:
        style_templates = COPY_TEMPLATES["global"]["female"]["casual"]

    return random.choice(style_templates)


def save_copy(copy_data: dict, output_dir: Path):
    """保存文案"""
    # JSON 格式
    json_path = output_dir / "copy.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(copy_data, f, ensure_ascii=False, indent=2)

    # 文本格式（方便复制）
    txt_path = output_dir / "copy.txt"
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"【标题】\n{copy_data['title']}\n\n")
        f.write(f"【文案】\n{copy_data['caption']}\n\n")
        f.write(f"【标签】\n{' '.join(copy_data['hashtags'])}\n")

    return json_path, txt_path


# ============ 主函数 ============

def main():
    parser = argparse.ArgumentParser(description="TikTok Fashion Video Generator")
    parser.add_argument("image", help="参考图片路径")
    parser.add_argument("--duration", type=int, default=30, choices=[15, 20, 25, 30],
                        help="视频时长(秒)")
    parser.add_argument("--market", default="indonesia", choices=["indonesia", "china", "global"],
                        help="目标市场")
    parser.add_argument("--gender", default="female", choices=["female", "male", "unisex"],
                        help="目标性别")
    parser.add_argument("--style", default="casual", choices=["casual", "formal", "streetwear"],
                        help="穿搭风格")
    parser.add_argument("--scene", default="fullbody", choices=["fullbody", "mirror", "upper"],
                        help="场景类型")
    parser.add_argument("--output", help="输出目录")

    args = parser.parse_args()

    # 检查 API Key
    if not API_KEY:
        print("❌ 错误: 未找到 DOUBAO_ARK API Key")
        print("   请设置环境变量或使用 api-keys-manager 配置")
        sys.exit(1)

    # 检查图片
    image_path = Path(args.image).expanduser()
    if not image_path.exists():
        print(f"❌ 错误: 图片不存在 {image_path}")
        sys.exit(1)

    # 创建输出目录
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(args.output) if args.output else Path.home() / "Downloads" / f"tiktok_fashion_{timestamp}"
    output_dir.mkdir(parents=True, exist_ok=True)
    segments_dir = output_dir / "segments"
    segments_dir.mkdir(exist_ok=True)

    # 选择动作模板
    if args.scene == "mirror":
        segments = SEGMENTS_MIRROR_SELFIE
    elif args.scene == "upper":
        segments = SEGMENTS_UPPER_BODY
    else:
        segments = SEGMENTS_FULLBODY

    # 根据时长选择段数
    num_segments = args.duration // 5
    segments = segments[:num_segments]

    print("=" * 60)
    print("🎬 TikTok Fashion Video Generator")
    print("=" * 60)
    print(f"📸 图片: {image_path}")
    print(f"⏱️  时长: {args.duration}秒 ({num_segments}段)")
    print(f"🎯 市场: {args.market} / {args.gender}")
    print(f"📁 输出: {output_dir}")
    print("=" * 60)

    # 上传图片
    image_url = upload_image(str(image_path))

    # 生成视频段落
    video_paths = []
    last_frame_url = image_url

    for i, prompt in enumerate(segments, 1):
        print(f"\n📹 生成第 {i}/{num_segments} 段")
        print(f"   {prompt[:50]}...")

        try:
            task_id = create_video_task(last_frame_url, prompt, duration=5)
            print(f"   任务ID: {task_id}")

            result = poll_task(task_id)

            video_url = result.get("content", {}).get("video_url")
            if video_url:
                video_path = segments_dir / f"segment_{i}.mp4"
                download_video(video_url, video_path)
                video_paths.append(video_path)
                print(f"   📁 已保存: {video_path.name}")

            # 获取尾帧
            last_frame = result.get("content", {}).get("last_frame_url")
            if last_frame:
                last_frame_url = last_frame

        except Exception as e:
            print(f"   ❌ 失败: {e}")
            continue

    if not video_paths:
        print("\n❌ 没有成功生成任何视频")
        sys.exit(1)

    # 拼接视频
    print(f"\n🔗 拼接 {len(video_paths)} 段视频...")
    final_path = output_dir / "final_video.mp4"
    concatenate_videos(video_paths, final_path)

    # 生成文案
    print(f"\n📝 生成文案...")
    copy_data = generate_copy(args.market, args.gender, args.style)
    json_path, txt_path = save_copy(copy_data, output_dir)

    # 输出结果
    print(f"\n{'=' * 60}")
    print("🎉 完成!")
    print(f"{'=' * 60}")
    print(f"🎬 视频: {final_path}")
    print(f"📝 文案: {txt_path}")
    print(f"⏱️  时长: {len(video_paths) * 5} 秒")
    print(f"\n【标题】\n{copy_data['title']}")
    print(f"\n【文案】\n{copy_data['caption']}")
    print(f"\n【标签】\n{' '.join(copy_data['hashtags'])}")


if __name__ == "__main__":
    main()
