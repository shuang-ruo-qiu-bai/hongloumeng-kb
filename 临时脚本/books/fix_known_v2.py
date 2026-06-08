import re as _re

with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

# Step 1: Remove "红楼梦" from known dict (too broad)
old_known = "known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦': '曹雪芹著，无名氏续，程伟元、高鹗整理'}"
new_known = "known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦脂评汇校本': '曹雪芹、脂砚斋'}"

if old_known not in code:
    # Maybe the old version is different
    old_known = "known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦': '曹雪芹著，无名氏续，程伟元、高鹗整理'}"

code = code.replace(old_known, new_known)

# Step 2: After parentheses extraction returns, add special case for exact book_name "红楼梦"
old_return = """                author = _re.sub(r'\\s+', ' ', candidate).strip()
                book_name = name[:m.start()].strip()
                return book_name, author"""
new_return = """                author = _re.sub(r'\\s+', ' ', candidate).strip()
                book_name = name[:m.start()].strip()
                # Special case: 原著 first book
                if book_name == '红楼梦' and name.endswith(')'):
                    author = '曹雪芹著，无名氏续，程伟元、高鹗整理'
                return book_name, author"""

code = code.replace(old_return, new_return)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
