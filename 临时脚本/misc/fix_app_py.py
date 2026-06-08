"""Fix escaped newlines in app.py _parse_chapter_notes function."""
with open('/opt/hongloumeng/app/app.py', 'r') as f:
    content = f.read()

# The issue: escape sequences in the heredoc were treated literally
# Fix all instances of the pattern
fixes = [
    ('split("\\n")', 'split(chr(10))'),
    ('"\\n".join(', 'chr(10).join('),
    ('"\\n\\n".join(', '(chr(10)*2).join('),
]

for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        print(f"Fixed: {old[:30]}")

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(content)
print("Done")
