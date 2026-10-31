"""星露谷风主页渲染器 v2 —— HTML(给浏览器截图) + SVG(兜底)，同一套坐标系统
布局命令写入 IR 列表，再分别输出 HTML 与 SVG，保证两版视觉一致。
"""
import base64, io, json, os
from PIL import Image
import spritelib as SP

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
W, H = 1012, 812
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
    if not os.path.exists(path):
        return ''      # 缺图时不炸，由调用方渲染占位
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


def _real_trees(g, out, w=1012, y_base=76):
    """用 CC0 树素材铺树线（直接落进 SVG，走 data URI）"""
    from PIL import Image as _I
    import io as _io, base64 as _b64
    plan = [(0, 168, 'oak'), (150, 196, 'pine_v'), (214, 140, 'maple'), (300, 210, 'spruce_w'),
            (372, 150, 'oak_b'), (420, 186, 'pine'), (486, 160, 'green_tree'), (560, 200, 'fir'),
            (630, 148, 'oak_c'), (688, 190, 'pine_b'), (752, 158, 'oak'), (820, 176, 'spruce_w')]
    for x, hh, name in plan:
        im = SP.raw_sticker(name)
        if im is None:
            continue
        scl = hh / im.height
        im2 = im.resize((max(8, int(im.width * scl)), hh), _I.LANCZOS)
        buf = _io.BytesIO(); im2.save(buf, 'PNG', optimize=True)
        uri = 'data:image/png;base64,' + _b64.b64encode(buf.getvalue()).decode()
        out.append(f'<image x="{x}" y="{y_base - hh}" width="{im2.width}" height="{hh}" href="{uri}"/>')


def scene_svg(w, h=128):
    """顶栏风景：天空 → 云 → 三层远山 → 树线 → 栅栏 → 草甸（16px 网格）"""
    S = []
    g = lambda x, y, ww, hh, c: S.append(f'<rect x="{x}" y="{y}" width="{ww}" height="{hh}" fill="{c}"/>')

    # 天空渐变（4 段色带，保持像素风）
    for i, c in enumerate(['#3f9ada', '#4ea6e2', '#5fb3ea', '#72c0f0', '#86cdf5', '#9ad8f8', '#b0e2fa']):
        g(0, i * 12, w, 12, c)

    # 云（3 层堆叠 + 高光）
    for cx, cy, cw in [(214, 6, 108), (452, 20, 64), (648, 4, 122)]:
        g(cx + 20, cy, cw - 40, 8, '#ffffff')
        g(cx + 8, cy + 8, cw - 16, 10, '#ffffff')
        g(cx, cy + 18, cw, 10, '#eef8ff')
        g(cx + 4, cy + 28, cw - 8, 6, '#d8ecfa')

    # 三层远山：越远越浅、带雪顶
    for mx, mw, mh, body, dark in [(60, 300, 40, '#7fb9a0', '#6aa68e'),
                                   (330, 360, 52, '#5f9f86', '#4d8b74'),
                                   (700, 340, 36, '#7fb9a0', '#6aa68e')]:
        base = 74
        S.append(f'<polygon points="{mx},{base-mh} {mx+mw},{base} {mx-mw},{base}" fill="{body}"/>')
        S.append(f'<polygon points="{mx},{base-mh} {mx+mw*0.24:.0f},{base-mh+12:.0f} {mx-mw*0.24:.0f},{base-mh+12:.0f}" fill="#e8f4ff"/>')
        S.append(f'<polygon points="{mx},{base-mh+12} {mx+mw*0.34:.0f},{base} {mx-mw*0.34:.0f},{base}" fill="{dark}"/>')

    # 树线（远近两层，深绿→浅绿）
    _real_trees(g, S)
    # 远树线（小、淡）
    for tx in range(-8, w, 30):
        g(tx + 9, 56, 5, 22, '#3f2a18')
        g(tx, 44, 24, 10, '#20572f')
        g(tx + 4, 38, 16, 8, '#2a6b3c')
    # 近树线（大、深，留出山体上缘）
    for tx in range(14, w, 52):
        g(tx + 10, 60, 6, 26, '#4a2f1c')
        g(tx, 48, 26, 12, '#1f6b3a')
        g(tx + 4, 42, 18, 8, '#2a8447')

    # 木栅栏（16px 节奏：立柱 + 双横杆 + 高光）
    for fx in range(0, w, 32):
        g(fx, 66, 8, 20, '#c98a4b')
        g(fx, 66, 8, 3, '#e2b26c')
        g(fx + 6, 68, 2, 16, '#8a5a2f')
    g(0, 70, w, 4, '#d9a45c')
    g(0, 70, w, 1, '#f0c987')
    g(0, 78, w, 4, '#c08b4e')
    g(0, 81, w, 1, '#a86d33')

    # 草甸（四段 + 草簇 + 小花）
    g(0, 88, w, 22, '#59c135')
    g(0, 88, w, 3, '#7ad06f')
    for px_ in range(0, w, 48):
        g(px_, 96 + (px_ // 48) % 3 * 4, 26, 5, '#4fae2e')
        g(px_ + 24, 102 + (px_ // 48) % 2 * 3, 18, 4, '#66c443')
    for gx in range(0, w, 16):
        g(gx, 94, 9, 4, '#4aa62c')
        g(gx + 8, 100, 6, 3, '#8fdc5b')
    g(0, 110, w, 18, '#3f9c2b')
    for gx in range(6, w, 24):
        g(gx, 114, 3, 6, '#62bd45')
        g(gx + 3, 112, 3, 8, '#79cf58')
        g(gx + 6, 115, 3, 5, '#62bd45')

    # 前景小物件：蘑菇 / 石子 / 花（散点贴纸感）
    for mx, my in [(96, 108), (410, 112), (700, 106)]:
        g(mx, my, 4, 6, '#e8e2d0')
        g(mx - 3, my - 3, 10, 4, '#c2352b')
        g(mx - 1, my - 4, 3, 2, '#ef6250')
    for rx, ry in [(180, 118), (520, 120), (860, 116)]:
        g(rx, ry, 5, 3, '#a39986')
        g(rx + 1, ry, 3, 1, '#cfc7b6')
    for fx, fy in [(268, 104), (600, 108), (790, 102)]:
        g(fx, fy, 2, 6, '#3f9c2b')
        g(fx - 2, fy - 3, 3, 3, '#ffd541')
        g(fx + 3, fy - 3, 3, 3, '#ffd541')
        g(fx - 2, fy + 1, 3, 3, '#ffd541')
        g(fx + 3, fy + 1, 3, 3, '#ffd541')
        g(fx + 1, fy - 1, 2, 2, '#f9a31b')

    # 木牌（左）：阴影 + 桩 + 板 + 高光 + 铆钉 + GitHub 猫
    g(24, 18, 12, 92, '#3d2414')
    g(278, 18, 12, 92, '#3d2414')
    g(22, 14, 284, 72, '#3d2414')
    g(28, 20, 272, 60, '#a9692f')
    g(28, 20, 272, 9, '#d69a4e')
    g(28, 20, 272, 3, '#f0c078')
    g(28, 71, 272, 9, '#6b3f22')
    g(34, 30, 4, 4, '#ffd541')
    g(290, 30, 4, 4, '#ffd541')
    g(34, 66, 4, 4, '#ffd541')
    g(290, 66, 4, 4, '#ffd541')
    # GitHub 猫头（16px 网格）
    g(54, 32, 42, 34, '#2a1a1a')
    g(60, 24, 10, 10, '#2a1a1a')
    g(80, 24, 10, 10, '#2a1a1a')
    g(60, 38, 30, 18, '#fdf3d0')
    g(64, 42, 8, 7, '#2a1a1a')
    g(78, 42, 8, 7, '#2a1a1a')
    g(65, 50, 20, 4, '#2a1a1a')
    g(56, 62, 12, 9, '#2a1a1a')

    # 小木屋（右）：烟囱 → 屋顶 → 墙体 → 门窗 → 台阶
    hx, hy = 826, 12
    g(hx + 132, hy - 6, 14, 26, '#8a8a8a')
    g(hx + 130, hy - 10, 18, 5, '#b0b0b0')
    S.append(f'<polygon points="{hx+78},{hy} {hx+186},{hy+40} {hx-30},{hy+40}" fill="#b8362c"/>')
    S.append(f'<polygon points="{hx+78},{hy+4} {hx+180},{hy+40} {hx-24},{hy+40}" fill="#d34a3a"/>')
    g(hx - 4, hy + 36, 164, 8, '#8f1a22')
    g(hx, hy + 44, 156, 62, '#a9692f')
    g(hx, hy + 44, 156, 8, '#d69a4e')
    for gy in range(hy + 56, hy + 104, 10):
        g(hx, gy, 156, 3, '#8a5a2f')
    g(hx, hy + 106, 156, 6, '#6b3f22')
    g(hx + 62, hy + 70, 34, 42, '#73452a')
    g(hx + 64, hy + 72, 30, 4, '#9a6238')
    g(hx + 88, hy + 86, 6, 6, '#ffd541')
    for wx in (hx + 16, hx + 108):
        g(wx, hy + 62, 30, 24, '#8fd3f4')
        g(wx, hy + 74, 30, 3, '#fdf3d0')
        g(wx + 14, hy + 62, 3, 24, '#fdf3d0')
        g(wx - 3, hy + 59, 36, 4, '#6b3f22')
    return ''.join(S)
