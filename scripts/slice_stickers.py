"""从 CC0 素材里自动切出贴纸：扫描连通块 → 输出 assets/stickers/<name>.png
素材来源：
  assets/source/Crop_Spritesheet.png   josehzz《Farming crops 16x16》CC0
  assets/source/trees.png              《Trees Mega Pack CC0》CC0（OpenGameArt）
"""
import os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'assets', 'source')
OUT = os.path.join(ROOT, 'assets', 'stickers')


def components(im, min_px=40, bg=None):
    """按 alpha>16 网格做连通块标记（4 邻域），返回 bbox 列表"""
    w, h = im.size
    px = im.load()
    seen = [[False] * w for _ in range(h)]
    boxes = []
    for y in range(h):
        for x in range(w):
            if seen[y][x]:
                continue
            if px[x, y][3] <= 16:
                seen[y][x] = True
                continue
            stack = [(x, y)]
            seen[y][x] = True
            x0 = x1 = x
            y0 = y1 = y
            n = 0
            while stack:
                cx, cy = stack.pop()
                n += 1
                x0 = min(x0, cx); x1 = max(x1, cx)
                y0 = min(y0, cy); y1 = max(y1, cy)
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
                    nx, ny = cx + dx, cy + dy
                    if 0 <= nx < w and 0 <= ny < h and not seen[ny][nx] and px[nx, ny][3] > 16:
                        seen[ny][nx] = True
                        stack.append((nx, ny))
            if n >= min_px:
                boxes.append((x0, y0, x1 + 1, y1 + 1, n))
    return boxes


def cut_sheet(fname, out_prefix, min_px=40, min_size=(10, 10), max_size=(400, 400)):
    im = Image.open(os.path.join(SRC, fname)).convert('RGBA')
    os.makedirs(OUT, exist_ok=True)
    made = []
    for (x0, y0, x1, y1, n) in components(im, min_px):
        w, h = x1 - x0, y1 - y0
        if not (min_size[0] <= w <= max_size[0] and min_size[1] <= h <= max_size[1]):
            continue
        c = im.crop((x0, y0, x1, y1))
        name = f'{out_prefix}_{x0}_{y0}_{w}x{h}.png'
        c.save(os.path.join(OUT, name))
        made.append((name, w, h, n))
    return made


if __name__ == '__main__':
    todo = [
        ('Crop_Spritesheet.png', 'crop', 60),
        ('trees.png', 'tree', 800),
    ]
    for fname, prefix, minpx in todo:
        if not os.path.exists(os.path.join(SRC, fname)):
            print('skip', fname)
            continue
        boxes = components(Image.open(os.path.join(SRC, fname)).convert('RGBA'), minpx)
        print(fname, 'components', len(boxes))
