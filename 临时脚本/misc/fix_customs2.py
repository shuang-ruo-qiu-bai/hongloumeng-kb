with open('/opt/hongloumeng/app/app.py', 'r') as f:
    code = f.read()

# Fix customs route
old = '''@app.route("/customs")
def customs():
    import json
    try:
        customs_path = Path(__file__).resolve().parent / "curated_customs.json"
        with open(customs_path) as f:
            data = json.load(f)
    except Exception:
        data = []
    return render_template("customs.html", customs_data=data)'''

new = '''@app.route("/customs")
def customs():
    return render_template("customs.html", customs_book=site_data.CUSTOMS_BOOK)'''

code = code.replace(old, new)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('done')
