#!/usr/bin/env python3
"""Fix poems_data.py: split 联句 3-line entry, add speakers, fix furong format."""
import re

with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    content = f.read()

# === Fix 1: Split 芦雪广 line 18 into 3 separate lines ===
old = '                    "锦罽暖亲猫。月窟翻银浪，霞城隐赤标。",'
new = '''                    "锦罽暖亲猫。",
                    "月窟翻银浪，",
                    "霞城隐赤标。",'''
assert old in content, "Line 18 not found!"
content = content.replace(old, new)

# === Fix 2: Add speaker notes to 芦雪广 ===
# Each speaker note as a comment above the line
# Line 17 (before split) = "埋琴稚子挑，石楼闲睡鹤。"
old_line17 = '                    "埋琴稚子挑，石楼闲睡鹤。",'
new_line17 = '                    "埋琴稚子挑（宝琴），石楼闲睡鹤（湘云）。",'
content = content.replace(old_line17, new_line17)

# === Fix 3: Add speaker_notes field to the lianju poem ===
# Insert after "lines" array closes
old_close = '''                ],
            },
            {'''
# Find the right insertion point - after the 芦雪广 poem's lines array
# Look for this pattern: the "芦雪广" lines array closing, then the next poem
import re as re2
idx = content.find('"芦雪广即景联句（节选）"')
# Find the end of this poem's dict
lines_end = content.find('"芦雪广即景联句（节选）"')
lines_end = content.find('[' , lines_end)
lines_end = content.find(']' , lines_end)
lines_end = content.find('],', lines_end)
if lines_end > 0:
    # Add speaker_notes field after the lines array
    notes = ''',
                "speaker_notes": [
                    "凤姐起句，李纨续",
                    "香菱",
                    "探春",
                    "李绮",
                    "李纹",
                    "岫烟",
                    "湘云",
                    "宝琴",
                    "黛玉",
                    "宝玉",
                    "宝钗",
                    "湘云",
                    "宝琴",
                    "湘云",
                    "宝钗",
                    "黛玉",
                    "宝玉",
                    "宝琴起，湘云续",
                    "湘云",
                    "黛玉",
                    "宝琴",
                    "湘云",
                    "黛玉",
                    "宝钗",
                    "宝琴",
                    "湘云",
                    "李纨收，李绮续",
                ]'''
    content = content[:lines_end+1] + notes + content[lines_end+1:]
    print("Added speaker_notes to lianju")
else:
    print("ERROR: Could not find lines array end")

# === Fix 4: Add speaker_notes to 中秋夜大观园联句 ===
mid_lines_end = content.find('"中秋夜大观园即景联句三十五韵（节选）"')
mid_lines_end = content.find('[', mid_lines_end)
mid_lines_end = content.find(']', mid_lines_end)
mid_lines_end = content.find('],', mid_lines_end)
if mid_lines_end > 0:
    mid_notes = ''',
                "speaker_notes": [
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                    "黛玉",
                    "湘云",
                ]'''
    content = content[:mid_lines_end+1] + mid_notes + content[mid_lines_end+1:]
    print("Added speaker_notes to 中秋联句")
else:
    print("ERROR: Could not find 中秋 lines array end")

# === Fix 5: Mark 芙蓉女儿诔 prose sections ===
# Find 芙蓉女儿诔 lines array and add line_types
furong_idx = content.find('"芙蓉女儿诔"')
furong_start = content.find('[', furong_idx)
furong_end = content.find(']', furong_start)
furong_close = content.find('],', furong_end)
if furong_close > 0:
    line_types = ''',
                "line_types": [
                    "prose", "prose", "prose", "prose", "",
                    "prose", "prose", "",
                    "prose", "prose", "prose", "prose", "prose", "",
                    "verse", "verse", "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse", "verse", "",
                    "verse", "verse", "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "verse",
                    "verse", "verse", "verse", "",
                    "verse", "",
                    "verse", "verse", "verse", "verse",
                    "",
                    "verse", "",
                ]'''
    content = content[:furong_close+1] + line_types + content[furong_close+1:]
    print("Added line_types to furong")
else:
    print("ERROR: Could not find furong lines array end")

# === Fix 6: Update poems.html template to handle speaker_notes and line_types ===
# Read template
with open('/opt/hongloumeng/app/templates/poems.html', 'r') as f:
    tpl = f.read()

# Update the poem card text rendering
old_render = '                    <div class="poem-card-text">{% for line in poem.lines %}{% if line %}<span class="poem-line">{{ line }}</span>{% else %}<span class="poem-break"></span>{% endif %}{% endfor %}</div>'

new_render = '''                    <div class="poem-card-text">{% for line in poem.lines %}
                        {%- set line_idx = loop.index0 -%}
                        {%- if poem.line_types is defined and poem.line_types[line_idx] is defined and poem.line_types[line_idx] == "prose" -%}
                            <p class="prose-line">{{ line }}</p>
                        {%- elif poem.speaker_notes is defined and poem.speaker_notes[line_idx] is defined and poem.speaker_notes[line_idx] -%}
                            {%- if line -%}
                                <span class="poem-line"><span class="poem-speaker">{{ poem.speaker_notes[line_idx] }}</span>{{ line }}</span>
                            {%- else -%}
                                <span class="poem-break"></span>
                            {%- endif -%}
                        {%- else -%}
                            {%- if line -%}
                                <span class="poem-line">{{ line }}</span>
                            {%- else -%}
                                <span class="poem-break"></span>
                            {%- endif -%}
                        {%- endif -%}
                    {%- endfor %}</div>'''

if old_render in tpl:
    tpl = tpl.replace(old_render, new_render)
    with open('/opt/hongloumeng/app/templates/poems.html', 'w') as f:
        f.write(tpl)
    print("Updated poems.html template")
else:
    print("ERROR: Old template render not found")
    # Debug: show what we have
    import re as re3
    m = re3.search(r'poem-card-text.*?</div>', tpl, re3.DOTALL)
    if m:
        print("Found render:", m.group()[:200])

# Add CSS for speaker names and prose lines
old_css_end = '</style>'
new_css = '''/* Speaker names in 联句 */
.poem-card-text .poem-speaker {
    font-size: 0.75em;
    color: var(--zhusha);
    font-family: var(--font-cite);
    margin-right: 0.4em;
    white-space: nowrap;
}
/* Prose lines in poems (e.g. 芙蓉女儿诔 preface) */
.poem-card-text .prose-line {
    text-indent: 2em;
    margin-bottom: 0.3em;
    line-height: 2.1;
}
/* Override for the prose-line to display as block with proper spacing */
.poem-card-text .prose-line {
    display: block;
}
'''
tpl = tpl.replace(old_css_end, new_css + '\n' + old_css_end)
with open('/opt/hongloumeng/app/templates/poems.html', 'w') as f:
    f.write(tpl)
print("Added CSS for speaker/prose")

# Write modified poems_data.py
with open('/opt/hongloumeng/app/poems_data.py', 'w') as f:
    f.write(content)
print("Saved poems_data.py")
