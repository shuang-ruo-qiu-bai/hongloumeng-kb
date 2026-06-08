with open('/opt/hongloumeng/app/templates/index.html') as f:
    html = f.read()

# Add overflow-x hidden to body
old = '.main { padding-top: 0 !important; padding-bottom: 0 !important; padding-left: 268px !important; max-width: calc(1200px + 268px + 1.5rem); box-sizing: border-box; }'

new = 'body { overflow-x: hidden; }\n.main { padding-top: 0 !important; padding-bottom: 0 !important; padding-left: 268px !important; max-width: calc(1200px + 268px + 1.5rem); box-sizing: border-box; }'

if old in html:
    html = html.replace(old, new)
    with open('/opt/hongloumeng/app/templates/index.html', 'w') as f:
        f.write(html)
    print('DONE')
else:
    print('ERROR: old not found')
