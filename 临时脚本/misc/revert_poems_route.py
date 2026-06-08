#!/usr/bin/env python3
"""Revert poems route to simple version (Sun Wen handled by global)."""
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

old = """@app.route("/poems")
def poems():
    """Poetry page — 蔡义江《红楼梦诗词曲赋全解》."""
    import json, os
    # Load Sun Wen captions for decorative images
    sw_cap_path = os.path.join(os.path.dirname(__file__), "static/sunwen/sunwen_captions.json")
    sunwen_captions = {}
    if os.path.exists(sw_cap_path):
        raw = json.load(open(sw_cap_path, "r"))
        for entry in raw:
            fname = "sunwen_%03d.jpg" % entry["index"]
            sunwen_captions[fname] = entry["caption"]
    return render_template("poems.html",
                           categories=poem_data.POEM_CATEGORIES,
                           sunwen_captions=sunwen_captions,
                           active_page="poems")"""

new = """@app.route("/poems")
def poems():
    """Poetry page — 蔡义江《红楼梦诗词曲赋全解》."""
    return render_template("poems.html",
                           categories=poem_data.POEM_CATEGORIES,
                           active_page="poems")"""

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    print('Reverted poems route to simple version')
else:
    print('Could not find poems route with captions - checking...')
    idx = content.find('sunwen_captions')
    if idx >= 0:
        print('Found sunwen_captions at', idx)
        print(content[idx-50:idx+100])
