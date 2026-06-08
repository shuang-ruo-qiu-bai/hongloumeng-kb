#!/usr/bin/env python3
"""Parallel download Sun Wen images with wget."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def download_one(item):
    name, url = item
    target = os.path.join(TARGET, name)
    if os.path.exists(target) and os.path.getsize(target) > 1000000:
        return f"SKIP {name}"
    r = subprocess.run(['wget', '-q', '--timeout=60', '-O', target, url],
                       capture_output=True, timeout=180)
    if r.returncode == 0:
        kb = os.path.getsize(target) // 1024
        return f"OK {name} ({kb}KB)"
    else:
        if os.path.exists(target):
            os.remove(target)
        return f"FAIL {name}: {r.stderr.decode()[:80]}"

ok = skip = fail = 0
with ThreadPoolExecutor(max_workers=8) as pool:
    futures = {pool.submit(download_one, f): f[0] for f in files}
    for fut in as_completed(futures):
        result = fut.result()
        print(result)
        if result.startswith('OK'):
            ok += 1
        elif result.startswith('FAIL'):
            fail += 1
        else:
            skip += 1

print(f"\nDone: {ok} OK, {skip} skipped, {fail} failed of {total} total")
