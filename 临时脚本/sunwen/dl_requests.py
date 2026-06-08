#!/usr/bin/env python3
"""Download Sun Wen images using requests library (handles URL encoding)."""
import json, os, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

TARGET = '/opt/hongloumeng/app/static/sunwen'
os.makedirs(TARGET, exist_ok=True)

# Fetch file list
print("Fetching file list...")
r = requests.get(
    'https://api.github.com/repos/changren-wcr/sunwen/contents/docs/assets/sunwen',
    headers={'User-Agent': 'python'},
    timeout=30
)
data = r.json()
files = [(f['name'], f['download_url']) for f in data if f['name'].endswith('.jpg')]
total = len(files)
print(f"Found {total} files")

def download_one(item):
    name, url = item
    target = os.path.join(TARGET, name)
    if os.path.exists(target) and os.path.getsize(target) > 1000000:
        return f"SKIP {name}"
    try:
        r = requests.get(url, timeout=120)
        if r.status_code == 200:
            with open(target, 'wb') as f:
                f.write(r.content)
            kb = len(r.content) // 1024
            return f"OK {name} ({kb}KB)"
        else:
            return f"FAIL {name}: HTTP {r.status_code}"
    except Exception as e:
        return f"FAIL {name}: {e}"

ok = skip = fail = 0
done = 0

with ThreadPoolExecutor(max_workers=6) as pool:
    futures = {pool.submit(download_one, f): f[0] for f in files}
    for fut in as_completed(futures):
        result = fut.result()
        done += 1
        print(f"[{done}/{total}] {result}")
        if result.startswith('OK'):
            ok += 1
        elif result.startswith('FAIL'):
            fail += 1
        else:
            skip += 1

print(f"\nDone: {ok} OK, {skip} skipped, {fail} failed of {total}")
