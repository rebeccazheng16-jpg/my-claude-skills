# Kirana 数字人视频生产工作流

> 本 skill 是 Kirana 视频生产的**主入口说明书**。
> 其他 skill（veo-video-gen, nano-banana-image-gen, veirfoo-pdrn-mask-kirana）是子工具，本文件是导航。

---

## 角色档案

| 属性 | 值 |
|------|-----|
| 名字 | Kirana |
| 定位 | 印尼华裔穆斯林，20-25岁，luxury lifestyle 博主 |
| Soul | 心静如水纯净善良的有钱女人。看到你挖了一大勺鱼子酱送进嘴里并浮现痛苦的表情，她只会笑笑并说"这东西真的好咸" |
| 语言 | 印尼语口播 |
| 三视图（唯一人脸锚点） | `~/Desktop/model/三视图/Kirana_chanel_turnaround_v2.jpg` |
| 素材库 | `~/Desktop/model/Kirana/` |

> ⚠️ **三视图路径是唯一真相来源**。如果三视图文件更新，本文件也要同步更新。

---

## 全局铁律（任何场景都适用）

### 1. 绝不在提示词里写角色外观
- ❌ 错误：`caramel-brown hijab, white cable-knit sweater`
- ✅ 正确：只传三视图参考图，提示词只写场景/动作/构图
- **原因**：文字描述优先级高于参考图，会覆盖掉三视图，导致角色面目全非

### 2. Veo 提示词必须加 negative prompt 防字幕
**固定 negative prompt（每次都加，不能省）：**
```
voiceover, narration, exaggerated expressions, dramatic gestures, theatrical performance,
text overlay, subtitle, caption, camera zoom, camera push, background music,
dark skin, yellow skin, warm color cast, foggy, hazy, soft focus, washed out, blurry
```
> ⚠️ `text overlay, subtitle, caption` 是防止视频里出现文字的核心词，**不能删**

### 3. 产品展示只展示银色管身
- VEIRFOO 产品参考图（`~/Desktop/Veirfoo/微信图片_20260223160455_35_64.jpg`）包含银色管 + 纸盒两件物体
- 传入该图时，提示词中必须加：`Show ONLY the silver cylindrical tube — ignore any box or cardboard packaging`

### 4. Veo 生成后必须验证
- 检查文件大小：正常 8s 720p 应 >1.5MB（<0.5MB = 黑屏）
- **听音频**：是角色在对话（口播）还是配音员在读稿（旁白）？旁白=硬标准失败，直接重跑
- 数据类台词（数字+权威背书）天然触发旁白模式 → 提示词必须加"speaks naturally as if telling a close friend, direct eye contact" + negative prompt 加 `documentary style, announcement voice, off-screen narrator, statistics reading`

### 5. 台词词数控制（8s 视频）
| 语速类型 | 词数 | 适用场景 |
|---------|------|---------|
| 正常贵妇语速 | 18–21词 | 科普、解释 |
| 偏慢（留停顿感） | 14–17词 | CTA、情感结尾 |
| 避免 | >22词 | 口型提前闭合 |

---

## 工作流步骤

### Step 1：确认脚本和台词
从 Obsidian 读取对应脚本的印尼语台词：
```
/Users/zhengrebecca/Documents/Obsidian Vault/30-Content/TikTok脚本/[脚本文件].md
```
或直接从源文件读取：
```
~/Desktop/Veirfoo/VEIRFOO_印尼TikTok投流脚本_5条_中印双语.txt
```

### Step 2：生成首尾帧（静图）
调用 **nano-banana-image-gen** skill，关键规则：
- 参考图：`-r ~/Desktop/model/三视图/Kirana_chanel_turnaround_v2.jpg`
- 模型：`gemini-3-pro-image-preview`，分辨率：4K，宽高比：9:16
- 提示词只写场景/动作，不写人物外观
- 输出路径：`~/Desktop/model/Kirana/[项目名]/[项目]_S[编号]_[first/last].jpg`

**自审（硬标准，失败静默重跑最多2次）：**
- [ ] 头巾颜色与三视图一致
- [ ] 服装与三视图一致
- [ ] 手部解剖正确，无多余手指/漂浮肢体
- [ ] 构图：半身 9:16，不裁头顶

**自审（软标准，通过后附一句评语）：**
- [ ] 气质：从容不表演，"她只会笑笑"的状态
- [ ] 整体清晰，自然光感，非广告棚感

### Step 3：用首尾帧生成 Veo 视频
调用 **veo-video-gen** skill，关键规则：
```bash
# API Key 自动从 ~/.config/gemini_api_key 读取，无需手动传入
# 首次配置：echo "你的APIKey" > ~/.config/gemini_api_key
python3 ~/.claude/skills/veo-video-gen/scripts/veo_video_gen.py \
  "[提示词]" \
  -i "[首帧路径]" -l "[尾帧路径]" \
  -r 720p -d 8 -a "9:16" \
  --negative-prompt "[固定negative prompt]" \
  -n "[文件名]" -o "[输出目录]"
```

**完整可用模板（直接换台词即可，已验证）：**

正向 prompt：
```
Woman on cream ivory sofa by a window with sheer white curtains on the left side, soft natural side light, bright airy cream interior, soft bokeh background. She [动作描述], speaks naturally and conversationally as if telling a close friend: '[印尼语台词]'. Calm serene wealthy young woman, subtle refined expressions, gentle composed demeanor. Minimal natural gestures, subtle expressions, NOT exaggerated. Fixed camera, no movement. Half-body portrait, 9:16 vertical. Anatomically correct, exactly two hands, no extra limbs, no extra fingers, no deformed hands, no floating limbs.
```

Negative prompt（固定，不可删减）：
```
voiceover, narration, documentary style, announcement voice, off-screen narrator, statistics reading, exaggerated expressions, dramatic gestures, theatrical performance, text overlay, subtitle, caption, camera zoom, camera push, background music, dark skin, yellow skin, warm color cast, foggy, hazy, soft focus, washed out, blurry
```

> ⚠️ 数据类台词（含数字/百分比/权威背书）天然触发旁白，必须用 "speaks...as if telling a close friend" 包裹，且数字建议印尼语拼写（`tiga puluh satu persen` 而非 `31%`）

**分辨率约束：**
- 720p + 文生视频：支持 4/6/8s
- 720p + **首尾帧模式**：只支持 **6/8s**（4s 报 use case not supported）← **默认用 8s**
- 1080p/4K：只支持 8s，4K 有概率生成黑屏

### Step 4：视频验证
```bash
ls -lh ~/Desktop/model/Kirana/[项目名]/*.mp4
# 正常 8s 720p 应 >1.5MB
```

### Step 5：（可选）去除音频
```bash
# 获取 ffmpeg 路径
python3 -c "import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())"
# 去除音频
[ffmpeg路径] -i input.mp4 -an -c:v copy output_silent.mp4
```

---

## 常见动作提示词库

| 动作类型 | 提示词片段 |
|---------|-----------|
| 看手机→抬头 | `looking down at vivid orange iPhone 17 Pro Max in hands with a slight smile, then gently lowers the phone and looks up at camera with a composed knowing expression` |
| 讲解手势 | `one hand resting on knee, other hand slightly raised with subtle open-palm gesture — completing a clear point` |
| 触脸思考 | `gently touches her cheek with one fingertip with a slight thoughtful lean forward, looking toward camera with composed explaining expression` |
| 手持银管展示 | `holds up a silver cylindrical tube at chest height with composed confident expression` |
| 上脸涂抹 | `gently touches her cheek with fingertips, slight forward lean, composed satisfied expression` |
| CTA 指向镜头 | `raises one finger toward camera with refined gesture, gentle composed smile, unhurried` |

---

## 项目索引

| 项目 | 路径 | 脚本 | 状态 |
|------|------|------|------|
| 02_韩国PDRN | `~/Desktop/model/Kirana/02_韩国PDRN/` | 投流脚本02 | 进行中 |
| T3_闺蜜安利型 | `~/Desktop/model/Kirana/T3/` | T3_闺蜜安利型 | 已完成 |

---

## 常见错误排查

| 错误 | 原因 | 解决 |
|------|------|------|
| HTTP 403 unregistered callers | background 任务未继承 GEMINI_API_KEY | 命令前加 `GEMINI_API_KEY="..."` |
| RAI safety filter / audio issue | Veo 音频安全过滤 | 调整提示词，减少强调词 |
| 视频文件极小（<0.5MB）| 黑屏 | 换 720p，避免 4K |
| 产品图出现管+盒 | 参考图包含两件物体 | 提示词加 "Show ONLY the silver cylindrical tube" |
| 角色外观与三视图不符 | 提示词写了外观描述 | 删除外观描述，只传三视图 |
| yt-dlp 下载 XHS 视频 | xhs-video-downloader skill 只支持账号主页 | 直接用 `python3 -m yt_dlp "xhslink..."` |

---

## 相关 Skill

| Skill | 用途 |
|-------|------|
| `nano-banana-image-gen` | 首尾帧静图生成 |
| `veo-video-gen` | Veo 3.1 视频生成 |
| `veirfoo-pdrn-mask-kirana` | PDRN 视频详细规范（含已验证动作片段） |
| `firstlast-frame-gen` | 首尾帧工作流总览 |
| `seedance-video-gen` | 备用视频生成（有音频控制） |
