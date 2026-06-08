#!/usr/bin/env python3
"""Deep investigation of note numbering in EPUB."""
import zipfile, re, json

EPUB = '/opt/hongloumeng/books/红楼梦/原著/红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub'
z = zipfile.ZipFile(EPUB, 'r')
names = z.namelist()

# Load novel_data.json to find chapters with gaps
with open('/opt/hongloumeng/app/novel_data.json', 'r') as f:
    novel = json.load(f)

# Find all chapters
# Read NCX
ncx = None
for n in names:
    if n.endswith('.ncx'):
        ncx = z.read(n).decode('utf-8')
        break

ch_pattern = re.compile(r'<text>(第[^<]*回[^<]*)</text>\s*</navLabel>\s*<content\s+src="([^"]+)"/>')
chapters = []
for title, href in ch_pattern.findall(ncx):
    chapters.append({'href': href, 'title': title.strip()})

print(f"Total chapters in NCX: {len(chapters)}")

# For each chapter, check:
# 1. Arabic [N] markers in body text
# 2. Chinese 〔N〕 markers in body text
# 3. Arabic [N] definitions in note section
# 4. Chinese 〔N〕 definitions in note section
# 5. Number sequence gaps

def extract_from_html(content):
    """Extract all note markers and definitions from HTML."""
    # Body note markers: <a id="wN">...</a> containing [N] or some text
    body_arabic = set()
    body_chinese = set()

    # Find all [N] patterns in text (not in definition section)
    # Definition section starts with <p class="note">
    note_section = False

    # Split by note paragraphs
    parts = re.split(r'<p class="note"[^>]*>', content)
    body_text = parts[0]  # Everything before first note definition

    # Arabic markers [N] in body
    for m in re.finditer(r'\[(\d+)\]', body_text):
        # Check it's a real marker (not inside another tag or style)
        pos = m.start()
        context = body_text[max(0,pos-50):pos+50]
        # Skip if inside a style or script tag
        if '<style' in context or '<script' in context:
            continue
        # It's a note reference if following some Chinese text or preceded by id
        body_arabic.add(int(m.group(1)))

    # Chinese markers 〔N〕 in body
    for m in re.finditer(r'[〔\[]([一二三四五六七八九十百零○〇]+)[〕\]\)]', body_text):
        pos = m.start()
        context = body_text[max(0,pos-50):pos+50]
        if '<style' in context or '<script' in context:
            continue
        body_chinese.add(m.group(1))

    # Now extract definitions from note paragraphs
    note_sections = re.findall(r'<p class="note"[^>]*>(.*?)</p>', content, re.DOTALL)

    def_arabic = set()
    def_chinese = set()

    for ns in note_sections:
        # Strip HTML for text content
        text = re.sub(r'<[^>]+>', '', ns).strip()
        # Arabic definition: [N]
        m = re.match(r'\[(\d+)\]', text)
        if m:
            def_arabic.add(int(m.group(1)))
        # Chinese definition: 〔N〕
        m = re.match(r'[〔\[]([一二三四五六七八九十百零○〇]+)[〕\]\)]', text)
        if m:
            def_chinese.add(m.group(1))

    return body_arabic, body_chinese, def_arabic, def_chinese

# Check all chapters
gaps_summary = []
for ch in chapters:
    href = ch['href']
    content = None
    for path in [href, 'text/' + href, 'Text/' + href]:
        if path in names:
            content = z.read(path).decode('utf-8')
            break
    if not content:
        continue

    body_arabic, body_chinese, def_arabic, def_chinese = extract_from_html(content)

    # Check gaps
    if def_arabic:
        expected = set(range(min(def_arabic), max(def_arabic) + 1))
        missing = expected - def_arabic
        extra = def_arabic - expected
        if missing:
            gaps_summary.append({
                'ch': ch,
                'body_arabic': sorted(body_arabic),
                'def_arabic': sorted(def_arabic),
                'missing': sorted(missing),
                'body_chinese': sorted(body_chinese),
                'def_chinese': sorted(def_chinese),
            })

# Print chapters with gaps
print(f"\nChapters with gaps in Arabic notes: {len(gaps_summary)}")
for g in gaps_summary:
    cm = re.search(r'第(.+?)回', g['ch']['title'])
    ch_num = cm.group(1) if cm else '?'
    print(f"\n=== Chapter {ch_num}: {g['ch']['title']} ===")
    print(f"  Body [N]: {g['body_arabic']}")
    print(f"  Def [N]: {g['def_arabic']}")
    print(f"  MISSING: {g['missing']}")
    print(f"  Chinese notes: body={g['body_chinese']}, def={g['def_chinese']}")

z.close()
