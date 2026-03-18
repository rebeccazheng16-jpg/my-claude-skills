# 九宫格图片生成器

根据参考图片生成3x3九宫格大图，每个格子为9:16竖版，包含不同pose/表情。

## 使用场景

- 用户说"生成九宫格"、"做个九宫格"、"9grid"
- 需要一张大图里展示同一人物/角色的多个pose

## 使用方法

### 输入参数
- **参考图片**（必需）：人物参考图路径
- **人物描述**（可选）：人物外观描述，默认从参考图推断
- **产品描述**（可选）：需要出现在画面中的产品描述
- **输出文件名**（可选）：默认 `九宫格_[日期].png`

### 流程

1. **确认生成**：九宫格需要生成9张图片，**必须先告知用户并获得同意**再开始（超过3张图片的规则）
2. **生成9张独立图片**：使用 Nano Banana 脚本逐张生成，每张不同pose
3. **拼接九宫格**：用PIL将9张图拼成3x3大图
4. **保存并打开**：保存到桌面，自动打开

### 9种Pose模板

根据场景选择合适的pose组合。以下为默认产品展示pose：

| 格子 | Pose | 英文提示词关键词 |
|------|------|-----------------|
| 1 | 正面展示 | holding product in front, looking at camera, friendly smile |
| 2 | 微笑特写 | warm smile, holding product near face, soft lighting |
| 3 | 查看产品 | examining product closely, curious expression, reading label |
| 4 | 推荐手势 | pointing at product, recommending, enthusiastic expression |
| 5 | 使用产品 | squeezing/opening product, demonstrating use |
| 6 | 3/4侧面 | three-quarter view, elegant pose, product visible |
| 7 | 镜子自拍 | mirror selfie style, casual, showing product |
| 8 | 产品特写 | holding product close to camera, product in focus |
| 9 | 涂抹/使用中 | applying product on skin, natural skincare routine |

### 生成命令

```bash
python3 ~/.claude/skills/nano-banana-image-gen/scripts/gemini_image_gen.py \
  "[英文提示词]" \
  -r "[参考图路径]" \
  -a "9:16" \
  -n "[文件名]"
```

### 拼接脚本

```bash
python3 ~/.claude/skills/9grid-generator/scripts/compose_grid.py \
  --input-dir [图片目录] \
  --output [输出路径]
```

## 重要规则

- **生成前必须征求用户同意**（9张图片 > 3张的阈值）
- 每张图的提示词必须包含人物外观描述以保持一致性
- 如果有产品，提示词中强调产品文字清晰不变形
- 所有图片统一9:16比例
- 使用后台任务并行生成以加快速度（最多3个并行，分3批）
- 最终大图尺寸：2304x4032（每格768x1344）
- 保存到桌面并自动打开
