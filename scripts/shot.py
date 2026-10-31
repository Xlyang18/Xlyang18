"""HTML → PNG 截图。跨平台：
   mac   : 本地 Chrome/Chromium/Edge headless
   linux : npx playwright（Actions 里装 chromium，不依赖 apt）
用法: python3 shot.py <html> <out.png> [宽] [高] [scale]
"""
import os, shutil, subprocess, sys, tempfile

MAC = [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/Applications/Chromium.app/Contents/MacOS/Chromium',
    '/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
]


def find_chrome():
    for c in MAC:
        if os.path.exists(c):
            return c
    for name in ('google-chrome', 'chromium', 'chromium-browser'):
        p = shutil.which(name)
        if p:
            return p
    return None


def shot_chrome(chrome, html_path, out_path, width, height, scale):
    prof = tempfile.mkdtemp()
    cmd = [chrome, '--headless=new', '--disable-gpu', '--hide-scrollbars',
           '--no-sandbox', '--disable-dev-shm-usage',
           '--no-first-run', '--no-default-browser-check', '--disable-extensions',
           f'--user-data-dir={prof}',
           f'--window-size={width},{height}',
           f'--force-device-scale-factor={scale}',
           f'--screenshot={out_path}',
           '--virtual-time-budget=8000',
           f'file://{html_path}']
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
    if not os.path.exists(out_path):
        print(r.stderr[-1500:])
        raise SystemExit('chrome screenshot failed')
    return out_path


def shot_playwright(html_path, out_path, width, height, scale):
    js = f'''
const {{ chromium }} = require('playwright');
(async () => {{
  const browser = await chromium.launch();
  const page = await browser.newPage({{ viewport: {{ width: {width}, height: {height} }}, deviceScaleFactor: {scale} }});
  await page.goto('file://{html_path}', {{ waitUntil: 'networkidle' }});
  await page.waitForTimeout(1200);
  await page.screenshot({{ path: '{out_path}' }});
  await browser.close();
}})();
'''
    p = '/tmp/_shot.js'
    open(p, 'w').write(js)
    r = subprocess.run(['node', p], capture_output=True, text=True, timeout=300)
    if not os.path.exists(out_path):
        print(r.stdout[-1000:], r.stderr[-1500:])
        raise SystemExit('playwright screenshot failed')
    return out_path


def shot(html_path, out_path, width, height, scale=2):
    chrome = find_chrome()
    if chrome:
        return shot_chrome(chrome, html_path, out_path, width, height, scale)
    return shot_playwright(html_path, out_path, width, height, scale)


if __name__ == '__main__':
    h, o = sys.argv[1], sys.argv[2]
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 1012
    hh = int(sys.argv[4]) if len(sys.argv) > 4 else 852
    s = float(sys.argv[5]) if len(sys.argv) > 5 else 2
    print(shot(h, o, w, hh, s))
    from PIL import Image
    print('size', Image.open(o).size)
