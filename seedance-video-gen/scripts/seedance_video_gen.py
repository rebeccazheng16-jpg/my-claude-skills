#!/usr/bin/env python3
"""
Seedance 1.5 Pro Video Generation Script v1.0
通过火山引擎 Ark API (doubao-seedance-1-5-pro-251215) 生成视频并保存到本地
异步模式：提交 → 轮询 → 下载
支持：文生视频、图生视频（首帧/首尾帧）、草稿预览
默认：9:16, 720p, 5s, 带音频
"""

import urllib.request
import urllib.error
import json
import base64
import sys
import os
import time
import argparse
from datetime import datetime


API_KEY = "fc882ab9-bc70-4999-8a7a-df978795cf3b"
MODEL = "doubao-seedance-1-5-pro-251215"
BASE_URL = "https://ark.cn-beijing.volces.com/api/v3/contents/generations/tasks"
DEFAULT_OUTPUT_DIR = os.path.expanduser("~/Desktop")

# 默认参数
DEFAULT_RATIO = "9:16"
DEFAULT_RESOLUTION = "720p"
DEFAULT_DURATION = 5
DEFAULT_GENERATE_AUDIO = True

# 轮询参数
POLL_INTERVAL = 10            # 秒
MAX_POLL_ATTEMPTS = 120       # 最多轮询 120 次 = 20 分钟


def _api_request(url, data=None, method="GET"):
    """发送 API 请求"""
    headers = {
        "Authorization": "Bearer {}".format(API_KEY),
        "Content-Type": "application/json"
    }

    body = json.dumps(data).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")), None
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        try:
            err_json = json.loads(error_body)
            # Ark API 错误格式
            err_obj = err_json.get("error", {})
            msg = err_obj.get("message", error_body[:300])
            code = err_obj.get("code", "")
            if code:
                msg = "{}: {}".format(code, msg)
        except Exception:
            msg = error_body[:300]
        return None, "HTTP {}: {}".format(e.code, msg)
    except urllib.error.URLError as e:
        return None, "网络错误: {}".format(e.reason)
    except Exception as e:
        return None, "未知错误: {}".format(str(e))


def _image_to_data_url(image_path):
    """读取本地图片并转为 data URL"""
    path = os.path.expanduser(image_path)
    if not os.path.exists(path):
        print("[错误] 图片不存在: {}".format(path))
        return None

    ext = os.path.splitext(path)[1].lower()
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".gif": "image/gif",
        ".heic": "image/heic",
        ".heif": "image/heif"
    }
    mime_type = mime_map.get(ext, "image/jpeg")

    with open(path, "rb") as f:
        img_data = base64.b64encode(f.read()).decode("utf-8")

    size_mb = os.path.getsize(path) / (1024 * 1024)
    if size_mb > 30:
        print("[错误] 图片超过 30MB 限制: {:.1f}MB".format(size_mb))
        return None

    print("[图片] 已加载: {} ({:.1f} MB)".format(os.path.basename(path), size_mb))
    return "data:{};base64,{}".format(mime_type, img_data)


def generate_video(
    prompt,
    output_name=None,
    output_dir=None,
    duration=None,
    ratio=None,
    resolution=None,
    generate_audio=None,
    camera_fixed=False,
    watermark=False,
    first_frame=None,
    last_frame=None,
    draft=False,
    seed=-1,
    return_last_frame=False
):
    """
    调用 Seedance 1.5 Pro API 生成视频

    Args:
        prompt: 视频描述提示词（中文或英文）
        output_name: 输出文件名（不含扩展名）
        output_dir: 输出目录
        duration: 视频时长（4-12秒），-1 自动
        ratio: 宽高比（9:16/16:9/4:3/3:4/1:1/21:9/adaptive）
        resolution: 分辨率（480p/720p/1080p）
        generate_audio: 是否生成音频
        camera_fixed: 是否固定镜头
        watermark: 是否加水印
        first_frame: 首帧图片路径（图生视频）
        last_frame: 尾帧图片路径（首尾帧模式）
        draft: 草稿模式（480p 预览，低消耗）
        seed: 随机种子（-1 随机）
        return_last_frame: 是否返回最后一帧 PNG
    """
    use_dir = output_dir or DEFAULT_OUTPUT_DIR
    use_duration = duration if duration is not None else DEFAULT_DURATION
    use_ratio = ratio or DEFAULT_RATIO
    use_resolution = resolution or DEFAULT_RESOLUTION
    use_audio = generate_audio if generate_audio is not None else DEFAULT_GENERATE_AUDIO

    os.makedirs(use_dir, exist_ok=True)

    # 草稿模式约束
    if draft:
        use_resolution = "480p"
        print("[草稿模式] 分辨率强制为 480p")

    # 构建 content 数组
    content = [{"type": "text", "text": prompt}]

    # 首帧图片
    if first_frame:
        if first_frame.startswith("http"):
            img_url = first_frame
        else:
            img_url = _image_to_data_url(first_frame)
            if not img_url:
                return None
        content.append({
            "type": "image_url",
            "image_url": {"url": img_url},
            "role": "first_frame"
        })
        # 图生视频默认用 adaptive 比例
        if ratio is None:
            use_ratio = "adaptive"

    # 尾帧图片
    if last_frame:
        if last_frame.startswith("http"):
            img_url = last_frame
        else:
            img_url = _image_to_data_url(last_frame)
            if not img_url:
                return None
        content.append({
            "type": "image_url",
            "image_url": {"url": img_url},
            "role": "last_frame"
        })

    # 构建请求体
    payload = {
        "model": MODEL,
        "content": content,
        "ratio": use_ratio,
        "resolution": use_resolution,
        "duration": use_duration,
        "generate_audio": use_audio,
        "camera_fixed": camera_fixed,
        "watermark": watermark,
        "draft": draft,
        "seed": seed
    }

    if return_last_frame:
        payload["return_last_frame"] = True

    # 打印请求信息
    mode = "草稿" if draft else ("首尾帧" if last_frame else ("图生视频" if first_frame else "文生视频"))
    print("\n" + "=" * 60)
    print("[Seedance 1.5 Pro] 视频生成")
    print("=" * 60)
    print("[配置] 时长={}s | 比例={} | 分辨率={} | 音频={} | 模式={}".format(
        use_duration, use_ratio, use_resolution, "开" if use_audio else "关", mode))
    prompt_preview = prompt[:120] + ("..." if len(prompt) > 120 else "")
    print("[提示词] {}".format(prompt_preview))

    # ========== 步骤 1：提交请求 ==========
    print("\n[步骤1] 提交视频生成请求...")
    result, err = _api_request(BASE_URL, data=payload, method="POST")
    if err:
        print("[错误] 提交失败: {}".format(err))
        return None

    task_id = result.get("id")
    if not task_id:
        print("[错误] 响应中没有 task id")
        print(json.dumps(result, indent=2, ensure_ascii=False)[:500])
        return None

    print("[成功] 任务已提交: {}".format(task_id))

    # ========== 步骤 2：轮询状态 ==========
    print("\n[步骤2] 等待视频生成（每{}秒检查一次）...".format(POLL_INTERVAL))
    poll_url = "{}/{}".format(BASE_URL, task_id)

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        time.sleep(POLL_INTERVAL)

        status_result, err = _api_request(poll_url, method="GET")
        if err:
            print("[轮询 {}/{}] 查询失败: {}，继续等待...".format(attempt, MAX_POLL_ATTEMPTS, err))
            continue

        status = status_result.get("status", "unknown")
        elapsed = attempt * POLL_INTERVAL
        mins = elapsed // 60
        secs = elapsed % 60

        if status == "succeeded":
            time_str = "{}分{}秒".format(mins, secs) if mins > 0 else "{}秒".format(secs)
            print("[轮询 {}/{}] 生成完成！(耗时约{})".format(attempt, MAX_POLL_ATTEMPTS, time_str))
            break
        elif status in ("failed", "cancelled", "expired"):
            error_info = status_result.get("error", {})
            print("[失败] 状态: {} | 错误: {}".format(status, json.dumps(error_info, ensure_ascii=False)))
            return None
        else:
            time_str = "{}分{}秒".format(mins, secs) if mins > 0 else "{}秒".format(secs)
            print("[轮询 {}/{}] {} (已等待{})".format(attempt, MAX_POLL_ATTEMPTS, status, time_str))
    else:
        print("\n[超时] 超过最大等待时间（{}分钟）".format(MAX_POLL_ATTEMPTS * POLL_INTERVAL // 60))
        print("[任务ID] {} （可稍后手动查询）".format(task_id))
        return None

    # ========== 步骤 3：下载视频 ==========
    print("\n[步骤3] 下载视频...")

    content_data = status_result.get("content", {})
    video_url = content_data.get("video_url", "")

    if not video_url:
        print("[错误] 响应中没有视频 URL")
        print("[调试] {}".format(json.dumps(status_result, indent=2, ensure_ascii=False)[:800]))
        return None

    # 构建文件名
    if output_name:
        filename = "{}.mp4".format(output_name)
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = "seedance_{}.mp4".format(timestamp)

    filepath = os.path.join(use_dir, filename)

    print("[下载] → {}".format(filename))

    try:
        dl_req = urllib.request.Request(video_url)
        with urllib.request.urlopen(dl_req, timeout=300) as resp:
            video_data = resp.read()

        with open(filepath, "wb") as f:
            f.write(video_data)

        file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print("[已保存] {} ({:.1f} MB)".format(filepath, file_size_mb))

    except Exception as e:
        print("[下载失败] {}".format(str(e)))
        print("[视频URL] {} （24小时内有效，请手动下载）".format(video_url))
        return None

    # 下载最后一帧（如果请求了）
    last_frame_url = content_data.get("last_frame_url", "")
    if last_frame_url and return_last_frame:
        frame_path = os.path.join(use_dir, "{}_lastframe.png".format(output_name or "seedance"))
        try:
            with urllib.request.urlopen(last_frame_url, timeout=60) as resp:
                with open(frame_path, "wb") as f:
                    f.write(resp.read())
            print("[最后一帧] {}".format(frame_path))
        except Exception as e:
            print("[最后一帧下载失败] {}".format(str(e)))

    # 打印使用信息
    usage = status_result.get("usage", {})
    if usage:
        tokens = usage.get("total_tokens", 0)
        print("[Token消耗] {}".format(tokens))

    actual_duration = status_result.get("duration", use_duration)
    actual_fps = status_result.get("framespersecond", 24)

    print("\n" + "=" * 60)
    print("[完成] 视频已生成")
    print("  → {}".format(filepath))
    print("  → 时长: {}s | {}fps | {}".format(actual_duration, actual_fps, use_resolution))
    print("=" * 60)

    return [filepath]


def main():
    parser = argparse.ArgumentParser(description="Seedance 1.5 Pro Video Generation")
    parser.add_argument("prompt", help="视频描述提示词（中文或英文）")
    parser.add_argument("-n", "--name", help="输出文件名（不含扩展名）")
    parser.add_argument("-o", "--output-dir", help="输出目录", default=None)
    parser.add_argument("-d", "--duration", type=int,
                        help="视频时长（4-12秒，-1自动）", default=None)
    parser.add_argument("-a", "--ratio",
                        choices=["9:16", "16:9", "4:3", "3:4", "1:1", "21:9", "adaptive"],
                        help="宽高比", default=None)
    parser.add_argument("-r", "--resolution", choices=["480p", "720p", "1080p"],
                        help="分辨率", default=None)
    parser.add_argument("--audio", dest="generate_audio", action="store_true", default=None,
                        help="开启音频生成（默认）")
    parser.add_argument("--no-audio", dest="generate_audio", action="store_false",
                        help="关闭音频生成（静音视频）")
    parser.add_argument("--camera-fixed", action="store_true", default=False,
                        help="固定镜头")
    parser.add_argument("--watermark", action="store_true", default=False,
                        help="添加水印")
    parser.add_argument("-i", "--first-frame", help="首帧图片路径或URL", default=None)
    parser.add_argument("--last-frame", help="尾帧图片路径或URL", default=None)
    parser.add_argument("--draft", action="store_true", default=False,
                        help="草稿模式（480p低消耗预览）")
    parser.add_argument("--seed", type=int, default=-1,
                        help="随机种子（-1随机）")
    parser.add_argument("--return-last-frame", action="store_true", default=False,
                        help="返回最后一帧PNG（用于视频衔接）")

    args = parser.parse_args()

    result = generate_video(
        prompt=args.prompt,
        output_name=args.name,
        output_dir=args.output_dir,
        duration=args.duration,
        ratio=args.ratio,
        resolution=args.resolution,
        generate_audio=args.generate_audio,
        camera_fixed=args.camera_fixed,
        watermark=args.watermark,
        first_frame=args.first_frame,
        last_frame=args.last_frame,
        draft=args.draft,
        seed=args.seed,
        return_last_frame=args.return_last_frame
    )

    if result:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
