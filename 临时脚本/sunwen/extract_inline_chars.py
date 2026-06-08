#!/usr/bin/env python3
"""Extract all inline images from EPUB with surrounding context."""
import zipfile, re, os

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

results = []
for n in sorted(names):
    if n.endswith('.html') or n.endswith('.xhtml'):
        content = z.read(n).decode('utf-8')
        # Match <img class="inline" ... /> patterns
        for m in re.finditer(r'<img[^>]*class="inline"[^>]*src="([^"]+)"[^>]*/>', content):
            src = m.group(1)
            idx = m.start()
            start = max(0, idx - 40)
            end = min(len(content), idx + len(m.group()) + 40)
            before = re.sub(r'<[^>]+>', '', content[start:idx]).strip()
            after = re.sub(r'<[^>]+>', '', content[idx+len(m.group()):end]).strip()
            results.append((n, src, before[-30:], after[:30]))

# Deduplicate by image file
seen = set()
for n, src, before, after in results:
    key = src
    if key not in seen:
        seen.add(key)
        ctx = (before + '【□】' + after).replace('\n', ' ').replace('\r', '')
        print(f"{src} | {ctx}")

# Also extract images to /tmp/inline_images/
outdir = '/tmp/inline_images'
os.makedirs(outdir, exist_ok=True)
count = 0
for name in names:
    if name.startswith('images/') and (name.endswith('.jpeg') or name.endswith('.jpg')):
        data = z.read(name)
        basename = os.path.basename(name)
        with open(os.path.join(outdir, basename), 'wb') as f:
            f.write(data)
        count += 1

print(f"\nExtracted {count} images to {outdir}/")
z.close()
