#!/usr/bin/env python3
"""Fix the corrupted merge result."""
import ast

path = '/opt/hongloumeng/app/poems_data.py'
with open(path, 'r') as f:
    content = f.read()

# The broken merged line ends with: 楼空鳷鹊"",
# And the "鹊，徒悬..." content was lost.
# We need to replace the broken line with the correct merged content.

old = '委金钿于草莽，拾翠羽于尘埃。楼空鳷鹊"",'
new = '委金钿于草莽，拾翠羽于尘埃。楼空鳷鹊，徒悬七夕之针；带断鸳鸯，谁续五丝之缕？况乃金天属节，白帝司时，孤衾有梦，空室无人。桐阶月暗，芳魂与倩影同销；蓉帐香残，娇喘共细言皆绝。连天衰草，岂独蒹葭；匝地悲声，无非蟋蟀。露苔晚砌，穿帘不度寒砧；雨荔秋垣，隔院希闻怨笛。芳名未泯，檐前鹦鹉犹呼；艳质将亡，槛外海棠预老。捉迷屏后，莲瓣无声；斗草庭前，兰芽枉待。抛残绣线，银笺彩缕谁裁？折断冰丝，金斗御香未熨。",'

if old in content:
    content = content.replace(old, new, 1)
    with open(path, 'w') as f:
        f.write(content)
    ast.parse(content)
    print("Fixed! Syntax OK")
else:
    print("ERROR: old string not found")
    # Debug
    idx = content.find('楼空鳷')
    if idx >= 0:
        print("Found '楼空鳷' at", idx)
        print(repr(content[idx:idx+80]))
