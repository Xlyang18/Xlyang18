"""从 GitHub 实时拉数据 → data.json（供 render.py 渲染像素主页）"""
import json, os, subprocess

TOKEN = os.environ.get('GH_TOKEN') or open(os.path.expanduser('~/.config/doucang-github/token')).read().strip()
USER = 'Xlyang18'
FEATURED = ['doucang', 'lightbox', 'teamtally', 'ruanyifeng-blog-reader']


def curl(args):
    return subprocess.run(['curl', '-s', '-m', '40'] + args, capture_output=True, text=True).stdout


def graphql(query):
    open('/tmp/_q.json', 'w').write(json.dumps({'query': query}))
    out = curl(['-H', f'Authorization: Bearer {TOKEN}', '-H', 'Content-Type: application/json',
                '-X', 'POST', '-d', '@/tmp/_q.json', 'https://api.github.com/graphql'])
    d = json.loads(out, strict=False)
    if 'errors' in d:
        raise SystemExit(d['errors'])
    return d['data']


def rest(path):
    out = curl(['-H', f'Authorization: Bearer {TOKEN}', '-H', 'Accept: application/vnd.github+json',
                f'https://api.github.com{path}'])
    return json.loads(out, strict=False)


def collect():
    g = graphql("""query{
      viewer{
        name bio
        followers{totalCount} following{totalCount}
        contributionsCollection{ totalCommitContributions
          contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount color } } } }
        repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, orderBy:{field:UPDATED_AT, direction:DESC}){ totalCount }
      }
    }""")
    v = g['viewer']
    cal = v['contributionsCollection']['contributionCalendar']

    # 贡献格子：53 周 x 7 天，按周对齐（GitHub 以周日为首行，与主页一致）
    days = [d for w in cal['weeks'] for d in w['contributionDays']]
    counts = [d['contributionCount'] for d in days]
    peak = max(counts) or 1

    def lvl(c):
        if c == 0:
            return 0
        r = c / peak
        return 1 if r < .2 else 2 if r < .4 else 3 if r < .6 else 4

    weeks = []
    for w in cal['weeks']:
        col = [lvl(d['contributionCount']) for d in w['contributionDays']]
        while len(col) < 7:
            col.append(0)
        weeks.append(col)

    # 精选仓库（REST 补 release 与语言）
    repos = []
    for slug in FEATURED:
        r = rest(f'/repos/{USER}/{slug}')
        rel = rest(f'/repos/{USER}/{slug}/releases/latest')
        repos.append({
            'name': slug,
            'title': r.get('name'),
            'desc': r.get('description') or '',
            'lang': (r.get('language') or '—'),
            'stars': r.get('stargazers_count', 0),
            'forks': r.get('forks_count', 0),
            'version': rel.get('tag_name') or '—',
            'updated': (r.get('pushed_at') or '')[:10],
            'released': (rel.get('published_at') or '')[:10],
            'private': r.get('private', False),
        })

    # 最近动态：按「事件种类+仓库」去重，保留最近的几条
    ev = rest(f'/users/{USER}/events/public?per_page=60')
    acts, seen = [], set()
    for e in ev:
        t = e.get('type')
        repo = e.get('repo', {}).get('name', '').split('/')[-1]
        when = e.get('created_at', '')[:10]
        key = (t, repo)
        if t == 'ReleaseEvent':
            tag = (e.get('payload') or {}).get('release', {}).get('tag_name', '')
            key = (t, repo, tag)
            text = f'Released {tag} in {repo}'
        elif t == 'PushEvent':
            if key in seen:
                continue
            text = f'Pushed to {repo}'
        elif t == 'WatchEvent':
            key = (t, repo, when)
            text = f'Starred {repo}'
        else:
            continue
        if key in seen:
            continue
        seen.add(key)
        acts.append({'icon': t.replace('Event', '').lower(), 'text': text, 'date': when})
        if len(acts) >= 4:
            break

    return {
        'user': USER,
        'name': v.get('name') or USER,
        'bio': v.get('bio') or '',
        'followers': v['followers']['totalCount'],
        'following': v['following']['totalCount'],
        'repos_total': v['repositories']['totalCount'],
        'contributions_total': cal['totalContributions'],
        'commits_total': v['contributionsCollection']['totalCommitContributions'],
        'weeks': weeks,
        'last_day': days[-1] if days else None,
        'span': [days[0]['date'], days[-1]['date']] if days else None,
        'repos': repos,
        'activity': acts,
        'avatar_color': '#2b2118',
    }


if __name__ == '__main__':
    data = collect()
    out = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'assets', 'data.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump(data, open(out, 'w'), ensure_ascii=False, indent=1)
    print('data.json written:', out)
    print('contributions', data['contributions_total'], 'repos', data['repos_total'], 'weeks', len(data['weeks']))
