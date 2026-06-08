#!/usr/bin/env python3
"""Add Sun Wen gallery route to app.py"""
import re

with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

if '/sunwen' in content:
    print('Route already exists, skipping')
else:
    old = '''@app.route("/editions")
def editions():
    """红楼版本 page."""
    return render_template("editions.html",
                           active_page="editions")


@app.route("/api/customs/chapter")'''

    new = '''@app.route("/editions")
def editions():
    """红楼版本 page."""
    return render_template("editions.html",
                           active_page="editions")


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
                           active_page="sunwen")


@app.route("/api/customs/chapter")'''

    if old in content:
        content = content.replace(old, new, 1)
        with open('/opt/hongloumeng/app/app.py', 'w') as f:
            f.write(content)
        print('Added /sunwen route successfully')
    else:
        print('ERROR: Could not find insertion point')
        m = re.search(r'@app\.route\("/editions"\)', content)
        if m:
            print('Found editions route at position', m.start())
        m = re.search(r'@app\.route\("/api/customs/chapter"\)', content)
        if m:
            print('Found api/customs/chapter at position', m.start())
        m = re.search(r'def editions\(\):', content)
        if m:
            print('Found editions def at position', m.start())
