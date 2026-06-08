with open('/opt/hongloumeng/app/static/style.css', 'r') as f:
    css = f.read()

# Center content containers on content pages
# Ensure page-content wrapper for content pages
rule = '\n/* Content pages: center the content blocks */\n.page-header + * {\n    max-width: 960px;\n    margin: 0 auto;\n}\n'

if 'page-header + *' not in css:
    css += rule

with open('/opt/hongloumeng/app/static/style.css', 'w') as f:
    f.write(css)
print('done')
