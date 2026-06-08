#!/usr/bin/env python3
import json
with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    content = f.read()
exec_vars = {}
exec(compile(content, 'poems_data.py', 'exec'), exec_vars)
cats = exec_vars['POEM_CATEGORIES']
for cat in cats:
    for poem in cat['poems']:
        if '芙蓉' in poem['title']:
            print("Total lines:", len(poem['lines']))
            print("-- Lines 45-65 --")
            for i, line in enumerate(poem['lines'][45:66], 45):
                print(f"  [{i}] {line[:100]}")
