#!/usr/bin/env python3
"""Download Sun Wen images from GitHub raw content."""
import json, os, urllib.request, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

TARGET_DIR = '/opt/hongloumeng/app/static/sunwen'
os.makedirs(TARGET_DIR, exist_ok=True)

# Get file list from API
url = 'https://api.github.com/repos/changren-wcr/sunwen/contents/docs/assets/sunwen'
print("Fetching file list...")
req = urllib.request.Request(url, headers={'User-Agent': 'python'})
data = json.loads(urllib.request.urlopen(req).read())

# Filter for .jpg files
files = [f for f in data if f['name'].endswith('.jpg')]
print(f"Found {len(files)} jpg files")

# One file has ? in name - need special handling for download_url
# GitHub encodes the URL already

def download_file(file_info):
    name = file_info['name']
    target_path = os.path.join(TARGET_DIR, name)
    if os.path.exists(target_path) and os.path.getsize(target_path) > 1000000:
        return f"SKIP {name} (exists)"
    try:
        urllib.request.urlretrieve(file_info['download_url'], target_path)
        size = os.path.getsize(target_path)
        return f"OK {name} ({size/1024:.0f}KB)"
    except Exception as e:
        return f"FAIL {name}: {e}"

# Download in parallel
success = 0
fail = 0
with ThreadPoolExecutor(max_workers=5) as pool:
    futures = {pool.submit(download_file, f): f['name'] for f in files}
    for fut in as_completed(futures):
        result = fut.result()
        if result.startswith('OK'):
            success += 1
        elif result.startswith('FAIL'):
            fail += 1
            print(result)
        print(result)

print(f"\nDone: {success} OK, {fail} failed, {len(files)-success-fail} skipped")
