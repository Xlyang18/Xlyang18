"""从 GitHub 实时拉数据 → data.json（供 render.py 渲染像素主页）
Actions 里用 REST（GITHUB_TOKEN 只读公开数据即可）；本机可用 GraphQL 拿精确贡献日历。
"""
import json, os, subprocess
from datetime import datetime, timedelta, timezone

TOKEN = os.environ.get('GH_TOKEN') or open(os.path.expanduser('~/.config/doucang-github/token')).read().strip()
USER = 'Xlyang18'
FEATURED = ['doucang', 'lightbox', 'teamtally', 'ruanyifeng-blog-reader']


def curl(args):
    return subprocess.run(['curl', '-s', '-m', '40'] + args, capture_output=True, text=True).stdout


def rest(path):
    out = curl(['-H', f'Authorization: Bearer {TOKEN}', '-H', 'Accept: application/vnd.github+json',
                f'https://api.github.com{path}'])
    try:
        return json.loads(out, strict=False)
    except Exception:
        return {}


def graphql(query):
    open('/tmp/_q.json', 'w').write(json.dumps({'query': query}))
    print('[graphql] token prefix:', TOKEN[:6], 'len', len(TOKEN))
    out = curl(['-H', f'Authorization: Bearer {TOKEN}', '-H', 'Content-Type: application/json',
                '-X', 'POST', '-d', '@/tmp/_q.json', 'https://api.github.com/graphql'])
    try:
        d = json.loads(out, strict=False)
    except Exception:
        print('[graphql] non-json response:', out[:200])
        return None
    if 'errors' in d or 'data' not in d:
        print('[graphql] error ->', str(d.get('errors'))[:200])
        return None
    return d['data']


def contribution_calendar():
    """优先 GraphQL（精确）；失败/无权限时用 REST 事件流估算"""
    for q in (
        'query{user(login:"%s"){contributionsCollection{totalCommitContributions '
        'contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}' % USER,
    ):
        d = graphql(q)
        if d and d.get('user'):
            cc = d['user']['contributionsCollection']
            cal = cc['contributionCalendar']
            days_all = [x for w in cal['weeks'] for x in w['contributionDays']]
            span = [days_all[0]['date'], days_all[-1]['date']] if days_all else None
            return [[x['contributionCount'] for x in w['contributionDays']] for w in cal['weeks']], \
                   cal['totalContributions'], cc['totalCommitContributions'], 'graphql', span

    # REST 兜底：用 events 估算（只覆盖最近 90 天，其余置 0）
    ev = rest(f'/users/{USER}/events/public?per_page=100')
    days = {}
    for e in ev if isinstance(ev, list) else []:
        d = e.get('created_at', '')[:10]
        if not d:
            continue
        n = 1
        if e.get('type') == 'PushEvent':
            n = (e.get('payload') or {}).get('size') or len((e.get('payload') or {}).get('commits') or []) or 1
        days[d] = days.get(d, 0) + n
    today = datetime.now(timezone.utc).date()
    start = today - timedelta(days=370)
    start -= timedelta(days=(start.weekday() + 1) % 7)   # 对齐到周日
    weeks, total = [], 0
    cur = start
    while cur <= today:
        col = []
        for _ in range(7):
            col.append(days.get(cur.isoformat(), 0))
            total += col[-1]
            cur += timedelta(days=1)
        weeks.append(col)
    d0 = (start)
    d1 = today
    return weeks, total, total, 'events(估算)', [d0.isoformat(), d1.isoformat()]


def collect():
    # ---- 用户基础信息（REST 不需要 GraphQL，Actions 里也稳定） ----
    u = rest(f'/users/{USER}')
    repos_all = rest(f'/users/{USER}/repos?per_page=100&sort=updated')
    if not isinstance(repos_all, list):
        repos_all = []
    public_repos = [r for r in repos_all if not r.get('private')]

    weeks_raw, total, commits, source, span = contribution_calendar()
    counts = [c for col in weeks_raw for c in col]
    peak = max(counts) or 1

    def lvl(c):
        if c == 0:
            return 0
        r = c / peak
        return 1 if r < .2 else 2 if r < .4 else 3 if r < .6 else 4

    weeks = [[lvl(c) for c in (col + [0] * (7 - len(col)))[:7]] for col in weeks_raw]

    # ---- 精选仓库 ----
    repos = []
    me = rest('/user')
    for r0 in public_repos[:8]:
        rel = rest(f"/repos/{USER}/{r0['name']}/releases/latest")
        r0['_version'] = rel.get('tag_name') or '—'
    # 按「有 release + 最近更新」排序挑 4 个
    cand = sorted(public_repos, key=lambda x: ((x.get('pushed_at') or '')), reverse=True)
    cand = [r0 for r0 in cand if r0['name'].lower() not in (USER.lower(), 'github-api-publish-guide')]
    # 收录口径：有 release / 有话题标签 / 体积 > 100KB（排除垃圾练习仓）
    # teamtally 是私有仓库：REST /users/{u}/repos 不返回，单独补进来
    tt = rest(f'/repos/{USER}/teamtally')
    if tt.get('name'):
        tt['_version'] = (rest(f'/repos/{USER}/teamtally/releases/latest').get('tag_name') or '—')
        cand.insert(0, tt)
    with_rel = [r0 for r0 in cand if r0.get('_version', '—') != '—']
    order = {'doucang': 0, 'lightbox': 1, 'teamtally': 2, 'ruanyifeng-blog-reader': 3}
    picks = sorted(cand, key=lambda r0: order.get(r0['name'].lower(), 99))
    picks = picks[:4]
    for r0 in picks:
        slug = r0['name']
        r = rest(f'/repos/{USER}/{slug}')
        rel = rest(f'/repos/{USER}/{slug}/releases/latest')
        if not r.get('name'):
            continue
        repos.append({
            'name': r['name'],
            'desc': r.get('description') or '',
            'lang': r.get('language') or '—',
            'stars': r.get('stargazers_count', 0),
            'version': rel.get('tag_name') or '—',
            'updated': (r.get('pushed_at') or '')[:10],
            'private': r.get('private', False),
        })

    # ---- 每个仓库的 README 摘要 + 最近提交 ----
    import base64 as _b64
    for repo in repos:
        slug = repo['name']
        rd = rest(f'/repos/{USER}/{slug}/readme')
        text = ''
        if rd.get('content'):
            try:
                raw = _b64.b64decode(rd['content']).decode('utf-8', 'ignore')
                lines = [l.strip() for l in raw.split('\n')]
                keep = []
                in_code = False
                for l in lines:
                    if l.startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code or not l:
                        continue
                    if l.startswith(('#', '!', '[', '<', '|', '---', '>', '-!', '<!--')):
                        continue
                    l = l.replace('**', '').replace('`', '').strip()
                    if len(l) > 8:
                        keep.append(l)
                    if len(' '.join(keep)) > 240:
                        break
                text = ' '.join(keep)[:240]
            except Exception:
                text = ''
        repo['readme'] = text
        cm = rest(f'/repos/{USER}/{slug}/commits?per_page=4')
        repo['commits'] = [{'msg': (c['commit']['message'].split('\n')[0])[:70],
                            'date': (c['commit']['author']['date'] or '')[:10],
                            'sha': c['sha'][:7]} for c in (cm if isinstance(cm, list) else [])]

    # ---- 最近动态（去重） ----
    ev = rest(f'/users/{USER}/events/public?per_page=60')
    acts, seen = [], set()
    for e in ev if isinstance(ev, list) else []:
        t = e.get('type')
        repo = e.get('repo', {}).get('name', '').split('/')[-1]
        when = e.get('created_at', '')[:10]
        if t == 'ReleaseEvent':
            tag = (e.get('payload') or {}).get('release', {}).get('tag_name', '')
            key, text = (t, repo, tag), f'Released {tag} in {repo}'
        elif t == 'PushEvent':
            key, text = (t, repo), f'Pushed to {repo}'
        elif t == 'WatchEvent':
            key, text = (t, repo, when), f'Starred {repo}'
        else:
            continue
        if key in seen:
            continue
        seen.add(key)
        acts.append({'text': text, 'date': when})
        if len(acts) >= 4:
            break

    # ---- 贴纸配色：按语言分组统计（给左栏 Trails 用） ----
    langs = {}
    for r0 in public_repos:
        if r0['name'].lower() == USER.lower():
            continue
        k = r0.get('language') or '文档/其他'
        langs[k] = langs.get(k, 0) + 1
    lang_rows = sorted(langs.items(), key=lambda kv: -kv[1])[:3]

    SIGN = '科技爱好者。想法在脑子里是草图，npm run build 之后就得能跑。'
    return {
        'tagline': SIGN,
        'langs': [{'name': k, 'count': v} for k, v in lang_rows],
        'user': USER,
        'name': u.get('name') or USER,
        'bio': u.get('bio') or '',
        'followers': u.get('followers', 0),
        'following': u.get('following', 0),
        'repos_total': u.get('public_repos', len(public_repos)),
        'contributions_total': total,
        'commits_total': commits,
        'calendar_source': source,
        'weeks': weeks,
        'span': span,
        'repos': repos,
        'activity': acts,
        'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),
    }


if __name__ == '__main__':
    data = collect()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'data.json')
    json.dump(data, open(out, 'w'), ensure_ascii=False, indent=1)
    print('data.json:', data['contributions_total'], 'contributions /', data['repos_total'], 'repos /',
          len(data['weeks']), 'weeks /', data['calendar_source'])
