"""置顶仓库：走 GitHub 网页端接口（GraphQL 无公开 mutation）
用法:
  python3 pinned.py                 # 列表
  python3 pinned.py add doucang lightbox teamtally   # 覆盖式设置
"""
import json, os, re, subprocess, sys

TOKEN = os.environ('GH_TOKEN') if False else (os.environ.get('GH_TOKEN') or open(os.path.expanduser('~/.config/doucang-github/token')).read().strip())
UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36'
API = 'https://api.github.com/graphql'


def curl(args):
    return subprocess.run(['curl', '-s', '-m', '40'] + args, capture_output=True, text=True).stdout


def gql(q, variables=None):
    payload = {'query': q}
    if variables:
        payload['variables'] = variables
    open('/tmp/_pin.json', 'w').write(json.dumps(payload))
    out = curl(['-H', f'Authorization: Bearer {TOKEN}', '-H', 'Content-Type: application/json',
                '-X', 'POST', '-d', '@/tmp/_pin.json', API])
    return json.loads(out, strict=False)


def state():
    d = gql('query{viewer{itemShowcase{items(first:10){nodes{__typename ... on Repository{name}}}}'
            ' repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC){nodes{name id}}}}')
    v = d['data']['viewer']
    ids = {n['name']: n['id'] for n in v['repositories']['nodes']}
    pinned = [n['name'] for n in v['itemShowcase']['items']['nodes'] if n.get('name')]
    return ids, pinned


def web_token(cookies=''):
    """GitHub 网页端 GraphQL 需要同会话 csrf+authenticity，这里只能取到 anonym 版本 → 用 REST 更新 profile 的 pinned 不可行。
    实际可行路径：用 PAT 调用网页 GraphQL（需要登录态 token，PAT 不被接受）。
    因此这里改用「prettifyItem」类接口的网页版：直接改 README 里的 pinned，让用户在网页手动确认。
    """
    return None


if __name__ == '__main__':
    ids, pinned = state()
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'list'
    if cmd == 'list':
        print('pinned:', pinned)
    else:
        want = sys.argv[2:]
        print('当前置顶:', pinned)
        print('目标置顶:', want)
        print('\n⚠️ GitHub 未开放通过 API 修改 Pinned（GraphQL 无 pinItem mutation）。')
        print('   请在 https://github.com/Xlyang18 页面上点 "Customize your pins" 手动勾选：')
        for name in want:
            print('   -', name)
