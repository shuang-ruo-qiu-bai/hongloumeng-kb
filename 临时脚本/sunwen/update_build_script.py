#!/usr/bin/env python3
"""Modify build_120_v3.py to use character map."""
import ast

with open('/tmp/build_120_v3.py', 'r') as f:
    content = f.read()

# 1. Add os import
old_imports = 'import zipfile, json, re'
new_imports = 'import zipfile, json, re, os'
content = content.replace(old_imports, new_imports)

# 2. Add char map loading after DST definition
old_dst = "DST  = '/opt/hongloumeng/app/novel_data.json'"
new_dst = """DST  = '/opt/hongloumeng/app/novel_data.json'

# Load inline character mapping
CHAR_MAP_PATH = '/tmp/inline_char_map.json'
if os.path.exists(CHAR_MAP_PATH):
    CHAR_MAP = json.load(open(CHAR_MAP_PATH, 'r'))
    print('Loaded %d char mappings from %s' % (len(CHAR_MAP), CHAR_MAP_PATH))
else:
    CHAR_MAP = {}
    print('WARNING: No char map found, will use fallback')"""
content = content.replace(old_dst, new_dst)

# 3. Replace the inline image replacement function
old_img_func = """    # Replace inline images (rare chars) with their alt text or placeholder
    # These are <img class="inline"> for rare Chinese characters
    def _replace_img(m):
        alt = m.group(1) or ''
        return alt if alt else '□'
    # Match any img tag, trying to capture alt text
    html = re.sub(r'<img[^>]*alt="([^"]*)"[^>]*>', _replace_img, html)
    html = re.sub(r'<img[^>]*>', '', html)"""

new_img_func = """    # Replace inline images with proper characters from character map
    def _replace_img(m):
        tag = m.group(0)
        src_m = re.search(r'src="([^"]+)"', tag)
        if src_m:
            fname = src_m.group(1).split('/')[-1]
            if fname in CHAR_MAP:
                return CHAR_MAP[fname]
        # Fallback: use alt text
        alt_m = re.search(r'alt="([^"]*)"', tag)
        if alt_m and alt_m.group(1):
            return alt_m.group(1)
        return chr(0xFFFD)  # replacement character as fallback

    # Handle all img tags in one pass
    html = re.sub(r'<img[^>]*>', _replace_img, html)"""

content = content.replace(old_img_func, new_img_func)

# 4. Add replacement char count check before saving
old_save = "with open(DST, 'w', encoding='utf-8') as f:"
new_save = """# Check for remaining replacement chars
all_text = ''.join(ch['content'] for ch in result)
replacement_count = all_text.count(chr(0xFFFD))
print('Remaining replacement chars (U+FFFD): %d' % replacement_count)

with open(DST, 'w', encoding='utf-8') as f:"""

content = content.replace(old_save, new_save)

with open('/tmp/build_120_v3.py', 'w') as f:
    f.write(content)

print('Updated build_120_v3.py successfully')

# Verify syntax
ast.parse(content)
print('Syntax check: OK')
