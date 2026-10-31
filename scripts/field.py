"""生成 README 里的 ASCII 像素草甸（原生 <pre> 渲染，不会被 GitHub 清洗）
草地 + 零星花草 + 小径，用极简字符，阅读时不抢戏。
"""
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(ROOT, 'assets')

# 7 行草甸，宽 60。. 草 . 空格  ,花  =小径  * 石头
FIELD = [
    "....,.  ....*....  ....,.  ....  ....*....  ....,.  ....  *....",
    "..  ....,...  ....  ....*...  ....  .......  ....,.  ....  ...",
    "....*....  ..  .......  ....,.  ....  ....*..  ....  ....,.  .",
    "..  ....,...  ....*...  ....  .......  ....,.  ....  ....*.  .",
    "....*....  ....  ....,.  ....*...  ....  .......  ....,.  ...*",
    "..  ....,...  ....  .......  ....,.  ....*...  ....  ....,.  .",
    "....*....  ....*...  ....  ....,.  ....  .......  ....*...  ..",
]


def build():
    inner = '\n'.join(FIELD)
    block = ('<details>\n<summary>🌿 <sub>the field</sub></summary>\n\n'
             f'<pre>{inner}</pre>\n\n</details>\n')
    readme = os.path.join(ROOT, 'README.md')
    src = open(readme).read()
    if 'the field' in src:
        start = src.index('<details>')
        end = src.index('</details>') + len('</details>\n')
        src = src[:start] + block + src[end:]
    else:
        src = src.replace('</div>\n\n<!--', '</div>\n\n' + block + '\n<!--')
    open(readme, 'w').write(src)
    print('readme updated', len(src))


if __name__ == '__main__':
    build()
