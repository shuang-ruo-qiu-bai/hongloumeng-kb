#!/usr/bin/env python3
"""Add Sun Wen nav link to base.html"""
with open('/opt/hongloumeng/app/templates/base.html', 'r') as f:
    content = f.read()

if 'sunwen' in content:
    print('Nav link already exists')
else:
    old = '                <a href="/library" class="{% if active_page == \'library\' %}active{% endif %}">红学文库</a>'
    new = '                <a href="/library" class="{% if active_page == \'library\' %}active{% endif %}">红学文库</a>\n                <a href="/sunwen" class="{% if active_page == \'sunwen\' %}active{% endif %}">孙温画册</a>'

    if old in content:
        content = content.replace(old, new, 1)
        with open('/opt/hongloumeng/app/templates/base.html', 'w') as f:
            f.write(content)
        print('Added nav link successfully')
    else:
        print('ERROR: Could not find nav insertion point')
        # Debug
        idx = content.find('红学文库')
        if idx >= 0:
            print('Found "红学文库" at', idx)
            print('Context:', content[idx-50:idx+100])
