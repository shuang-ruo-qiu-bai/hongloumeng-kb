#!/usr/bin/env python3
"""Generate simplified Chinese captions from Sun Wen image filenames."""
import json, os, re

TARGET_DIR = '/opt/hongloumeng/app/static/sunwen'

# Use opencc for traditional -> simplified conversion
try:
    from opencc import OpenCC
    converter = OpenCC('t2s')
except ImportError:
    converter = None
    print("WARNING: opencc not available, using traditional captions")

# Manual override for the file with the ? character
FILENAME_FIXES = {
    # The file with ? in name - use the user-provided simplified caption
    "147第77回 连？证撵出大观园.jpg": "连赃证撵出大观园",
}

def extract_caption(filename):
    """Extract and clean caption from filename."""
    # Remove .jpg extension
    name = filename.replace('.jpg', '')

    # Remove leading number prefix (e.g., "001 ", "001第", "002第")
    name = re.sub(r'^\d{3}\s*', '', name)
    name = re.sub(r'^\d{3}', '', name)

    # Remove chapter info prefix patterns like "第1回 ", "第1-2回 " etc.
    # These are often at the start: "第1回 石頭記..." or included: "001第1回 石頭記..."
    # After removing the number prefix, we might still have "第1回 " at start

    # Strip leading space
    name = name.strip()

    # If starts with chapter info, keep it but clean up
    # "第1回 石頭記大觀園全景" -> "第1回 石頭記大觀園全景"

    # Remove trailing parenthetical notes like "(原簽誤)"
    name = re.sub(r'\([^)]*\)', '', name)

    # Clean up extra spaces
    name = re.sub(r'\s+', '', name)

    return name

def generate_captions():
    """Generate captions JSON file."""
    if not os.path.isdir(TARGET_DIR):
        print(f"ERROR: {TARGET_DIR} not found")
        return

    files = sorted([f for f in os.listdir(TARGET_DIR) if f.endswith('.jpg')])
    print(f"Found {len(files)} image files")

    captions = []

    for filename in files:
        # Check for manual override
        if filename in FILENAME_FIXES:
            caption = FILENAME_FIXES[filename]
        else:
            caption = extract_caption(filename)

        # Convert to simplified
        if converter:
            caption = converter.convert(caption)

        captions.append({
            "filename": filename,
            "caption": caption
        })

    # Write captions file
    output_path = os.path.join(TARGET_DIR, 'captions.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(captions)} captions to {output_path}")
    print("First 5 captions:")
    for c in captions[:5]:
        print(f"  {c['filename']} -> {c['caption']}")
    print("Last 3 captions:")
    for c in captions[-3:]:
        print(f"  {c['filename']} -> {c['caption']}")

if __name__ == '__main__':
    generate_captions()
