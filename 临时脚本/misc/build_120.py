"""Extract 120-chapter 红楼梦 EPUB --> novel_data.json"""
import zipfile, json, re, os

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
DST  = '/opt/hongloumeng/app/novel_data.json'

z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

# Read nav.xhtml for chapter structure
nav = None
for n in names:
    if 'nav' in n.lower():
        nav = z.read(n).decode('utf-8')
        break

if not nav:
    # Try finding toc
    for n in names:
        if 'toc' in n.lower():
            nav = z.read(n).decode('utf-8')
            break

print(f"Nav content length: {len(nav) if nav else 0}")

# Extract chapter links from nav - look for patterns like:
# <a href="...">第X回 ...</a>
chapters = []
if nav:
    # Find all links with chapter patterns
    pattern = re.compile(r'<a[^>]*href=["\']([^"\']+)["\']>\s*(第[一二三四五六七八九十百零]+回[^<]*)\s*</a>')
    matches = pattern.findall(nav)
    print(f"Found {len(matches)} chapters via pattern 1")

    if len(matches) < 80:
        # Try broader pattern
        pattern2 = re.compile(r'<a[^>]*href=["\']([^"\']+)["\']>([^<]*第[一二三四五六七八九十百零]+回[^<]*)</a>')
        matches = pattern2.findall(nav)
        print(f"Found {len(matches)} chapters via pattern 2")

    if len(matches) < 80:
        # Just find all links
        all_links = re.findall(r'<a[^>]*href=["\']([^"\']+)["\']>([^<]+)</a>', nav)
        print(f"All links: {len(all_links)}")
        # Filter for chapter-like links
        matches = [(h, t) for h, t in all_links if '回' in t]
        print(f"Chapter links: {len(matches)}")

    for href, title in matches:
        chapters.append({'href': href, 'title': title.strip()})

print(f"\nTotal chapters to extract: {len(chapters)}")
for i, ch in enumerate(chapters[:5]):
    print(f"  {i+1}. {ch['title']} -> {ch['href']}")
if len(chapters) > 5:
    print(f"  ...")
    for ch in chapters[-3:]:
        print(f"  {ch['title']} -> {ch['href']}")

# Now extract content from each chapter
def strip_html(html):
    """Strip HTML tags and clean up text."""
    # Remove script and style
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    # Remove comments
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    # Block-level tags to newline
    html = re.sub(r'</?(p|div|h[1-6]|blockquote|li)[^>]*>', '\n', html)
    # br to newline
    html = re.sub(r'<br\s*/?>', '\n', html)
    # Remove all other tags
    html = re.sub(r'<[^>]+>', '', html)
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    # Normalize whitespace
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n\s*\n+', '\n\n', html)
    return html.strip()

def get_chapter_number(title):
    """Extract chapter number from title like '第一回' or '第八十回'."""
    m = re.match(r'第(.+?)回', title)
    if not m:
        return 0
    cn = m.group(1)
    num_map = {
        '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
        '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    }
    if cn in num_map:
        return num_map[cn]
    elif '十' in cn:
        parts = cn.split('十')
        tens = num_map.get(parts[0], 1) if parts[0] else 1
        ones = num_map.get(parts[1], 0) if parts[1] else 0
        return tens * 10 + ones
    return 0

result = []
for ch in chapters:
    # Resolve href relative to EPUB root
    href = ch['href']
    if href.startswith('Text/') or href.startswith('text/'):
        pass  # Already correct
    # Read the file
    try:
        content = z.read(href).decode('utf-8')
    except:
        # Try with common prefixes
        found = False
        for prefix in ['', 'Text/', 'text/', 'OEBPS/', 'OEBPS/Text/']:
            try:
                content = z.read(prefix + href).decode('utf-8')
                found = True
                break
            except:
                continue
        if not found:
            print(f"  WARNING: Cannot read {href}")
            continue

    # Strip HTML
    text = strip_html(content)
    if not text:
        print(f"  WARNING: Empty content for {ch['title']}")
        continue

    num = get_chapter_number(ch['title'])
    if num == 0:
        num = len(result) + 1  # fallback

    result.append({
        'num': num,
        'title': ch['title'],
        'content': text
    })
    if num <= 3 or num > 115:
        print(f"  Ch {num}: {ch['title']} ({len(text)} chars)")

z.close()

# Sort by chapter number
result.sort(key=lambda x: x['num'])
print(f"\nTotal extracted: {len(result)} chapters")
if result:
    print(f"First: Ch{result[0]['num']} {result[0]['title']}")
    print(f"Last: Ch{result[-1]['num']} {result[-1]['title']}")

# Validate we have all 120
nums = sorted([ch['num'] for ch in result])
expected = list(range(1, 121))
missing = [n for n in expected if n not in nums]
if missing:
    print(f"MISSING chapters: {missing}")
else:
    print("All 120 chapters complete!")

# Save
json_out = json.dumps({'chapters': result}, ensure_ascii=False, indent=2)
with open(DST, 'w', encoding='utf-8') as f:
    f.write(json_out)
print(f"\nSaved to {DST} ({len(json_out)} bytes)")
