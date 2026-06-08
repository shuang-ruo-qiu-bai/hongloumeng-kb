#!/usr/bin/env python3
"""Fix the 鳷/鹊 split in poems_data.py."""
import ast

path = '/opt/hongloumeng/app/poems_data.py'
with open(path, 'r') as f:
    content = f.read()

old = '"委金钿于草莽，拾翠羽于尘埃。楼空鳷",\n                    "",\n                    "鹊，徒悬七夕之针'
new = '"委金钿于草莽，拾翠羽于尘埃。楼空鳷鹊，徒悬七夕之针'
content = content.replace(old, new)

with open(path, 'w') as f:
    f.write(content)

ast.parse(content)
print("Fixed and syntax OK")
