"""生成可交互像素前端站点（GitHub Pages）→ dist/
全响应式、全按钮可交互、卡片可跳转仓库；像素字号放大到可读区间。
"""
import base64, json, os, shutil
import svrt as SV
import letter as LT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
DIST = os.path.join(ROOT, 'dist')
D = json.load(open(os.path.join(ASSETS, 'data.json')))

GH = 'https://github.com/Xlyang18'
SHOTS = {'doucang': 'shot-doucang.png', 'lightbox': 'shot-lightbox.png', 'teamtally': 'shot-teamtally.png'}
REPO_ICON = {'doucang': 'coffee', 'lightbox': 'strawberry', 'teamtally': 'corn',
             'ruanyifeng-blog-reader': 'tomato', 'github-api-publish-guide': 'chest'}
NAV = [('Overview', 'inventory', '#top'), ('Repositories', 'crafting', '#repos'),
       ('Projects', 'collections', '#repos'), ('Pull requests', 'social', f'{GH}?tab=repositories'),
       ('Issues', 'animals', f'{GH}/Xlyang18/issues'), ('Marketplace', 'map', f'{GH}?tab=stars'),
       ('Settings', 'options', 'https://github.com/settings/profile')]


def b64(path):
    p = os.path.join(ASSETS, path)
    return base64.b64encode(open(p, 'rb').read()).decode() if os.path.exists(p) else ''


FONT_PX = b64('fonts/fusion-pixel-8px-proportional-zh_hans.ttf.woff2')
FONT_SV = b64('fonts/Stardew_Valley.ttf')


def cur(name):
    return REPO_ICON.get(name, 'strawberry')


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def short(text, limit=130):
    """摘要截断：优先在标点处收口，避免出现「要么还」「- [下载]」这类残渣"""
    import re as _re
    t = (text or '').strip()
    t = _re.sub(r'\s+[-•]\s+', ' ', t)           # 去掉 markdown 列表符号
    t = _re.sub(r'[：:]\s*，', '，', t)
    t = _re.sub(r'\s{2,}', ' ', t)
    for junk in ['- [', '[下载]', '[点击]', '](http', '![']:
        i = t.find(junk)
        if i > 20:
            t = t[:i]
    t = t.rstrip(' -—·|')
    if len(t) <= limit:
        return t
    cut = t[:limit]
    for i in range(len(cut) - 1, max(0, limit - 34), -1):
        if cut[i] in '。！？；，、)]」':
            return cut[:i + 1] if cut[i] in '。！？' else cut[:i] + '…'
    return cut + '…'


def scene_svg():
    import scene_sv
    return scene_sv.scene_svg(1520)


def nav_html():
    out = ''
    for i, (name, icon, href) in enumerate(NAV):
        ext = ' target="_blank" rel="noopener"' if href.startswith('http') else ''
        out += (f'<a class="tab{" on" if i == 0 else ""}" href="{href}"{ext} data-nav="{name}">'
                f'<img class="tabico" src="{SV.tab(icon, 28)}" alt=""><span>{name}</span></a>')
    out += (f'<button class="tab gold" id="btn-contrib" title="查看贡献图">'
            f'<img class="tabico" src="{SV.icon("stardrop", 28)}" alt="">'
            f'<span>{D["contributions_total"]}</span></button>')
    out += ('<button class="tab small" id="btn-theme" title="切换浅色/夜间" aria-label="切换主题">'
            f'<img class="tabico" src="{SV.tab("options", 28)}" alt=""></button>')
    out += (f'<a class="tab small" href="{GH}" target="_blank" rel="noopener" title="打开 GitHub 主页">'
            f'<img class="tabico" src="{SV.tab("exit", 28)}" alt=""></a>')
    return f'<nav class="nav" aria-label="主导航">{out}</nav>'


def repo_rows():
    out = ''
    for i, r in enumerate(D['repos']):
        n = r['name']
        out += (f'<a class="repo{" on" if i == 0 else ""}" href="{GH}/{esc(n)}" target="_blank" '
                f'rel="noopener" data-repo="{esc(n)}" title="{esc(n)} — 点击定位卡片，⌘+点击直接开仓库">'
                f'<img class="repoico" src="{SV.icon(cur(n), 20)}" alt="">'
                f'<span>{esc(n)}</span>'
                f'<img class="starico" src="{SV.icon("stardrop", 18)}" alt=""></a>')
    return out


def cards():
    out = ''
    for r in D['repos']:
        n = r['name']
        url = f'{GH}/{n}'
        shot = SHOTS.get(n)
        thumb = (f'<div class="thumb" style="background-image:url(data:image/png;base64,{b64(shot)})"></div>'
                 if shot else f'<div class="thumb none"><img src="{SV.icon(cur(n), 32)}" alt=""></div>')
        commits = ''.join(
            f'<li><a href="{url}/commit/{esc(c["sha"])}" target="_blank" rel="noopener">'
            f'<code>{esc(c["sha"])}</code></a><span>{esc(c["msg"])}</span><i>{esc(c["date"][5:])}</i></li>'
            for c in r.get('commits', [])[:4])
        out += f'''<article class="card" data-repo="{esc(n)}">
  <a class="thumb-link" href="{url}" target="_blank" rel="noopener" tabindex="-1" aria-hidden="true">{thumb}</a>
  <div class="card-main">
    <header>
      <img class="cico" src="{SV.icon(cur(n), 22)}" alt="">
      <a class="title" href="{url}" target="_blank" rel="noopener">{esc(n)}</a>
      <span class="badge">{esc(r["lang"])}</span>
      <span class="ver">{esc(r["version"])}</span>
    </header>
    <p class="summary">{short(r["readme"] or r["desc"])}</p>
    <details class="more">
      <summary>展开 README 摘要 · 最近提交</summary>
      <p class="readme-full">{esc(r["readme"] or r["desc"])}</p>
      <ul class="commits">{commits}</ul>
    </details>
    <footer>
      <span>★ {r["stars"]}</span><span>更新 {esc(r["updated"])}</span>
      <a class="go" href="{url}" target="_blank" rel="noopener">打开仓库 →</a>
    </footer>
  </div>
</article>'''
    return out


def graph():
    out = ''
    for col in D['weeks']:
        out += '<div class="w">' + ''.join(f'<i class="lv{lv}"></i>' for lv in col) + '</div>'
    return out


def page():
    tag = D.get('tagline', '科技爱好者。想法在脑子里是草图，npm run build 之后就得能跑。')
    tag_html = esc(tag).replace('npm run build', '<code class="cmdtxt">npm run build</code>')
    pets = ''.join(f'<img src="{SV.animal(k, 26)}" alt="{k}" title="{k}">'
                   for k in ['white_chicken', 'brown_chicken', 'blue_chicken', 'duck',
                             'goat', 'pig', 'rabbit', 'horse'])
    acts = ''.join(f'<li><span>{esc(a["text"])}</span><i>{esc(a["date"][5:])}</i></li>'
                   for a in D['activity'])
    return f'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Xlyang18 · 像素农场主页</title>
<meta name="description" content="{esc(tag)}">
<link rel="icon" href="data:image/png;base64,{b64('avatar-pixel.png')}">
<style>
@font-face{{font-family:SVf;src:url(data:font/ttf;base64,{FONT_SV}) format('truetype');font-display:swap}}
@font-face{{font-family:Px;src:url(data:font/woff2;base64,{FONT_PX}) format('woff2');font-display:swap}}
:root{{
  --wood-d:#6b3f22;--wood:#a9692f;--wood-l:#d69a4e;--wood-ll:#f0c078;
  --panel:#f4e0b4;--panel-hi:#fdf3d0;--panel-lo:#ddc08a;
  --ink:#33200e;--ink2:#654322;--green:#3f8f42;--green-d:#26602a;
  --gold:#ffd541;--grass:#6cbb3c;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{background:var(--grass);color:var(--ink);font-family:Px,SVf,monospace;font-size:16px;line-height:27px;letter-spacing:.2px;
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;overflow-x:hidden}}
img{{image-rendering:pixelated;display:block}}
a{{color:inherit;text-decoration:none}}
button{{font:inherit;color:inherit;background:none;border:0;cursor:pointer}}
.wrap{{max-width:100%;margin:0 auto;background:var(--grass);min-height:100vh}}
/* 顶栏画面：等比裁切，任何宽度都不变形、不撑破 */
.scene{{height:clamp(120px,13vw,206px);overflow:hidden;position:relative;background:#7fcbf0}}
.scene svg{{display:block;width:100%;height:100%;object-position:left center}}
/* 导航 */
.nav{{display:flex;flex-wrap:wrap;align-items:center;gap:7px;padding:8px clamp(8px,1.5vw,16px);
  background:var(--panel-lo);border-top:3px solid var(--wood-ll);border-bottom:3px solid var(--wood-d);
  position:sticky;top:0;z-index:30}}
.tab{{font-family:SVf,Px,monospace;display:inline-flex;align-items:center;gap:7px;height:38px;padding:0 13px 0 5px;background:var(--wood-l);
  border:2px solid var(--wood-d);box-shadow:inset 0 2px 0 var(--wood-ll),inset 0 -3px 0 var(--wood-d);
  white-space:nowrap;transition:transform .08s,filter .08s}}
.tab:hover{{transform:translateY(-1px);filter:brightness(1.08)}}
.tab:active{{transform:translateY(1px);filter:brightness(.95)}}
.tab.on{{background:var(--gold)}}
.tab.gold{{background:var(--gold);margin-left:auto}}
.tab.small{{padding:0 6px}}
.tabico{{width:28px;height:28px;flex:none}}
/* 面包屑 */
.crumbs{{display:flex;align-items:center;gap:9px;padding:0 clamp(8px,1.5vw,16px);min-height:38px;
  background:var(--panel-hi);border-bottom:3px solid var(--wood-d);color:var(--ink2);font-size:15px}}
.crumbs b{{font-weight:normal;color:var(--wood-d)}}
.crumbs a:hover{{text-decoration:underline}}
/* 三栏 */
.cols-inner{{max-width:1720px;margin:0 auto}}
.cols{{display:grid;grid-template-columns:262px minmax(0,1fr) 316px;gap:16px;
  padding:16px clamp(12px,1.6vw,24px) 26px;align-items:start}}
.panel{{background:var(--panel);border:3px solid var(--wood-d);padding:13px;margin-bottom:13px;
  box-shadow:inset 0 3px 0 var(--panel-hi),inset 0 -3px 0 var(--panel-lo),0 0 0 1px rgba(107,63,34,.35),4px 5px 0 rgba(59,36,16,.28)}}
.ph{{display:flex;align-items:center;gap:9px;margin-bottom:11px;font-size:16.5px;
  border-bottom:2px solid var(--panel-lo);padding-bottom:7px}}
.ico{{width:20px;height:20px;flex:none}}
/* 仓库列表 */
.repo{{display:flex;align-items:center;gap:9px;height:38px;padding:0 9px;margin-bottom:6px;
  background:var(--panel-hi);border:2px solid var(--wood);box-shadow:inset 0 -2px 0 var(--panel-lo);
  transition:background .1s,transform .08s}}
.repo:hover{{background:#ffeebf;transform:translateX(2px)}}
.repo.on{{background:#ffe9a8;border-color:var(--wood-d);box-shadow:inset 4px 0 0 var(--green),inset 0 -2px 0 #e8c983}}
.repo span{{flex:1;min-width:0;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;font-size:15px}}
.repoico{{width:20px;height:20px;flex:none}} .starico{{width:18px;height:18px;flex:none}}
/* 搜索 */
.searchwrap{{position:relative;margin-bottom:10px}}
.search{{width:100%;height:36px;padding:0 34px 0 10px;background:var(--panel-hi);border:2px solid var(--wood);
  box-shadow:inset 2px 2px 0 var(--panel-lo);color:var(--ink);font:inherit;font-size:14.5px}}
.search::placeholder{{color:#9b7a52}}
.searchwrap::after{{content:'⌕';position:absolute;right:10px;top:50%;transform:translateY(-50%);
  color:var(--wood);font-size:19px;pointer-events:none}}
/* 主区 */
h1{{font-family:SVf,Px,monospace;font-size:31px;line-height:36px;font-weight:normal;display:flex;align-items:center;gap:11px;flex-wrap:wrap}}
.badge{{font-size:12.5px;background:var(--green);color:#fff;border:2px solid var(--green-d);padding:2px 8px}}
.tagline{{font-size:17px;line-height:26px;color:var(--wood-d);background:rgba(255,255,255,.6);
  border-left:5px solid var(--green);padding:7px 11px;margin:7px 0 9px}}
.cmdtxt{{font-family:Px,monospace;background:var(--wood-d);color:#ffe9a8;padding:0 5px;font-size:15px}}
.sub{{color:var(--ink2);font-size:15px}}
.metabar{{display:flex;flex-wrap:wrap;gap:16px;color:var(--ink2);border-bottom:2px solid var(--panel-lo);
  padding:9px 0;margin:9px 0 11px;font-size:15px}}
/* 信件 */
.letter{{position:relative;border:2px solid var(--wood-d);background-color:#ffe8bd;
  background-image:linear-gradient(rgba(255,255,255,.35),rgba(255,255,255,.35));
  background-size:32px 32px;box-shadow:inset 0 0 0 2px #f6d3a0,inset 0 0 22px rgba(160,110,50,.16);
  padding:18px 20px 20px;margin-bottom:16px;color:#3d2711;font-size:15.5px;line-height:29px;letter-spacing:.3px}}
.letter h4{{font-size:15px;color:#8a5a2f;font-weight:normal;border-bottom:1px dashed #c9a26a;
  padding-bottom:6px;margin-bottom:8px;letter-spacing:.5px}}
.letter-wrap{{position:relative;margin-bottom:18px}}
.letter-wrap::before{{content:'';position:absolute;left:-3px;top:-3px;right:-3px;bottom:-3px;
  border:3px solid var(--wood-d);box-shadow:0 0 0 1px rgba(107,63,34,.3);pointer-events:none}}
.letter p{{margin:0 0 10px}}
.letter p:last-child{{margin-bottom:0}}
/* 卡片 */
.cards{{display:grid;gap:12px}}
.card{{display:grid;grid-template-columns:142px minmax(0,1fr);gap:13px;background:var(--panel-hi);
  border:2px solid var(--wood);box-shadow:inset 0 -2px 0 var(--panel-lo);padding:11px;cursor:pointer;
  transition:transform .1s,box-shadow .1s}}
.card:hover{{transform:translateY(-2px);box-shadow:inset 0 -2px 0 var(--panel-lo),3px 5px 0 rgba(59,36,16,.24)}}
.card.hide{{display:none}}
.thumb-link{{display:block}}
.thumb{{width:142px;height:100px;background-size:cover;background-position:top center;
  border:2px solid var(--wood-d);transition:filter .1s}}
.thumb-link:hover .thumb{{filter:brightness(1.08) saturate(1.06)}}
.thumb.none{{display:grid;place-items:center;background:linear-gradient(var(--wood-l),var(--wood))}}
.thumb.none img{{width:34px;height:34px}}
.card-main{{min-width:0}}
.card-main header{{display:flex;align-items:center;gap:9px;flex-wrap:wrap}}
.cico{{width:22px;height:22px;flex:none}}
.title{{font-family:SVf,Px,monospace;font-size:19px;border-bottom:2px solid transparent}}
.title:hover{{border-bottom-color:var(--gold)}}
.ver{{font-size:13.5px;color:var(--wood-d)}}
.summary{{font-size:15.5px;line-height:26px;margin:6px 0 7px}}
.more summary{{cursor:pointer;color:var(--green-d);font-size:14.5px;list-style:none;padding:3px 0}}
.more summary::-webkit-details-marker{{display:none}}
.more summary::before{{content:'▸ ';}}
.more[open] summary::before{{content:'▾ ';}}
.more summary:hover{{text-decoration:underline}}
.readme-full{{font-size:15px;line-height:26px;color:var(--ink2);margin:7px 0;padding-left:12px;
  border-left:3px solid var(--panel-lo)}}
.commits{{list-style:none;font-size:14.5px;line-height:23px;color:var(--ink2)}}
.commits li{{display:flex;gap:9px;align-items:baseline}}
.commits a:hover code{{background:var(--green-d)}}
.commits code{{background:var(--wood-d);color:#ffe9a8;padding:1px 5px;font-family:Px,monospace;
  font-size:12.5px;flex:none}}
.commits span{{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.commits i{{font-style:normal;flex:none;color:var(--wood)}}
.card footer{{display:flex;align-items:center;gap:15px;font-size:14.5px;color:var(--ink2);
  margin-top:8px;border-top:1px dashed var(--panel-lo);padding-top:7px}}
.go{{margin-left:auto;color:var(--green-d);border-bottom:2px solid var(--gold)}}
.go:hover{{background:#ffe9a8}}
/* 右栏 */
.profile{{display:flex;gap:11px;align-items:flex-start}}
.avaframe{{position:relative;width:66px;height:66px;flex:none;border:3px solid var(--wood-d);
  background:var(--ink);box-shadow:inset 0 0 0 3px var(--gold)}}
.avaframe img.ava{{position:absolute;inset:3px;width:54px;height:54px;object-fit:cover}}
.pintag{{position:absolute;right:-9px;bottom:-8px;width:20px;height:20px}}
.lines{{margin-top:9px;font-size:15px;line-height:26px}}
.lines a:hover{{text-decoration:underline;color:var(--green-d)}}
.acts{{list-style:none}}
.acts li{{display:flex;gap:9px;font-size:15px;line-height:25px;border-bottom:2px dotted var(--panel-lo)}}
.acts li span{{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.acts li i{{font-style:normal;color:var(--ink2);flex:none}}
.graph{{display:grid;grid-template-columns:repeat(53,1fr);gap:2px}}
.graph .w{{display:grid;grid-template-rows:repeat(7,1fr);gap:2px}}
.graph i{{aspect-ratio:1;background:#e8e0c8}}
.graph .lv1{{background:#c6e6a0}} .graph .lv2{{background:#7fd050}}
.graph .lv3{{background:#2f9c2f}} .graph .lv4{{background:#17632a}}
.gfoot{{display:flex;flex-wrap:wrap;gap:4px 10px;justify-content:space-between;font-size:13px;color:var(--ink2);margin-top:7px}}
.gfoot span{{white-space:nowrap}}
.petgrid{{display:flex;flex-wrap:wrap;gap:8px}}
.petgrid img{{width:26px;height:26px;transition:transform .1s}}
.petgrid img:hover{{transform:scale(1.2)}}
.banner{{display:flex;align-items:center;justify-content:center;gap:10px;padding:13px 8px;
  background:linear-gradient(var(--wood-l),var(--wood));border:3px solid var(--wood-d);
  box-shadow:inset 0 3px 0 var(--wood-ll),inset 0 -3px 0 var(--wood-d);color:var(--panel-hi);
  font-size:15px;line-height:20px;text-align:center}}
/* 页脚 */
.footer{{display:flex;flex-wrap:wrap;align-items:center;gap:11px;padding:12px clamp(8px,1.5vw,16px);
  background:var(--panel-hi);border-top:3px solid var(--wood-d);color:var(--ink2);font-size:14px}}
.footer b{{font-weight:normal;color:var(--wood-d);border-bottom:3px solid #f0a020;padding-bottom:2px}}
/* 夜间 */
body.night{{--panel:#2f2a3d;--panel-hi:#3d3550;--panel-lo:#241f31;--ink:#f6ead0;--ink2:#d6c6a6;--grass:#22301f}}
body.night .letter,body.night .letter p,body.night .letter h4{{color:#f0e6cc !important}}
body.night .letter{{background-color:#3a3350;box-shadow:inset 0 0 0 2px #55496f}}
body.night .summary,body.night .sub{{color:#f6ead0}}
body.night .readme-full,body.night .commits,body.night .metabar,body.night .lines,
body.night .gfoot,body.night .footer,body.night .acts li i{{color:#d6c6a6}}
body.night .tab,body.night .nav{{color:#2a1a1a}}
body.night .crumbs{{--ink2:#5a3a1c}}
/* 响应式 */
@media (max-width:1180px){{
  .cols{{grid-template-columns:236px minmax(0,1fr)}}
  .side{{grid-column:1/-1;display:grid;grid-template-columns:1fr 1fr;gap:13px}}
  .side .panel{{margin:0}}
}}
@media (max-width:900px){{
  .cols{{grid-template-columns:1fr}}
  .side-left,.side{{grid-column:auto}}
  .side{{grid-template-columns:1fr}}
  .nav .tab span{{display:none}}
  .nav .tab{{height:40px;padding:0 10px}}
  .nav .tab.gold{{margin-left:0}}
  .nav .tab.gold span{{display:inline}}
  .scene{{height:120px}}
  .tagline{{font-size:16px}}
}}
@media (max-width:640px){{
  .scene{{height:112px}}
  .scene svg{{transform-origin:left center}}
  body{{font-size:16px;line-height:26px}}
  .card{{grid-template-columns:1fr}}
  .thumb,.thumb-link{{width:100%}}
  .thumb{{width:100%;height:158px}}
  h1{{font-size:26px}}
  .letter{{font-size:15px;line-height:26px}}
  .scene{{height:100px}}
  .nav{{gap:5px}}
}}
@media (prefers-reduced-motion:reduce){{*{{transition:none!important;animation:none!important}}}}
</style>
</head>
<body>
<div class="wrap" id="top">
  <div class="scene">{scene_svg()}</div>
  {nav_html()}
  <div class="crumbs"><img class="ico" src="{SV.uico('bundle', 18)}" alt="">
    <a href="{GH}" target="_blank" rel="noopener"><b>Xlyang18</b></a><span>/</span>
    <a href="https://xlyang18.github.io/">README.md</a></div>

  <div class="cols">
    <aside class="side-left">
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('animals', 20)}" alt=""><span>Your Repositories</span></div>
        <div class="searchwrap"><input class="search" id="q" type="search"
          placeholder="Filter repositories…" aria-label="筛选仓库"></div>
        <div id="repo-list">{repo_rows()}</div>
      </div>
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}" alt=""><span>Contribution</span></div>
        <div class="graph" id="contrib-block">{graph()}</div>
        <div class="gfoot"><span>{D["contributions_total"]} contributions</span>
          <span>{D["span"][0][5:]} – {D["span"][1][5:]}</span></div>
      </div>
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('animals', 20)}" alt=""><span>Animals</span></div>
        <div class="petgrid">{pets}</div>
      </div>
    </aside>

    <main>
      <div class="panel">
        <h1>{esc(D["user"])} <span class="badge">Hi there</span></h1>
        <div class="tagline">{tag_html}</div>
        <div class="metabar">
          <span>★ {D["repos_total"]} repositories</span>
          <span>◆ {D["contributions_total"]} contributions</span>
          <span>⌛ since 2021</span>
        </div>
        <div class="letter-wrap">{LT.letter_html(per=34)}</div>
        <div class="ph" id="repos"><img class="ico" src="{SV.icon('keg', 20)}" alt=""><span>Recent repositories</span></div>
        <div class="cards" id="cards">{cards()}</div>
      </div>
    </main>

    <aside class="side">
      <div class="panel">
        <div class="profile">
          <div class="avaframe"><img class="ava" src="data:image/png;base64,{b64('avatar-pixel.png')}" alt="头像">
            <img class="pintag" src="{SV.icon('strawberry', 18)}" alt=""></div>
          <div><div style="font-size:21px">{esc(D["user"])}</div>
            <div class="sub" style="font-size:14px">{esc(D["bio"])}</div></div>
        </div>
        <div class="lines">
          <div><a href="{GH}?tab=followers" target="_blank" rel="noopener">{D["followers"]} follower</a></div>
          <div><a href="{GH}?tab=following" target="_blank" rel="noopener">{D["following"]} following</a></div>
          <div><a href="{GH}?tab=repositories" target="_blank" rel="noopener">{D["repos_total"]} repositories</a></div>
        </div>
      </div>
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}" alt=""><span>Activity</span></div>
        <ul class="acts">{acts}</ul>
        <div class="banner" style="margin-top:11px"><img src="{SV.icon('coffee', 30)}" alt=""
          style="width:30px;height:30px"><span>Build together.<br>Grow together.</span></div>
      </div>
    </aside>
  </div>

  <div class="footer"><img class="ico" src="{SV.uico('bundle', 18)}" alt=""><span>Xlyang18</span><b>README.md</b>
    <span style="margin-left:auto">数据更新：{esc(D.get("updated_at", "")[:16])}</span></div>
</div>

<script>
(function(){{
  var $ = function(s, r){{ return (r || document).querySelector(s); }};
  var $$ = function(s, r){{ return Array.prototype.slice.call((r || document).querySelectorAll(s)); }};
  var GH = {json.dumps(GH)};

  /* 1. 搜索过滤（含空状态提示） */
  var q = $('#q'), cardsBox = $('#cards');
  q.addEventListener('input', function(){{
    var v = this.value.trim().toLowerCase();
    $$('.card').forEach(function(c){{
      c.classList.toggle('hide', !!v && c.dataset.repo.toLowerCase().indexOf(v) < 0);
    }});
    $$('#repo-list .repo').forEach(function(a){{
      a.style.display = (!v || a.dataset.repo.toLowerCase().indexOf(v) >= 0) ? '' : 'none';
    }});
    var empty = $('#empty-tip');
    if (!$$('.card:not(.hide)').length) {{
      if (!empty) {{
        empty = document.createElement('p');
        empty.id = 'empty-tip';
        empty.textContent = '没有匹配的仓库 —— 换个关键词试试';
        empty.style.cssText = 'padding:16px;text-align:center;color:#654322';
        cardsBox.appendChild(empty);
      }}
    }} else if (empty) {{ empty.remove(); }}
  }});

  /* 2. 左栏仓库：点击定位卡片；⌘/Ctrl/Shift+点击 直接开仓库 */
  $$('#repo-list .repo').forEach(function(a){{
    a.addEventListener('click', function(e){{
      if (e.metaKey || e.ctrlKey || e.shiftKey) return;
      var name = a.dataset.repo;
      var card = $('.card[data-repo="' + name + '"]');
      if (!card) return;
      e.preventDefault();
      $$('#repo-list .repo').forEach(function(x){{ x.classList.remove('on'); }});
      a.classList.add('on');
      card.classList.remove('hide');
      card.scrollIntoView({{behavior:'smooth', block:'center'}});
      card.animate([{{outline:'3px solid #ffd541'}},{{outline:'3px solid transparent'}}],
                   {{duration:1400, easing:'ease-out'}});
    }});
  }});

  /* 3. 导航高亮 + 回到顶部 */
  $$('.tab[data-nav]').forEach(function(t){{
    t.addEventListener('click', function(){{
      $$('.tab[data-nav]').forEach(function(x){{ x.classList.remove('on'); }});
      t.classList.add('on');
      if (t.getAttribute('href') === '#top') window.scrollTo({{top:0, behavior:'smooth'}});
    }});
  }});

  /* 4. 贡献徽章 → 滚动到贡献图 */
  var bc = $('#btn-contrib');
  if (bc) bc.addEventListener('click', function(){{
    var b = $('#contrib-block');
    b.scrollIntoView({{behavior:'smooth', block:'center'}});
    b.animate([{{filter:'brightness(1.7)'}},{{filter:'brightness(1)'}}], {{duration:900}});
  }});

  /* 5. 主题切换（记住选择） */
  var tb = $('#btn-theme');
  function applyTheme(t){{ document.body.classList.toggle('night', t === 'night'); }}
  try {{ applyTheme(localStorage.getItem('sv-theme') || 'day'); }} catch(e) {{}}
  tb.addEventListener('click', function(){{
    var next = document.body.classList.contains('night') ? 'day' : 'night';
    applyTheme(next);
    try {{ localStorage.setItem('sv-theme', next); }} catch(e) {{}}
  }});

  /* 6. 点卡片空白处 → 打开对应仓库（内部链接/details 不拦截） */
  $$('.card').forEach(function(c){{
    c.addEventListener('click', function(e){{
      if (e.target.closest('a, details, summary, button')) return;
      window.open(GH + '/' + c.dataset.repo, '_blank', 'noopener');
    }});
  }});

  /* 7. Esc 清空搜索 */
  document.addEventListener('keydown', function(e){{
    if (e.key === 'Escape' && document.activeElement === q) {{
      q.value = ''; q.dispatchEvent(new Event('input'));
    }}
  }});
}})();
</script>
</body>
</html>'''


def build():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)
    html = page()
    open(os.path.join(DIST, 'index.html'), 'w').write(html)
    open(os.path.join(DIST, '.nojekyll'), 'w').write('')
    print('dist/index.html', len(html))
    return DIST


if __name__ == '__main__':
    build()
