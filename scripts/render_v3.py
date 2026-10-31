"""渲染星露谷风主页 v3 —— 全套像素化 UI + 大量贴纸
输出 preview/render.html（浏览器截图用）
"""
import json, os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *  # noqa
import spritelib as SP

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
D = json.load(open(os.path.join(ASSETS, 'data.json')))

FS = 12
LH = 20
PH = 22
COLH = BOT - TOP

SHOTS = {'doucang': 'shot-doucang.png', 'lightbox': 'shot-lightbox.png', 'teamtally': 'shot-teamtally.png'}
# 每个仓库配一个作物贴纸（形象化）
REPO_CROP = {'doucang': 'coffee' if False else 'card', 'lightbox': 'melon', 'teamtally': 'wheat',
             'ruanyifeng-blog-reader': 'tomato', 'Xlyang18': 'scroll'}


def cut(s, n):
    return s if len(s) <= n else s[:n]


def ds(d):
    return d[5:].replace('/', '.')


def crop_for(name):
    for k, v in REPO_CROP.items():
        if name.lower().startswith(k.lower()[:6]):
            return v
    return ['eggplant', 'lemon', 'strawberry', 'cabbage', 'orange'][hash(name) % 5]


def ico(kind, size=16):
    """程序化图标"""
    return SP.icon(kind, size if size % 8 == 0 else 16)


def st(name, px):
    """作物/树贴纸"""
    return SP.sticker(name, px / max(1, SP.raw_sticker(name).height if SP.raw_sticker(name) else px))


# ---------------- 贴纸层（撒在面板背后的装饰） ----------------
def scatter_layer():
    """左右两栏留白处撒作物/植物贴纸，制造星露谷「农场杂物」感"""
    items = [
        # (name, left, top, px)
        ('windingbush', 4, 470, 120), ('sunflower', 132, 520, 116), ('orghids', 6, 640, 96),
        ('pottedtree', 148, 660, 104), ('vines', 26, 726, 92), ('cactus', 158, 760, 86),
        ('coconut', 108, 620, 34), ('seedbag', 60, 596, 30),
    ]
    html = ''
    for name, x, y, px in items:
        im = SP.raw_sticker(name)
        if im is None:
            continue
        w = int(px * im.width / im.height)
        html += (f'<img class="deco" src="{SP.sticker(name, px / im.height)}" '
                 f'style="left:{x}px;top:{y}px;width:{w}px;height:{px}px">')
    # 右侧留白（贡献图下方到页脚）
    items2 = [('orchids', 724, 700, 92), ('windingbush', 930, 690, 108), ('pottedtree', 812, 706, 96)]
    for name, x, y, px in items2:
        im = SP.raw_sticker(name)
        if im is None:
            continue
        w = int(px * im.width / im.height)
        html += (f'<img class="deco" src="{SP.sticker(name, px / im.height)}" '
                 f'style="left:{x}px;top:{y}px;width:{w}px;height:{px}px">')
    return f'<div class="deco-layer">{html}</div>'


# ---------------- 顶栏 + 导航 ----------------
def nav_bar():
    items = [('Overview', 'home'), ('Repositories', 'book'), ('Projects', 'card'),
             ('Pull requests', 'fork'), ('Issues', 'bug'), ('Marketplace', 'shop'), ('Explore', 'compass')]
    html = ''.join(
        f'<div class="tab{" on" if i == 0 else ""}"><img class="ico16" src="{ico(ic)}"><span>{n}</span></div>'
        for i, (n, ic) in enumerate(items))
    html += (f'<div class="tab gold star"><img class="ico16" src="{ico("star")}">'
             f'<span>{D["contributions_total"]}</span></div>'
             f'<div class="tab small"><img class="ico16" src="{SP.sticker("avatar" if False else "tulip", 1)}"></div>'
             f'<div class="tab small"><img class="ico16" src="{ico("button")}"></div>')
    return (f'<div class="nav">{html}</div>'
            f'<div class="crumbs"><img class="ico14" src="{ico("book")}"><b>Xlyang18</b>'
            f'<span class="slash">/</span>README.md</div>')


# ---------------- 左栏 ----------------
def left_col():
    rows = ''
    for i, r in enumerate(D['repos']):
        c = crop_for(r['name'])
        rows += (f'<div class="repo{" on" if i == 0 else ""}">'
                 f'<img class="cropico" src="{SP.sticker(c, 1)}">'
                 f'<span>{cut(r["name"], 15)}</span>'
                 f'<img class="starico" src="{ico("star")}"></div>')
    acts = ''.join(
        f'<div class="act"><img class="actico" src="{ico("fork" if "Push" in a["text"] else "star")}">'
        f'<span>{cut(a["text"], 20)}</span><i>{ds(a["date"])}</i></div>'
        for a in D['activity']) or '<div class="act"><span>暂无公开动态</span></div>'
    TREES = ['pine_v', 'oak', 'palm']
    trails = ''.join(
        f'<div class="track"><img src="{SP.sticker(TREES[i % 3], {"pine_v": 0.5, "oak": 0.09, "palm": 0.16}[TREES[i % 3]])}">'
        f'<span>{cut(l["name"], 12)}</span><b>{l["count"]}</b></div>'
        for i, l in enumerate(D.get('langs', [])[:3]))
    return f'''<div class="panel" style="height:{COLH}px">
<div class="ph"><img class="ico16" src="{ico('leaf')}"><span>Your Repositories</span>
  <span class="plus">+</span></div>
<div class="input">Filter repositories…</div>
{rows}
<div class="newbtn"><img class="ico16" src="{ico('shop')}">New repository</div>
<div class="rule"></div>
<div class="ph"><img class="ico16" src="{ico('flower')}"><span>Activity</span></div>
{acts}
<div class="harvest">
  <div class="harvest-t"><img class="ico14" src="{ico('leaf')}">Harvest</div>
  <div class="harvest-g">
    <img src="{SP.sticker('wheat', 1)}"><img src="{SP.sticker('melon', 1)}"><img src="{SP.sticker('tomato', 1)}">
    <img src="{SP.sticker('lemon', 1)}"><img src="{SP.sticker('strawberry', 1)}"><img src="{SP.sticker('grapes', 1)}">
    <img src="{SP.sticker('coconut', 1)}"><img src="{SP.sticker('seedbag', 1)}"><img src="{SP.sticker('cabbage', 1)}">
    <img src="{SP.sticker('pineapple', 1)}"><img src="{SP.sticker('potato', 1)}"><img src="{SP.sticker('card', 1)}">
  </div>
</div>
<div class="tracks">
  <div class="harvest-t"><img class="ico14" src="{ico('compass')}">Trails</div>
  {trails}
</div>
</div>'''


# ---------------- 中栏 ----------------
def mid_col():
    bio = D['bio']
    b1, b2 = cut(bio, 15), bio[15:30]
    cards = ''
    for r in D['repos']:
        name = r['name']
        shot_uri = file_uri(SHOTS[name]) if name in SHOTS else ''
        thumb = (f'<img class="shot" src="{shot_uri}">' if shot_uri
                 else f'<div class="shot none"><img src="{SP.sticker(crop_for(name), 0.9)}"><span>待截图</span></div>')
        cards += f'''<div class="card">
  <img class="cardcrop" src="{SP.sticker(crop_for(name), 1)}">
  <div class="card-body">
    <div class="card-head"><span class="card-title">{cut(name, 20)}</span><img class="starico" src="{ico("star")}"></div>
    <div class="card-desc">{cut(r["desc"], 24)}</div>
    <div class="meta"><i class="dot"></i>{r["lang"]}<i class="sep"></i>★ {r["stars"]}<i class="sep"></i>{r["version"]}<i class="sep"></i>{ds(r["updated"])}</div>
  </div>
  {thumb}
</div>'''
    return f'''<div class="panel" style="height:{COLH}px">
<div class="repohead">
  <div class="titles">
    <div class="bigtitle">{D["user"]} <span class="badge">Hi there</span></div>
    <div class="sub">{b1}</div><div class="sub">{b2}</div>
  </div>
  <div class="codebtn"><img class="ico14" src="{ico('star')}">Follow</div>
</div>
<div class="metabar"><i class="dot"></i><img class="ico14" src="{ico('book')}"><span>★ {D["repos_total"]} repos</span>
<i class="sep"></i><img class="ico14" src="{ico('coin')}"><span>{D["contributions_total"]} contributions</span><i class="sep"></i><span>2021</span></div>
<div class="ph"><img class="ico16" src="{ico('heart')}"><span>About me</span></div>
<ul class="about">
  <li>在读大学生 · 喜爱把日常小需求做成能用的应用</li>
  <li>主力栈 Electron + Vite + React · 副业 Java / Python</li>
  <li>摄影、咖啡、文玩核桃 · 所有应用本地优先</li>
</ul>
<div class="ph"><img class="ico16" src="{ico('leaf')}"><span>Recent repositories</span></div>
{cards}
<div class="pager"><img class="ico14" src="{ico('button')}">1 / 1<img class="ico14" src="{ico('button')}"></div>
</div>'''


# ---------------- 右栏 ----------------
def right_col():
    cells = ''
    for col in D['weeks']:
        inner = ''.join(f'<i class="lv{lv}"></i>' for lv in col)
        cells += f'<div class="w">{inner}</div>'
    acts = ''.join(
        f'<div class="act"><img class="actico" src="{ico("fork" if "Push" in a["text"] else "star")}">'
        f'<span>{cut(a["text"], 15)}</span><i>{ds(a["date"])}</i></div>'
        for a in D['activity'])
    bio = D['bio']
    avatar_uri = file_uri('avatar-pixel.png')
    vers = ''.join(
        f'<div class="ver"><img class="vecrop" src="{SP.sticker(crop_for(r["name"]), 0.6)}">'
        f'<span>{cut(r["name"], 11)}</span><b>{r["version"]}</b></div>'
        for r in D['repos'])
    return f'''<div class="panel side">
<div class="profile">
  <div class="avaframe"><img class="ava" src="{avatar_uri}">
    <img class="pintag" src="{SP.sticker('tulip', 1)}"></div>
  <div class="pinfo">
    <div class="pname">{D["user"]}</div>
    <div class="pbio">{cut(bio, 13)}</div><div class="pbio">{bio[13:26]}</div>
  </div>
</div>
<div class="plines">
  <div><img class="ico14" src="{ico('heart')}">{D["followers"]} follower</div>
  <div><img class="ico14" src="{ico('pin')}">{D["following"]} following</div>
  <div><img class="ico14" src="{ico('home')}">{D["repos_total"]} repositories</div>
</div>
</div>

<div class="panel side">
<div class="ph"><img class="ico16" src="{ico('leaf')}"><span>Contribution Graph</span></div>
<div class="graph">{cells}</div>
<div class="gfoot"><img class="ico14" src="{ico('coin')}"><span>{D["contributions_total"]} contributions</span>
<span>{ds(D["span"][0])} – {ds(D["span"][1])}</span></div>
</div>

<div class="panel side last">
<div class="ph"><img class="ico16" src="{ico('flower')}"><span>Activity</span></div>
{acts}
<div class="vers">
  <div class="vers-t"><img class="ico14" src="{ico('card')}">Release Ladder</div>
  {vers}
</div>
<div class="banner"><img class="bannerart" src="{SP.sticker('sunflower', 0.5)}">Build together.<br>Grow together.</div>
</div>'''


def css():
    F8 = font_b64('fusion-pixel-8px-proportional-zh_hans.ttf.woff2')
    return f'''
@font-face{{font-family:Px;src:url(data:font/woff2;base64,{F8}) format('woff2');font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px}}
body{{background:{C['grass']};font-family:Px,monospace;color:{C['ink']};font-size:{FS}px;line-height:{LH}px;
  -webkit-font-smoothing:none;font-smooth:never;text-rendering:optimizeSpeed}}
img{{image-rendering:pixelated}}
.wrap{{position:relative;width:{W}px;height:{H}px;background:{C['grass']};
  background-image:repeating-linear-gradient(0deg,rgba(0,0,0,.045) 0 2px,transparent 2px 8px),
                   repeating-linear-gradient(90deg,rgba(0,0,0,.045) 0 2px,transparent 2px 8px)}}
.scene{{display:block;width:{W}px;height:128px}}
.nav{{display:flex;align-items:center;gap:6px;padding:8px 12px;height:46px;background:{C['paper_d']};
  border-bottom:3px solid {C['wood_d']};box-shadow:inset 0 -2px 0 {C['wood']},inset 0 3px 0 #f0d9a8}}
.tab{{display:flex;align-items:center;gap:5px;height:30px;padding:0 9px 0 6px;background:{C['wood_l']};
  border:2px solid {C['wood_d']};box-shadow:inset 0 2px 0 #f0d2a6,inset 0 -3px 0 #8a5a2f;white-space:nowrap}}
.tab.on{{background:{C['gold']};box-shadow:inset 0 2px 0 #ffe89a,inset 0 -3px 0 #b8860b}}
.tab.gold{{background:{C['gold']}}}
.tab.small{{padding:0 6px}}
.tab.star{{margin-left:auto}}
.ico16{{width:16px;height:16px}}
.ico14{{width:14px;height:14px;vertical-align:-2px;margin-right:4px}}
.crumbs{{display:flex;align-items:center;height:32px;padding:0 16px;background:{C['paper_l']};
  border-bottom:3px solid {C['wood_d']};box-shadow:inset 0 -2px 0 {C['paper_d']};color:{C['ink2']}}}
.crumbs b{{font-weight:normal;color:{C['wood_d']}}} .slash{{margin:0 7px;color:{C['ink2']}}}
.cols{{position:relative;padding:0 {PAD}px;min-height:{COLH + 16}px}}
.col{{position:absolute;top:8px}}
.l{{left:{PAD}px;width:{COL_L}px}} .m{{left:{MX}px;width:{COL_M}px}} .r{{left:{RX}px;width:{COL_R}px}}
.panel{{background:{C['paper']};border:3px solid {C['wood_d']};padding:10px;margin-bottom:10px;
  box-shadow:inset 0 3px 0 {C['paper_l']},inset 0 -3px 0 {C['paper_d']},
             4px 4px 0 rgba(59,23,37,.3),inset 0 0 0 1px rgba(255,255,255,.35)}}
.ph{{display:flex;align-items:center;gap:6px;height:{PH}px;margin-bottom:4px;color:{C['ink']}}}
.plus{{margin-left:auto;width:20px;height:20px;display:grid;place-items:center;background:{C['wood_l']};
  border:2px solid {C['wood_d']};box-shadow:inset 0 -2px 0 #8a5a2f}}
.input{{height:26px;line-height:22px;padding:0 7px;background:{C['paper_l']};border:2px solid {C['wood']};
  box-shadow:inset 2px 2px 0 {C['paper_d']};color:{C['ink2']};margin-bottom:8px}}
.repo{{position:relative;display:flex;align-items:center;gap:6px;height:30px;padding:0 7px;margin-bottom:4px;
  background:{C['paper_l']};border:2px solid {C['wood']};box-shadow:inset 0 -2px 0 {C['paper_d']}}}
.repo.on{{background:#ffe9a8;border-color:{C['wood_d']};box-shadow:inset 4px 0 0 {C['green']},inset 0 -2px 0 #e8c983}}
.repo span{{overflow:hidden;white-space:nowrap;flex:1}}
.cropico{{width:16px;height:16px}}
.starico{{width:14px;height:14px}}
.newbtn{{display:flex;align-items:center;gap:6px;height:30px;margin-top:10px;padding:0 8px;background:{C['wood_l']};
  border:2px solid {C['wood_d']};box-shadow:inset 0 2px 0 #f0d2a6,inset 0 -3px 0 #8a5a2f;color:{C['ink']}}}
.rule{{height:2px;background:{C['paper_d']};margin:11px 0 9px;box-shadow:0 1px 0 {C['paper_l']}}}
.act{{display:flex;align-items:center;gap:5px;padding:2px 0;border-bottom:2px dotted {C['paper_d']};white-space:nowrap}}
.act span{{overflow:hidden;text-overflow:ellipsis;flex:1}}
.act i{{font-style:normal;color:{C['ink2']}}}
.actico{{width:14px;height:14px;flex:none}}
.harvest{{margin-top:10px;padding-top:8px;border-top:2px solid {C['paper_d']}}}
.harvest-t{{display:flex;align-items:center;gap:5px;color:{C['ink']};margin-bottom:6px}}
.harvest-g{{display:flex;flex-wrap:wrap;gap:5px}}
.harvest-g img{{width:18px;height:18px}}
.tracks{{margin-top:8px;padding-top:6px;border-top:2px solid {C['paper_d']}}}
.track{{display:flex;align-items:center;gap:6px;height:24px}}
.track img{{width:22px;height:22px;object-fit:contain;filter:drop-shadow(1px 1px 0 rgba(0,0,0,.25))}}
.track span{{flex:1;overflow:hidden;white-space:nowrap}}
.track b{{font-weight:normal;color:{C['wood_d']}}}
.vers{{margin-top:7px;padding-top:7px;border-top:2px solid {C['paper_d']}}}
.vers-t{{display:flex;align-items:center;gap:5px;color:{C['ink']};margin-bottom:5px}}
.ver{{display:flex;align-items:center;gap:5px;line-height:19px}}
.ver span{{flex:1;overflow:hidden;white-space:nowrap}}
.ver b{{font-weight:normal;color:{C['wood_d']}}}
.vecrop{{width:16px;height:16px}}
.seedrow{{display:flex;gap:6px;align-items:flex-end;margin-top:10px;padding-top:8px;border-top:2px solid {C['paper_d']}}}
.seedrow img{{width:18px;height:18px}}
.repohead{{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}}
.bigtitle{{font-size:22px;line-height:26px}}
.badge{{padding:0 6px;background:{C['green']};border:2px solid #0d6b1e;color:#fff;font-size:{FS}px;
  vertical-align:3px;box-shadow:inset 0 -2px 0 #0d6b1e}}
.sub{{color:{C['ink2']};white-space:nowrap;overflow:hidden}}
.codebtn{{display:flex;align-items:center;gap:4px;flex:none;height:26px;padding:0 10px;background:{C['green']};
  border:2px solid #0d6b1e;color:#fff;box-shadow:inset 0 2px 0 #39b84a,inset 0 -3px 0 #0d6b1e}}
.metabar{{display:flex;align-items:center;gap:4px;color:{C['ink2']};padding:6px 0;
  border-bottom:2px solid {C['paper_d']};margin-bottom:8px;white-space:nowrap}}
.dot{{width:8px;height:8px;background:{C['gold']};border:1px solid {C['ink']};margin-right:5px;display:inline-block}}
.sep{{width:4px;height:4px;background:{C['wood']};margin:0 7px;display:inline-block}}
.about{{list-style:none;margin-bottom:6px;line-height:19px}}
.about li{{padding-left:14px;position:relative}}
.about li:before{{content:'▪';position:absolute;left:0;color:{C['green']}}}
.card{{position:relative;display:flex;gap:6px;align-items:center;background:{C['paper_l']};
  border:2px solid {C['wood']};padding:3px 6px;margin-bottom:4px;box-shadow:inset 0 -2px 0 {C['paper_d']}}}
.cardcrop{{width:20px;height:20px;flex:none}}
.card-body{{flex:1;min-width:0}}
.card-head{{display:flex;justify-content:space-between;align-items:center}}
.card-title{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:17px}}
.card-desc{{color:{C['ink2']};white-space:nowrap;overflow:hidden;line-height:16px}}
.meta{{display:flex;align-items:center;color:{C['ink2']};white-space:nowrap;line-height:16px}}
.shot{{width:84px;height:54px;object-fit:cover;border:2px solid {C['wood_d']};flex:none;background:#fff;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.15)}}
.shot.none{{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;
  background:linear-gradient(#d69a4e,#a9692f);color:#fdf3d0;font-size:9px;line-height:10px}}
.shot.none img{{width:22px;height:22px}}
.pager{{display:flex;justify-content:center;align-items:center;gap:6px;color:{C['ink2']}}}
.profile{{display:flex;gap:8px}}
.avaframe{{position:relative;width:62px;height:62px;flex:none;border:3px solid {C['wood_d']};
  background:{C['ink']};box-shadow:inset 0 0 0 3px {C['gold']},2px 2px 0 rgba(0,0,0,.3)}}
.ava{{position:absolute;inset:3px;width:50px;height:50px;object-fit:cover}}
.pintag{{position:absolute;right:-9px;bottom:-7px;width:20px;height:20px}}
.pinfo{{min-width:0}} .pname{{font-size:18px;line-height:20px}}
.pbio{{color:{C['ink2']};white-space:nowrap;overflow:hidden}}
.plines{{margin-top:6px;line-height:22px}}
.plines .ico14{{width:14px;height:14px}}
.graph{{display:grid;grid-template-columns:repeat(53,1fr);gap:2px;width:100%}}
.graph .w{{display:grid;grid-template-rows:repeat(7,1fr);gap:2px}}
.graph i{{aspect-ratio:1;width:100%;background:#e8e0c8;box-shadow:inset 0 0 0 1px rgba(0,0,0,.05)}}
.graph .lv0{{background:#e8e0c8}} .graph .lv1{{background:#c6e6a0}}
.graph .lv2{{background:#7fd050}} .graph .lv3{{background:#2f9c2f}} .graph .lv4{{background:#17632a}}
.gfoot{{display:flex;justify-content:space-between;align-items:center;color:{C['ink2']};margin-top:5px;font-size:10px}}
.banner{{margin-top:6px;height:40px;display:flex;align-items:center;justify-content:center;gap:6px;
  text-align:center;background:linear-gradient(#d69a4e,#b87a37);border:3px solid {C['wood_d']};
  box-shadow:inset 0 3px 0 #f0c078,inset 0 -3px 0 #6b3f22;color:{C['paper_l']}}}
.bannerart{{width:20px;height:36px}}
.footer{{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:8px;height:40px;
  padding:0 16px;background:{C['paper_l']};border-top:3px solid {C['wood_d']};
  box-shadow:inset 0 3px 0 #fff;color:{C['ink2']}}}
.footer span{{color:{C['ink']}}}
.footer b{{font-weight:normal;color:{C['wood_d']};border-bottom:3px solid {C['orange']};padding-bottom:2px}}
.deco-layer{{position:absolute;inset:0;pointer-events:none;z-index:0}}
.deco{{position:absolute;opacity:.95;filter:drop-shadow(2px 3px 0 rgba(0,0,0,.18))}}
'''


def build():
    body = (f'<div class="wrap">'
            f'<svg class="scene" viewBox="0 0 {W} 128" preserveAspectRatio="none">{scene_svg(W)}</svg>'
            f'{nav_bar()}<div class="cols">'
            f'<div class="col l">{left_col()}</div>'
            f'<div class="col m">{mid_col()}</div>'
            f'<div class="col r">{right_col()}</div>'
            f'</div>'
            f'<div class="footer"><img class="ico14" src="{ico("book")}"><span>Xlyang18</span><b>README.md</b></div>'
            f'</div>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head>'
            f'<body>{body}</body></html>')
    out = os.path.join(ROOT, 'preview', 'render.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(html)
    return out


if __name__ == '__main__':
    print('written', build())
