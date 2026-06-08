#!/usr/bin/env python3
"""Replace the entire 芙蓉女儿诔 entry in poems_data.py with correct content from novel."""
import json, re

# --- Step 1: Extract complete 芙蓉女儿诔 from novel ---
data = json.load(open('/opt/hongloumeng/app/novel_data.json'))
ch78 = [c for c in data['chapters'] if c['num'] == 78][0]
content = ch78['content']

start = content.find('维')
end_marker = '呜呼哀哉！尚飨'
end_idx = content.find(end_marker)
if end_idx < 0:
    end_idx = start + 9000
else:
    end_idx += len(end_marker)

elegy = content[start:end_idx]

# Strip annotation markers
elegy = re.sub(r'\[\d+\]', '', elegy)
elegy = re.sub(r'〔[一二三四五六七八九十\d]+〕', '', elegy)
elegy = elegy.replace('\r\n', '\n')
elegy = re.sub(r'\n{3,}', '\n\n', elegy)

# Clean individual line fragments
# Fix "楼空鳷\n鹊" -> "楼空鳷鹊"
elegy = re.sub(r'鳷\n鹊', '鳷鹊', elegy)

sections = elegy.split('\n\n')

# --- Step 2: Build lines and line_types ---
lines = []
line_types = []

# Helper functions
def add_prose(text):
    """Add a prose line"""
    t = text.strip()
    if t:
        lines.append(t)
        line_types.append("prose")

def add_verse(text):
    """Add a verse line"""
    t = text.strip().replace('\n', '')
    if t:
        lines.append(t)
        line_types.append("verse")

def add_blank():
    lines.append("")
    line_types.append("")

# Section 0: "维" - merge with section 1
# Add "维" to the beginning of section 1 content
s1_text = "维" + sections[1].strip().replace('\n', '')
add_prose(s1_text)

# Sections 2-9: prose paragraphs
# Sections 5 and 6 were split by EPUB page break (鳷|鹊), merge them
s5_saved = None
for i in range(2, 10):
    text = sections[i].strip().replace('\n', '')
    if not text:
        continue
    if i == 5:
        # Save section 5 and merge with section 6
        s5_saved = text
        continue
    if i == 6 and s5_saved:
        text = s5_saved + text
        s5_saved = None
    add_blank()
    add_prose(text)
if s5_saved:
    add_blank()
    add_prose(s5_saved)

# Sections 10-28: verse lines (招魂辞 兮-lines)
add_blank()
for i in range(10, 29):
    text = sections[i].strip().replace('\n', '')
    if text:
        add_verse(text)

# Section 29: 若夫鸿蒙而居 section (currently MISSING from poems_data)
# Split into natural verse lines
s29 = sections[29].strip().replace('\n', '')
if s29:
    add_blank()
    # Split by sentence patterns
    # Each group of 2-4 short clauses makes one verse line
    verse_lines_s29 = [
        "若夫鸿蒙而居，寂静以处，虽临于兹，余亦莫睹。",
        "搴烟萝而为步幛，列枪蒲而森行伍。",
        "警柳眼之贪眠，释莲心之味苦。",
        "素女约于桂岩，宓妃迎于兰渚。",
        "弄玉吹笙，寒簧击敔。",
        "征嵩岳之妃，启骊山之姥。",
        "龟呈洛浦之灵，兽作咸池之舞。",
        "潜赤水兮龙吟，集珠林兮凤翥。",
        "爰格爰诚，匪簠匪筥。",
        "发轫乎霞城，返旌乎玄圃。",
        "既显微而若通，复氤氲而倏阻。",
        "离合兮烟云，空蒙兮雾雨。",
        "尘霾敛兮星高，溪山丽兮月午。",
        "何心意之忡忡，若寤寐之栩栩。",
        "余乃欷歔怅望，泣涕彷徨。",
        "人语兮寂历，天籁兮筼筜。",
        "鸟惊散而飞，鱼唼喋以响。",
        "志哀兮是祷，成礼兮期祥。",
    ]
    for vl in verse_lines_s29:
        add_verse(vl)

# Section 30: closing
add_blank()
s30_text = sections[30].strip().replace('\n', '')
if s30_text:
    # "呜呼哀哉！尚飨" - remove any trailing punctuation issues
    s30_text = s30_text.rstrip('。，；')
    add_verse(s30_text)

# --- Step 3: Build the replacement entry ---
entry_lines = []
entry_lines.append('    # 17. 芙蓉女儿诔')
entry_lines.append('    # ' + '=' * 46)
entry_lines.append('    {')
entry_lines.append('        "slug": "furong_lei",')
entry_lines.append('        "name": "芙蓉女儿诔",')
entry_lines.append('        "poems": [')
entry_lines.append('            {')
entry_lines.append('                "id": "furong",')
entry_lines.append('                "title": "芙蓉女儿诔",')
entry_lines.append('                "chapter": "第七十八回",')
entry_lines.append('                "author": "贾宝玉",')
entry_lines.append('                "lines": [')
for l in lines:
    entry_lines.append('                    "%s",' % l.replace('"', '\\"'))
entry_lines.append('                ],')
entry_lines.append('                "line_types": [')
for lt in line_types:
    entry_lines.append('                    "%s",' % lt)
entry_lines.append('                ],')
entry_lines.append('            },')
entry_lines.append('        ],')
entry_lines.append('    },')

replacement = '\n'.join(entry_lines)

print("=== NEW ENTRY ===")
print(replacement)

# --- Step 4: Replace in poems_data.py ---
with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    poems_data = f.read()

# Find the 芙蓉 section boundaries
start_marker = "    # 17. 芙蓉女儿诔"
end_marker = "    # 18. 杂篇"

old_start = poems_data.find(start_marker)
old_end = poems_data.find(end_marker)

if old_start >= 0 and old_end > old_start:
    old_section = poems_data[old_start:old_end]
    new_data = poems_data[:old_start] + replacement + "\n" + poems_data[old_end:]

    with open('/opt/hongloumeng/app/poems_data.py', 'w') as f:
        f.write(new_data)

    print("\n=== REPLACED ===")
    print("Old length:", len(old_section))
    print("New length:", len(replacement))

    # Verify syntax
    try:
        ast = compile(new_data, '/opt/hongloumeng/app/poems_data.py', 'exec')
        print("Syntax: OK")
    except SyntaxError as e:
        print("Syntax ERROR:", e)
else:
    print("ERROR: Could not find section boundaries")
    print("start_marker found at:", old_start)
    print("end_marker found at:", old_end)
