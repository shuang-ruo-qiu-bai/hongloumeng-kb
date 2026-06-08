#!/usr/bin/env python3
"""Final comprehensive character mapping for all inline images.
Uses multiple strategies to determine each character.
"""
import json

# Complete mapping with reasoning for each entry
# Key = image filename, Value = [character, source/reason]
CHAR_MAP = {
    # === Chapter 1 Notes ===
    '00004.jpeg': ['頫', 'context: 曹頫 (Cao Fu, father of Cao Xueqin)'],
    '00005.jpeg': ['鹍', 'context: 靖应鹍藏本 (Jing Yingkun's manuscript)'],
    '00006.jpeg': ['袴', 'known phrase: 锦衣纨袴'],
    '00007.jpeg': ['匵', 'ancient text: 玉在匵中求善价 (Analects)'],
    '00008.jpeg': ['累', 'context: 闲文累瘰 (verbose/tedious)'],
    '00009.jpeg': ['紬', 'known phrase: 翠幄青紬车 (silk carriage cover)'],

    # === Chapter 3 ===
    '00010.jpeg': ['槅', 'known phrase: 玻璃槅 (glass partition)'],
    '00011.jpeg': ['懒', 'known phrase: 惫懒 (rascal)'],
    '00012.jpeg': ['闱', 'note context: 仪门 from 闱门 (side gate)'],
    '00013.jpeg': ['亞', 'note context: 黼黻 亞形图案 (glyph shape)'],

    # === Chapter 3 Note ===
    '00014.jpeg': ['颦', 'note explicitly gives: 病心而颦（通"颦"）'],
    '00015.jpeg': ['痣', 'known phrase: 胭脂痣 (birthmark)'],
    '00016.jpeg': ['麴', 'context: 凤乳之麴 (ferment for brewing)'],
    '00017.jpeg': ['㐀', 'variant note: 山点改为㐀 (丘 variant)'],
    '00018.jpeg': ['麴', 'note explains: 酿酒用的发酵物 (qū yeast)'],

    # === Chapter 4 ===
    '00019.jpeg': ['讹', 'book title: 订讹杂录 by 胡鸣玉'],
    '00020.jpeg': ['舔', 'context: 舔舌咂嘴 (licking lips)'],
    '00021.jpeg': ['䙆', 'Ming history: 四䙆袄子 (slit garment)'],
    '00022.jpeg': ['鬏', 'context: 散挽着鬏儿 (hair bun)'],

    # === Chapter 8 ===
    '00025.jpeg': ['颤', 'known phrase: 手打颤儿 (hand trembling)'],
    '00026.jpeg': ['毬', 'colloquial: 管你毬相干 (expletive)'],

    # === Chapter 9 Note ===
    '00027.jpeg': ['赑', 'dragon legend: 赑屃 (bixi, tortoise-dragon)'],
    '00028.jpeg': ['𧈢', '杨慎 list: between 饕餮 and 睚眦'],

    # === Chapter 11 ===
    '00030.jpeg': ['哗', 'onomatopoeia: 哗拉拉 (splashing sound)'],
    '00031.jpeg': ['綍', '礼记 quote: 其出如綍 (fú, imperial decree)'],
    '00032.jpeg': ['搀', 'context: 搀扶 (support by the arm)'],
    '00033.jpeg': ['着', '贾母语: 才着气的人 (just angered)'],

    # === Chapter 13 ===
    '00034.jpeg': ['珖', '贾家族谱: between 贾琮 and 贾珩'],
    '00035.jpeg': ['鞓', '北静王腰带: 碧玉红鞓带 (leather belt)'],

    # === Chapter 15 ===
    '00036.jpeg': ['鹡', '香名: 鹡鸰香 (brotherly affection incense)'],
    '00037.jpeg': ['舄', 'context: 越仙舄 (immortal's shoes)'],
    '00038.jpeg': ['塞', '凤姐动作: 拿来塞在自己枕边'],

    # === Chapter 17 ===
    '00039.jpeg': ['䓈', '扬雄传: 飏䓈芳苓'],
    '00040.jpeg': ['闪', '大观园: 奇花闪灼 (flowers shimmering)'],
    '00041.jpeg': ['蘼', 'known phrase: 荼蘼架 (trellis)'],
    '00042.jpeg': ['䓞', 'plant name: 䓞兰 (a fragrant plant)'],
    '00043.jpeg': ['䓞', 'same as 00042: 金䓞草'],
    '00044.jpeg': ['𦽅', 'plant list: 藿𦽅姜荨'],

    # === Chapter 17 ===
    '00045.jpeg': ['字', 'pattern: 卍字卍'],
    '00046.jpeg': ['字', 'pattern: 卍卍字'],
    '00047.jpeg': ['窥', '成语: 以筦窥天 (looking at sky through tube)'],

    # === Chapter 19 ===
    '00048.jpeg': ['蜇', '虾须帘: 蜇，海中大虾也'],

    # === Chapter 19 ===
    '00049.jpeg': ['大', '茗烟笑道 (this image is decorative/regular char)'],

    # === Chapter 19 / 21 Notes ===
    '00050.jpeg': ['蹭', 'lipped verb: 蹭上了一点儿 (rubbed on)'],
    '00051.jpeg': ['蹭', 'note gives: 同蹭、蹭 (variant character)'],

    # === Chapter 20 ===
    '00052.jpeg': ['黹', '习俗: 忌针黹 (no needlework on certain days)'],

    # === Chapter 21 ===
    '00053.jpeg': ['灭', '庄子: 灭工倕之指 (eliminate the artisan's fingers)'],

    # === Chapter 22 ===
    '00054.jpeg': ['拧', '凤姐语: 你和我拧的 (wrangling)'],
    '00055.jpeg': ['揾', '戏曲: 漫揾英雄泪 (wipe away tears)'],

    # === Chapter 22 Note ===
    '00056.jpeg': ['缄', 'variant note: 插→缄口禁言'],

    # === Chapter 23 ===
    '00057.jpeg': ['𧚨', '锦罽𧚨衾 (a type of blanket)'],
    '00058.jpeg': ['𧚨', 'same as 00057: note describes the character'],

    # === Chapter 26 Note ===
    '00059.jpeg': ['屃', 'dragon: 赑屃 (bixi)'],

    # === Chapter 26 Note ===
    '00060.jpeg': ['苏', '方言: 噜苏 (verbose/tedious)'],
    '00061.jpeg': ['臜', 'known word: 腌臜 (dirty)'],

    # === Chapter 27 ===
    '00062.jpeg': ['飖', 'context: 绣带飘飖 (ribbons fluttering)'],

    # === Chapter 27 ===
    '00063.jpeg': ['爖', '晴雯语: 茶炉子也不爖 (light the stove)'],

    # === Chapter 29 ===
    '00064.jpeg': ['瓊', '贾家族名: between 贾璜 and 贾琼'],

    # === Chapter 29 ===
    '00065.jpeg': ['撏', '凤姐语: 把胡子还撏了 (pull out beard)'],

    # === Chapter 30 ===
    '00066.jpeg': ['鷀', 'known: 花鷀 (cormorant-like bird)'],

    # === Chapter 30 Note ===
    '00067.jpeg': ['靋', 'note: 靋/扚 (dialect for pinch)'],

    # === Chapter 30 Note ===
    '00068.jpeg': ['𠃊', '蔷字: 回写作𠃊 (radical form)'],

    # === Chapter 38 ===
    '00069.jpeg': ['掐', '宝钗: 掐了桂蕊 (pick flower stamens)'],

    # === Chapter 38 Note ===
    '00070.jpeg': ['琎', '人名: 李琎 (汝阳郡王)'],

    # === Chapter 40 ===
    '00071.jpeg': ['跴', '刘姥姥: 跴走土地 (step on ground)'],

    # === Chapter 40 Note ===
    '00072.jpeg': ['添', 'variant note: 剩的添上里子'],

    # === Chapter 40 Note ===
    '00073.jpeg': ['瑛', '人名: 杨孟瑛 (Ming official)'],

    # === Chapter 41 ===
    '00074.jpeg': ['削', '凤姐: 把皮削了 (peel)'],

    # === Chapter 41 ===
    '00075.jpeg': ['瓠', '妙玉杯: 瓠瓟斝 (gourd-shaped cup)'],
    '00076.jpeg': ['𤨎', '妙玉杯: 点犀𤨎 (rhinoceros horn cup)'],

    # === Chapter 41 Note ===
    '00077.jpeg': ['訾', 'note: 飺本当作訾 (variant character for 飺)'],

    # === Chapter 42 Note ===
    '00078.jpeg': ['䶎', 'variant: 鼾䶎 (variant of 齁, snoring)'],

    # === Chapter 42 ===
    '00079.jpeg': ['笼', '惜春: 另笼上风炉子 (set up stove)'],

    # === Chapter 43 ===
    '00080.jpeg': ['蹽', '宝玉: 顺着街就蹽下去了 (run off)'],

    # === Chapter 44 Note ===
    '00081.jpeg': ['慰', 'variant: 原作慰一→熨一 (variant reading)'],

    # === Chapter 44 Note ===
    '00082.jpeg': ['窝', '竹剪刀: 对头窝弯 (bamboo strip bent)'],

    # === Chapter 45 Note ===
    '00083.jpeg': ['抱', 'variant: 你必抱怨 (variant note)'],

    # === Chapter 45 ===
    '00084.jpeg': ['辖', '凤姐: 辖了我去 (control/manage)'],

    # === Chapter 45 ===
    '00085.jpeg': ['爇', '秋窗: 摇摇爇短檠 (burn the lamp)'],

    # === Chapter 45 Note ===
    '00086.jpeg': ['卹', '抚恤 variant: 抚卹'],

    # === Chapter 46 ===
    '00087.jpeg': ['𪉷', '邢夫人: 禀性愚𪉷 (stubborn)'],

    # === Chapter 46 ===
    '00088.jpeg': ['顉', '宝玉: 看你顉着头过去了 (lower head)'],

    # === Chapter 46 Note ===
    '00089.jpeg': ['𩓞', 'note: 顉/𩓞 (variant of bowing head)'],

    # === Chapter 47 ===
    '00090.jpeg': ['砉', '薛蟠挨打: 砉的一声 (sound of hit)'],

    # === Chapter 48 ===
    '00091.jpeg': ['玚', '建安七子: 应玚 (Yang)'],

    # === Chapter 49 ===
    '00092.jpeg': ['䇭', '烤鹿肉: 铁丝䇭 (wire basket)'],

    # === Chapter 49 Note ===
    '00093.jpeg': ['棅', '高棅: 唐诗品汇总序 author'],

    # === Chapter 50 ===
    '00094.jpeg': ['栉', '宝玉冒雪: 栉了一枝红梅 (pick a branch)'],

    # === Chapter 50 ===
    '00095.jpeg': ['骥', '谜语: 骥何劳缚紫绳 (fine horse)'],

    # === Chapter 50 Note ===
    '00096.jpeg': ['硝', 'variant: 绡原作硝'],

    # === Chapter 50 Note ===
    '00097.jpeg': ['騄', '马名: 騄耳 (Lu'er, famous horse)'],

    # === Chapter 51 ===
    '00098.jpeg': ['潄', '温水潄 (rinse with warm water)'],

    # === Chapter 51 Note ===
    '00099.jpeg': ['瘗', '杨贵妃: 初瘗时 (buried)'],

    # === Chapter 58 ===
    '00100.jpeg': ['劚', '园中: 劚树 (cut/trim trees)'],

    # === Chapter 59 Note ===
    '00101.jpeg': ['閒', '闲字 variant: 間→閒'],

    # === Chapter 60 ===
    '00102.jpeg': ['犟', '赵姨娘: 瞪着眼犟摔 (stubborn)'],

    # === Chapter 61 ===
    '00108.jpeg': ['捽', '柳家的: 屄毛捽下来 (pull out)'],

    # === Chapter 62 ===
    '00109.jpeg': ['𠸎', '香菱: 满嘴里汗𠸎 (nonsense)'],

    # === Chapter 63 ===
    '00110.jpeg': ['绒', '芳官: 酡红青绒三色 (velvet-colored)'],

    # === Chapter 63 ===
    '00111.jpeg': ['蘼', '荼蘼花 (same as 00041)'],

    # === Chapter 64 ===
    '00112.jpeg': ['蘅', '贾蘅 (Jia family member name in clan list)'],

    # === Chapter 64 ===
    '00113.jpeg': ['哗', '嘻哗喇乱响 (commotion sound)'],

    # === Chapter 65 Note ===
    '00114.jpeg': ['撞', '撞丧 (insult phrase)'],

    # === Chapter 66 ===
    '00115.jpeg': ['闭', '每日关门闭户 (close doors)'],

    # === Chapter 69 Note ===
    '00116.jpeg': ['娇', '娇俏 (variant note)'],

    # === Chapter 70 ===
    '00117.jpeg': ['籆', '放风筝: 拨籆 (reel)'],
    '00118.jpeg': ['籆', 'note: 籆子 (spool)'],

    # === Chapter 74 ===
    '00119.jpeg': ['橫', '钗横鬓乱 (disheveled hair)'],

    # === Chapter 76 ===
    '00120.jpeg': ['崴', '贾赦: 崴了腿 (sprained ankle)'],

    # === Chapter 76 ===
    '00121.jpeg': ['屃', '赑屃 (same as 00059)'],
    '00122.jpeg': ['婺', '星名: 婺女 (constellation)'],

    # === Chapter 76 Note ===
    '00123.jpeg': ['捞', '捞嘴 (variant note)'],

    # === Chapter 76 Note (continued) ===
    '00124.jpeg': ['屃', '赑屃 (same as 00059, 00121)'],

    # === Chapter 78 ===
    '00125.jpeg': ['嫿', '姽嫿将军 (beautiful/quiet)'],
    '00126.jpeg': ['绡', '鲛绡 (mermaid silk)'],

    # === 芙蓉女儿诔 ===
    '00127.jpeg': ['蘋', '蘋蘩蕴藻 (water plants for sacrifice)'],
    '00128.jpeg': ['薋', '薋葹妒其臭 (weeds, chen)'],
    '00129.jpeg': ['茝', '茝兰竟被芟 (fragrant herb)'],
    '00130.jpeg': ['鉏', '被芟鉏 (s Cythe锄)'],
    '00131.jpeg': ['顑', '色陈顑颔 (emaciated)'],
    '00132.jpeg': ['謑', '诼谣謑诟 (shame/disgrace)'],
    '00133.jpeg': ['羽', '拾翠羽于尘埃 (feather)'],
    '00134.jpeg': ['鳷', '楼空鳷鹊 (a mythical bird)'],
    '00135.jpeg': ['诐', '钳诐奴之口 (slanderous)'],
    '00136.jpeg': ['繖', '望繖盖之陆离 (canopy/umbrella)'],
    '00137.jpeg': ['鹥', '御鸾鹥以征 (a mythical bird)'],
    '00138.jpeg': ['薆', '闻馥郁而薆然 (fragrant)'],
    '00139.jpeg': ['纕', '纫蘅杜以为纕 (belt/sash)'],
    '00140.jpeg': ['筼', '天籁兮筼筜 (bamboo)'],
    '00141.jpeg': ['筼', '天籁兮筼筜 (same as 00140)'],

    # === Chapter 78 Note ===
    '00142.jpeg': ['楎', '朱祐楎 (Ming prince)'],

    # === Chapter 78 Note ===
    '00143.jpeg': ['鍮', '金银鍮石 (toushi, a mineral)'],
    '00144.jpeg': ['馡', '同馡，香气 (fragrance)'],

    # === Chapter 78 Note ===
    '00145.jpeg': ['疣', '决疣溃痈 (wart/carbuncle)'],

    # === Chapter 86 Note ===
    '00146.jpeg': ['𠀥', '琴谱符号 (guqin notation)'],

    # === Chapter 87 ===
    '00147.jpeg': ['呖', '唏呖哗喇 (rustling sound)'],

    # === Chapter 88 ===
    '00148.jpeg': ['掯', '别逼掯 (force/pressure)'],

    # === Chapter 92 Note ===
    '00149.jpeg': ['瓌', '任瓌 (Tang official, husband)'],

    # === Chapter 92 Note ===
    '00150.jpeg': ['鷟', '张鷟 (Zhuo, Tang writer)'],

    # === Chapter 94 ===
    '00151.jpeg': ['隤', '海棠忽摧隤 (wither/decay)'],

    # === Chapter 97 ===
    '00152.jpeg': ['腴', '丰肩腴体 (plump/fleshy)'],
    '00153.jpeg': ['䁙', '眼䁙 (glance/dazzle)'],

    # === Chapter 99 Note ===
    '00154.jpeg': ['頍', '頍弁 (hat/headpiece)'],
    '00155.jpeg': ['紞', '索紞 (Jin dynasty person)'],

    # === Chapter 102 ===
    '00156.jpeg': ['缊', '缊交感 (subtle interaction)'],

    # === Chapter 103 ===
    '00157.jpeg': ['匵', '玉在匵中求善价 (same as 00007)'],

    # === Chapter 109 ===
    '00158.jpeg': ['鬏', '挽着鬏儿 (same as 00022)'],

    # === Chapter 111 Note ===
    '00159.jpeg': ['缡', '褵也作缡 (bridal veil)'],
    '00160.jpeg': ['縗', '同縗麻 (hemp mourning garment)'],

    # === Chapter 117 ===
    '00161.jpeg': ['臜', '腌臜 (same as 00061)'],

    # === Chapter 120 ===
    '00162.jpeg': ['糊', '糊口谋衣 (scrape a living)'],
}

# Write the mapping as a Python file
lines = ['# Auto-generated character mapping for inline images',
         '# Key: image filename, Value: character',
         'INLINE_CHAR_MAP = {']
for fname, (char, reason) in sorted(CHAR_MAP.items()):
    lines.append(f"    '{fname}': '{char}',  # {reason}")
lines.append('}')

with open('/tmp/inline_char_map.py', 'w') as f:
    f.write('\n'.join(lines))

print(f"Total mapped: {len(CHAR_MAP)}")
print(f"Written to /tmp/inline_char_map.py")

# Also check which image files exist but aren't in the mapping
import zipfile, re
EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

found_files = set()
for n in sorted(names):
    if not (n.endswith('.html') or n.endswith('.xhtml')):
        continue
    content = z.read(n).decode('utf-8')
    for m in re.finditer(r'<img[^>]*class="inline"[^>]*src="([^"]+)"[^>]*/>', content):
        fname = m.group(1).split('/')[-1]
        found_files.add(fname)

mapped = set(CHAR_MAP.keys())
unmapped = found_files - mapped

if unmapped:
    print(f"\nStill unmapped ({len(unmapped)}):")
    for f in sorted(unmapped):
        print(f"  {f}")
else:
    print(f"\nAll {len(found_files)} image files mapped!")

z.close()
