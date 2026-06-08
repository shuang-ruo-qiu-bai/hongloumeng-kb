import json, sys

# Test chapter 1 API
import urllib.request

try:
    resp = urllib.request.urlopen('http://127.0.0.1:5000/api/canon/chapter/1', timeout=10)
    d = json.loads(resp.read())
    print("Keys:", list(d.keys()))
    print("Arabic notes:", len(d.get("arabic_notes", [])))
    print("Chinese notes:", len(d.get("chinese_notes", [])))
    if d.get("arabic_notes"):
        print("First Arabic note:", d["arabic_notes"][0])
    if d.get("chinese_notes"):
        print("First Chinese note:", d["chinese_notes"][0])
    print("Content[:100]:", d["content"][:100])
    print("SUCCESS")
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)
