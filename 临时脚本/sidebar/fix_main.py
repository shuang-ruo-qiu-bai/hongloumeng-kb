with open('/opt/hongloumeng/app/templates/index.html') as f:
    html = f.read()

old = """.main { padding-top: 0 !important; padding-bottom: 0 !important; padding-left: 268px !important; }
.search-form { margin: 0 auto; }"""

new = """.main { padding-top: 0 !important; padding-bottom: 0 !important; padding-left: 268px !important; max-width: calc(1200px + 268px + 1.5rem); box-sizing: border-box; }
.search-form { margin: 0 auto; }"""

if old in html:
    html = html.replace(old, new)
    with open('/opt/hongloumeng/app/templates/index.html', 'w') as f:
        f.write(html)
    print('DONE')
else:
    print('ERROR: old not found')
