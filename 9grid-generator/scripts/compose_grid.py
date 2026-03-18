"""
九宫格拼接脚本
将目录中的9张图片拼成3x3大图，保持9:16整体比例。
"""
import argparse
import os
import sys
from PIL import Image


def compose_grid(input_dir, output_path, cols=3, rows=3):
    """将input_dir中的图片按文件名排序，拼成 cols x rows 的网格。"""
    files = sorted([
        f for f in os.listdir(input_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))
    ])

    if len(files) < cols * rows:
        print(f"[错误] 需要 {cols * rows} 张图片，目录中只有 {len(files)} 张")
        sys.exit(1)

    files = files[:cols * rows]

    # 读取第一张获取单格尺寸
    first = Image.open(os.path.join(input_dir, files[0]))
    cell_w, cell_h = first.size

    # 创建大图
    grid_w = cell_w * cols
    grid_h = cell_h * rows
    grid = Image.new('RGB', (grid_w, grid_h))

    for idx, f in enumerate(files):
        img = Image.open(os.path.join(input_dir, f))
        # 如果尺寸不一致，resize到第一张的尺寸
        if img.size != (cell_w, cell_h):
            img = img.resize((cell_w, cell_h), Image.LANCZOS)
        row = idx // cols
        col = idx % cols
        grid.paste(img, (col * cell_w, row * cell_h))
        print(f"  [{idx+1}/{cols*rows}] {f}")

    grid.save(output_path, quality=95)
    size_mb = os.path.getsize(output_path) / 1024 / 1024
    print(f"[完成] {output_path} ({grid_w}x{grid_h}, {size_mb:.1f} MB)")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="九宫格拼接")
    parser.add_argument("--input-dir", "-i", required=True, help="包含9张图片的目录")
    parser.add_argument("--output", "-o", required=True, help="输出文件路径")
    parser.add_argument("--cols", type=int, default=3, help="列数（默认3）")
    parser.add_argument("--rows", type=int, default=3, help="行数（默认3）")
    args = parser.parse_args()

    compose_grid(args.input_dir, args.output, args.cols, args.rows)
