with open('/opt/hongloumeng/app/static/script.js') as f:
    lines = f.readlines()

open_count = 0
dom_lines = []
for i, line in enumerate(lines, 1):
    if 'DOMContentLoaded' in line:
        open_count += 1
        dom_lines.append(i)
    if line.strip().endswith('});'):
        close_count = 0
        # count close parens
    s = line.strip()
    if s == '});':
        close_count += 1
        dom_lines.append(i)

print(f"Total lines: {len(lines)}")
print(f"DOMContentLoaded found at lines: {[l for l in dom_lines if 'DOMContentLoaded' in lines[l-1]]}")
print(f"}); at lines: {[l for l in dom_lines if lines[l-1].strip() == '});'}")
