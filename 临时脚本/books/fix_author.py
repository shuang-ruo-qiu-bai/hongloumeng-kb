with open('/opt/hongloumeng/app/app.py') as f:
    code = f.read()

old = "known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟'}"
new = "known = {'红楼梦大辞典': '冯其庸、李希凡', '红楼梦诗词曲赋全解': '蔡义江', '红楼梦研究稀见资料汇编': '一粟', '红楼梦': '曹雪芹著，无名氏续，程伟元、高鹗整理'}"

code = code.replace(old, new)

with open('/opt/hongloumeng/app/app.py', 'w') as f:
    f.write(code)
print('DONE')
