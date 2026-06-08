import re

# ── Fix 1: Update canon API endpoint to separate body from notes ──
with open("/opt/hongloumeng/app/app.py") as f:
    code = f.read()

old_api = '''@app.route("/api/canon/chapter/<int:num>")
def api_canon_chapter(num):
    import json, os, re
    novel_path = os.path.join(os.path.dirname(__file__), "novel_data.json")
    with open(novel_path) as f:
        data = json.load(f)
    for ch in data["chapters"]:
        if ch["num"] == num:
            content = ch["content"]
            arabic_notes = []
            chinese_notes = []
            for m in re.finditer(r"\[(\d+)\]([^。]*。?)", content):
                arabic_notes.append({"num": int(m.group(1)), "text": m.group(2).strip()})
            for m in re.finditer(r"[〔\[]([一二三四五六七八九十百零〇]+)[〕\]]([^。]*。?)", content):
                chinese_notes.append({"num": m.group(1), "text": m.group(2).strip()})
            return jsonify({"title": ch["title"], "content": content, "arabic_notes": arabic_notes, "chinese_notes": chinese_notes})
    return jsonify({"error": "章节不存在"}), 404'''

new_api = '''@app.route("/api/canon/chapter/<int:num>")
def api_canon_chapter(num):
    import json, os, re
    novel_path = os.path.join(os.path.dirname(__file__), "novel_data.json")
    with open(novel_path) as f:
        data = json.load(f)
    for ch in data["chapters"]:
        if ch["num"] == num:
            content = ch["content"]
            lines = content.split("\\n")
            body_lines = []
            notes_lines = []
            in_notes = False
            for line in lines:
                stripped = line.strip()
                if not in_notes and re.match(r"^\\[\\d+\\]", stripped):
                    in_notes = True
                if in_notes:
                    notes_lines.append(line)
                else:
                    body_lines.append(line)
            body_text = "\\n".join(body_lines).strip()
            arabic_notes = []
            chinese_notes = []
            for line in notes_lines:
                stripped = line.strip()
                m = re.match(r"^\\[(\\d+)\\](.+)", stripped)
                if m:
                    arabic_notes.append({"num": int(m.group(1)), "text": m.group(2).strip()})
                m = re.match(r"^[〔\\[]([一二三四五六七八九十百零〇]+)[〕\\]](.+)", stripped)
                if m:
                    chinese_notes.append({"num": m.group(1), "text": m.group(2).strip()})
            return jsonify({"title": ch["title"], "content": body_text, "arabic_notes": arabic_notes, "chinese_notes": chinese_notes})
    return jsonify({"error": "章节不存在"}), 404'''

code = code.replace(old_api, new_api)

# ── Fix 2: Scholar ordering ──
code = code.replace(
    'return render_template("scholars.html", scholars=SCHOLARS, order=sorted(SCHOLARS.keys()))',
    'from data import SCHOLAR_ORDER\n    return render_template("scholars.html", scholars=SCHOLARS, order=SCHOLAR_ORDER)'
)

with open("/opt/hongloumeng/app/app.py", "w") as f:
    f.write(code)
print("app.py fixes applied")

# ── Fix 3: Timeline centering in CSS ──
with open("/opt/hongloumeng/app/static/style.css") as f:
    css = f.read()

css = css.replace(
    ".timeline {\n    position: relative;\n    max-width: 800px;\n    padding-left: 2rem;\n}",
    ".timeline {\n    position: relative;\n    max-width: 800px;\n    margin: 0 auto;\n    padding-left: 2rem;\n}"
)

with open("/opt/hongloumeng/app/static/style.css", "w") as f:
    f.write(css)
print("CSS fix applied")
