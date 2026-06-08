"""Rewrite _parse_chapter_notes in app.py with proper newlines."""
import re

with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

# Define the replacement function with proper newlines using chr(10)
NL = chr(10)

new_fn = f'''
def _parse_chapter_notes(content):
    """Separate main text from footnotes.
    Returns (main_text, arabic_notes_list, chinese_notes_list).
    """
    lines = content.split({NL!r})
    note_start = len(lines)
    for i in range(len(lines) - 1, -1, -1):
        s = lines[i].strip()
        if not s:
            continue
        if re.match(r"^\\[\\d+\\]", s) or re.match(r"^[\\u3002\\u3014\\]", s):
            note_start = i
        else:
            break
    for i in range(note_start - 1, -1, -1):
        s = lines[i].strip()
        if re.match(r"^\\[\\d+\\]", s) or re.match(r"^[\\u3002\\u3014\\]", s):
            note_start = i
        else:
            break

    main_text = NL.join(lines[:note_start]).strip()
    note_lines = lines[note_start:]

    arabic = {{}}
    chinese = {{}}
    cur_type = None
    cur_key = None
    cur_parts = []

    for line in note_lines:
        s = line.strip()
        ma = re.match(r"^\\[(\\d+)\\]\\s*(.*)", s)
        mc = re.match(r"^[\\u3002\\u3014]([一二三四五六七八九十百零○]+)[\\u3003\\u3015]\\s*(.*)", s)
        if ma:
            if cur_key is not None and cur_parts:
                t = NL.join(cur_parts).strip()
                if cur_type == "arabic":
                    arabic[cur_key] = t
                else:
                    chinese[cur_key] = t
            cur_type = "arabic"
            cur_key = int(ma.group(1))
            cur_parts = [ma.group(2)] if ma.group(2) else []
        elif mc:
            if cur_key is not None and cur_parts:
                t = NL.join(cur_parts).strip()
                if cur_type == "arabic":
                    arabic[cur_key] = t
                else:
                    chinese[cur_key] = t
            cur_type = "chinese"
            cur_key = mc.group(1)
            cur_parts = [mc.group(2)] if mc.group(2) else []
        elif cur_key is not None:
            cur_parts.append(s) if s else cur_parts.append("")

    if cur_key is not None and cur_parts:
        t = NL.join(cur_parts).strip()
        if cur_type == "arabic":
            arabic[cur_key] = t
        else:
            chinese[cur_key] = t

    arabic_list = sorted([{{"num": k, "text": v}} for k, v in arabic.items()], key=lambda x: x["num"])
    chinese_list = sorted([{{"num": k, "text": v}} for k, v in chinese.items()],
        key=lambda x: sum(int(c) if c.isdigit() else max(0, "一二三四五六七八九十百零○".find(c)) for c in x["num"]))

    return main_text, arabic_list, chinese_list
'''

# Replace the old function
old_start = content.find('def _parse_chapter_notes(content):')
if old_start >= 0:
    # Find the next function or end of file
    rest = content[old_start:]
    # Find the next def at the same indentation level
    next_def = re.search(r'\n(?=def |@app\.route|\n#)', rest)
    if next_def:
        end = old_start + next_def.start()
    else:
        end = len(content)

    before = content[:old_start]
    after = content[end:]
    content = before + new_fn + after

    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    print(f'Replaced _parse_chapter_notes successfully')
else:
    print('_parse_chapter_notes not found!')
