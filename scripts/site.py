"""生成可交互像素前端站点（GitHub Pages）→ dist/
- 纯静态 HTML/CSS/JS，无框架、无外部依赖
- 素材全部内联（星露谷原生贴图 + 原版字体），单页可直接打开
- 数据来自 assets/data.json（Actions 每日刷新）
"""
import base64, json, os, shutil
import svrt as SV
import letter as LT

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')
DIST = os.path.join(ROOT, 'dist')
D = json.load(open(os.path.join(ASSETS, 'data.json')))

W = 1200


def b64(path):
    p = os.path.join(ASSETS, path)
    if not os.path.exists(p):
        return ''
    return base64.b64encode(open(p, 'rb').read()).decode()


FONT_PX = b64('fonts/fusion-pixel-8px-proportional-zh_hans.ttf.woff2')
FONT_SV = b64('fonts/Stardew_Valley.ttf')
SHOTS = {'doucang': 'shot-doucang.png', 'lightbox': 'shot-lightbox.png', 'teamtally': 'shot-teamtally.png'}
REPO_ICON = {'doucang': 'coffee', 'lightbox': 'strawberry', 'teamtally': 'corn',
             'ruanyifeng-blog-reader': 'tomato', 'github-api-publish-guide': 'chest'}

NAV = [('Overview', 'inventory'), ('Repositories', 'crafting'), ('Projects', 'collections'),
       ('Pull requests', 'social'), ('Issues', 'animals'), ('Marketplace', 'map'), ('Settings', 'options')]


def cur(name):
    return REPO_ICON.get(name, 'strawberry')


def esc(s):
    return (s or '').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def esc_js(s):
    return json.dumps(s or '', ensure_ascii=False)


def scene_svg():
    """顶栏农场画面（复用 scene_sv 的构图，宽度自适应）"""
    import scene_sv
    return scene_sv.scene_svg()


def nav_html():
    tabs = ''.join(
        f'<button class="tab{" on" if i == 0 else ""}" data-nav="{n.lower()}">'
        f'<img class="tabico" src="{SV.tab(k, 30)}" alt=""><span>{n}</span></button>'
        for i, (n, k) in enumerate(NAV))
    tabs += (f'<button class="tab gold"><img class="tabico" src="{SV.icon("stardrop", 28)}" alt="">'
             f'<span id="contrib-count">{D["contributions_total"]}</span></button>')
    tabs += f'<button class="tab small" id="btn-theme" title="切换主题"><img class="tabico" src="{SV.tab("options", 28)}" alt=""></button>'
    tabs += f'<a class="tab small" href="https://github.com/Xlyang18" title="GitHub"><img class="tabico" src="{SV.tab("exit", 28)}" alt=""></a>'
    return f'<nav class="nav">{tabs}</nav>'


def repo_rows():
    out = ''
    for i, r in enumerate(D['repos']):
        out += (f'<button class="repo{" on" if i == 0 else ""}" data-repo="{esc(r["name"])}">'
                f'<img class="repoico" src="{SV.icon(cur(r["name"]), 20)}" alt="">'
                f'<span>{esc(r["name"])}</span>'
                f'<img class="starico" src="{SV.icon("stardrop", 18)}" alt=""></button>')
    return out


def cards():
    out = ''
    for r in D['repos']:
        name = r['name']
        shot = SHOTS.get(name)
        thumb = (f'<div class="thumb" style="background-image:url(data:image/png;base64,{b64(shot)})"></div>'
                 if shot else f'<div class="thumb none"><img src="{SV.icon(cur(name), 32)}" alt=""></div>')
        commits = ''.join(
            f'<li><code>{esc(c["sha"])}</code><span>{esc(c["msg"])}</span><i>{c["date"][5:]}</i></li>'
            for c in r.get('commits', [])[:4])
        out += f'''<article class="card" data-repo="{esc(name)}">
  {thumb}
  <div class="card-main">
    <header>
      <img class="cico" src="{SV.icon(cur(name), 22)}" alt="">
      <h3>{esc(name)}</h3>
      <span class="badge">{esc(r["lang"])}</span>
      <span class="ver">{esc(r["version"])}</span>
    </header>
    <p class="summary">{esc(r["readme"][:120] or r["desc"])}</p>
    <details class="more">
      <summary>展开 README 摘要 · 最近提交</summary>
      <p class="readme-full">{esc(r["readme"] or r["desc"])}</p>
      <ul class="commits">{commits}</ul>
    </details>
    <footer>
      <span>★ {r["stars"]}</span><span>更新 {esc(r["updated"])}</span>
      <a href="https://github.com/Xlyang18/{esc(name)}" target="_blank" rel="noopener">查看仓库 →</a>
    </footer>
  </div>
</article>'''
    return out


def graph():
    cells = ''
    for col in D['weeks']:
        cells += '<div class="w">' + ''.join(f'<i class="lv{lv}"></i>' for lv in col) + '</div>'
    return cells


def page():
    tag = D.get('tagline', '科技爱好者。想法在脑子里是草图，npm run build 之后就得能跑。')
    tag_html = esc(tag).replace('npm run build', '<code class="cmdtxt">npm run build</code>')
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
  --ink:#3b2410;--ink2:#7a5730;--green:#3f8f42;--green-d:#2a6b2e;
  --gold:#ffd541;--grass:#6cbb3c;--sky:#7fcbf0;
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:var(--grass);color:var(--ink);font-family:SVf,Px,monospace;font-size:14px;line-height:21px;
  -webkit-font-smoothing:none;font-smooth:never;overflow-x:hidden}}
img{{image-rendering:pixelated;display:block}}
a{{color:inherit;text-decoration:none}}
.wrap{{max-width:{W}px;margin:0 auto;background:var(--grass);min-height:100vh;position:relative}}
.scene{{overflow:hidden}}
.scene svg{{display:block;width:100%;height:200px;object-fit:cover}}
.nav{{display:flex;flex-wrap:wrap;align-items:center;gap:6px;padding:8px 14px;background:var(--panel-lo);
  border-top:3px solid var(--wood-ll);border-bottom:3px solid var(--wood-d)}}
.tab{{display:flex;align-items:center;gap:5px;height:34px;padding:0 11px 0 5px;background:var(--wood-l);
  border:2px solid var(--wood-d);box-shadow:inset 0 2px 0 var(--wood-ll),inset 0 -3px 0 var(--wood-d);
  cursor:pointer;color:var(--ink);font:inherit;white-space:nowrap;transition:transform .06s}}
.tab:hover{{transform:translateY(-1px);filter:brightness(1.06)}}
.tab:active{{transform:translateY(1px)}}
.tab.on{{background:var(--gold)}}
.tab.gold{{background:var(--gold);margin-left:auto}}
.tab.small{{padding:0 6px}}
.tabico{{width:28px;height:28px}}
.crumbs{{display:flex;align-items:center;gap:7px;height:34px;padding:0 16px;background:var(--panel-hi);
  border-bottom:3px solid var(--wood-d);color:var(--ink2)}}
.crumbs b{{font-weight:normal;color:var(--wood-d)}}
.cols{{display:grid;grid-template-columns:250px 1fr 300px;gap:10px;padding:10px 16px 16px;align-items:start}}
.panel{{background:var(--panel);border:3px solid var(--wood-d);padding:11px;
  box-shadow:inset 0 3px 0 var(--panel-hi),inset 0 -3px 0 var(--panel-lo),4px 4px 0 rgba(59,36,16,.3)}}
.ph{{display:flex;align-items:center;gap:6px;margin-bottom:7px}}
.ico{{width:20px;height:20px}}
.side .panel{{margin-bottom:10px}}
.repo{{display:flex;align-items:center;gap:7px;width:100%;height:32px;padding:0 7px;margin-bottom:4px;
  background:var(--panel-hi);border:2px solid var(--wood);box-shadow:inset 0 -2px 0 var(--panel-lo);
  cursor:pointer;font:inherit;color:var(--ink);text-align:left;transition:transform .06s}}
.repo:hover{{background:#ffeebf}}
.repo.on{{background:#ffe9a8;border-color:var(--wood-d);box-shadow:inset 4px 0 0 var(--green),inset 0 -2px 0 #e8c983}}
.repo span{{flex:1;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}}
.repoico{{width:20px;height:20px;flex:none}}
.starico{{width:18px;height:18px;flex:none}}
.tagline{{font-size:15px;line-height:21px;color:var(--wood-d);background:rgba(255,255,255,.5);
  border-left:5px solid var(--green);padding:4px 9px;margin:3px 0 6px}}
.cmdtxt{{font-family:Px,monospace;background:var(--wood-d);color:#ffe9a8;padding:0 4px;font-size:12px;border-radius:2px}}
h1{{font-size:26px;line-height:30px;font-weight:normal;display:flex;align-items:center;gap:9px}}
.badge{{font-size:11px;background:var(--green);color:#fff;border:2px solid var(--green-d);padding:1px 6px}}
.sub{{color:var(--ink2);font-size:13px}}
.metabar{{display:flex;flex-wrap:wrap;gap:10px;align-items:center;color:var(--ink2);
  border-bottom:2px solid var(--panel-lo);padding:6px 0;margin:6px 0}}
.letter{{border:2px solid var(--wood-d);background-color:#ffe2af;
  box-shadow:inset 0 0 0 2px #f3c98a;padding:9px 11px 10px;margin-bottom:10px;color:#5a3a1a;
  font-size:12.5px;line-height:19px}}
.letter h4{{font-family:SVf,Px,monospace;font-size:13px;color:#8a5a2f;font-weight:normal;
  border-bottom:1px dashed #c9a26a;padding-bottom:4px;margin-bottom:6px;letter-spacing:.4px}}
.letter p{{margin:0 0 4px}}
.cards{{display:grid;gap:9px}}
.card{{display:grid;grid-template-columns:132px 1fr;gap:10px;background:var(--panel-hi);
  border:2px solid var(--wood);box-shadow:inset 0 -2px 0 var(--panel-lo);padding:8px;transition:transform .07s}}
.card:hover{{transform:translateY(-2px);box-shadow:inset 0 -2px 0 var(--panel-lo),3px 4px 0 rgba(59,36,16,.25)}}
.card.hide{{display:none}}
.thumb{{width:132px;height:92px;background-size:cover;background-position:top center;border:2px solid var(--wood-d)}}
.thumb.none{{display:grid;place-items:center;background:linear-gradient(var(--wood-l),var(--wood))}}
.thumb.none img{{width:32px;height:32px}}
.card-main header{{display:flex;align-items:center;gap:7px;flex-wrap:wrap}}
.cico{{width:22px;height:22px}}
h3{{font-size:16px;font-weight:normal}}
.ver{{font-size:12px;color:var(--wood-d)}}
.summary{{color:var(--ink);font-size:12.5px;line-height:18px;margin:4px 0 5px}}
.more summary{{cursor:pointer;color:var(--wood-d);font-size:12px;list-style:none}}
.more summary::-webkit-details-marker{{display:none}}
.more summary::before{{content:'▸ ';color:var(--green)}}
.more[open] summary::before{{content:'▾ '}}
.readme-full{{font-size:12px;line-height:18px;color:var(--ink2);margin:5px 0;padding-left:10px;
  border-left:3px solid var(--panel-lo)}}
.commits{{list-style:none;font-size:12px;line-height:19px;color:var(--ink2)}}
.commits li{{display:flex;gap:7px}}
.commits code{{background:var(--wood-d);color:#ffe9a8;padding:0 4px;font-family:Px,monospace;font-size:11px;flex:none}}
.commits span{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.commits i{{font-style:normal;flex:none;color:var(--wood)}}
.card footer{{display:flex;gap:12px;font-size:12px;color:var(--ink2);margin-top:5px;
  border-top:1px dashed var(--panel-lo);padding-top:4px}}
.card footer a{{margin-left:auto;color:var(--green-d);border-bottom:2px solid var(--gold)}}
.acts li{{display:flex;gap:7px;font-size:12.5px;line-height:22px;border-bottom:2px dotted var(--panel-lo);list-style:none}}
.acts li span{{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
.acts li i{{font-style:normal;color:var(--ink2);flex:none}}
.graph{{display:grid;grid-template-columns:repeat(53,1fr);gap:2px}}
.graph .w{{display:grid;grid-template-rows:repeat(7,1fr);gap:2px}}
.graph i{{aspect-ratio:1;background:#e8e0c8}}
.graph .lv1{{background:#c6e6a0}} .graph .lv2{{background:#7fd050}}
.graph .lv3{{background:#2f9c2f}} .graph .lv4{{background:#17632a}}
.gfoot{{display:flex;justify-content:space-between;font-size:11px;color:var(--ink2);margin-top:5px}}
.petgrid{{display:flex;flex-wrap:wrap;gap:6px}}
.petgrid img{{width:26px;height:26px}}
.profile{{display:flex;gap:9px;align-items:flex-start}}
.avaframe{{position:relative;width:64px;height:64px;flex:none;border:3px solid var(--wood-d);
  background:var(--ink);box-shadow:inset 0 0 0 3px var(--gold)}}
.avaframe img.ava{{position:absolute;inset:3px;width:52px;height:52px;object-fit:cover}}
.pintag{{position:absolute;right:-9px;bottom:-8px;width:20px;height:20px}}
.lines{{margin-top:7px;font-size:13px;line-height:23px}}
.banner{{margin-top:8px;height:54px;display:flex;align-items:center;justify-content:center;gap:8px;
  background:linear-gradient(var(--wood-l),var(--wood));border:3px solid var(--wood-d);
  box-shadow:inset 0 3px 0 var(--wood-ll),inset 0 -3px 0 var(--wood-d);color:var(--panel-hi);
  font-size:12.5px;line-height:17px;text-align:center}}
.footer{{display:flex;align-items:center;gap:8px;padding:9px 16px;background:var(--panel-hi);
  border-top:3px solid var(--wood-d);color:var(--ink2);font-size:12.5px}}
.footer b{{font-weight:normal;color:var(--wood-d);border-bottom:3px solid #f0a020;padding-bottom:2px}}
.search{{width:100%;height:28px;padding:0 8px;background:var(--panel-hi);border:2px solid var(--wood);
  box-shadow:inset 2px 2px 0 var(--panel-lo);color:var(--ink);font:inherit;font-size:13px}}
/* 夜间主题 */
body.night{{--panel:#2f2a3d;--panel-hi:#3d3550;--panel-lo:#241f31;--ink:#f0e2c0;--ink2:#c9b795;
  --grass:#22301f;--gold:#ffd541}}
body.night .letter,body.night .letter p,body.night .letter h4{{color:#ede3c8 !important}}
body.night .letter{{background-color:#3a3350;box-shadow:inset 0 0 0 2px #55496f}}
body.night .summary{{color:#ede3c8}}
body.night .readme-full,body.night .commits{{color:#c9b795}}
body.night .letter h4{{color:#c9b795;border-color:#55496f}}
body.night .repo,body.night .card,body.night .search{{color:var(--ink)}}
body.night .readme-full{{color:#c9b795}}
body.night .tab,body.night .nav{{color:#2a1a1a}}
@media (max-width:1080px){{
  .cols{{grid-template-columns:1fr}}
  .side{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
  .tagline{{font-size:14px}}
}}
@media (max-width:640px){{
  .nav{{gap:4px;padding:6px}}
  .tab{{height:30px;padding:0 7px 0 4px;font-size:12px}}
  .tabico{{width:24px;height:24px}}
  .side{{grid-template-columns:1fr}}
  .card{{grid-template-columns:1fr}}
  .thumb{{width:100%;height:120px}}
}}
</style>
</head>
<body>
<div class="wrap">
  <div class="scene">{scene_svg()}</div>
  {nav_html()}
  <div class="crumbs"><img class="ico" src="{SV.uico('bundle', 18)}" alt=""><b>Xlyang18</b><span>/</span>README.md</div>

  <div class="cols">
    <aside class="side-left">
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('animals', 20)}" alt=""><span>Your Repositories</span></div>
        <div id="repo-list">{repo_rows()}</div>
      </div>
      <div class="panel" style="margin-top:10px">
        <div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}" alt=""><span>Contribution</span></div>
        <div class="graph">{graph()}</div>
        <div class="gfoot"><span>{D["contributions_total"]} contributions</span><span>{D["span"][0][5:]} – {D["span"][1][5:]}</span></div>
      </div>
      <div class="panel" style="margin-top:10px">
        <div class="ph"><img class="ico" src="{SV.icon('animals', 20)}" alt=""><span>Animals</span></div>
        <div class="petgrid">
          {''.join(f'<img src="{SV.animal(k, 26)}" alt="" title="{k}">' for k in ['white_chicken','brown_chicken','blue_chicken','duck','goat','pig','rabbit','horse'])}
        </div>
      </div>
    </aside>

    <main>
      <div class="panel">
        <h1>{esc(D["user"])} <span class="badge">Hi there</span></h1>
        <div class="tagline">{tag_html}</div>
        <div class="sub">{esc(D["bio"])}</div>
        <div class="metabar">
          <span>★ {D["repos_total"]} repositories</span>
          <span>◆ {D["contributions_total"]} contributions</span>
          <span>⌛ since 2021</span>
        </div>
        <div class="ph"><img class="ico" src="{SV.uico('mail', 20)}" alt=""><span>Letter</span></div>
        {LT.letter_html()}
        <div class="ph"><img class="ico" src="{SV.icon('keg', 20)}" alt=""><span>Recent repositories</span></div>
        <div class="cards" id="cards">{cards()}</div>
      </div>
    </main>

    <aside class="side">
      <div class="panel">
        <div class="profile">
          <div class="avaframe"><img class="ava" src="data:image/png;base64,{b64('avatar-pixel.png')}" alt="">
            <img class="pintag" src="{SV.icon('strawberry', 18)}" alt=""></div>
          <div><div style="font-size:19px">{esc(D["user"])}</div>
            <div class="sub" style="font-size:12px">{esc(D["bio"])}</div></div>
        </div>
        <div class="lines">
          <div>{D["followers"]} follower</div>
          <div>{D["following"]} following</div>
          <div>{D["repos_total"]} repositories</div>
        </div>
      </div>
      <div class="panel">
        <div class="ph"><img class="ico" src="{SV.icon('artisan', 20)}" alt=""><span>Activity</span></div>
        <ul class="acts">{''.join(f'<li><span>{esc(a["text"])}</span><i>{a["date"][5:]}</i></li>' for a in D["activity"])}</ul>
        <div class="banner"><img src="{SV.icon('coffee', 30)}" alt="" style="width:30px;height:30px">
          <span>Build together.<br>Grow together.</span></div>
      </div>
    </aside>
  </div>

  <div class="footer"><img class="ico" src="{SV.uico('bundle', 18)}" alt=""><span>Xlyang18</span><b>README.md</b>
    <span style="margin-left:auto">数据更新：{esc(D.get("updated_at", "")[:16])}</span></div>
</div>

<script>
(function(){{
  var tagline = {esc_js(tag)};
  // 搜索过滤
  var search = document.createElement('input');
  search.className = 'search'; search.placeholder = 'Filter repositories…';
  search.setAttribute('aria-label', '筛选仓库');
  var list = document.getElementById('repo-list');
  list.parentNode.insertBefore(search, list);
  search.addEventListener('input', function(){{
    var q = this.value.toLowerCase();
    document.querySelectorAll('.card').forEach(function(c){{
      c.classList.toggle('hide', q && c.dataset.repo.toLowerCase().indexOf(q) < 0);
    }});
    document.querySelectorAll('.repo').forEach(function(b){{
      b.style.display = (!q || b.dataset.repo.toLowerCase().indexOf(q) >= 0) ? '' : 'none';
    }});
  }});
  // 左侧选中同步滚动到对应卡片
  document.querySelectorAll('.repo').forEach(function(btn){{
    btn.addEventListener('click', function(){{
      document.querySelectorAll('.repo').forEach(function(b){{ b.classList.remove('on'); }});
      btn.classList.add('on');
      var card = document.querySelector('.card[data-repo="' + btn.dataset.repo + '"]');
      if (card) {{
        card.classList.remove('hide');
        card.scrollIntoView({{behavior:'smooth', block:'center'}});
        card.style.outline = '3px solid #ffd541';
        setTimeout(function(){{ card.style.outline = ''; }}, 1200);
      }}
    }});
  }});
  // 主题切换（浅色 / 夜间农场）
  document.getElementById('btn-theme').addEventListener('click', function(){{
    document.body.classList.toggle('night');
    try {{ localStorage.setItem('sv-theme', document.body.classList.contains('night') ? 'night' : 'day'); }} catch(e) {{}}
  }});
  try {{ if (localStorage.getItem('sv-theme') === 'night') document.body.classList.add('night'); }} catch(e) {{}}
  // 导航按钮：平滑定位
  document.querySelectorAll('.tab[data-nav]').forEach(function(t){{
    t.addEventListener('click', function(){{
      document.querySelectorAll('.tab[data-nav]').forEach(function(x){{ x.classList.remove('on'); }});
      t.classList.add('on');
      window.scrollTo({{top: 0, behavior: 'smooth'}});
    }});
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
