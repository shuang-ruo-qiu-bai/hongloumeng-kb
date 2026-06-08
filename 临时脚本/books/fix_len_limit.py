with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

# Fix 1: Raise the 30-char limit to 50 for author extraction
code = code.replace(
    "if len(candidate) <= 30 and '卷' not in candidate:",
    "if len(candidate) <= 50 and '卷' not in candidate:"
)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
