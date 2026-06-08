#!/usr/bin/env python3
"""Add Sun Wen caption helper to Flask template globals."""
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

# Add after the context_processor
old = """@app.context_processor
def inject_user():
    return {"current_user": current_user}"""

new = """@app.context_processor
def inject_user():
    return {"current_user": current_user}

# Sun Wen decorative image captions
_SUNWEN_CAPTIONS = {}
_sw_path = Path(__file__).resolve().parent / "static/sunwen/sunwen_captions.json"
if _sw_path.exists():
    try:
        raw = json.loads(_sw_path.read_text(encoding="utf-8"))
        for entry in raw:
            fname = "sunwen_%03d.jpg" % entry["index"]
            _SUNWEN_CAPTIONS[fname] = entry["caption"]
    except Exception:
        pass

@app.context_processor
def inject_sunwen():
    def sunwen_caption(filename):
        return _SUNWEN_CAPTIONS.get(filename, "")
    return {"sunwen_caption": sunwen_caption}"""

if old in content:
    content = content.replace(old, new)
    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    print('Added Sun Wen template helper')
else:
    print('ERROR: inject_user not found')
