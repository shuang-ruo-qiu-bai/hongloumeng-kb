with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

old_block = """        book_name = name
        author = ''
        # Known specific books
        known = {'红楼梦大词典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦': '曹雪芹著，无名氏续，程伟元、高鹗整理'}
        # Pattern: last (...) as author
        matches = list(_re.finditer(r'\\(([^()]+?)(?:著)?\\)\\s*$', name))
        if not matches:
            matches = list(_re.finditer(r'（([^（）]+?)）\\s*$', name))
        if matches:
            m = matches[-1]
            candidate = m.group(1).strip()
            if len(candidate) <= 30 and '卷' not in candidate:
                author = _re.sub(r'\\s+', ' ', candidate).strip()
                book_name = name[:m.start()].strip()
                return book_name, author
        # Known books"""

new_block = """        book_name = name
        author = ''
        # Known specific books
        known = {'红楼梦大词典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦': '曹雪芹著，无名氏续，程伟元、高鹗整理'}
        # Check known books first (exact match on stripped name)
        if name in known:
            return name, known[name]
        # Pattern: last (...) as author
        matches = list(_re.finditer(r'\\(([^()]+?)(?:著)?\\)\\s*$', name))
        if not matches:
            matches = list(_re.finditer(r'（([^（）]+?)）\\s*$', name))
        if matches:
            m = matches[-1]
            candidate = m.group(1).strip()
            if len(candidate) <= 30 and '卷' not in candidate:
                author = _re.sub(r'\\s+', ' ', candidate).strip()
                book_name = name[:m.start()].strip()
                return book_name, author
        # Known books (partial match)"""

code = code.replace(old_block, new_block)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
