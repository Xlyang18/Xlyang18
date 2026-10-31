"""贴纸库：CC0 素材切图 + 程序化像素工匠图标（GUI 按钮、徽章、面板边框）
所有图标都是 16 网格对齐的像素画，统一 3 色渐变 + 描边，风格与作物素材一致。
"""
import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
STICK = os.path.join(ASSETS, 'stickers')

# ---------- 调色板 ----------
P = dict(
    ink='#2a1a1a', ink2='#4a2c1e',
    wood_d='#6b3f22', wood='#a9692f', wood_l='#d69a4e', wood_ll='#f0c078',
    gold_d='#8a5a00', gold='#e0a800', gold_l='#ffd541',
    paper_d='#c9a26a', paper='#f0d9a8', paper_l='#fdf3d0',
    grass_d='#1f5a2e', grass='#2f8f3f', grass_l='#5cc24f', grass_ll='#a6ea6a',
    red='#c2352b', red_l='#ef6250',
    blue='#2f7ec2', blue_l='#7ec8f0',
    white='#ffffff',
)

# ---------- 原始素材索引（按切图编号）----------
# 按切图编号（同 width 时深度序）索引；值 = (w, h, 深度序)
# 索引 = (素材表行, 列) —— 与 sprites.py 的 16x16 网格一致，稳定可靠
# 索引 = (素材表行, 列)；已逐格肉眼核对
# 索引 = (行, 列)，与精灵表网格逐格核对过
CROP_RC = {
    'eggplant': (3, 0),     # 紫茄子
    'lemon': (3, 6),        # 柠檬
    'melon': (2, 6),        # 绿甜瓜
    'tomato': (2, 0),       # 番茄
    'strawberry': (6, 0),   # 草莓
    'apple': (8, 0),        # 橙红苹果
    'orange': (8, 0),       # 同上（橙）
    'pineapple': (4, 0),    # 菠萝
    'cabbage': (2, 7),      # 圆白菜
    'potato': (7, 0),       # 土豆
    'wheat': (5, 1),        # 小麦
    'corn': (9, 0),         # 玉米
    'sunflower': (9, 6),    # 向日葵
    'rose': (0, 6),         # 玫瑰
    'tulip': (0, 7),        # 郁金香
    'flower': (9, 7),       # 小黄花
    'seedbag': (4, 6),      # 种子袋
    'card': (5, 0),         # 配方卡
    'scroll': (7, 6),       # 卷轴/木牌
    'grapes': (5, 6),       # 葡萄
    'coconut': (6, 6),      # 椰壳
}

TREE_IDX = {
    # 按「高度升序 → x」排序后的序号（75 个连通块）
    'bush_s': (1,), 'bush_b': (16,), 'grove': (15,), 'bush_c': (19,),
    'pine_v': (5,), 'spruce_w': (8,), 'pine': (12,), 'fir': (17,),
    'oak': (24,), 'maple': (25,), 'oak_b': (31,), 'poplar': (32,), 'oak_g': (33,),
    'oak_c': (37,), 'acacia': (39,), 'oak_d': (40,), 'orange': (41,), 'green_tree': (42,),
    'oak_e': (46,), 'oak_f': (47,), 'oak_h': (48,), 'teal_tree': (50,), 'lime_tree': (72,),
    'apple_tree': (59,), 'pine_b': (61,), 'palm': (30,),
}


def _crop_sorted(w, h):
    fs = [f for f in os.listdir(STICK) if f.startswith('crop_') and f.endswith(f'_{w}x{h}.png')]

    def key(f):
        base = f[5:-4]
        x, y, _ = base.split('_')
        return (int(y), int(x))
    return sorted(fs, key=key)


def _tree_sorted():
    fs = [f for f in os.listdir(STICK) if f.startswith('tree_')]
    def key(f):
        base = f[5:-4]
        x, y, wh = base.split('_')
        w, h = map(int, wh.split('x'))
        return (w, h, -int(y), int(x))
    return sorted(fs, key=key)


PLANT_FILES = ['pottedtree', 'sunflower', 'windingbush', 'orchids', 'vines', 'cactus']


def _sticker_path(prefix, key):
    for f in os.listdir(STICK):
        if f.startswith(key + '_') and f.endswith('.png'):
            return os.path.join(STICK, f)
    return None


def raw_sticker(name):
    """取切好的作物/树贴纸（RGBA）"""
    if name in CROP_RC:
        row, col = CROP_RC[name]
        sheet = Image.open(os.path.join(ASSETS, 'source', 'Crop_Spritesheet.png')).convert('RGBA')
        return sheet.crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))
    if name in TREE_IDX:
        fs = _tree_sorted()
        i = TREE_IDX[name][0]
        if i < len(fs):
            return Image.open(os.path.join(STICK, fs[i])).convert('RGBA')
    if name in PLANT_FILES:
        p = os.path.join(ASSETS, 'source', name + '.png')
        if os.path.exists(p):
            return Image.open(p).convert('RGBA')
    return None


def to_uri(im):
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def resize_nn(im, w, h):
    return im.resize((w, h), Image.NEAREST)


_cache = {}


def sticker(name, scale=1.0):
    """贴纸 data URI，按 scale 缩放到 16 网格倍数"""
    key = ('st', name, round(scale, 2))
    if key in _cache:
        return _cache[key]
    im = raw_sticker(name)
    if im is None:
        return ''
    w = max(8, int(round(im.width * scale / 8)) * 8)
    h = max(8, int(round(im.height * scale / 8)) * 8)
    _cache[key] = to_uri(resize_nn(im, w, h))
    return _cache[key]


# ---------- 程序化像素图标 ----------
def _canvas(w, h):
    return Image.new('RGBA', (w, h), (0, 0, 0, 0))


def _rgb(hexs):
    hexs = hexs.lstrip('#')
    return tuple(int(hexs[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def px(draw, x, y, c, s=1):
    draw.rectangle([x, y, x + s - 1, y + s - 1], fill=_rgb(c))


def bevel_box(draw, x, y, w, h, base, light, dark, ink='#2a1a1a', t=1):
    """像素斜角凸起盒：外描边 + 上左高光 + 下右阴影"""
    draw.rectangle([x, y, x + w - 1, y + h - 1], fill=_rgb(ink))
    draw.rectangle([x + t, y + t, x + w - 1 - t, y + h - 1 - t], fill=_rgb(base))
    draw.rectangle([x + t, y + t, x + w - 1 - t, y + t], fill=_rgb(light))
    draw.rectangle([x + t, y + t, x + t, y + h - 1 - t], fill=_rgb(light))
    draw.rectangle([x + t, y + h - 1 - t, x + w - 1 - t, y + h - 1 - t], fill=_rgb(dark))
    draw.rectangle([x + w - 1 - t, y + t, x + w - 1 - t, y + h - 1 - t], fill=_rgb(dark))


def icon_button(size=32):
    """木质按钮底板（16 网格）"""
    im = _canvas(size, size)
    from PIL import ImageDraw
    d = ImageDraw.Draw(im)
    bevel_box(d, 0, 0, size, size, P['wood'], P['wood_ll'], P['wood_d'])
    return im


def icon_pin(size=32):
    """图钉贴纸：红头 + 木杆 + 阴影"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    d.ellipse([3 * s, 1 * s, 12 * s, 9 * s], fill=_rgb(P['red']))
    d.ellipse([5 * s, 3 * s, 10 * s, 7 * s], fill=_rgb(P['red_l']))
    d.rectangle([7 * s, 8 * s, 9 * s, 14 * s], fill=_rgb('#8a8a8a'))
    d.rectangle([6 * s, 13 * s, 10 * s, 15 * s], fill=_rgb('#5a5a5a'))
    return im


def icon_heart(size=32):
    """红心（贡献/喜欢）像素 —— 12x12 网格"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 12)
    # 两瓣 + 下方收尖
    for (x0, y0, x1, y1) in [(1, 1, 6, 4), (6, 1, 11, 4), (1, 4, 11, 7),
                             (2, 7, 10, 9), (4, 9, 8, 11)]:
        d.rectangle([x0 * s, y0 * s, x1 * s - 1, y1 * s - 1], fill=_rgb(P['red']))
    d.rectangle([2 * s, 2 * s, 4 * s - 1, 3 * s - 1], fill=_rgb(P['red_l']))
    return im


def icon_star(size=32):
    """金星（收藏/星数）"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 12)
    rows = [(4, 0, 8), (4, 1, 8), (1, 4, 15), (2, 5, 14), (3, 6, 13), (4, 7, 12), (5, 8, 11)]
    for x0, y, w in rows:
        d.rectangle([x0 * s, y * s, (x0 + w) * s - 1, (y + 1) * s - 1], fill=_rgb(P['gold']))
    d.rectangle([4 * s, 1 * s, 7 * s - 1, 2 * s - 1], fill=_rgb(P['gold_l']))
    # 两条腿
    d.rectangle([3 * s, 9 * s, 5 * s - 1, 11 * s - 1], fill=_rgb(P['gold']))
    d.rectangle([7 * s, 9 * s, 9 * s - 1, 11 * s - 1], fill=_rgb(P['gold']))
    return im


def icon_book(size=32):
    """仓库/文档图标：木书架 + 三本书"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    bevel_box(d, 1 * s, 3 * s, 14 * s, 12 * s, P['wood_d'], P['wood_l'], '#3d2414')
    for i, c in enumerate([P['red'], P['blue'], P['grass']]):
        x = (3 + i * 4) * s
        d.rectangle([x, (5 + (i % 2)) * s, x + 3 * s - 1, 13 * s], fill=_rgb(c))
    d.rectangle([3 * s, 5 * s, 6 * s - 1, 5 * s], fill=_rgb(P['paper_l']))
    return im


def icon_fork(size=32):
    """分支/拉取请求：木牌 + 分叉线"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    d.rectangle([6 * s, 2 * s, 9 * s, 6 * s], fill=_rgb(P['grass']))
    d.rectangle([2 * s, 10 * s, 5 * s, 14 * s], fill=_rgb(P['grass']))
    d.rectangle([10 * s, 10 * s, 13 * s, 14 * s], fill=_rgb(P['grass']))
    d.rectangle([7 * s, 6 * s, 8 * s, 10 * s], fill=_rgb(P['grass_d']))
    d.rectangle([3 * s, 10 * s, 12 * s, 11 * s], fill=_rgb(P['grass_d']))
    d.rectangle([3 * s, 7 * s, 4 * s, 10 * s], fill=_rgb(P['grass_d']))
    d.rectangle([11 * s, 7 * s, 12 * s, 10 * s], fill=_rgb(P['grass_d']))
    return im


def icon_bug(size=32):
    """Issues：红色小虫"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    d.ellipse([4 * s, 4 * s, 12 * s, 13 * s], fill=_rgb(P['red']))
    d.ellipse([6 * s, 6 * s, 10 * s, 9 * s], fill=_rgb(P['red_l']))
    d.rectangle([7 * s, 2 * s, 8 * s, 4 * s], fill=_rgb(P['ink2']))
    for y in (6, 8, 10):
        d.rectangle([2 * s, y * s, 4 * s - 1, (y + 1) * s - 1], fill=_rgb(P['ink2']))
        d.rectangle([12 * s, y * s, 14 * s - 1, (y + 1) * s - 1], fill=_rgb(P['ink2']))
    return im


def icon_shop(size=32):
    """Marketplace：商店帐篷"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    for i in range(4):
        c = P['red'] if i % 2 == 0 else P['paper_l']
        d.rectangle([(1 + i * 4) * s, 2 * s, (4 + i * 4) * s - 1, 6 * s], fill=_rgb(c))
    d.rectangle([2 * s, 6 * s, 13 * s, 14 * s], fill=_rgb(P['wood_l']))
    d.rectangle([6 * s, 8 * s, 9 * s, 14 * s], fill=_rgb(P['wood_d']))
    return im


def icon_compass(size=32):
    """Explore：指南针"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    d.ellipse([1 * s, 1 * s, 15 * s, 15 * s], fill=_rgb(P['paper']))
    d.ellipse([2 * s, 2 * s, 14 * s, 14 * s], fill=_rgb(P['blue_l']))
    d.polygon([(8 * s, 3 * s), (10 * s, 8 * s), (8 * s, 9 * s), (6 * s, 8 * s)], fill=_rgb(P['red']))
    d.polygon([(8 * s, 13 * s), (10 * s, 8 * s), (8 * s, 7 * s), (6 * s, 8 * s)], fill=_rgb(P['white']))
    return im


def icon_home(size=32):
    """Overview：小木屋"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    d.polygon([(8 * s, 1 * s), (15 * s, 7 * s), (1 * s, 7 * s)], fill=_rgb(P['red']))
    d.rectangle([2 * s, 7 * s, 13 * s, 14 * s], fill=_rgb(P['wood']))
    d.rectangle([6 * s, 9 * s, 9 * s, 14 * s], fill=_rgb(P['wood_d']))
    d.rectangle([3 * s, 9 * s, 5 * s, 11 * s], fill=_rgb(P['gold_l']))
    return im


def icon_card(size=32):
    """项目/配方卡：木框 + 羊皮纸"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 16)
    bevel_box(d, 1 * s, 2 * s, 14 * s, 12 * s, P['wood'], P['wood_ll'], P['wood_d'])
    d.rectangle([3 * s, 4 * s, 12 * s, 12 * s], fill=_rgb(P['paper_l']))
    for i in range(3):
        d.rectangle([4 * s, (5 + i * 2) * s, (10 - i) * s, (5 + i * 2) * s], fill=_rgb(P['wood_d']))
    d.rectangle([4 * s, 10 * s, 6 * s, 11 * s], fill=_rgb(P['red']))
    return im


def icon_leaf(size=32):
    """叶子（标题装饰）"""
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 12)
    d.ellipse([2 * s, 2 * s, 10 * s, 9 * s], fill=_rgb(P['grass_l']))
    d.rectangle([5 * s, 8 * s, 7 * s, 11 * s], fill=_rgb(P['grass_d']))
    d.rectangle([3 * s, 3 * s, 5 * s, 5 * s], fill=_rgb(P['grass_ll']))
    return im


def icon_flower(size=32):
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 12)
    for cx, cy in ((5, 1), (1, 5), (9, 5), (5, 9)):
        d.rectangle([cx * s, cy * s, (cx + 2) * s - 1, (cy + 2) * s - 1], fill=_rgb(P['gold']))
    d.rectangle([5 * s, 5 * s, 7 * s - 1, 7 * s - 1], fill=_rgb('#8a5a00'))
    return im


def icon_coin(size=32):
    from PIL import ImageDraw
    im = _canvas(size, size)
    d = ImageDraw.Draw(im)
    s = max(1, size // 12)
    d.ellipse([1 * s, 1 * s, 11 * s, 11 * s], fill=_rgb(P['gold']))
    d.ellipse([2 * s, 2 * s, 8 * s, 8 * s], fill=_rgb(P['gold_l']))
    return im


ICONS = dict(card=icon_card, button=icon_button, pin=icon_pin, heart=icon_heart, star=icon_star, book=icon_book,
             fork=icon_fork, bug=icon_bug, shop=icon_shop, compass=icon_compass, home=icon_home,
             leaf=icon_leaf, flower=icon_flower, coin=icon_coin)


def icon(name, size=32):
    """程序化图标 data URI（size 需为 8/16 的倍数以保锐利）"""
    if name in _cache:
        im = _cache[name]
    else:
        im = ICONS[name](size)
        _cache[name] = im
    if im.width != size:
        im = im.resize((size, size), Image.NEAREST)
    return to_uri(im)


if __name__ == '__main__':
    names = ['eggplant', 'tomato', 'corn', 'sunflower', 'strawberry', 'apple', 'melon', 'cabbage', 'scroll',
             'seedbag', 'crate', 'pineapple', 'oak', 'birch', 'pine', 'apple_tree', 'maple', 'bush', 'palm',
             'pottedtree', 'orchids', 'vines', 'cactus', 'windingbush']
    miss = [n for n in names if raw_sticker(n) is None]
    print('missing:', miss)
    for n in names:
        im = raw_sticker(n)
        if im:
            print(f'{n:14} {im.width}x{im.height}')
