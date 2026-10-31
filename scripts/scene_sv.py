"""顶栏风景 v2：全部星露谷游戏原生素材拼装
树 = 游戏 Stage_5 图集切出的单棵；房子/筒仓/鸡舍 = 游戏建筑贴图；
栅栏 = 游戏 Fence 图集；动物/作物 = 游戏物品图标。
"""
import os
import svrt as SV

W, H = 1012, 196
GROUND = 108      # 地平线：树根落在草地上沿，下方留给栅栏与草地


def _img(uri, x, y, w, h, shadow=False):
    sh = ' style="filter:drop-shadow(2px 3px 0 rgba(28,20,12,.32))"' if shadow else ''
    return f'<image x="{int(x)}" y="{int(y)}" width="{int(w)}" height="{int(h)}" href="{uri}"{sh}/>'


def _size(name, w):
    im = SV.load(name)
    if im is None:
        return w, max(1, int(w * 1.4))
    bb = im.getbbox() or (0, 0, im.width, im.height)
    cw, ch = bb[2] - bb[0], bb[3] - bb[1]
    return w, max(1, int(w * ch / cw))


def tree_html(key, x, w, ground=GROUND, max_h=96):
    name = SV.TREES1[key]
    if SV.load(name) is None:
        return ''
    w, h = _size(name, w)
    if h > max_h:                       # 封顶，避免树出画
        w = int(w * max_h / h)
        h = max_h
    return _img(SV.trimmed_uri(name, w), x, ground - h, w, h, shadow=True)


def build_html(key, x, w, ground=GROUND, max_h=104):
    name = SV.BUILD[key]
    if SV.load(name) is None:
        return ''
    w, h = _size(name, w)
    if h > max_h:
        w = int(w * max_h / h)
        h = max_h
    return _img(SV.trimmed_uri(name, w), x, ground - h, w, h, shadow=True)


def item(key, x, y, w):
    return _img(SV.icon(key, w), x, y, w, w)


def animal(key, x, y, w):
    return _img(SV.animal(key, w), x, y, w, w)


def scene():
    S = []
    R = lambda x, y, w, h, c: S.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{c}"/>')

    for i, c in enumerate(['#5fb6e6', '#6fc0eb', '#7fcbf0', '#90d5f5', '#a2dff9', '#b5e8fc']):
        R(0, i * 15, W, 15, c)

    for cx, cy, cw in [(188, 8, 116), (426, 24, 70), (664, 6, 130)]:
        R(cx + 20, cy, cw - 40, 9, '#ffffff')
        R(cx + 8, cy + 9, cw - 16, 12, '#ffffff')
        R(cx, cy + 21, cw, 9, '#eff9ff')

    for mx, mw, mh, body, dark in [(30, 300, 44, '#86b48c', '#6f9f78'),
                                   (320, 400, 56, '#6f9f78', '#5b8a66'),
                                   (740, 330, 40, '#86b48c', '#6f9f78')]:
        S.append(f'<polygon points="{mx},{GROUND-mh} {mx+mw},{GROUND} {mx-mw},{GROUND}" fill="{body}"/>')
        S.append(f'<polygon points="{mx},{GROUND-mh} {mx+mw*0.22:.0f},{GROUND-mh+12:.0f} {mx-mw*0.22:.0f},{GROUND-mh+12:.0f}" fill="#eaf7ff"/>')
        S.append(f'<polygon points="{mx},{GROUND-mh+12} {mx+mw*0.36:.0f},{GROUND} {mx-mw*0.36:.0f},{GROUND}" fill="{dark}"/>')

    R(0, GROUND, W, H - GROUND, '#6cbb3c')
    R(0, GROUND, W, 5, '#8ad253')
    for gx in range(0, W, 16):
        R(gx, GROUND + 10, 9, 6, '#5cae31')
        R(gx + 8, GROUND + 24, 7, 5, '#7ccf45')
        R(gx + 3, GROUND + 40, 8, 5, '#4f9c29')
    R(0, H - 34, W, 34, '#5aa62e')
    for gx in range(6, W, 20):
        R(gx, H - 28, 3, 9, '#6fc13a')
        R(gx + 5, H - 31, 3, 12, '#83d54d')
        R(gx + 10, H - 20, 3, 8, '#4f9c29')

    plan = [(132, 'oak', 46), (188, 'pine', 44), (238, 'maple', 42), (286, 'oak_teal', 40),
            (330, 'mahogany', 42), (378, 'pine_deep', 40), (420, 'oak_autumn', 40),
            (462, 'apple', 40), (504, 'maple_dark', 38), (544, 'pine_yellow', 38),
            (586, 'cherry', 38), (628, 'mahogany_olive', 40), (672, 'oak', 38),
            (710, 'maple_pink', 36), (748, 'mango', 38), (786, 'pine', 36),
            (822, 'oak_autumn', 36), (858, 'mahogany', 34), (892, 'pine_yellow', 34), (926, 'maple', 34)]
    for x, key, w in plan:
        S.append(tree_html(key, x, w))

    ft = SV.fence_tile('wood', 24)
    for fx in range(-6, W, 24):
        S.append(f'<image x="{fx}" y="{GROUND+10}" width="24" height="24" href="{ft}"/>')

    S.append(build_html('silo', 900, 40))
    S.append(build_html('coop', 918, 50))
    S.append(build_html('house3', 946, 96))

    for key, ax in [('white_chicken', 26), ('brown_chicken', 50), ('blue_chicken', 72)]:
        S.append(animal(key, ax, GROUND + 46, 22))
    for key, ax, ay, aw in [('pumpkin', 122, GROUND + 48, 18), ('tomato', 150, GROUND + 52, 16),
                            ('strawberry', 174, GROUND + 46, 16), ('melon', 196, GROUND + 54, 18),
                            ('coffee', 220, GROUND + 50, 16), ('shard', 242, GROUND + 48, 16),
                            ('corn', 690, GROUND + 50, 16), ('grape', 714, GROUND + 54, 18)]:
        S.append(item(key, ax, ay, aw))

    R(22, 16, 12, 100, '#3d2414')
    R(278, 16, 12, 100, '#3d2414')
    R(20, 12, 282, 72, '#3d2414')
    R(26, 18, 270, 60, '#c08b4e')
    R(26, 18, 270, 6, '#e0a869')
    R(26, 72, 270, 6, '#96652f')
    for dx in (32, 288):
        R(dx, 24, 5, 5, '#ffd541')
        R(dx, 66, 5, 5, '#ffd541')
    # GitHub 标识（猫头简化块 + 字）
    R(52, 32, 40, 30, '#2a1a1a')
    R(58, 24, 10, 10, '#2a1a1a')
    R(78, 24, 10, 10, '#2a1a1a')
    R(58, 38, 28, 16, '#fdf3d0')
    R(62, 42, 7, 6, '#2a1a1a')
    R(75, 42, 7, 6, '#2a1a1a')
    R(63, 49, 16, 4, '#2a1a1a')
    R(54, 60, 10, 8, '#2a1a1a')
    S.append('<text x="104" y="60" font-family="PingFang SC, Helvetica, sans-serif" font-size="30" '
             'font-weight="700" fill="#3b2410">GitHub</text>')
    return ''.join(S)


def scene_svg():
    return (f'<svg class="scene" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'viewBox="0 0 {W} {H}" width="{W}" height="{H}" '
            f'style="display:block;width:{W}px;height:{H}px;image-rendering:pixelated" shape-rendering="crispEdges">'
            + scene() + '</svg>')


if __name__ == '__main__':
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'preview', 'scene.html')
    open(out, 'w').write('<!doctype html><style>*{margin:0}svg{display:block}</style>' + scene_svg())
    print(out, os.path.getsize(out))
