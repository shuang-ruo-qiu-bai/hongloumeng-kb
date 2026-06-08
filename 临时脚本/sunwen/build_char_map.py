#!/usr/bin/env python3
"""Build character mapping from EPUB inline image contexts."""
import zipfile, re, json

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

results = []
for n in sorted(names):
    if not (n.endswith('.html') or n.endswith('.xhtml')):
        continue
    content = z.read(n).decode('utf-8')
    for m in re.finditer(r'<img[^>]*class="inline"[^>]*src="([^"]+)"[^>]*/>', content):
        src = m.group(1)
        idx = m.start()
        start = max(0, idx - 60)
        end = min(len(content), idx + len(m.group()) + 80)
        before = re.sub(r'<[^>]+>', '', content[start:idx]).strip()
        after = re.sub(r'<[^>]+>', '', content[idx+len(m.group()):end]).strip()
        fname = src.split('/')[-1]
        results.append({'file': fname, 'before': before[-40:], 'after': after[:40]})

# Deduplicate by file
seen = set()
unique = []
for r in results:
    if r['file'] not in seen:
        seen.add(r['file'])
        unique.append(r)

print(f"Total unique inline images: {len(unique)}")

for r in unique:
    print(f"{r['file']} | {r['before']}【□】{r['after']}")

z.close()
