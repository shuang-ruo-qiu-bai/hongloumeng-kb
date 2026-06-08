import re

with open('/opt/hongloumeng/app/app.py', 'r') as f:
    code = f.read()

# Fix history
code = code.replace(
    '@app.route("/history")\ndef history():\n    return render_template("history.html")',
    '@app.route("/history")\ndef history():\n    from data import HISTORY_PERIODS\n    return render_template("history.html", periods=HISTORY_PERIODS)'
)

# Fix scholars
code = code.replace(
    '@app.route("/scholars")\ndef scholars():\n    return render_template("scholars.html")',
    '@app.route("/scholars")\ndef scholars():\n    from data import SCHOLARS\n    return render_template("scholars.html", scholars=SCHOLARS, order=sorted(SCHOLARS.keys()))'
)

# Fix library
code = code.replace(
    '@app.route("/library")\ndef library():\n    return render_template("library.html")',
    '@app.route("/library")\ndef library():\n    from data import LIBRARY_CATEGORIES as cats\n    return render_template("library.html", categories=cats)'
)

# Fix canon
code = code.replace(
    '@app.route("/canon")\ndef canon():\n    return render_template("canon.html")',
    '@app.route("/canon")\ndef canon():\n    from poems_data import canon_data\n    return render_template("canon.html", **canon_data)'
)

# Fix poems
code = code.replace(
    '@app.route("/poems")\ndef poems():\n    return render_template("poems.html")',
    '@app.route("/poems")\ndef poems():\n    from poems_data import poems_data\n    return render_template("poems.html", **poems_data)'
)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('routes fixed')
