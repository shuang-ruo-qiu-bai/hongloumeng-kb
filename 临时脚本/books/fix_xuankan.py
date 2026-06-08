with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

# Replace named_books to include 选集
old = """        named_books = {
            '红楼风俗名物谭：邓云乡论红楼梦': ('红楼风俗名物谭', '邓云乡'),
        }"""
new = """        named_books = {
            '红楼风俗名物谭：邓云乡论红楼梦': ('红楼风俗名物谭', '邓云乡'),
            '不惑之获：《红楼梦学刊》40年精选文集（全三卷） (《红楼梦学刊》编辑部)': ('《红楼梦学刊》选集', '《红楼梦学刊》编辑部'),
        }"""
code = code.replace(old, new)

# Also remove the old colon-stripping special case (no longer needed)
old2 = "                # Strip colon prefix for known cases\n                if author == '《红楼梦学刊》编辑部' and '不惑之获：' in book_name:\n                    book_name = book_name.split('：', 1)[1]"
new2 = ""
code = code.replace(old2, new2)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
