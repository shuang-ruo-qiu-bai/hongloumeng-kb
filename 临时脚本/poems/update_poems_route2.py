#!/usr/bin/env python3
"""Update poems route with better captions lookup dict."""
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

old = '''@app.route("/poems")
def poems():
    """Poetry page — 蔡义江《红楼梦诗词曲赋全解》."""
    import json, os
    # Load Sun Wen captions for decorative images
    sw_cap_path = os.path.join(os.path.dirname(__file__), "static/sunwen/sunwen_captions.json")
    sunwen_captions = []
    if os.path.exists(sw_cap_path):
        sunwen_captions = json.load(open(sw_cap_path, "r"))
    return render_template("poems.html",
                           categories=poem_data.POEM_CATEGORIES,
                           sunwen_captions=sunwen_captions,
                           active_page="poems")'''

new = '''@app.route("/poems")
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
                           active_page="poems")'''

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    print('Updated poems route with captions dict lookup')
else:
    print('ERROR: Could not find old poems route')
