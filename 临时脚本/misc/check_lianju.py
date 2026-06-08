#!/usr/bin/env python3
import json
with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    content = f.read()
exec_vars = {}
exec(compile(content, 'poems_data.py', 'exec'), exec_vars)
cats = exec_vars['POEM_CATEGORIES']

# Show ALL 联句 lines
for cat in cats:
    for poem in cat['poems']:
        if '联句' in poem['title']:
            print(f"\n=== {poem['title']} ===")
            for i, line in enumerate(poem['lines']):
                print(f"  [{i:2d}] {line}")
