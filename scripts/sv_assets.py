"""从星露谷 wiki 抓取【游戏原生素材】（单格贴图），存到 assets/sv/
这些文件在 wiki 上即是游戏内 Content 目录拆出的原图（未做二次绘制）。
来源：stardewvalleywiki.com/mediawiki/images（CC BY-NC-SA 4.0，商用需授权；个人主页署名使用）
"""
import json, os, subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'assets', 'sv')
LIST = '/tmp/wikiallimgs.json'

# 需要抓的游戏原素材（文件名为 wiki 上的确切名称）
NEED = [
    # —— UI 标签页（游戏内 Options/Inventory 面板右上角那排） ——
    'Animals_Tab.png', 'Collections_Tab.png', 'Crafting_Tab.png', 'Inventory_Tab.png',
    'Map_Tab.png', 'Social_Tab.png', 'Skills_Tab.png',
    # —— 状态/成就图标 ——
    'Animals_Icon.png', 'Artisan_Icon.png', 'Time_Icon.png', 'Achievements_Icon.png',
    'All_Seasons_Icon.png', 'Abandoned_House_Icon.png',
    # —— 咖啡线（豆藏主项目） ——
    'Coffee.png', 'Coffee_Bean.png', 'Coffee_Maker.png',
    'Coffee_Stage_3.png', 'Coffee_Stage_4.png', 'Coffee_Stage_5.png', 'Coffee_Stage_6.png', 'Coffee_Stage_7.png',
    # —— 工具/装备 ——
    'Chest.png', 'Big_Chest.png', 'Scarecrow.png', 'Sprinkler.png', 'Furnace.png', 'Keg.png',
    'Animal_Catalogue.png', 'Straw_Hat.png',
    # —— 动物 ——
    'Blue_Chicken.png', 'White_Chicken.png', 'Brown_Chicken.png', 'Blue_Chicken_v2.png',
    'Pig.png', 'Goat.png', 'Duck.png', 'Rabbit.png', 'Horse.png', 'Cat.png', 'Dog.png',
    # —— 果树/树木 ——
    'Apple_Sapling.png', 'Cherry_Sapling.png', 'Apricot_Sapling.png', 'Orange_Sapling.png',
    # —— 作物（官方 48px 大图标） ——
    'Strawberry.png', 'Tomato.png', 'Corn.png', 'Melon.png', 'Pumpkin.png', 'Wheat.png',
    'Potato.png', 'Grape.png', 'Blueberry.png', 'Ancient_Fruit.png', 'Sweet_Gem_Berry.png',
    'Hops.png', 'Bok_Choy.png', 'Cauliflower.png', 'Red_Cabbage.png',
    # —— 节庆/装饰 ——
    'Junimo.png', 'Banner.png', 'Star_Flag.png', 'Golden_Walnut.png', 'Prismatic_Shard.png',
    'Stardrop.png', 'Iridium_Ore.png', 'Gold_Ore.png',
]


def main():
    imgs = json.load(open(LIST))
    by = {i['name']: i for i in imgs}
    os.makedirs(OUT, exist_ok=True)
    ok, miss = [], []
    for name in NEED:
        it = by.get(name)
        if not it:
            miss.append(name)
            continue
        dst = os.path.join(OUT, name)
        if not os.path.exists(dst) or os.path.getsize(dst) < 100:
            subprocess.run(['curl', '-s', '-m', '40', '-o', dst, it['url']])
        if os.path.exists(dst) and os.path.getsize(dst) > 100:
            ok.append(name)
        else:
            miss.append(name)
    print(f'ok {len(ok)} / miss {len(miss)}')
    if miss:
        print('missing:', ', '.join(miss))


if __name__ == '__main__':
    main()
