"""星露谷真实素材库（SV Real Assets）
所有贴图均为星露谷游戏内原图（来自 stardewvalleywiki.com 官方 wiki 拆包图集），未做任何二次绘制。
坐标/切法对照游戏 Content 目录结构。
"""
import base64, io, os
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SV = os.path.join(ROOT, 'assets', 'sv')

_cache = {}


def load(name):
    """name 形如 'Coffee.png' / 'trees/Oak_Stage_5.png'"""
    if name in _cache:
        return _cache[name]
    p = os.path.join(SV, name)
    if not os.path.exists(p):
        return None
    im = Image.open(p).convert('RGBA')
    _cache[name] = im
    return im


def uri(name, w=None, h=None):
    """原图转 data URI；w/h 为显示尺寸（保持整数倍缩放保像素锐度）"""
    im = load(name)
    if im is None:
        return ''
    if w:
        h = h or int(im.height * w / im.width)
        im = im.resize((int(w), int(h)), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def trimmed_uri(name, w):
    """去掉透明边后的图，按宽度缩放到 w（树/建筑用）"""
    im = load(name)
    if im is None:
        return ''
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    h = int(im.height * w / im.width)
    im = im.resize((int(w), h), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


def frame(name, index, cols, cell_w, cell_h, w=None):
    """从图集里切第 index 格（多帧贴图，如 Silo 192x512 = 4 帧纵向）"""
    im = load(name)
    if im is None:
        return ''
    r, c = divmod(index, cols)
    im = im.crop((c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h))
    bb = im.getbbox()
    if bb:
        im = im.crop(bb)
    if w:
        im = im.resize((int(w), int(im.height * w / im.width)), Image.NEAREST)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    return 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()


# ---------------- 命名索引（全部游戏原生） ----------------
TABS = {  # 游戏内右侧标签页（64x68 整块，含木框）
    'inventory': 'Inventory_Tab.png', 'crafting': 'Crafting_Tab.png',
    'collections': 'Collections_Tab.png', 'social': 'Social_Tab.png',
    'animals': 'Animals_Tab.png', 'map': 'Map_Tab.png',
}

ICONS = {  # 游戏内 32~48 图标
    'animals': 'Animals_Icon.png', 'artisan': 'Artisan_Icon.png', 'time': 'Time_Icon.png',
    'achieve': 'Achievements_Icon.png', 'seasons': 'All_Seasons_Icon.png',
    'coffee': 'Coffee.png', 'bean': 'Coffee_Bean.png', 'coffee_maker': 'Coffee_Maker.png',
    'chest': 'Chest.png', 'big_chest': 'Big_Chest.png', 'scarecrow': 'Scarecrow.png',
    'sprinkler': 'Sprinkler.png', 'furnace': 'Furnace.png', 'keg': 'Keg.png',
    'catalogue': 'Animal_Catalogue.png', 'strawhat': 'Straw_Hat.png',
    'strawberry': 'Strawberry.png', 'tomato': 'Tomato.png', 'corn': 'Corn.png',
    'melon': 'Melon.png', 'pumpkin': 'Pumpkin.png', 'wheat': 'Wheat.png',
    'potato': 'Potato.png', 'grape': 'Grape.png', 'blueberry': 'Blueberry.png',
    'ancient': 'Ancient_Fruit.png', 'gem_berry': 'Sweet_Gem_Berry.png',
    'cauliflower': 'Cauliflower.png', 'red_cabbage': 'Red_Cabbage.png',
    'shard': 'Prismatic_Shard.png', 'stardrop': 'Stardrop.png',
    'iridium': 'Iridium_Ore.png', 'gold_ore': 'Gold_Ore.png',
    'walnut': 'Golden_Walnut.png',
}

ANIMALS = {
    'blue_chicken': 'Blue_Chicken.png', 'white_chicken': 'White_Chicken.png',
    'brown_chicken': 'Brown_Chicken.png', 'pig': 'Pig.png', 'goat': 'Goat.png',
    'duck': 'Duck.png', 'rabbit': 'Rabbit.png', 'horse': 'Horse.png',
}

TREES1 = {  # 单棵完整树（从游戏 Stage_5 四帧图集切出）
    'oak': 'tree1/oak_0.png', 'oak_teal': 'tree1/oak_1.png', 'oak_autumn': 'tree1/oak_2.png',
    'maple': 'tree1/maple_0.png', 'maple_dark': 'tree1/maple_1.png', 'maple_pink': 'tree1/maple_2.png',
    'pine': 'tree1/pine_0.png', 'pine_deep': 'tree1/pine_1.png', 'pine_yellow': 'tree1/pine_2.png',
    'mahogany': 'tree1/mahogany_0.png', 'mahogany_olive': 'tree1/mahogany_1.png', 'mahogany_autumn': 'tree1/mahogany_2.png',
    'apple': 'trees/Apple_Stage_5_Fruit.png', 'cherry': 'trees/Cherry_Stage_5_Fruit.png',
    'mango': 'trees/Mango_Stage_5_Fruit.png',
}

TREES = {  # 成熟树（游戏内贴图，4 帧横排原图）
    'oak': 'trees/Oak_Stage_5.png', 'oak2': 'trees/Oak_Stage_4.png',
    'maple': 'trees/Maple_Stage_5.png', 'pine': 'trees/Pine_Stage_5.png',
    'pine2': 'trees/Pine_Stage_4.png', 'mahogany': 'trees/Mahogany_Stage_5.png',
    'apple': 'trees/Apple_Stage_5_Fruit.png', 'cherry': 'trees/Cherry_Stage_5_Fruit.png',
    'mango': 'trees/Mango_Stage_5_Fruit.png', 'mahogany2': 'trees/Mahogany_Stage_3.png',
}

BUILD = {'silo': 'build/Silo.png', 'coop': 'build/Coop.png', 'big_coop': 'build/Big_Coop.png',
         'well': 'build/Well.png', 'house2': 'build/House_(tier_2).png', 'house3': 'build/House_(tier_3).png'}

FENCE = {'wood': 'fence/Wood_Fence.png', 'stone': 'fence/Stone_Fence.png',
         'iron': 'fence/Iron_Fence.png', 'hardwood': 'fence/Hardwood_Fence.png'}


def tab(name, w=32):
    return uri(TABS[name], w, int(w * 68 / 64))


def icon(name, w=22):
    return uri(ICONS[name], w)


def animal(name, w=22):
    return uri(ANIMALS[name], w)


def tree(name, w=56):
    return trimmed_uri(TREES[name], w)


def build(name, w=64):
    return trimmed_uri(BUILD[name], w)


def fence_tile(name='wood', w=16):
    return uri(FENCE[name], w, w)


if __name__ == '__main__':
    print('tabs', len(TABS), 'icons', len(ICONS), 'trees', len(TREES),
          'animals', len(ANIMALS), 'build', len(BUILD), 'fence', len(FENCE))
    miss = [v for v in list(TABS.values()) + list(ICONS.values()) + list(ANIMALS.values())
            + list(TREES.values()) + list(BUILD.values()) + list(FENCE.values())
            if not os.path.exists(os.path.join(SV, v))]
    print('missing files:', miss)
