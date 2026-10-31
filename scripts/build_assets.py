"""一次抓取全部素材：项目截图 → assets/shot-*.png
Actions 与本地通用（用 GITHUB_TOKEN / 本机 token）。"""
import json, os, subprocess, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(os.path.dirname(HERE), 'assets')
TOKEN = os.environ.get('GH_TOKEN') or open(os.path.expanduser('~/.config/doucang-github/token')).read().strip()
USER = 'Xlyang18'
FEATURED = {
    'doucang': 'docs/screenshots/01-home.png',
    'lightbox': 'screenshots/01-启动主界面.png',
    'teamtally': 'docs/screenshots/01-数据看板.png',
}


def fetch(repo, path):
    q = '/'.join(urllib.parse.quote(seg) for seg in path.split('/'))
    data = subprocess.run(['curl', '-sL', '-m', '90',
                           '-H', f'Authorization: Bearer {TOKEN}',
                           '-H', 'Accept: application/vnd.github.raw',
                           f'https://api.github.com/repos/{USER}/{repo}/contents/{q}'],
                          capture_output=True).stdout
    if len(data) < 5000:
        data = subprocess.run(['curl', '-sL', '-m', '90',
                               f'https://raw.githubusercontent.com/{USER}/{repo}/main/{q}'],
                              capture_output=True).stdout
    return data if len(data) > 5000 else None


def crop(data, dst, size=(300, 200)):
    from PIL import Image
    im = Image.open(__import__('io').BytesIO(data)).convert('RGB')
    w, h = im.size
    tw, th = w, int(w * size[1] / size[0])
    if th > h:
        th, tw = h, int(h * size[0] / size[1])
    left, top = (w - tw) // 2, int((h - th) * 0.35)
    im.crop((left, top, left + tw, top + th)).resize(size, Image.LANCZOS).save(dst, optimize=True)


if __name__ == '__main__':
    ok = 0
    for repo, path in FEATURED.items():
        data = fetch(repo, path)
        if not data:
            print('shot MISS', repo)
            continue
        crop(data, os.path.join(ASSETS, f'shot-{repo}.png'))
        print('shot ok', repo, os.path.getsize(os.path.join(ASSETS, f'shot-{repo}.png')))
        ok += 1
    print(f'assets ready: {ok}/{len(FEATURED)}')
