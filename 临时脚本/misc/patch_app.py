with open('/opt/hongloumeng/app/app.py', 'r') as f:
    code = f.read()

# Add sys.path fix after imports
old = 'from __future__ import annotations\n\nimport json\nimport os\nimport re\nimport time\nimport uuid\nfrom pathlib import Path'
new = old + '\nimport sys\nsys.path.insert(0, str(Path(__file__).resolve().parent))\nsys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))'

code = code.replace(old, new)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('patched')
