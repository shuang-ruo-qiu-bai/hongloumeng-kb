#!/usr/bin/env python3
"""Fix nav-brand CSS to prevent wrapping."""
with open('/opt/hongloumeng/app/static/style.css', 'r') as f:
    css = f.read()

old = """.nav-brand {
    font-family: var(--font-heading);
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--jin);
    text-decoration: none;
    letter-spacing: 0.15em;
}"""

new = """.nav-brand {
    font-family: var(--font-heading);
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--jin);
    text-decoration: none;
    letter-spacing: 0.15em;
    white-space: nowrap;
}"""

if old in css:
    css = css.replace(old, new)
    with open('/opt/hongloumeng/app/static/style.css', 'w') as f:
        f.write(css)
    print('Fixed nav-brand CSS: added white-space: nowrap')
else:
    print('ERROR: Could not find nav-brand CSS block')
    # Debug
    idx = css.find('.nav-brand')
    if idx >= 0:
        print('Found at', idx)
        print(css[idx:idx+300])
