import json

# 1. Update app.py with canon route + API
app_path = '/opt/hongloumeng/app/app.py'
with open(app_path, 'r') as f:
    content = f.read()

# Replace canon route
old_canon = '''@app.route("/canon")
def canon():
    """红楼原著 page."""
    return render_template("canon.html",
                           active_page="canon")'''

new_canon = '''@app.route("/canon")
def canon():
    """红楼原著 page — 回目列表 + 阅读."""
    novel_path = str(Path(__file__).parent / "novel_data.json")
    try:
        with open(novel_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"chapters": []}
    return render_template("canon.html",
                           active_page="canon",
                           chapters=data.get("chapters", []))'''

content = content.replace(old_canon, new_canon)

# Add API route after canon route (find a good insertion point)
# Insert after the imports but before the first route, or after canon
api_route = '''

@app.route("/api/canon/chapter/<int:chapter_num>")
def api_canon_chapter(chapter_num):
    """Return the content of a specific chapter."""
    novel_path = str(Path(__file__).parent / "novel_data.json")
    try:
        with open(novel_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        return jsonify({"error": str(e)}), 500

    for ch in data.get("chapters", []):
        if ch["num"] == chapter_num:
            return jsonify(ch)

    return jsonify({"error": "Chapter not found"}), 404
'''

# Insert after the canon route function body
insert_point = content.find('                           active_page="canon")')
insert_point = content.find('\n', insert_point) + 1
content = content[:insert_point] + api_route + content[insert_point:]

with open(app_path, 'w') as f:
    f.write(content)

print("Updated app.py")
