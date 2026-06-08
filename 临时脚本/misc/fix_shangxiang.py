#!/usr/bin/env python3
"""Fix 尚飨 missing exclamation mark."""
path = '/opt/hongloumeng/app/poems_data.py'
with open(path, 'r') as f:
    content = f.read()

old = '"呜呼哀哉！尚飨",'
new = '"呜呼哀哉！尚飨！",'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    import ast
    ast.parse(content)
    print('Fixed: added ！ after 尚飨')
else:
    print('Pattern not found')
    idx = content.find('尚飨')
    if idx >= 0:
        print(repr(content[idx:idx+30]))
