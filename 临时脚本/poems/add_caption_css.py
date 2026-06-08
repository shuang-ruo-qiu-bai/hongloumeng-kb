#!/usr/bin/env python3
"""Add Sun Wen caption CSS to style.css."""
with open('/opt/hongloumeng/app/static/style.css', 'r') as f:
    css = f.read()

new_css = """

/* -- Sun Wen decorative image captions -- */
.sunwen-caption {
    font-family: var(--font-cite);
    font-size: 0.78rem;
    color: #999;
    text-align: center;
    padding: 0.4rem 0 0.2rem;
    line-height: 1.4;
}

.poetry-banner {
    margin: 1.5rem auto;
    max-width: 720px;
    text-align: center;
}

.poetry-banner img {
    width: 100%;
    height: auto;
    border-radius: 6px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
}
"""

css += new_css
with open('/opt/hongloumeng/app/static/style.css', 'w') as f:
    f.write(css)
print('Added sunwen caption CSS')
