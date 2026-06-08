#!/usr/bin/env python3
"""Rewrite sidebar CSS — remove fixed positioning, simple hamburger toggle"""
import re

CSS_PATH = '/opt/hongloumeng/app/static/style.css'

with open(CSS_PATH, 'r') as f:
    css = f.read()

original = css

# === 1. sidebar: remove fixed positioning ===
css = css.replace(
    '''    position: fixed;
    left: 0;
    top: 56px;
    bottom: 0;
    z-index: 99;''',
    '''    position: relative;'''
)

# === 2. sidebar-handle: rewrite to toggle button ===
old_handle_start = css.find('/* Sidebar handle')
old_handle_end = css.find('\n/* Rename input', old_handle_start)
if old_handle_start == -1 or old_handle_end == -1:
    old_handle_end = css.find('.sidebar-rename-input', old_handle_start)
    if old_handle_end == -1:
        print("ERROR: Could not find end of sidebar-handle section")
        exit(1)

new_handle_block = '''/* Sidebar handle — toggle button (hamburger) */
.sidebar-handle {
    width: 24px;
    min-width: 24px;
    cursor: pointer;
    background: transparent;
    transition: background 0.15s;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    border-right: 1px solid var(--border);
}
.sidebar-handle:hover {
    background: rgba(201, 169, 110, 0.15);
}
.sidebar-handle::after {
    content: '☰';
    font-size: 16px;
    color: var(--mo-muted);
    line-height: 1;
}'''

css = css[:old_handle_start] + new_handle_block + css[old_handle_end:]

# === 3. collapsed: remove !important and fix collapsed+handle rule ===
collapsed_old_1 = '''.sidebar.collapsed {
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    overflow: hidden;
    border: none;
}
.sidebar.collapsed + .sidebar-handle {
    left: 0 !important;
}'''

collapsed_new_1 = '''.sidebar.collapsed {
    width: 0;
    min-width: 0;
    padding: 0;
    overflow: hidden;
    border: none;
}'''

if collapsed_old_1 in css:
    css = css.replace(collapsed_old_1, collapsed_new_1)
else:
    print("WARNING: Could not find collapsed !important rules (attempt 1)")

# Also try alternative format
collapsed_old_2 = '''.sidebar.collapsed {
    width: 0 !important;
    min-width: 0 !important;
    padding: 0 !important;
    overflow: hidden;
    border: none;
}
'''

collapsed_new_2 = '''.sidebar.collapsed {
    width: 0;
    min-width: 0;
    padding: 0;
    overflow: hidden;
    border: none;
}
'''

if collapsed_old_2 in css:
    css = css.replace(collapsed_old_2, collapsed_new_2)
    print("Applied collapsed fix (variant 2)")

# Also handle just the !important rules directly (safety net)
css = css.replace('width: 0 !important;', 'width: 0;')
css = css.replace('min-width: 0 !important;', 'min-width: 0;')
css = css.replace('padding: 0 !important;', 'padding: 0;')
css = css.replace('.sidebar.collapsed + .sidebar-handle {\n    left: 0 !important;\n}', '')

# === 4. Mobile: update collapsed transform - remove !important ===
css = css.replace(
    '.sidebar.collapsed {\n        transform: translateX(-100%);\n        width: 260px !important;\n        min-width: 260px !important;\n    }',
    '.sidebar.collapsed {\n        transform: translateX(-100%);\n        width: 260px;\n        min-width: 260px;\n    }'
)

if css == original:
    print("WARNING: No changes were made to the CSS")
else:
    with open(CSS_PATH, 'w') as f:
        f.write(css)
    print("CSS updated successfully")
