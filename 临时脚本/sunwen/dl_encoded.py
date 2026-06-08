#!/usr/bin/env python3
"""Download Sun Wen images with URL-encoded URLs."""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

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

def encode_github_url(raw_url):
    """URL-encode the path part of a GitHub raw URL."""
    # Split at .com/ and encode the path part
    # raw.githubusercontent.com/owner/repo/branch/path
    prefix = 'https://raw.githubusercontent.com/'
    if raw_url.startswith(prefix):
        path = raw_url[len(prefix):]
        # Split path into components and encode each
        parts = path.split('/')
        encoded_parts = [quote(p, safe='') for p in parts]
        return prefix + '/'.join(encoded_parts)
    return raw_url

def download_one(item):
    name, raw_url = item
    target = os.path.join(TARGET, name)
    if os.path.exists(target) and os.path.getsize(target) > 1000000:
        return f"SKIP {name}"

    url = encode_github_url(raw_url)
    r = subprocess.run(
        ['wget', '-q', '--timeout=60', '-O', target, url],
        capture_output=True, timeout=180
    )
    if r.returncode == 0:
        kb = os.path.getsize(target) // 1024
        return f"OK {name} ({kb}KB)"
    else:
        if os.path.exists(target):
            os.remove(target)
        err = r.stderr.decode()[:100] if r.stderr else 'unknown error'
        return f"FAIL {name}: {err}"

ok = skip = fail = 0
done_count = 0

with ThreadPoolExecutor(max_workers=6) as pool:
    futures = {pool.submit(download_one, f): f[0] for f in files}
    for fut in as_completed(futures):
        result = fut.result()
        done_count += 1
        print(f"[{done_count}/{total}] {result}")
        if result.startswith('OK'):
            ok += 1
        elif result.startswith('FAIL'):
            fail += 1
        else:
            skip += 1

print(f"\nDone: {ok} OK, {skip} skipped, {fail} failed of {total}")
