"""Extract 120-chapter 红楼梦 EPUB with proper note/character handling."""
import zipfile, json, re

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
DST  = '/opt/hongloumeng/app/novel_data.json'

z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

# Read NCX
ncx_content = None
for n in names:
    if n.endswith('.ncx'):
        ncx_content = z.read(n).decode('utf-8')
        break

# Parse NCX chapter entries
chapters = []
pattern = re.compile(r'<text>(第[^<]*回[^<]*)</text>\s*</navLabel>\s*<content\s+src="([^"]+)"/>')
for title, href in pattern.findall(ncx_content):
    chapters.append({'href': href, 'title': title.strip()})

def clean_text(html):
    # Remove scripts and styles
    html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    html = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    html = re.sub(r'<!--.*?-->', '', html, flags=re.DOTALL)
    
    # Replace inline images (rare chars) with their alt text or placeholder
    # These are <img class="inline"> for rare Chinese characters
    def _replace_img(m):
        alt = m.group(1) or ''
        return alt if alt else '□'
    # Match any img tag, trying to capture alt text
    html = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', _replace_img, html)
    html = re.sub(r'<img[^>]*>', '', html)
    
    # Fix PUA character  (U+E13D) - represents the "g" part of "ng" in pinyin phonetic notation
    # EPUB text: làn +  = làng, hén +  = héng, etc.
    html = html.replace('', 'g')
    
    # Convert block-level tags to newlines
    html = re.sub(r'</?(?:p|div|h[1-6]|blockquote|li|table|tr|aside)[^>]*>', '\n', html)
    html = re.sub(r'<br\s*/?>', '\n', html)
    
    # Remove all remaining HTML tags
    html = re.sub(r'<[^>]+>', '', html)
    
    # Decode HTML entities
    html = html.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<')
    html = html.replace('&gt;', '>').replace('&quot;', '"').replace('&#39;', "'")
    html = html.replace('&mdash;', '—').replace('&hellip;', '…')
    
    # Handle common entity patterns like &#xNNNN;
    html = re.sub(r'&#x([0-9a-fA-F]+);', lambda m: chr(int(m.group(1), 16)), html)
    html = re.sub(r'&#(\d+);', lambda m: chr(int(m.group(1))), html)
    
    # Normalize whitespace
    html = re.sub(r'[ \t]+', ' ', html)
    html = re.sub(r'\n\s*\n\s*\n+', '\n\n', html)
    
    return html.strip()

NUM_MAP = {
    '一': 1, '二': 2, '三': 3, '四': 4, '五': 5,
    '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
    '○': 0, '〇': 0, '零': 0,
}

def parse_cn(s):
    s = s.strip()
    if s in NUM_MAP:
        return NUM_MAP[s]
    if '十' in s:
        parts = s.split('十')
        tens = parse_cn(parts[0]) if parts[0] else 1
        ones = parse_cn(parts[1]) if parts[1] and parts[1] in NUM_MAP else 0
        return tens * 10 + ones
    total = 0
    for c in s:
        if c in NUM_MAP:
            total = total * 10 + NUM_MAP[c]
    return total if total > 0 else 0

result = []
for ch in chapters:
    href = ch['href']
    content = None
    for path in [href, 'text/' + href, 'Text/' + href]:
        if path in names:
            content = z.read(path).decode('utf-8')
            break
    if content is None:
        print(f"  MISSING: {href} ({ch['title']})")
        continue

    text = clean_text(content)
    if not text:
        print(f"  EMPTY: {ch['title']}")
        continue

    title = ch['title']
    cm = re.match(r'第(.+?)回(?:至(?:第)?(.+?)回)?', title)
    if not cm:
        print(f"  PARSE FAIL: {title}")
        continue

    cn_first = parse_cn(cm.group(1))
    cn_second = parse_cn(cm.group(2)) if cm.group(2) else None

    if cn_second:
        for n in range(cn_first, cn_second + 1):
            result.append({'num': n, 'title': title, 'content': text})
        print(f"  Ch {cn_first}-{cn_second}: {title} ({len(text)} chars)")
    else:
        result.append({'num': cn_first, 'title': title, 'content': text})
        if cn_first <= 3 or cn_first == 80 or cn_first >= 118:
            print(f"  Ch {cn_first}: {title} ({len(text)} chars)")

z.close()

result.sort(key=lambda x: x['num'])
print(f"\nTotal: {len(result)} chapter entries")

nums = [ch['num'] for ch in result]
missing = [n for n in range(1, 121) if n not in nums]
if missing:
    print(f"MISSING: {missing}")
else:
    print("All 120 chapters complete!")

with open(DST, 'w', encoding='utf-8') as f:
    json.dump({'chapters': result}, f, ensure_ascii=False, indent=2)
print(f"Saved to {DST}")
