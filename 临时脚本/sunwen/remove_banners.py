#!/usr/bin/env python3
"""Remove all Sun Wen decorative banners I incorrectly added."""
import re

files_to_fix = {
    'canon.html': (
        '\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_003.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_003.jpg") }}</figcaption>\n</figure>\n\n<!-- Chapter list (回目 grid) -->',
        '\n\n<!-- Chapter list (回目 grid) -->'
    ),
    'editions.html': (
        '\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_060.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_060.jpg") }}</figcaption>\n</figure>\n\n<div class="edition-intro">',
        '\n\n<div class="edition-intro">'
    ),
    'customs.html': (
        '\n<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_037.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_037.jpg") }}</figcaption>\n</figure>\n\n<!-- Book intro -->',
        '\n\n<!-- Book intro -->'
    ),
    'history.html': (
        '<figure class="page-banner">\n    <img src="/static/sunwen/sunwen_010.jpg" alt="孙温绘《红楼梦》" loading="lazy">\n    <figcaption class="sunwen-caption">{{ sunwen_caption("sunwen_010.jpg") }}</figcaption>\n</figure>\n\n',
        ''
    ),
}

for fname, (old, new) in files_to_fix.items():
    path = '/opt/hongloumeng/app/templates/' + fname
    with open(path, 'r') as f:
        content = f.read()
    if old in content:
        content = content.replace(old, new)
        with open(path, 'w') as f:
            f.write(content)
        print(fname + ': removed banner')
    else:
        print(fname + ': pattern not found')
        # Partial match check
        idx = content.find('page-banner')
        if idx >= 0:
            print('  Found "page-banner" at', idx)
            print(repr(content[idx:idx+150]))
