"""渲染星露谷风主页 → preview/render.html（浏览器截图用）"""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from art import *  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
D = json.load(open(os.path.join(ASSETS, 'data.json')))

FS = 12
LH = 20
PH = 20
COLH = BOT - TOP
COLH2 = COLH - 300

SHOTS = {'doucang': 'shot-doucang.png', 'lightbox': 'shot-lightbox.png', 'teamtally': 'shot-teamtally.png'}
ICONS = ['tomato', 'bean', 'corn', 'rose']


def cut(s, n):
    return s if len(s) <= n else s[:n]


def ds(d):
    return d[5:].replace('-', '/')


def nav_bar():
    items = [('Overview', 'card'), ('Repositories', 'soil'), ('Projects', 'turnip_s'), ('Pull requests', 'bean_s'),
             ('Issues', 'tomato_s'), ('Marketplace', 'rose_s'), ('Explore', 'sunflower_s')]
    html = ''.join(f'<div class="tab{" on" if i == 0 else ""}"><img class="ico" src="{sprite_uri(c)}"><span>{n}</span></div>'
                   for i, (n, c) in enumerate(items))
    html += (f'<div class="tab gold star"><img class="ico" src="{sprite_uri("sunflower")}"><span>{D["contributions_total"]}</span></div>'
             '<div class="tab small"><i class="mini"></i></div><div class="tab small">☰</div>')
    return f'<div class="nav">{html}</div><div class="crumbs"><img class="ico" src="{sprite_uri("coffee")}"><b>Xlyang18</b><i>/</i>README.md</div>'


def left_col():
    rows = ''
    for i, r in enumerate(D['repos']):
        rows += (f'<div class="repo{" on" if i == 0 else ""}"><img class="ico" src="{sprite_uri(ICONS[i % 4])}">'
                 f'<span>{cut(r["name"], 15)}</span><b>★</b></div>')
    acts = ''.join(f'<div class="act"><span>{cut(a["text"], 22)}</span><i>{ds(a["date"])}</i></div>'
                   for a in D['activity']) or '<div class="act"><span>暂无公开动态</span></div>'
    return f'''<div class="panel" style="height:{COLH}px">
{ph('seed', 'Your Repositories', '+')}
<div class="input">Filter repositories…</div>
{rows}
<div class="newbtn"><img class="ico" src="{sprite_uri('card')}">New repository</div>
<div class="rule"></div>
{ph('bean', 'Activity')}
{acts}
</div>'''


def mid_col():
    bio = D['bio']
    b1, b2 = cut(bio, 15), bio[15:30]
    cards = ''
    for r in D['repos']:
        name = r['name']
        shot_uri = file_uri(SHOTS[name]) if name in SHOTS else ''
        thumb = (f'<img class="shot" src="{shot_uri}">' if shot_uri
                 else f'<div class="shot none"><img src="{sprite_uri("seed")}"><span>no shot</span></div>')
        cards += f'''<div class="card">
  <div class="card-body">
    <div class="card-head"><span class="card-title">{cut(name, 21)}</span><span class="star">★</span></div>
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
  <div class="codebtn">Follow ▾</div>
</div>
<div class="metabar"><i class="dot"></i>★ {D["repos_total"]} repos<i class="sep"></i>{D["contributions_total"]} contributions<i class="sep"></i>2021</div>
{ph('tomato', 'About me')}
<ul class="about">
  <li>在读大学生，喜欢把日常小需求做成能用的应用</li>
  <li>主力栈 Electron + Vite + React</li>
  <li>摄影、咖啡、文玩核桃；副业 Java / Python</li>
  <li>所有应用本地优先：不联网、不上传</li>
</ul>
{ph('sunflower_s', 'Recent repositories')}
{cards}
<div class="pager"><span>←</span>1 / 1<span>→</span></div>
</div>'''


def right_col():
    avatar_uri = file_uri('avatar-pixel.png') or sprite_uri('turnip')
    cells = ''
    for col in D['weeks']:
        inner = ''.join(f'<i class="lv{lv}"></i>' for lv in col)
        cells += f'<div class="w">{inner}</div>'
    acts = ''.join(f'<div class="act"><span>{cut(a["text"], 16)}</span><i>{ds(a["date"])}</i></div>'
                   for a in D['activity'])
    bio = D['bio']
    return f'''<div class="panel side">
<div class="profile">
  <div class="avaframe"><img class="ava" src="{avatar_uri}"><i class="pintag"><img src="{sprite_uri('rose')}"></i></div>
  <div class="pinfo">
    <div class="pname">{D["user"]}</div>
    <div class="pbio">{cut(bio, 13)}</div><div class="pbio">{bio[13:26]}</div>
  </div>
</div>
<div class="plines"><div>{D["followers"]} follower</div><div>{D["following"]} following</div><div>{D["repos_total"]} repositories</div></div>
</div>

<div class="panel side">
{ph('seed', 'Contribution Graph')}
<div class="graph">{cells}</div>
<div class="gfoot"><span>{D["contributions_total"]} contributions</span><span>{ds(D["span"][0])} – {ds(D["span"][1])}</span></div>
</div>

<div class="panel side last" style="height:{COLH2}px">
{ph('bean', 'Activity')}
{acts}
<div class="banner">Build together.<br>Grow together.</div>
</div>'''


def css():
    F8 = font_b64('fusion-pixel-8px-proportional-zh_hans.ttf.woff2')
    return f'''
@font-face{{font-family:Px;src:url(data:font/woff2;base64,{F8}) format('woff2');font-display:block}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{W}px}}
body{{background:{C['grass']};font-family:Px,monospace;color:{C['ink']};font-size:{FS}px;line-height:{LH}px;
  -webkit-font-smoothing:none;font-smooth:never;text-rendering:optimizeSpeed}}
img.ico{{width:{FS}px;height:{FS}px;image-rendering:pixelated;margin-right:6px;vertical-align:-2px;flex:none}}
.wrap{{position:relative;width:{W}px;height:{H}px;background:{C['grass']};
  background-image:repeating-linear-gradient(0deg,rgba(0,0,0,.05) 0 2px,transparent 2px 8px)}}
.scene{{display:block;width:{W}px;height:128px;image-rendering:pixelated}}
.nav{{display:flex;align-items:center;gap:6px;padding:8px 12px;height:44px;background:{C['paper_d']};border-bottom:3px solid {C['wood_d']}}}
.tab{{display:flex;align-items:center;height:28px;padding:0 8px 0 6px;background:{C['wood_l']};border:2px solid {C['wood_d']};
  box-shadow:inset 0 2px 0 #f0d2a6,inset 0 -3px 0 #8a5a2f;white-space:nowrap}}
.tab.on{{background:{C['gold']}}} .tab.gold{{background:{C['gold']}}} .tab.small{{padding:0 8px}}
.tab.star{{margin-left:auto}}
.mini{{width:14px;height:14px;background:{C['ink']};box-shadow:inset 0 0 0 2px {C['purple']}}}
.crumbs{{display:flex;align-items:center;height:34px;padding:0 16px;background:{C['paper_l']};border-bottom:3px solid {C['wood_d']};box-shadow:inset 0 -2px 0 {C['paper_d']}}}
.crumbs b{{font-weight:normal;color:{C['wood_d']}}} .crumbs i{{font-style:normal;margin:0 8px;color:{C['ink2']}}}
.cols{{position:relative;padding:0 {PAD}px;min-height:{BOT-TOP+16}px}}
.col{{position:absolute;top:8px}}
.l{{left:{PAD}px;width:{COL_L}px}} .m{{left:{MX}px;width:{COL_M}px}} .r{{left:{RX}px;width:{COL_R}px}}
.panel{{background:{C['paper']};border:3px solid {C['wood_d']};padding:10px;margin-bottom:10px;
  box-shadow:inset 0 3px 0 {C['paper_l']},inset 0 -3px 0 {C['paper_d']},4px 4px 0 rgba(59,23,37,.3)}}
.ph{{display:flex;align-items:center;height:{PH}px;margin-bottom:6px}}
.plus{{margin-left:auto;width:20px;height:20px;display:grid;place-items:center;background:{C['wood_l']};border:2px solid {C['wood_d']}}}
.input{{height:26px;line-height:22px;padding:0 6px;background:{C['paper_l']};border:2px solid {C['wood']};color:{C['ink2']};margin-bottom:8px}}
.repo{{display:flex;align-items:center;height:28px;padding:0 6px;margin-bottom:4px;background:{C['paper_l']};border:2px solid {C['wood']}}}
.repo.on{{background:#ffe9a8;border-color:{C['wood_d']};box-shadow:inset 4px 0 0 {C['green']}}}
.repo span{{overflow:hidden;white-space:nowrap}}
.repo b{{margin-left:auto;color:{C['orange']}}}
.newbtn{{display:flex;align-items:center;height:28px;margin-top:10px;padding:0 8px;background:{C['wood_l']};border:2px solid {C['wood_d']};box-shadow:inset 0 -3px 0 #8a5a2f}}
.rule{{height:2px;background:{C['paper_d']};margin:10px 0 8px}}
.act{{display:flex;justify-content:space-between;gap:4px;padding:3px 0;border-bottom:2px dotted {C['paper_d']};white-space:nowrap}}
.act span{{overflow:hidden;text-overflow:ellipsis}} .act i{{font-style:normal;color:{C['ink2']}}}
.repohead{{display:flex;justify-content:space-between;gap:8px;align-items:flex-start}}
.bigtitle{{font-size:22px;line-height:26px}}
.badge{{padding:0 6px;background:{C['green']};border:2px solid #0d6b1e;color:#fff;font-size:{FS}px;vertical-align:3px}}
.sub{{color:{C['ink2']};white-space:nowrap;overflow:hidden}}
.codebtn{{flex:none;height:26px;line-height:20px;padding:0 10px;background:{C['green']};border:2px solid #0d6b1e;color:#fff;box-shadow:inset 0 -3px 0 #0d6b1e}}
.metabar{{display:flex;align-items:center;color:{C['ink2']};padding:6px 0;border-bottom:2px solid {C['paper_d']};margin-bottom:6px;white-space:nowrap}}
.dot{{width:8px;height:8px;background:{C['gold']};border:1px solid {C['ink']};margin-right:6px;flex:none;display:inline-block}}
.sep{{width:4px;height:4px;background:{C['wood']};margin:0 7px;flex:none;display:inline-block}}
.about{{list-style:none;margin-bottom:6px}}
.about li{{padding-left:12px;position:relative}}
.about li:before{{content:'▪';position:absolute;left:0;color:{C['green']}}}
.card{{display:flex;gap:7px;align-items:center;background:{C['paper_l']};border:2px solid {C['wood']};padding:4px 6px;margin-bottom:5px}}
.card-body{{flex:1;min-width:0}}
.card-head{{display:flex;justify-content:space-between}}
.card-title{{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.star{{color:{C['orange']}}}
.card-desc{{color:{C['ink2']};white-space:nowrap;overflow:hidden;line-height:18px}}
.meta{{display:flex;align-items:center;color:{C['ink2']};white-space:nowrap;line-height:18px}}
.shot{{width:88px;height:56px;object-fit:cover;border:2px solid {C['wood_d']};flex:none;background:#fff}}
.shot.none{{display:grid;place-items:center;background:{C['wood_l']};color:{C['ink2']};font-size:10px}}
.shot.none img{{width:24px;height:24px;image-rendering:pixelated;margin:auto}}
.pager{{display:flex;justify-content:center;align-items:center;gap:8px;color:{C['ink2']}}}
.pager span{{width:22px;height:20px;display:grid;place-items:center;background:{C['wood_l']};border:2px solid {C['wood_d']}}}
.profile{{display:flex;gap:8px}}
.avaframe{{position:relative;width:64px;height:64px;flex:none;border:3px solid {C['wood_d']};background:{C['ink']};box-shadow:inset 0 0 0 3px {C['gold']}}}
.ava{{position:absolute;inset:3px;width:52px;height:52px;image-rendering:pixelated;object-fit:cover}}
.pintag{{position:absolute;right:-8px;bottom:-6px;width:18px;height:18px;background:{C['paper_l']};border:2px solid {C['wood_d']};display:grid;place-items:center}}
.pintag img{{width:14px;height:14px;image-rendering:pixelated}}
.pinfo{{min-width:0}} .pname{{font-size:18px;line-height:20px}}
.pbio{{color:{C['ink2']};white-space:nowrap;overflow:hidden}}
.plines{{margin-top:6px;line-height:22px}}
.graph{{display:grid;grid-template-columns:repeat(53,1fr);gap:2px;width:100%}}
.graph .w{{display:grid;grid-template-rows:repeat(7,1fr);gap:2px}}
.graph i{{aspect-ratio:1;width:100%;background:#e8e0c8}}
.graph .lv0{{background:#e8e0c8}}
.graph .lv1{{background:#c6e6a0}} .graph .lv2{{background:#7fd050}}
.graph .lv3{{background:#2f9c2f}} .graph .lv4{{background:#17632a}}
.gfoot{{display:flex;justify-content:space-between;color:{C['ink2']};margin-top:4px;font-size:10px}}
.footer{{position:absolute;left:0;right:0;bottom:0;display:flex;align-items:center;height:40px;padding:0 16px;background:{C['paper_l']};
  border-top:3px solid {C['wood_d']};box-shadow:inset 0 3px 0 #fff;color:{C['ink2']}}}
.footer span{{margin-right:8px;color:{C['ink']}}}
.footer b{{font-weight:normal;color:{C['wood_d']};border-bottom:3px solid {C['orange']};padding-bottom:2px}}
.footer:before{{content:'';width:18px;height:18px;margin-right:8px;background:#000;border-radius:50%;
  clip-path:polygon(0 60%,30% 60%,30% 40%,70% 40%,70% 60%,100% 60%,100% 100%,0 100%)}}
.banner{{margin-top:6px;height:52px;display:grid;place-items:center;text-align:center;background:{C['wood_l']};
  border:3px solid {C['wood_d']};box-shadow:inset 0 3px 0 #f0d2a6}}
'''


def build():
    body = (f'<div class="wrap">'
            f'<svg class="scene" viewBox="0 0 {W} 128" preserveAspectRatio="none">{scene_svg(W)}</svg>'
            f'{nav_bar()}<div class="cols">'
            f'<div class="col l">{left_col()}</div>'
            f'<div class="col m">{mid_col()}</div>'
            f'<div class="col r">{right_col()}</div>'
            f'</div></div>'
            f'<div class="footer"><span>Xlyang18</span><b>README.md</b></div></div>')
    html = f'<!doctype html><html><head><meta charset="utf-8"><style>{css()}</style></head><body>{body}</body></html>'
    out = os.path.join(ROOT, 'preview', 'render.html')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'w').write(html)
    return out


if __name__ == '__main__':
    print('written', build())
