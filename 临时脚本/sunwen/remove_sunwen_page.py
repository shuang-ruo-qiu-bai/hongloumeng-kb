#!/usr/bin/env python3
"""Remove Sun Wen page route and nav link, keep captions JSON on server."""
import re

# 1. Remove nav link from base.html
with open('/opt/hongloumeng/app/templates/base.html', 'r') as f:
    content = f.read()

old_nav = '                <a href="/sunwen" class="{% if active_page == \'sunwen\' %}active{% endif %}">孙温画册</a>\n'
if old_nav in content:
    content = content.replace(old_nav, '')
    with open('/opt/hongloumeng/app/templates/base.html', 'w') as f:
        f.write(content)
    print('Removed Sun Wen nav link')
else:
    print('Nav link not found')

# 2. Remove route from app.py
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

old_route = '''

@app.route("/sunwen")
def sunwen():
    """孙温画册 gallery."""
    import json, os
    cap_path = os.path.join(os.path.dirname(__file__), "static/sunwen/sunwen_captions.json")
    captions = []
    if os.path.exists(cap_path):
        captions = json.load(open(cap_path, "r"))
    return render_template("sunwen.html",
                           sunwen_captions=captions,
                           active_page="sunwen")'''

if old_route in content:
    content = content.replace(old_route, '')
    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    print('Removed /sunwen route')
else:
    print('Route not found (might have slight whitespace diff)')
    # Try with extra newlines
    for pattern in ['/sunwen', 'def sunwen', 'sunwen_captions']:
        if pattern in content:
            idx = content.find(pattern)
            print(f'  "{pattern}" found at pos {idx}')

# 3. Keep captions JSON
import os
cap_path = '/opt/hongloumeng/app/static/sunwen/sunwen_captions.json'
if os.path.exists(cap_path):
    print(f'Captions JSON kept at {cap_path}')
