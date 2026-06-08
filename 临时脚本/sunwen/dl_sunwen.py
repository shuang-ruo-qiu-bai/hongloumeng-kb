#!/usr/bin/env python3
"""Download Sun Wen images with wget."""
import json, os, subprocess, sys

TARGET = '/opt/hongloumeng/app/static/sunwen'
os.makedirs(TARGET, exist_ok=True)

# Fetch file list
print("Fetching file list...")
raw = subprocess.check_output([
    'curl', '-s',
    'https://api.github.com/repos/changren-wcr/sunwen/contents/docs/assets/sunwen'
])
data = json.loads(raw)

files = [(f['name'], f['download_url']) for f in data if f['name'].endswith('.jpg')]
total = len(files)
print(f"Found {total} files")

ok = 0
skip = 0
fail = 0

for i, (name, url) in enumerate(files, 1):
    target = os.path.join(TARGET, name)

    # Skip if exists and > 1MB
    if os.path.exists(target) and os.path.getsize(target) > 1000000:
        skip += 1
        continue

    print(f"[{i}/{total}] {name}...", end=' ', flush=True)
    result = subprocess.run(['wget', '-q', '--timeout=60', '-O', target, url],
                          capture_output=True, timeout=120)
    if result.returncode == 0:
        kb = os.path.getsize(target) // 1024
        print(f"OK ({kb}KB)")
        ok += 1
    else:
        print("FAILED")
        fail += 1
        if os.path.exists(target):
            os.remove(target)

print(f"\nDone: {ok} OK, {skip} skipped, {fail} failed")
print(f"Total: {ok+skip+fail}/{total}")
