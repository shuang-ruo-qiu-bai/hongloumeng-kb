#!/usr/bin/env python3
"""Fix corrupted poems route via direct string replacement."""
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

old = '@app.route(/poems)\ndef poems():\n    Poetry page - Cai Yijiang Hongloumeng poetry collection.\n    return render_template(poems.html,\n                           categories=poem_data.POEM_CATEGORIES,\n                           active_page=poems)'

new = '@app.route("/poems")\ndef poems():\n    """Poetry page - Cai Yijiang Hongloumeng poetry collection."""\n    return render_template("poems.html",\n                           categories=poem_data.POEM_CATEGORIES,\n                           active_page="poems")'

if old in content:
    content = content.replace(old, new, 1)
    with open('/opt/hongloumeng/app/app.py', 'w') as f:
        f.write(content)
    import ast
    ast.parse(content)
    print('Fixed! Syntax OK')
else:
    print('ERROR: old pattern not found')
    # Debug
    idx = content.find('route(/poems)')
    if idx >= 0:
        print('Found at', idx)
        print(repr(content[idx:idx+200]))
    else:
        # Check for any pattern
        for pat in ['@app.route', 'poems', 'route(/poems)']:
            idx = content.find(pat)
            if idx >= 0:
                print('Found "%s" at %d' % (pat, idx))
