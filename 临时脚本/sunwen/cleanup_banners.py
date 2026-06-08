#!/usr/bin/env python3
"""Remove broken Sun Wen banner remnants from canon and history."""
import re

for fname in ['canon.html', 'history.html']:
    path = '/opt/hongloumeng/app/templates/' + fname
    with open(path, 'r') as f:
        content = f.read()

    # Find and remove any page-banner figure elements
    # Pattern: <figure class="page-banner"> ... </figure> with or without quotes
    pattern = r'<figure\s+class=["\']*page-banner["\']*>.*?</figure>\n*'
    before = len(content)
    content = re.sub(pattern, '', content, flags=re.DOTALL)
    after = len(content)
    removed = before - after
    if removed > 0:
        print(fname + ': removed %d bytes of banner markup' % removed)
    else:
        print(fname + ': no banner found')

    with open(path, 'w') as f:
        f.write(content)
