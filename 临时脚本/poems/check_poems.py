#!/usr/bin/env python3
import json
with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    content = f.read()
exec_vars = {}
exec(compile(content, 'poems_data.py', 'exec'), exec_vars)
cats = exec_vars['POEM_CATEGORIES']

for cat in cats:
    for poem in cat['poems']:
        if '芙蓉' in poem['title'] and '诔' in poem['title']:
            print("Title:", poem['title'])
            print("Chapter:", poem['chapter'])
            print("Author:", poem.get('author',''))
            print("Total lines:", len(poem['lines']))
            print()
            print("-- First 20 lines --")
            for i, line in enumerate(poem['lines'][:20]):
                print(f"  [{i}] {repr(line[:80])}")
            print()
            print("-- Lines 28-45 --")
            for i, line in enumerate(poem['lines'][28:45], 28):
                print(f"  [{i}] {repr(line[:80])}")
        if '联句' in poem['title']:
            print()
            print("--- LIANJU ---")
            print("Title:", poem['title'])
            print("Total lines:", len(poem['lines']))
            print("-- First 20 lines --")
            for i, line in enumerate(poem['lines'][:20]):
                print(f"  [{i}] {repr(line[:80])}")
