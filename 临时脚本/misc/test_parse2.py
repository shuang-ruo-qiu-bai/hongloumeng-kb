# Test the actual _parse_book function from app.py
import re as _re

# Copy of the actual function from app.py
def _parse_book(fn):
    name = fn.strip()
    if name.endswith('.md'):
        name = _re.sub(r'_by_PaddleOCR.*', '', name)
    if '.' in name:
        parts = name.rsplit('.', 1)
        name = parts[0].strip()
    book_name = name
    author = ''
    known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦脂评汇校本': '曹雪芹、脂砚斋'}
    matches = list(_re.finditer(r'\(([^()]+?)(?:著)?\)\s*$', name))
    if not matches:
        matches = list(_re.finditer(r'（([^（）]+?)）\s*$', name))
    if matches:
        m = matches[-1]
        candidate = m.group(1).strip()
        if len(candidate) <= 30 and '卷' not in candidate:
            author = _re.sub(r'\s+', ' ', candidate).strip()
            book_name = name[:m.start()].strip()
            if book_name == '红楼梦' and name.endswith(')'):
                author = '曹雪芹著，无名氏续，程伟元、高鹗整理'
            return book_name, author
    for k, v in known.items():
        if k in name:
            return name, v
    m = _re.match(r'^([一-鿿]{2,4})\s+', name)
    if m:
        known_authors = {'吴世昌','胡适','俞平伯','周汝昌','张爱玲','王昆仑','何其芳','李希凡','冯其庸','余英时','林冠夫','梁归智','蔡元培','潘重规','柯岚','俞晓红','胡適','陈维昭'}
        if m.group(1) in known_authors:
            return name[m.end():].strip(), m.group(1)
    m = _re.match(r'^([一-鿿]{2,4})[：:](.+)$', name)
    if m and _re.match(r'^[一-鿿]{2,4}$', m.group(1)):
        return m.group(2).strip(), m.group(1).strip()
    if ' ' in name:
        parts = name.rsplit(' ', 1)
        if _re.match(r'^[一-鿿·]{2,4}$', parts[1].strip()):
            return parts[0].strip(), parts[1].strip()
    m = _re.match(r'^([一-鿿]{2,4})[：:]\s*(.+)$', name)
    if m:
        return m.group(2).strip(), m.group(1).strip()
    return book_name, author

tests = [
    '红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub',
    '红楼梦脂评汇校本.epub',
    '石头记索隐 蔡元培.epub',
    '吴世昌 红楼碎墨 .pdf',
    '王国维《红楼梦评论》笺说 (俞晓红).pdf',
]

for t in tests:
    n, a = _parse_book(t)
    print(f'book_name="{n}" author="{a}"')
