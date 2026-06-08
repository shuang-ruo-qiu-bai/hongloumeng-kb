import re

with open('/opt/hongloumeng/app/app.py', 'r') as f:
    code = f.read()

# Replace customs route
old_customs = '''@app.route("/customs")
def customs():
    return render_template("customs.html")'''

new_customs = '''@app.route("/customs")
def customs():
    import json
    try:
        customs_path = Path(__file__).resolve().parent / "curated_customs.json"
        with open(customs_path) as f:
            data = json.load(f)
    except Exception:
        data = []
    return render_template("customs.html", customs_data=data)'''

code = code.replace(old_customs, new_customs)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('done')
