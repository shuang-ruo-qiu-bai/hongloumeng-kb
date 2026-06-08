#!/usr/bin/env python3
"""Fix 芙蓉女儿诔 formatting in poems_data.py"""
import json, re, sys

# --- Step 1: Get complete text from novel ---
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

sections = elegy.split('\n\n')
print("Total sections:", len(sections))
for i, s in enumerate(sections):
    stripped = s.strip().replace('\n', ' ')
    if stripped:
        preview = stripped[:150] + "..." if len(stripped) > 150 else stripped
        print("Section %d: %s" % (i, preview))
