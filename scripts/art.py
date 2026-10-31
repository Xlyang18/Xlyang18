"""星露谷风主页渲染器 v2 —— HTML(给浏览器截图) + SVG(兜底)，同一套坐标系统
布局命令写入 IR 列表，再分别输出 HTML 与 SVG，保证两版视觉一致。
"""
import base64, io, json, os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ASSETS = os.path.join(ROOT, 'assets')

C = dict(
    wood_l='#dba463', wood='#a86d33', wood_d='#73172d', ink='#3b1725', ink2='#8e5252',
    paper='#f3e2b8', paper_l='#fdf3d6', paper_d='#e2c893',
    grass_l='#9cdb43', grass='#59c135', grass_d='#24523b',
    sky_l='#8fd3f4', sky='#59c9f1', sky_d='#2b7fb0',
    gold='#ffd541', orange='#f9a31b', green='#14a02e', red='#b4202a', purple='#793a80',
)
W, H = 1012, 852
PAD = 16
LX = 16
COL_L, COL_R = 240, 300
GAP = 10
MX = LX + COL_L + GAP
COL_M = W - 2 * PAD - COL_L - COL_R - GAP * 2
RX = MX + COL_M + GAP
TOP = 152
BOT = H - 56
PH = 20          # 面板标题行高
LH = 20          # 正文字高
INKW = lambda s, sz=16: sum(sz if ord(ch) > 0x2000 else sz * 0.5 for ch in str(s))

# ---------------- 素材 ----------------
_sc = {}


def sheet():
    if 's' not in _sc:
        _sc['s'] = Image.open(os.path.join(ASSETS, 'source', 'Crop_Spritesheet.png')).convert('RGBA')
    return _sc['s']


SPR = {'coffee': (7, 0), 'coffee_s': (7, 2), 'tomato': (2, 0), 'tomato_s': (2, 2), 'corn': (9, 0),
       'corn_s': (9, 2), 'sunflower': (9, 6), 'sunflower_s': (9, 8), 'strawberry': (6, 0),
       'strawberry_s': (6, 2), 'turnip': (0, 1), 'turnip_s': (0, 2), 'bean': (1, 0), 'bean_s': (1, 1),
       'rose': (0, 6), 'rose_s': (0, 10), 'seed': (8, 6), 'soil': (5, 6), 'card': (5, 0),
       'grape': (5, 6), 'melon': (3, 6), 'sprout': (7, 3)}


def sprite_uri(name):
    if name in _sc:
        return _sc[name]
    row, col = SPR[name]
    im = sheet().crop((col * 16, row * 16, col * 16 + 16, row * 16 + 16))
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    uri = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    _sc[name] = uri
    return uri


def file_uri(rel):
    path = os.path.join(ASSETS, rel)
    mime = 'image/png' if path.lower().endswith('.png') else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(open(path, 'rb').read()).decode()


def font_b64(name):
    return base64.b64encode(open(os.path.join(ASSETS, 'fonts', name), 'rb').read()).decode()


# ---------------- 布局积木：返回 HTML 片段，SVG 版另行生成 ----------------
def panel_open(cls=''):
    return f'<div class="panel {cls}">'


def ph(icon, label, right=''):
    r = f'<span class="plus">{right}</span>' if right else ''
    return f'<div class="ph"><img class="ico" src="{sprite_uri(icon)}"><span>{label}</span>{r}</div>'


def scene_svg(w, h=128):
    S = []
    g = lambda x, y, ww, hh, c: S.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="{c}"/>')
    g(0, 0, w, h, C['sky'])
    for cx, cy, cw in [(236, 6, 104), (440, 26, 56), (640, 8, 120)]:
        g(cx + 16, cy, cw - 32, 16, '#ffffff')
        g(cx, cy + 8, cw, 16, '#ffffff')
        g(cx + 10, cy + 24, cw - 20, 8, '#e3f4ff')
    for mx, mw, mh in [(70, 320, 36), (360, 360, 48), (690, 340, 32)]:
        b = 96
        S.append(f'<polygon points="{mx},{b-mh} {mx+mw},{b} {mx-mw},{b}" fill="{C["grass_d"]}"/>')
        S.append(f'<polygon points="{mx},{b-mh} {mx+mw*0.2:.0f},{b-mh+14:.0f} {mx-mw*0.2:.0f},{b-mh+14:.0f}" fill="#2f6b4a"/>')
    for tx, th in [(96, 56), (268, 40), (560, 64), (660, 44), (900, 52)]:
        g(tx + 6, 76 - th // 2, 4, th // 2, C['wood_d'])
        g(tx, 76 - th, 16, 10, '#1a7a3e')
        g(tx - 4, 76 - th + 10, 24, 12, '#1a7a3e')
        g(tx, 76 - th + 22, 16, 8, C['grass_d'])
        g(tx + 2, 76 - th + 2, 6, 4, '#24523b')
    g(0, 96, w, 32, C['grass'])
    for gx in range(0, w, 16):
        g(gx, 98, 8, 4, C['grass_l'] if (gx // 16) % 2 else C['grass_d'])
    for gx in range(8, w, 32):
        g(gx, 110, 4, 4, C['grass_l'])
    g(0, 122, w, 6, '#3f8a2e')
    for bx in (20, 216):   # 左下/中下灌木
        g(bx, 112, 20, 8, '#24523b'); g(bx + 4, 106, 12, 6, '#1a7a3e'); g(bx + 6, 104, 6, 4, '#59c135')
    # 木牌
    g(38, 22, 12, 92, C['wood_d'])
    g(286, 22, 12, 92, C['wood_d'])
    g(22, 14, 292, 72, C['wood_d'])
    g(28, 20, 280, 60, C['wood'])
    g(28, 20, 280, 9, C['wood_l'])
    g(28, 71, 280, 9, '#8a5a2f')
    for dx in (34, 296):
        g(dx, 26, 6, 6, C['gold'])
        g(dx, 64, 6, 6, C['gold'])
    g(52, 30, 40, 32, C['ink'])
    g(58, 24, 9, 9, C['ink'])
    g(79, 24, 9, 9, C['ink'])
    g(58, 36, 28, 17, C['paper_l'])
    g(62, 40, 7, 6, C['ink'])
    g(75, 40, 7, 6, C['ink'])
    g(63, 47, 17, 4, C['ink'])
    g(55, 58, 11, 8, C['ink'])
    # 小木屋
    hx, hy = 830, 10
    S.append(f'<polygon points="{hx+78},{hy} {hx+174},{hy+36} {hx-18},{hy+36}" fill="{C["red"]}"/>')
    g(hx + 6, hy + 30, 146, 11, '#8f1a22')
    g(hx, hy + 41, 157, 62, C['wood'])
    g(hx, hy + 41, 157, 8, C['wood_l'])
    for gy in range(hy + 54, hy + 102, 11):
        g(hx, gy, 157, 3, '#8a5a2f')
    g(hx + 62, hy + 64, 34, 39, C['wood_d'])
    g(hx + 87, hy + 81, 6, 6, C['gold'])
    g(hx + 17, hy + 58, 28, 22, C['sky_l'])
    g(hx + 17, hy + 68, 28, 3, '#ffffff')
    g(hx + 30, hy + 58, 3, 22, '#ffffff')
    g(hx + 109, hy + 58, 28, 22, C['sky_l'])
    g(hx + 122, hy + 58, 3, 22, '#ffffff')
    return ''.join(S)
