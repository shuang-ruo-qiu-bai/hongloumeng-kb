#!/usr/bin/env python3
"""Fix the 鳷/鹊 split by directly editing poem_data.py lines."""
import ast

path = '/opt/hongloumeng/app/poems_data.py'
with open(path, 'r') as f:
    lines = f.readlines()

# Find the lines
for i, line in enumerate(lines):
    if '楼空鳷' in line:
        line1538 = i  # Python 0-indexed
        line1540 = i + 2
        print(f"Found '楼空鳷' at line {i+1}")
        break

# line1538 contains: '...委金钿于草莽，拾翠羽于尘埃。楼空鳷",\n'
# line1540 contains: '"",\n'
# line1541 (line1540+1) contains: '"鹊，徒悬七夕之针..."
# After merging: line1538 first part + '鹊' + line1541 remainder

l1538 = lines[line1538].rstrip('\n\r')
l1540 = lines[line1540].rstrip('\n\r')
l1541 = lines[line1540 + 1].rstrip('\n\r')

print(f"Line {line1538+1}: {l1538}")
print(f"Line {line1540+1}: {l1540}")
print(f"Line {line1540+2}: {l1541[:60]}...")

# Merge: remove trailing '",' from l1538, prepend '鹊' to l1541 content
# l1538 ends with '楼空鳷",'
# l1541 starts with '"鹊，徒悬...'
if l1538.endswith('",') and '楼空鳷' in l1538:
    base = l1538[:-2]  # remove '",'
    # l1541 starts with '"鹊'
    q_text = l1541.lstrip()
    if q_text.startswith('"鹊'):
        q_text = q_text[1:]  # remove leading '"'

    merged = base + '鹊' + q_text
    # Replace the three lines with one merged line
    indent = ' ' * 20
    lines[line1538] = indent + merged + '\n'
    # Remove the blank and the next line
    del lines[line1540]
    del lines[line1540]  # after deleting line1540, what was line1541 shifts up by 1

    print("After merge:")
    print(f"  {lines[line1538].strip()[:80]}...")

with open(path, 'w') as f:
    f.writelines(lines)

# Verify syntax
content = ''.join(lines)
ast.parse(content)
print("Syntax OK")
