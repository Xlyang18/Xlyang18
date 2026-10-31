"""星露谷风主页 v4 —— 全部图标/贴纸改用游戏原生素材
布局沿用参考图的「游戏 UI」骨架：顶栏画面 → 标签页行 → 面包屑 → 三栏面板。
所有 icon 来自 svrt.py（游戏内 Tabs/Icons/Animals/Trees/Build/Fence 原图）。
"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import svrt as SV
import scene_sv as SC

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
D = json.load(open(os.path.join(ASSETS, 'data.json')))

# 尺寸体系（16 网格对齐）
W, H = 1012, 880
TOP, BOT = 276, H - 52
LX, COL_L, COL_R, GAP = 16, 240, 300, 10
MX = LX + COL_L + GAP
COL_M = W - 2 * LX - COL_L - COL_R - GAP * 2
RX = MX + COL_M + GAP
NAV_H = 46
CRUMB_H = 32
FS = 12

# 星露谷游戏 UI 配色（取自游戏菜单面板）
C = dict(
    wood_d='#6b3f22', wood='#a9692f', wood_l='#d69a4e', wood_ll='#f0c078',
    panel='#f4e0b4', panel_hi='#fdf3d0', panel_lo='#ddc08a',
    ink='#3b2410', ink2='#7a5730',
    green='#3f8f42', green_d='#2a6b2e', gold='#ffd541', red='#c2352b', blue='#2f7ec2',
    grass='#6cbb3c', grass_d='#4f9c29',
)

SHOTS = {'doucang': 'shot-doucang.png', 'lightbox': 'shot-lightbox.png', 'teamtally': 'shot-teamtally.png'}
REPO_ICON = {'doucang': 'coffee', 'lightbox': 'strawberry', 'teamtally': 'corn',
             'ruanyifeng-blog-reader': 'tomato', 'github-api-publish-guide': 'chest'}


def cur(name):
    return REPO_ICON.get(name, 'strawberry')


def b64file(rel):
    p = os.path.join(ASSETS, rel)
    if not os.path.exists(p):
        return ''
    import base64
    return 'data:image/png;base64,' + base64.b64encode(open(p, 'rb').read()).decode()


def cut(s, n):
    return s if len(s) <= n else s[:n]


def ds(d):
    return d[5:].replace('-', '/')


# ---------------- 导航：游戏原生标签页图标 + 木框 ----------------
NAV = [('Overview', 'inventory'), ('Repositories', 'crafting'), ('Projects', 'collections'),
       ('Pull requests', 'social'), ('Issues', 'animals'), ('Marketplace', 'map')]


def nav():
    tabs = ''.join(
        f'<div class="tab{" on" if i == 0 else ""}"><img class="tabico" src="{SV.tab(k, 30)}"><span>{n}</span></div>'
        for i, (n, k) in enumerate(NAV))
    tabs += (f'<div class="tab gold"><img class="tabico" src="{SV.icon("stardrop", 28)}">'
             f'<span>{D["contributions_total"]}</span></div>')
    tabs += f'<div class="tab small"><img class="tabico" src="{SV.icon("time", 28)}"></div>'
    tabs += f'<div class="tab small"><img class="tabico" src="{SV.icon("chest", 28)}"></div>'
    crumb = (f'<div class="crumbs"><img class="cico" src="{SV.icon("chest", 18)}">'
             f'<b>Xlyang18</b><span class="slash">/</span>README.md</div>')
    return f'<div class="nav">{tabs}</div>{crumb}'


# ---------------- 左栏 ----------------
def left():
    rows = ''
    for i, r in enumerate(D['repos']):
        rows += (f'<div class="repo{" on" if i == 0 else ""}">'
                 f'<img class="repoico" src="{SV.icon(cur(r["name"]), 20)}">'
                 f'<span>{cut(r["name"], 15)}</span>'
                 f'<img class="starico" src="{SV.icon("stardrop", 18)}"></div>')
    acts = ''.join(
        f'<div class="act"><img class="aico" src="{SV.icon("keg" if "Push" in a["text"] else "chest", 18)}">'
        f'<span>{cut(a["text"], 19)}</span><i>{ds(a["date"])}</i></div>'
        for a in D['activity']) or '<div class="act"><span>暂无公开动态</span></div>'
    # 游戏原生物品陈列（Harvest 区）
    harvest = ''.join(f'<img src="{SV.icon(k, 22)}">' for k in
                      ['coffee', 'tomato', 'corn', 'melon', 'pumpkin', 'wheat', 'grape', 'potato',
                       'strawberry', 'blueberry', 'cauliflower', 'red_cabbage', 'shard', 'gem_berry'])
    animals = ''.join(f'<img src="{SV.animal(k, 22)}">' for k in
                      ['white_chicken', 'brown_chicken', 'blue_chicken', 'duck', 'goat', 'pig'])
    trails = ''.join(
        f'<div class="track"><img src="{SV.icon(ic, 18)}"><span>{cut(l["name"], 12)}</span><b>{l["count"]}</b></div>'
        for l, ic in zip(D.get('langs', [])[:3], ['keg', 'furnace', 'chest']))
    return f'''<div class="panel" style="height:{BOT-TOP}px">
<div class="ph"><img class="ico" src="{SV.icon('animals', 20)}"><span>Your Repositories</span><span class="plus">+</span></div>
<div class="input">Filter repositories…</div>
{rows}
<div class="newbtn"><img class="ico" src="{SV.icon('catalogue', 20)}">New repository</div>
<div class="rule"></div>
<div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}"><span>Activity</span></div>
{acts}
<div class="rule"></div>
<div class="ph"><img class="ico" src="{SV.icon('seasons', 20)}"><span>Harvest</span></div>
<div class="grid12">{harvest}{animals}</div>
<div class="ph" style="margin-top:6px"><img class="ico" src="{SV.icon('achieve', 20)}"><span>Trails</span></div>
{trails}
</div>'''


# ---------------- 中栏 ----------------
def mid():
    bio = D['bio']
    b1, b2 = cut(bio, 15), bio[15:30]
    cards = ''
    for r in D['repos']:
        name = r['name']
        shot_uri = b64file(SHOTS[name]) if name in SHOTS else ''
        thumb = (f'<img class="shot" src="{shot_uri}">' if shot_uri
                 else f'<div class="shot none"><img src="{SV.icon(cur(name), 26)}"><span>待截图</span></div>')
        cards += f'''<div class="card">
  <img class="cico2" src="{SV.icon(cur(name), 24)}">
  <div class="card-body">
    <div class="card-head"><span class="card-title">{cut(name, 20)}</span>
      <img class="starico" src="{SV.icon('stardrop', 16)}"></div>
    <div class="card-desc">{cut(r["desc"], 24)}</div>
    <div class="meta"><i class="dot"></i>{r["lang"]}<i class="sep"></i>★ {r["stars"]}<i class="sep"></i>{r["version"]}<i class="sep"></i>{ds(r["updated"])}</div>
  </div>
  {thumb}
</div>'''
    return f'''<div class="panel" style="height:{BOT-TOP}px">
<div class="repohead">
  <div class="titles">
    <div class="bigtitle">{D["user"]} <span class="badge">Hi there</span></div>
    <div class="sub">{b1}</div><div class="sub">{b2}</div>
  </div>
  <div class="codebtn"><img class="ico" src="{SV.icon('stardrop', 18)}">Follow</div>
</div>
<div class="metabar"><img class="ico" src="{SV.icon('chest', 18)}"><span>★ {D["repos_total"]} repos</span>
<img class="ico" src="{SV.icon('animals', 18)}" style="margin-left:10px"><span>{D["contributions_total"]} contributions</span>
<img class="ico" src="{SV.icon('time', 18)}" style="margin-left:10px"><span>2021</span></div>
<div class="ph"><img class="ico" src="{SV.icon('coffee', 20)}"><span>About me</span></div>
<ul class="about">
  <li>在读大学生 · 喜爱把日常小需求做成能用的应用</li>
  <li>主力栈 Electron + Vite + React · 副业 Java / Python</li>
  <li>摄影、咖啡、文玩核桃 · 所有应用本地优先</li>
</ul>
<div class="ph"><img class="ico" src="{SV.icon('keg', 20)}"><span>Recent repositories</span></div>
{cards}
<div class="pager"><img class="ico" src="{SV.icon('chest', 18)}">1 / 1<img class="ico" src="{SV.icon('chest', 18)}"></div>
</div>'''


# ---------------- 右栏 ----------------
def right():
    cells = ''
    for col in D['weeks']:
        cells += '<div class="w">' + ''.join(f'<i class="lv{lv}"></i>' for lv in col) + '</div>'
    acts = ''.join(
        f'<div class="act"><img class="aico" src="{SV.icon("keg" if "Push" in a["text"] else "chest", 18)}">'
        f'<span>{cut(a["text"], 14)}</span><i>{ds(a["date"])}</i></div>'
        for a in D['activity'])
    bio = D['bio']
    vers = ''.join(
        f'<div class="ver"><img src="{SV.icon(cur(r["name"]), 18)}"><span>{cut(r["name"], 10)}</span><b>{r["version"]}</b></div>'
        for r in D['repos'])
    return f'''<div class="panel side">
<div class="profile">
  <div class="avaframe"><img class="ava" src="{b64file('avatar-pixel.png')}">
    <img class="pintag" src="{SV.icon('strawberry', 18)}"></div>
  <div class="pinfo">
    <div class="pname">{D["user"]}</div>
    <div class="pbio">{cut(bio, 13)}</div><div class="pbio">{bio[13:26]}</div>
  </div>
</div>
<div class="plines">
  <div><img class="ico" src="{SV.icon('animals', 18)}">{D["followers"]} follower</div>
  <div><img class="ico" src="{SV.icon('artisan', 18)}">{D["following"]} following</div>
  <div><img class="ico" src="{SV.icon('chest', 18)}">{D["repos_total"]} repositories</div>
</div>
</div>

<div class="panel side">
<div class="ph"><img class="ico" src="{SV.icon('seasons', 20)}"><span>Contribution Graph</span></div>
<div class="graph">{cells}</div>
<div class="gfoot"><img class="ico" src="{SV.icon('stardrop', 16)}"><span>{D["contributions_total"]} contributions</span>
<span>{ds(D["span"][0])} – {ds(D["span"][1])}</span></div>
</div>

<div class="panel side last">
<div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}"><span>Activity</span></div>
{acts}
<div class="vers"><div class="ph" style="margin-top:6px"><img class="ico" src="{SV.icon('keg', 18)}"><span>Release Ladder</span></div>{vers}</div>
<div class="banner"><img class="bico" src="{SV.icon('coffee', 30)}"><span>Build together.<br>Grow together.</span></div>
</div>'''


CSS_TMPL = '''
@font-face{font-family:Px;src:url(data:font/woff2;base64,__FONT__) format('woff2');font-display:block}
*{margin:0;padding:0;box-sizing:border-box}
html,body{width:__W__px}
body{background:__GRASS__;font-family:Px,monospace;color:__INK__;font-size:__FS__px;line-height:20px;
 -webkit-font-smoothing:none;font-smooth:never}
img{image-rendering:pixelated}
.wrap{position:relative;width:__W__px;height:__H__px;overflow:hidden}
.nav{display:flex;align-items:center;gap:5px;padding:7px 12px;height:46px;background:__PANELLO__;
 border-top:3px solid __WOODLL__;border-bottom:3px solid __WOODD__;box-shadow:inset 0 -2px 0 __WOOD__}
.tab{display:flex;align-items:center;gap:4px;height:32px;padding:0 9px 0 4px;background:__WOODL__;
 border:2px solid __WOODD__;box-shadow:inset 0 2px 0 __WOODLL__,inset 0 -3px 0 __WOODD__;white-space:nowrap}
.tab.on{background:__GOLD__;box-shadow:inset 0 2px 0 #ffe98a,inset 0 -3px 0 #b8860b}
.tab.gold{background:__GOLD__}
.tab.small{padding:0 5px}
.tab:first-child{margin-left:0}
.tab ~ .tab.gold{margin-left:auto}
.tabico{width:30px;height:30px}
.crumbs{display:flex;align-items:center;gap:6px;height:32px;padding:0 16px;background:__PANELHI__;
 border-bottom:3px solid __WOODD__;box-shadow:inset 0 -2px 0 __PANELLO__;color:__INK2__}
.crumbs b{font-weight:normal;color:__WOODD__}
.slash{margin:0 4px}
.cols{position:relative;padding:0 __LX__px}
.col{position:absolute;top:8px}
.l{left:__LX__px;width:__COL_L__px}
.m{left:__MX__px;width:__COL_M__px}
.r{left:__RX__px;width:__COL_R__px}
.panel{background:__PANEL__;border:3px solid __WOODD__;padding:10px;margin-bottom:9px;
 box-shadow:inset 0 3px 0 __PANELHI__,inset 0 -3px 0 __PANELLO__,4px 4px 0 rgba(59,36,16,.32)}
.ph{display:flex;align-items:center;gap:6px;margin-bottom:4px;color:__INK__}
.ico{width:20px;height:20px;flex:none}
.plus{margin-left:auto;width:20px;height:20px;display:grid;place-items:center;background:__WOODL__;
 border:2px solid __WOODD__;box-shadow:inset 0 -2px 0 __WOODD__}
.input{height:26px;line-height:22px;padding:0 7px;background:__PANELHI__;border:2px solid __WOOD__;
 box-shadow:inset 2px 2px 0 __PANELLO__;color:__INK2__;margin-bottom:7px}
.repo{display:flex;align-items:center;gap:6px;height:28px;padding:0 6px;margin-bottom:3px;
 background:__PANELHI__;border:2px solid __WOOD__;box-shadow:inset 0 -2px 0 __PANELLO__}
.repo.on{background:#ffe9a8;border-color:__WOODD__;box-shadow:inset 4px 0 0 __GREEN__,inset 0 -2px 0 #e8c983}
.repo span{flex:1;overflow:hidden;white-space:nowrap}
.repoico{width:20px;height:20px}
.starico{width:18px;height:18px;flex:none}
.newbtn{display:flex;align-items:center;gap:6px;height:30px;margin-top:8px;padding:0 8px;background:__WOODL__;
 border:2px solid __WOODD__;box-shadow:inset 0 2px 0 __WOODLL__,inset 0 -3px 0 __WOODD__}
.rule{height:2px;background:__PANELLO__;margin:7px 0 6px;box-shadow:0 1px 0 __PANELHI__}
.act{display:flex;align-items:center;gap:5px;padding:1px 0;border-bottom:2px dotted __PANELLO__;white-space:nowrap}
.act span{flex:1;overflow:hidden;text-overflow:ellipsis}
.act i{font-style:normal;color:__INK2__}
.aico{width:18px;height:18px;flex:none}
.grid12{display:flex;flex-wrap:wrap;gap:4px}
.grid12 img{width:21px;height:21px}
.track{display:flex;align-items:center;gap:6px;height:22px}
.track span{flex:1;overflow:hidden;white-space:nowrap}
.track b{font-weight:normal;color:__WOODD__}
.repohead{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}
.bigtitle{font-size:22px;line-height:26px}
.badge{padding:0 6px;background:__GREEN__;border:2px solid __GREEN_D__;color:#fff;font-size:12px;
 vertical-align:3px;box-shadow:inset 0 -2px 0 __GREEN_D__}
.sub{color:__INK2__;white-space:nowrap;overflow:hidden}
.codebtn{display:flex;align-items:center;gap:4px;flex:none;height:28px;padding:0 10px;background:__GREEN__;
 border:2px solid __GREEN_D__;color:#fff;box-shadow:inset 0 2px 0 #4fa852,inset 0 -3px 0 __GREEN_D__}
.metabar{display:flex;align-items:center;color:__INK2__;padding:4px 0;border-bottom:2px solid __PANELLO__;margin-bottom:5px;white-space:nowrap}
.dot{width:8px;height:8px;background:__GOLD__;border:1px solid __INK__;margin-right:5px;display:inline-block}
.sep{width:4px;height:4px;background:__WOOD__;margin:0 7px;display:inline-block}
.about{list-style:none;margin-bottom:5px;line-height:18px}
.about li{padding-left:14px;position:relative}
.about li:before{content:'▪';position:absolute;left:0;color:__GREEN__}
.card{position:relative;display:flex;gap:6px;align-items:center;background:__PANELHI__;
 border:2px solid __WOOD__;padding:3px 6px;margin-bottom:4px;box-shadow:inset 0 -2px 0 __PANELLO__}
.cico2{width:24px;height:24px;flex:none}
.card-body{flex:1;min-width:0}
.card-head{display:flex;justify-content:space-between;align-items:center}
.card-title{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;line-height:17px}
.card-desc{color:__INK__;white-space:nowrap;overflow:hidden;line-height:16px;opacity:.85}
.meta{display:flex;align-items:center;color:__INK2__;white-space:nowrap;line-height:16px}
.shot{width:84px;height:52px;object-fit:cover;border:2px solid __WOODD__;flex:none;background:#fff}
.shot.none{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:1px;
 background:linear-gradient(__WOODL__,__WOOD__);color:__PANELHI__;font-size:9px;line-height:10px}
.shot.none img{width:26px;height:26px}
.pager{display:flex;justify-content:center;align-items:center;gap:6px;color:__INK2__}
.profile{display:flex;gap:8px}
.avaframe{position:relative;width:60px;height:60px;flex:none;border:3px solid __WOODD__;background:__INK__;
 box-shadow:inset 0 0 0 3px __GOLD__,2px 2px 0 rgba(0,0,0,.3)}
.ava{position:absolute;inset:3px;width:48px;height:48px;object-fit:cover}
.pintag{position:absolute;right:-9px;bottom:-8px;width:20px;height:20px}
.pinfo{min-width:0}
.pname{font-size:18px;line-height:20px}
.pbio{color:__INK2__;white-space:nowrap;overflow:hidden}
.plines{margin-top:6px;line-height:21px}
.graph{display:grid;grid-template-columns:repeat(53,1fr);gap:2px;width:100%}
.graph .w{display:grid;grid-template-rows:repeat(7,1fr);gap:2px}
.graph i{aspect-ratio:1;width:100%;background:#e8e0c8}
.graph .lv0{background:#e8e0c8}
.graph .lv1{background:#c6e6a0}
.graph .lv2{background:#7fd050}
.graph .lv3{background:#2f9c2f}
.graph .lv4{background:#17632a}
.gfoot{display:flex;justify-content:space-between;align-items:center;color:__INK2__;margin-top:5px;font-size:10px}
.vers{margin-top:4px}
.ver{display:flex;align-items:center;gap:5px;height:20px}
.ver span{flex:1;overflow:hidden;white-space:nowrap}
.ver b{font-weight:normal;color:__WOODD__}
.banner{margin-top:6px;height:46px;display:flex;align-items:center;justify-content:center;gap:7px;
 background:linear-gradient(__WOODL__,__WOOD__);border:3px solid __WOODD__;
 box-shadow:inset 0 3px 0 __WOODLL__,inset 0 -3px 0 __WOODD__;color:__PANELHI__;text-align:center;line-height:16px}
.bico{width:30px;height:30px}
.footer{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;gap:8px;height:40px;
 padding:0 16px;background:__PANELHI__;border-top:3px solid __WOODD__;box-shadow:inset 0 3px 0 #fff;color:__INK2__}
.footer b{font-weight:normal;color:__WOODD__;border-bottom:3px solid #f0a020;padding-bottom:2px}
'''


def css():
    import base64
    f = base64.b64encode(open(os.path.join(ASSETS, 'fonts',
                                           'fusion-pixel-8px-proportional-zh_hans.ttf.woff2'), 'rb').read()).decode()
    rep = dict(__FONT__=f, __W__=W, __H__=H, __FS__=FS, __LX__=LX, __COL_L__=COL_L,
               __COL_M__=COL_M, __COL_R__=COL_R, __MX__=MX, __RX__=RX,
               __GRASS__=C['grass'], __INK__=C['ink'], __INK2__=C['ink2'],
               __PANEL__=C['panel'], __PANELHI__=C['panel_hi'], __PANELLO__=C['panel_lo'],
               __WOOD__=C['wood'], __WOODL__=C['wood_l'], __WOODLL__=C['wood_ll'], __WOODD__=C['wood_d'],
               __GREEN__=C['green'], __GREEN_D__=C['green_d'], __GOLD__=C['gold'])
    out = CSS_TMPL
    for k, v in rep.items():
        out = out.replace(k, str(v))
    return out


def build():
    body = (f'<div class="wrap">'
            f'{SC.scene_svg()}'
            f'{nav()}'
            f'<div class="cols">'
            f'<div class="col l">{left()}</div>'
            f'<div class="col m">{mid()}</div>'
            f'<div class="col r">{right()}</div>'
            f'</div>'
            f'<div class="footer"><img class="ico" src="{SV.icon("chest", 18)}"><span>Xlyang18</span><b>README.md</b></div>'
            f'</div>')
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body>{body}</body></html>'
    out = os.path.join(ROOT, 'preview', 'render.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(html)
    return out


if __name__ == '__main__':
    print('written', build(), os.path.getsize(os.path.join(ROOT, 'preview', 'render.html')))
