#!/usr/bin/env python3
"""Generate complete inline image → character mapping from EPUB context."""
import zipfile, re, json

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

# Gather all inline image occurrences with context
image_occurrences = {}  # filename → list of contexts
for n in sorted(names):
    if not (n.endswith('.html') or n.endswith('.xhtml')):
        continue
    content = z.read(n).decode('utf-8')
    for m in re.finditer(r'<img[^>]*class="inline"[^>]*src="([^"]+)"[^>]*/>', content):
        src = m.group(1)
        fname = src.split('/')[-1]
        idx = m.start()
        start = max(0, idx - 100)
        end = min(len(content), idx + len(m.group()) + 200)
        context = content[start:end]
        if fname not in image_occurrences:
            image_occurrences[fname] = []
        image_occurrences[fname].append(context)

z.close()

# Build character mapping
# Strategy: if a note explicitly gives the character in () or （）, use that.
# For body text, match well-known 红楼梦 passages.

char_map = {}

for fname, contexts in sorted(image_occurrences.items()):
    combined = ''.join(contexts)

    char = None

    # Strategy 1: Note explicitly says （×通"Y"）or （Y）or 同"Y"
    m = re.search(r'[（\(]通["""]?([^""")」』]+)["""]?[）\)]', combined)
    if m:
        char = m.group(1).strip()

    if not char:
        m = re.search(r'[（\(]一作["""]?([^""")」』]+)["""]?[）\)]', combined)
        if m:
            char = m.group(1).strip()

    if not char:
        m = re.search(r'同["""「『]?([^""」』]+)["""」』]?[）\)]', combined)
        if m and len(m.group(1)) <= 2:
            char = m.group(1).strip()

    # Strategy 2: Note says "即Y" where Y is the character
    if not char:
        m = re.search(r'即["""「『]?([''""]?)([^""」』\s\(\)（）、。]{1,3})[''""]?["""」』]?[）\)]', combined)
        # Only use if clear

    # Strategy 3: Known 红楼梦 phrases
    known_phrases = {
        '00004.jpeg': ('頫', '曹頫'),   # context: 认为是曹頫
        '00005.jpeg': ('鹍', '靖应鹍藏本'),
        '00006.jpeg': ('袴', '锦衣纨袴'),
        '00007.jpeg': ('匵', '玉在匵中求善价 (Analects)'),
        '00008.jpeg': ('累', '闲文累瘰'),
        '00009.jpeg': ('紬', '翠幄青紬车'),
        '00010.jpeg': ('槅', '玻璃槅'),
        '00011.jpeg': ('懒', '惫懒'),
        '00014.jpeg': ('颦', '病心而颦'),
        '00015.jpeg': ('痣', '胭脂痣'),
        '00016.jpeg': ('麴', '凤乳之麴'),
        '00019.jpeg': ('讹', '订讹杂录'),
        '00020.jpeg': ('舔', '舔舌咂嘴'),
        '00022.jpeg': ('鬏', '散挽着鬏儿'),
        '00025.jpeg': ('颤', '手打颤儿'),
        '00026.jpeg': ('毬', '管你毬相干'),
        '00027.jpeg': ('赑', '赑屃'),
        '00030.jpeg': ('哗', '哗拉拉'),
        '00031.jpeg': ('綍', '其出如綍'),
        '00032.jpeg': ('搀', '搀扶'),
        '00035.jpeg': ('鞓', '碧玉红鞓带'),
        '00036.jpeg': ('鹡', '鹡鸰香'),
        '00037.jpeg': ('舄', '越仙舄'),
        '00038.jpeg': ('塞', '拿来塞在自己枕边'),
        '00040.jpeg': ('闪', '奇花闪灼'),
        '00041.jpeg': ('蘼', '荼蘼架'),
        '00045.jpeg': ('字', '卍字卍'),  # or 卐
        '00046.jpeg': ('字', '卍卍字'),
        '00047.jpeg': ('窥', '以筦窥天'),
        '00052.jpeg': ('黹', '忌针黹'),
        '00059.jpeg': ('屃', '赑屃'),
        '00060.jpeg': ('苏', '噜苏'),
        '00061.jpeg': ('臜', '腌臜'),
        '00062.jpeg': ('飖', '绣带飘飖'),
        '00063.jpeg': ('爖', '茶炉子也不爖'),  # uncertain
        '00065.jpeg': ('撏', '把胡子还撏了'),
        '00066.jpeg': ('鷀', '花鷀'),  # 鸬鹚
        '00068.jpeg': ('□', '回写作囗'),  # actually just 口/囗 as radical
        '00070.jpeg': ('琎', '李琎'),  # 汝阳郡王
        '00073.jpeg': ('瑛', '杨孟瑛'),
        '00074.jpeg': ('削', '把皮削了'),
        '00085.jpeg': ('爇', '摇摇爇短檠'),
        '00087.jpeg': ('𪉷', '愚𪉷'),  # or 戆(愚戇)
        '00090.jpeg': ('砉', '砉的一声'),
        '00091.jpeg': ('玚', '应玚'),
        '00092.jpeg': ('罩', '铁丝罩'),
        '00093.jpeg': ('棅', '高棅'),  # 唐诗品汇总序
        '00095.jpeg': ('骥', '骥何劳缚紫绳'),
        '00097.jpeg': ('騄', '騄耳'),
        '00098.jpeg': ('涮', '温水涮'),
        '00099.jpeg': ('瘗', '初瘗时'),
        '00100.jpeg': ('劚', '劚树'),
        '00101.jpeg': ('閒', '閒字'),
        '00111.jpeg': ('蘼', '荼蘼花'),
        '00114.jpeg': ('撞', '撞丧'),
        '00115.jpeg': ('闭', '关门闭户'),
        '00117.jpeg': ('籆', '拨籆'),
        '00118.jpeg': ('籆', '籆子'),
        '00119.jpeg': ('橫', '钗横'),  # 钗横鬓乱
        '00120.jpeg': ('崴', '崴了腿'),
        '00121.jpeg': ('屃', '赑屃'),
        '00122.jpeg': ('婺', '婺女'),
        '00124.jpeg': ('屃', '赑屃'),
        '00125.jpeg': ('嫿', '姽嫿将军'),
        '00126.jpeg': ('绡', '污鲛绡'),
        '00127.jpeg': ('蘋', '蘋蘩蕴藻'),
        '00131.jpeg': ('顑', '色陈顑颔'),
        '00133.jpeg': ('羽', '拾翠羽'),
        '00134.jpeg': ('鳷', '楼空鳷鹊'),
        '00136.jpeg': ('繖', '望繖盖'),
        '00137.jpeg': ('鹥', '御鸾鹥'),
        '00138.jpeg': ('薆', '薆然'),  # 薆然香气
        '00139.jpeg': ('纕', '纫蘅杜以为纕'),
        '00142.jpeg': ('楎', '朱祐楎'),
        '00143.jpeg': ('鍮', '金银鍮石'),
        '00144.jpeg': ('馡', '馡馡香气'),
        '00145.jpeg': ('疣', '决疣溃痈'),
        '00147.jpeg': ('呖', '唏呖哗喇'),
        '00148.jpeg': ('掯', '别逼掯'),
        '00149.jpeg': ('瓌', '任瓌'),
        '00150.jpeg': ('鷟', '张鷟'),
        '00151.jpeg': ('隤', '海棠忽摧隤'),
        '00152.jpeg': ('腴', '丰肩腴体'),
        '00153.jpeg': ('䁙', '眼䁙'),
        '00154.jpeg': ('頍', '頍弁'),
        '00155.jpeg': ('紞', '索紞'),
        '00156.jpeg': ('缊', '缊交感'),  # uncertain
        '00157.jpeg': ('匵', '玉在匵中'),
        '00158.jpeg': ('鬏', '挽着鬏儿'),
        '00159.jpeg': ('缡', '褵也作缡'),
        '00160.jpeg': ('縗', '同縗麻'),
        '00161.jpeg': ('臜', '腌臜'),
        '00162.jpeg': ('糊', '糊口谋衣'),
    }

    if fname in known_phrases:
        char = known_phrases[fname][0]
        reason = known_phrases[fname][1]
    else:
        reason = 'MANUAL_CHECK'

    # Save character
    if char and char != '□':
        char_map[fname] = char
    else:
        char_map[fname] = '□'  # still unknown

# Print mapping as JSON
print(json.dumps(char_map, ensure_ascii=False, indent=2))
print(f'\nTotal: {len(char_map)} images, {sum(1 for v in char_map.values() if v != "□")} mapped')

# Also find which ones still need manual review
unmapped = [f for f, c in char_map.items() if c == '□']
if unmapped:
    print(f'\nUnmapped ({len(unmapped)}):')
    for f in unmapped:
        ctx = image_occurrences[f][0]
        text = re.sub(r'<[^>]+>', '', ctx).strip()[:120]
        print(f'  {f}: ...{text}...')
