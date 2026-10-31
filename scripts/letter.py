"""中栏补充区块：星露谷「信件」式自我介绍（答先生提出的当前状态：现状 / 在做什么 / 怎么做的）"""
import os
import svrt as SV

# 第一版文案（提交预览用），先生确认后再改
LETTER = dict(
    title='Letter from the Farm',
    lines=[
        '我是熊路阳，一个对前沿科技上瘾的在校大学生，看见有意思的技术就想上手试试。',
        '现在在做的事：把脑子里那些「要是能有个 App 就好了」的零碎想法，一个接一个做成真能用的软件——豆藏管咖啡豆、光匣整理照片、TeamTally 算营业额，都是从一张便签变成 .app 的。',
        '',
        '怎么做的：需求自己写清楚，和 AI 一起拆步骤、写代码、跑测试；我把关方向与取舍，它负责把想法变成能编译、能上架的东西。',
        '',
        'P.S. 下一个想做的，已经写在待办里了。',
    ],
)


def _w(s):
    """全角算 1，半角算 0.55"""
    return sum(0.55 if ord(c) < 128 else 1 for c in s)


def wrap(lines, per=26):
    """按字符数均匀折行，行尾尽量落在标点后，保证每行宽度接近"""
    out = []
    for ln in lines:
        if not ln:
            out.append('')
            continue
        rest = ln
        while _w(rest) > per:
            cut = per
            # 在 [per-6, per+2] 区间内找标点断点，找不到就硬折
            for i in range(min(len(rest) - 1, per + 2), max(0, per - 6), -1):
                if rest[i - 1] in '，。；：、）」 ':
                    cut = i
                    break
            out.append(rest[:cut])
            rest = rest[cut:].lstrip()
        if rest:
            out.append(rest)
    return out


def letter_html(width=422):
    """游戏原生信件样式：羊皮纸底 + 木框 + 像素字"""
    paper = SV.uri('Letter_paper.png', 32)
    return f'''<div class="letter" style="background-image:url({paper})">
  <div class="letter-head">{LETTER['title']}</div>
  <div class="letter-body">
    {''.join('<p>' + (l if l else '&nbsp;') + '</p>' for l in wrap(LETTER['lines']))}
  </div>
</div>'''


if __name__ == '__main__':
    print(letter_html()[:400])
