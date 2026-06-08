#!/usr/bin/env python3
"""Remove Sun Wen image reference from poems.html since all images are deleted."""
with open('/opt/hongloumeng/app/templates/poems.html', 'r') as f:
    content = f.read()

old = """<figure class="poetry-banner">
    <img src="/static/sunwen/sunwen_001.jpg" alt="孙温绘《红楼梦》" loading="lazy">
    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_001.jpg") }}</figcaption>
</figure>"""

# Replace with original div-only version (no figcaption/孙温)
new = """<div class="poetry-banner">
</div>"""

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/templates/poems.html', 'w') as f:
        f.write(content)
    print('Removed Sun Wen image from poems.html')
else:
    print('Pattern not found')
    idx = content.find('sunwen')
    if idx >= 0:
        print('Found at', idx)
        print(repr(content[idx:idx+200]))
