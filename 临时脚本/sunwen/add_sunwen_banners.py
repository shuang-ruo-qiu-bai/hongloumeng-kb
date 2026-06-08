#!/usr/bin/env python3
"""Add decorative Sun Wen banners with captions to key pages."""
import re

# Canon page: add banner after canon-header
with open('/opt/hongloumeng/app/templates/canon.html', 'r') as f:
    canon = f.read()

old_canon = '    <p class="page-subtitle">中国艺术研究院《红楼梦》校注本 · 脂评汇校本</p>\n</div>'
new_canon = old_canon + """

<figure class="page-banner">
    <img src="/static/sunwen/sunwen_003.jpg" alt="孙温绘《红楼梦》" loading="lazy">
    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_003.jpg") }}</figcaption>
</figure>"""

if old_canon in canon:
    canon = canon.replace(old_canon, new_canon)
    with open('/opt/hongloumeng/app/templates/canon.html', 'w') as f:
        f.write(canon)
    print('canon.html: added sunwen_003')
else:
    print('canon.html: pattern not found')

# Editions page: add banner after page-header
with open('/opt/hongloumeng/app/templates/editions.html', 'r') as f:
    editions = f.read()

old_editions = '</div>\n\n<div class="edition-intro">'
new_editions = '</div>\n\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_060.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_060.jpg") }}</figcaption>\n</figure>\n\n<div class="edition-intro">'

if old_editions in editions:
    editions = editions.replace(old_editions, new_editions)
    with open('/opt/hongloumeng/app/templates/editions.html', 'w') as f:
        f.write(editions)
    print('editions.html: added sunwen_060')
else:
    print('editions.html: pattern not found')

# History page: add banner after page-header
with open('/opt/hongloumeng/app/templates/history.html', 'r') as f:
    history = f.read()

old_history = '</div>\n\n<div class="timeline-container">'
new_history = '</div>\n\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_010.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_010.jpg") }}</figcaption>\n</figure>\n\n<div class="timeline-container">'

if old_history in history:
    history = history.replace(old_history, new_history)
    with open('/opt/hongloumeng/app/templates/history.html', 'w') as f:
        f.write(history)
    print('history.html: added sunwen_010')
else:
    print('history.html: pattern not found')
    idx = history.find('timeline-container')
    if idx >= 0:
        print('  Found timeline-container at', idx)

# Customs page: add banner after page-header
with open('/opt/hongloumeng/app/templates/customs.html', 'r') as f:
    customs = f.read()

old_customs = '</div>\n\n<!-- Book intro -->'
new_customs = '</div>\n\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_037.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_037.jpg") }}</figcaption>\n</figure>\n\n<!-- Book intro -->'

if old_customs in customs:
    customs = customs.replace(old_customs, new_customs)
    with open('/opt/hongloumeng/app/templates/customs.html', 'w') as f:
        f.write(customs)
    print('customs.html: added sunwen_037')
else:
    print('customs.html: pattern not found')
