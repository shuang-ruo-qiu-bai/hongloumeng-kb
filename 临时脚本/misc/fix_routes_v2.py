import re

with open("/opt/hongloumeng/app/app.py") as f:
    code = f.read()

# 1. /canon route
code = code.replace(
    'from poems_data import canon_data\n    return render_template("canon.html", **canon_data)',
    'import json, os\n    novel_path = os.path.join(os.path.dirname(__file__), "novel_data.json")\n    with open(novel_path) as f:\n        data = json.load(f)\n    return render_template("canon.html", chapters=data["chapters"])'
)

# 2. /poems route
code = code.replace(
    'from poems_data import poems_data\n    return render_template("poems.html", **poems_data)',
    'from poems_data import POEM_CATEGORIES\n    return render_template("poems.html", categories=POEM_CATEGORIES)'
)

# 3. /library route
code = code.replace(
    'from data import LIBRARY_CATEGORIES as cats\n    return render_template("library.html", categories=cats)',
    'import os, glob\n    books_dir = "/opt/hongloumeng/books/红楼梦"\n    categories = []\n    for subdir in sorted(os.listdir(books_dir)):\n        subpath = os.path.join(books_dir, subdir)\n        if not os.path.isdir(subpath) or subdir.startswith("."):\n            continue\n        books = []\n        for f in sorted(glob.glob(os.path.join(subpath, "*"))):\n            fn = os.path.basename(f)\n            if fn.startswith("._") or fn.startswith("."):\n                continue\n            ext = os.path.splitext(fn)[1].upper().replace(".", "")\n            size_kb = os.path.getsize(f) // 1024\n            size_str = "%dKB" % size_kb if size_kb < 1024 else "%.1fMB" % (size_kb/1024.0)\n            books.append({"path": fn, "name": fn.rsplit(".", 1)[0], "format": ext, "size": size_str})\n        categories.append({"name": subdir, "books": books})\n    return render_template("library.html", categories=categories)'
)

# 4. Add /api/canon/chapter/<int:num>
API_CANON = '''
@app.route("/api/canon/chapter/<int:num>")
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
    return jsonify({"error": "章节不存在"}), 404

'''

code = code.replace('@app.route("/editions")', API_CANON + '@app.route("/editions")')

# 5. Add /api/customs/chapter
API_CUSTOMS = '''
@app.route("/api/customs/chapter")
def api_customs_chapter():
    title = request.args.get("title", "")
    if not title:
        return jsonify({"error": "missing title"}), 400
    curated_path = os.path.join(os.path.dirname(__file__), "curated_customs.json")
    with open(curated_path) as f:
        all_chapters = json.load(f)
    for group in all_chapters:
        for item in group:
            if item.get("title") == title:
                return jsonify({"content": item.get("content", "")})
    return jsonify({"error": "章节不存在"}), 404

'''

code = code.replace('@app.route("/editions")', API_CUSTOMS + '@app.route("/editions")')

with open("/opt/hongloumeng/app/app.py", "w") as f:
    f.write(code)
print("FIXES APPLIED OK")
