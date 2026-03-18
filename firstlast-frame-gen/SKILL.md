# 首尾帧静图生成 Skill

> 用 Nano Banana 为每段视频生成首帧和尾帧静图，再交给即梦（Jimeng）做首尾帧视频生成，保证人物连贯一致。

## 触发方式

用户说以下任一内容时使用本 skill：
- "帮我生成首尾帧"
- "给这段生成首帧/尾帧"
- "首尾帧素材"
- 提供了视频脚本段落，要求生成对应的静图

---

## 核心原理

```
[Nano Banana 生成首帧] → [Nano Banana 生成尾帧] → [用户导入即梦]
      ↓                          ↓
  描述该段开始时              描述该段结束时
  人物是什么状态               人物是什么状态
```

即梦的首尾帧功能：上传首帧+尾帧图片，即梦生成中间的动态过渡。
人物一致性由 Nano Banana 的参考图（seed image）保证。

---

## 调用命令

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "英文提示词" \
  -r ~/Desktop/角色种子图.png \
  -m gemini-3.1-flash-image-preview \
  -a 9:16 \
  -n 文件名 \
  -o ~/Desktop
```

**关键参数：**
- 模型：`gemini-3.1-flash-image-preview`（唯一支持9:16且不被地区封锁的模型）
- 比例：`9:16`（竖屏，适配TikTok/Reels）
- 参考图：传角色的 seed image（AI生成图可以传，真人照片会被安全策略拦截）

---

## 提示词结构

### 首帧（描述这段视频开始时的状态）

```
[角色固定描述] + [场景环境] + [人物此刻的动作/姿态] + [情绪/表情] + [风格词]
```

### 尾帧（描述这段视频结束时的状态）

```
[角色固定描述，需体现变化] + [场景环境] + [人物完成动作后的状态] + [表情/情绪] + [风格词]
```

**要点：**
- 首帧和尾帧的角色描述要一致（同一套服装、同一个场景）
- 尾帧要体现"这段发生了什么"的结果状态
- 表情写自然平静（`calm natural smile`），不要写 excited/dramatic
- 防畸形词加在末尾（见下方）

---

## 防畸形通用词（每次必加在提示词末尾）

```
Anatomically correct, exactly two hands, no extra limbs, no extra fingers,
no deformed hands, no floating limbs, natural human proportions.
```

按场景追加：
| 场景 | 追加 |
|------|------|
| 手持物品 | `one hand holding [item], other hand relaxed at side` |
| 双手入镜 | `both hands clearly visible, five fingers each` |
| 产品展示 | `no deformed packaging, product label clearly readable` |

---

## Kirana 角色固定描述

**旧造型（seg01-02，出门前）：**
```
A beautiful young Indonesian-Chinese Muslim woman in her early 20s with extremely fair
porcelain skin and luminous glass-skin glow. She wears a loose cream/beige pashmina hijab
draped gracefully and a tailored camel blazer.
```

**新造型（seg03+，换装后）：**
```
A beautiful young Indonesian-Chinese Muslim woman in her early 20s with extremely fair
porcelain skin and luminous glass-skin glow. She wears a loose milk-tea caramel brown
pashmina hijab, an oversized cream white knit sweater, and relaxed wide-leg light blue
denim jeans.
```

**种子图路径：** `~/Desktop/Kirana_seed_v1.png`

---

## 通用风格词（加在每张图末尾）

```
Natural lifestyle photography, Instagram aesthetic, soft natural light,
half-body shot, clean minimal background.
```

---

## 完整工作流示例（3段vlog）

| 段落 | 首帧描述重点 | 尾帧描述重点 |
|------|------------|------------|
| seg01 窗边 | 坐着低头看手机 | 站起来，手拿手机，准备出门 |
| seg02 衣帽间 | 站在衣帽间浏览衣服 | 手持选好的白针织毛衣，满意地看着 |
| seg03 新造型 | 穿好新装站在镜前（已换造型） | 拎包走到衣帽间门口，准备出发 |

每段提交2个 Nano Banana 任务（首帧+尾帧），可并行运行。

---

## 注意事项

1. **Veo 尾帧不可用**：Veo 视频末尾容易漂移（人物换装、背影、闭眼），不要从 Veo 视频提取尾帧，必须用 Nano Banana 专门生成
2. **3张以上图片先征求用户同意**再并行提交
3. **生成完成后打开图片**让用户确认，再进入下一步
4. 即梦不支持 API，将首尾帧图片路径告知用户，让用户手动上传

---

## 相关文件

- Nano Banana 脚本：`~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py`
- Kirana 素材库：`~/Desktop/Kirana_frame*.png`
- 角色种子图：`~/Desktop/Kirana_seed_v1.png`
