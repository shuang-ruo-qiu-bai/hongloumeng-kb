with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

# Add direct book name/author mapping before parentheses extraction section
old = """        book_name = name
        author = ''
        # Known specific books
        known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦脂评汇校本': '曹雪芹、脂砚斋'}
        # Pattern: last (...) as author"""

new = """        book_name = name
        author = ''
        # Known specific books
        known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦脂评汇校本': '曹雪芹、脂砚斋'}
        # Direct name → (book_name, author) overrides
        named_books = {
            '红楼风俗名物谭：邓云乡论红楼梦': ('红楼风俗名物谭', '邓云乡'),
        }
        if name in named_books:
            return named_books[name]
        # Pattern: last (...) as author"""

code = code.replace(old, new)

# After parentheses extraction, strip colon prefix for 编辑部
old2 = """                # Special case: 原著 first book
                if book_name == '红楼梦' and name.endswith(')'):
                    author = '曹雪芹著，无名氏续，程伟元、高鹗整理'
                return book_name, author"""

new2 = """                # Special case: 原著 first book
                if book_name == '红楼梦' and name.endswith(')'):
                    author = '曹雪芹著，无名氏续，程伟元、高鹗整理'
                # Strip colon prefix when book starts with 4-char subtitle
                if '：' in book_name:
                    prefix, rest = book_name.split('：', 1)
                    if len(prefix) <= 6 and author and not _re.match(r'^[一-鿿]{2,4}$', prefix):
                        book_name = rest
                return book_name, author"""

code = code.replace(old2, new2)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
