"""星露谷风素材切片工具：从 CC0 精灵表裁出单个 16x16 图元，放大后转 base64 PNG"""
import base64, io, os
from PIL import Image

SHEET = '/Users/xlyang/Documents/appZoo/github-profile/assets/source/Crop_Spritesheet.png'
_cache = {}


def load():
    if 'sheet' not in _cache:
        _cache['sheet'] = Image.open(SHEET).convert('RGBA')
    return _cache['sheet']


def sprite(row, col, scale=1, pad=0):
    """取精灵表第 row 行第 col 列的 16x16，放大 scale 倍，四周补 pad（透明）"""
    im = load()
    cell = im.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))
    if style_pad := pad:
        out = Image.new('RGBA', (16 + style_pad * 2, 16 + style_pad * 2), (0, 0, 0, 0))
        out.alpha_composite(cell, (style_pad, style_pad))
        cell = out
    if scale != 1:
        cell = cell.resize((cell.width * scale, cell.height * scale), Image.NEAREST)
    return cell


def data_uri(img):
    buf = io.BytesIO()
    img.save(buf, format='PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


# 常用图元坐标（行, 列）—— 已逐格核对
COFFEE = dict(portrait=(7, 0), sprout=(7, 2), small=(7, 3), medium=(7, 4), tall=(7, 5))
TOMATO = dict(portrait=(2, 0), sprout=(2, 2), small=(2, 3), medium=(2, 4), tall=(2, 5), dead=(2, 6))
GREENBEAN = dict(portrait=(1, 0), vine=(1, 1), trellis=(1, 3), trellis2=(1, 4))
STRAWBERRY = dict(portrait=(6, 0), sprout=(6, 2), small=(6, 3), medium=(6, 4), tall=(6, 5))
CORN = dict(portrait=(9, 0), sprout=(9, 2), small=(9, 3), medium=(9, 4), tall=(9, 5))
SUNFLOWER = dict(portrait=(9, 6), sprout=(9, 8), small=(9, 9), medium=(9, 10), tall=(9, 11))
TURNIP = dict(portrait=(0, 1), sprout=(0, 2), small=(0, 3), medium=(0, 4), tall=(0, 5))
ROSE = dict(portrait=(0, 6), bloom=(0, 7), bud=(0, 8), small=(0, 9), sprout=(0, 10))
LEAF = dict(seedbag=(8, 6), soil=(5, 6), portrait_card=(5, 0), wood=(4, 6))


def ico(name, scale=1, pad=0):
    """按名字取图元 data URI"""
    table = {'coffee': COFFEE, 'tomato': TOMATO, 'greenbean': GREENBEAN, 'strawberry': STRAWBERRY,
             'corn': CORN, 'sunflower': SUNFLOWER, 'turnip': TURNIP, 'rose': ROSE, 'leaf': LEAF}
    grp, key = name.split('.')
    rc = table[grp][key]
    return data_uri(sprite(rc[0], rc[1], scale, pad))


if __name__ == '__main__':
    out = '/Users/xlyang/Documents/appZoo/github-profile/preview/sprite_test.html'
    names = ['coffee.portrait', 'coffee.sprout', 'coffee.small', 'coffee.medium', 'coffee.tall',
             'tomato.portrait', 'tomato.small', 'tomato.tall', 'greenbean.vine', 'strawberry.portrait',
             'corn.portrait', 'sunflower.portrait', 'sunflower.tall', 'turnip.portrait', 'rose.bloom',
             'rose.portrait', 'leaf.seedbag', 'leaf.soil']
    tiles = ''.join(f'<div class=t><img src="{ico(n,4,1)}"><span>{n}</span></div>' for n in names)
    open(out, 'w').write(f'''<!doctype html><meta charset=utf-8><style>
body{{background:#f6e4bd;font:12px monospace}} .t{{display:inline-block;text-align:center;margin:6px;background:#e2b26c;padding:6px}}
img{{image-rendering:pixelated;display:block;margin:auto}}</style>{tiles}''')
    print('written', out)
