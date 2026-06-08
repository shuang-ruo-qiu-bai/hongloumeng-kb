#!/usr/bin/env python3
"""Update poems.html to use global sunwen_caption helper."""
with open('/opt/hongloumeng/app/templates/poems.html', 'r') as f:
    content = f.read()

old = '    <figcaption class="sunwen-caption">{{ sunwen_captions.get("sunwen_001.jpg", "") }}</figcaption>'
new = '    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_001.jpg") }}</figcaption>'

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/templates/poems.html', 'w') as f:
        f.write(content)
    print('Updated poems.html to use global helper')
else:
    print('Old text not found, checking...')
    idx = content.find('sunwen-caption')
    if idx >= 0:
        print('Found at', idx)
        print(content[idx:idx+100])
