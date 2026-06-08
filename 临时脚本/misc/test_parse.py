import re as _re

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
    for k, v in known.items():
        if k in name:
            print(f"  [known match] {k} in {name}")
            return name, v
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
            print(f"  [parens match] book_name={book_name}, author={author}")
            return book_name, author
    for k, v in known.items():
        if k in name:
            print(f"  [known match 2] {k} in {name}")
            return name, v
    m = _re.match(r'^([一-鿿]{2,4})\s+', name)
    if m:
        known_authors = {'吴世昌','胡适','俞平伯','周汝昌','张爱玲','王昆仑','何其芳','李希凡','冯其庸','余英时','林冠夫','梁归智','蔡元培','潘重规','柯岚','俞晓红','胡適','陈维昭'}
        if m.group(1) in known_authors:
            print(f"  [lead author] {m.group(1)}")
            return name[m.end():].strip(), m.group(1)
    m = _re.match(r'^([一-鿿]{2,4})[：:](.+)$', name)
    if m and _re.match(r'^[一-鿿]{2,4}$', m.group(1)):
        print(f"  [colon] book={m.group(2)} author={m.group(1)}")
        return m.group(2).strip(), m.group(1).strip()
    if ' ' in name:
        parts = name.rsplit(' ', 1)
        if _re.match(r'^[一-鿿·]{2,4}$', parts[1].strip()):
            print(f"  [space end] book={parts[0]} author={parts[1]}")
            return parts[0].strip(), parts[1].strip()
    m = _re.match(r'^([一-鿿]{2,4})[：:]\s*(.+)$', name)
    if m:
        print(f"  [colon2] book={m.group(2)} author={m.group(1)}")
        return m.group(2).strip(), m.group(1).strip()
    print(f"  [fallback] book_name={book_name}")
    return book_name, author

# Test cases
tests = [
    '红楼梦 (曹雪芹  无名氏  程伟元  高鹗  中国艺术研究院红楼梦研究所).epub',
    '红楼梦脂评汇校本.epub',
    '不惑之获：《红楼梦学刊》40年精选文集（全三卷） (《红楼梦学刊》编辑部).epub',
    '红楼梦大辞典 增订本.pdf',
    '红楼梦诗词曲赋全解.epub',
    '红楼梦研究稀见资料汇编.pdf',
    '吴世昌 红楼碎墨 .pdf',
    '命若朝霜：《红楼梦》里的法律、社会与女性 (柯岚) .epub',
    '王国维《红楼梦评论》笺说 (俞晓红).pdf',
    '石头记索隐 蔡元培.epub',
]

for t in tests:
    print(f'\n--- {t}')
    n, a = _parse_book(t)
    print(f'  => book_name="{n}" author="{a}"')
