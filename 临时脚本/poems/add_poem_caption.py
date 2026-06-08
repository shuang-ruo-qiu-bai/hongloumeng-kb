#!/usr/bin/env python3
"""Add Sun Wen caption to poems.html."""
with open('/opt/hongloumeng/app/templates/poems.html', 'r') as f:
    content = f.read()

old = """<div class="poetry-banner">
    <img src="/static/sunwen/sunwen_001.jpg" alt="孙温绘《红楼梦》" loading="lazy">
</div>"""

new = """<figure class="poetry-banner">
    <img src="/static/sunwen/sunwen_001.jpg" alt="孙温绘《红楼梦》" loading="lazy">
    <figcaption class="sunwen-caption">{{ sunwen_captions.get("sunwen_001.jpg", "") }}</figcaption>
</figure>"""

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/templates/poems.html', 'w') as f:
        f.write(content)
    print('Added caption to poems.html')
else:
    print('ERROR: old content not found')
    # Debug
    idx = content.find('poetry-banner')
    if idx >= 0:
        print('Found poetry-banner at', idx)
        print(content[idx:idx+200])
