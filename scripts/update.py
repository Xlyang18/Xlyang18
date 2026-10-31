"""
一键流程：抓数据 → 渲染 HTML → 无头 Chrome 截图 → 输出 assets/hero.png
用法：
  python3 update.py            # 完整流程
  python3 update.py --push     # 完整流程并上传到 Xlyang18/Xlyang18
"""
import os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PY = sys.executable


def run(*args):
    print('>', ' '.join(str(a) for a in args))
    r = subprocess.run([PY] + list(args), cwd=HERE)
    if r.returncode:
        raise SystemExit(f'failed: {args[0]}')


def main():
    run('github_data.py')
    run('render_v4.py')
    out = os.path.join(ROOT, 'assets', 'hero.png')
    run('shot.py', os.path.join(ROOT, 'preview', 'render.html'), out, '1012', '880', '2')
    # 二分尺寸压缩（GitHub 图片建议 < 1MB）
    from PIL import Image
    im = Image.open(out)
    im = im.resize((1012, 880), Image.LANCZOS).convert('P', palette=Image.ADAPTIVE, colors=200)
    small = os.path.join(ROOT, 'assets', 'hero_next.png')
    im.convert('P').save(small, optimize=True)
    size = os.path.getsize(small)
    if size < 900_000:
        os.replace(small, out)
    else:
        os.remove(small)
    print('hero.png', os.path.getsize(out), 'bytes')

    if '--push' in sys.argv:
        run('push.py', os.path.join(ROOT, 'README.md'), out)


if __name__ == '__main__':
    main()
