"""Parse cleaned novel TXT → structured JSON for reading page."""
import json, re

SRC = "/opt/hongloumeng/raw/红楼梦/红楼梦脂评汇校本-cleaned.txt"
DST = "/opt/hongloumeng/app/novel_data.json"

with open(SRC, "r") as f:
    text = f.read()

# Find all chapter headers: 第X回 TITLE
# Pattern: "第壹回" to "第八十回" at start of line
pattern = re.compile(r'^(第[一二三四五六七八九十百零]+回　[^\n]+)', re.MULTILINE)
matches = list(pattern.finditer(text))

chapters = []
for i, m in enumerate(matches):
    title_line = m.group(1)
    # Get content from end of this header to start of next header (or end of file)
    start = m.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    content = text[start:end].strip()

    # Parse chapter number
    num_match = re.match(r'第(.+?)回', title_line)
    chapter_num = 0
    if num_match:
        cn = num_match.group(1)
        # Convert Chinese number
        num_map = {
            "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
            "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
            "百": 100, "零": 0,
        }
        if cn == "一": chapter_num = 1
        elif cn == "二": chapter_num = 2
        elif cn == "三": chapter_num = 3
        elif cn == "四": chapter_num = 4
        elif cn == "五": chapter_num = 5
        elif cn == "六": chapter_num = 6
        elif cn == "七": chapter_num = 7
        elif cn == "八": chapter_num = 8
        elif cn == "九": chapter_num = 9
        elif cn == "十": chapter_num = 10
        elif "十" in cn:
            parts = cn.split("十")
            if parts[0] == "":  # 十一, 十二...
                chapter_num = 10 + num_map.get(parts[1], 0)
            else:  # 二十, 二十一...
                chapter_num = 10 * num_map.get(parts[0], 0) + num_map.get(parts[1], 0) if parts[1] else 10 * num_map.get(parts[0], 0)
        if chapter_num == 0:
            chapter_num = i + 1  # fallback

    # Clean up content
    content = content.strip()

    chapters.append({
        "num": chapter_num,
        "title": title_line,
        "content": content,
    })

data = {"chapters": chapters}
with open(DST, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(chapters)} chapters to {DST}")
print(f"First: {chapters[0]['title']}")
print(f"Last: {chapters[-1]['title']}")
