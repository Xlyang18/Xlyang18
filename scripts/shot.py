"""用 webkit2png 之类的思路行不通 —— 这里用 SVG foreignObject 直接抓 HTML（Chrome 原生），
再由 PIL 栅格化。失败则退回 PIL 绘制。
用法: python3 shot.py <html> <out.png> [宽] [高]
"""
import base64, os, subprocess, sys, tempfile

CANDIDATES = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
]


def find_chrome():
    for c in CANDIDATES:
        if os.path.exists(c):
            return c
    return None


def shot(html_path, out_path, width, height, scale=2):
    chrome = find_chrome()
    if not chrome:
        raise SystemExit('no chrome')
    prof = tempfile.mkdtemp()
    cmd = [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--no-first-run', '--no-default-browser-check', '--disable-extensions',
           f'--user-data-dir={prof}',
           f'--window-size={width},{height}',
           f'--force-device-scale-factor={scale}',
           f'--screenshot={out_path}',
           '--virtual-time-budget=6000',
           '--default-background-color=00000000',
           f'file://{html_path}']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    _ = r
    if not os.path.exists(out_path):
        print(r.stderr[-2000:])
        raise SystemExit('screenshot failed')
    return out_path


if __name__ == '__main__':
    h = sys.argv[1]
    o = sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1012
    hh = int(sys.argv[4]) if len(sys.argv) > 4 else 852
    print(shot(h, o, w, hh))
    from PIL import Image
    print(Image.open(o).size)
