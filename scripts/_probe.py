"""测试各 GraphQL 查询在 Actions 环境下的可行性（定位 4828:F225C 错误源）"""
import json, subprocess, sys

TOK = sys.argv[1] if len(sys.argv) > 1 else open('/Users/xlyang/.config/doucang-github/token').read().strip()

QUERIES = {
    'viewer': "query{viewer{login}}",
    'name_bio': "query{viewer{name bio}}",
    'followers': "query{viewer{followers{totalCount}}}",
    'contrib_window': 'query{viewer{contributionsCollection(from:"2025-11-01T00:00:00Z", to:"2026-10-31T23:59:59Z"){contributionCalendar{totalContributions}}}}',
    'contrib_default': "query{viewer{contributionsCollection{totalCommitContributions contributionCalendar{totalContributions}}}}",
    'repos': "query{viewer{repositories(first:100, ownerAffiliations:OWNER, privacy:PUBLIC, orderBy:{field:UPDATED_AT, direction:DESC}){totalCount}}}",
}


def run(q):
    open('/tmp/_qq.json', 'w').write(json.dumps({'query': q}))
    r = subprocess.run(['curl', '-s', '-m', '30', '-H', f'Authorization: Bearer {TOK}',
                        '-H', 'Content-Type: application/json', '-X', 'POST', '-d', '@/tmp/_qq.json',
                        'https://api.github.com/graphql'], capture_output=True, text=True)
    return r.stdout[:300]


for k, q in QUERIES.items():
    print(f'--- {k}')
    print(run(q))
