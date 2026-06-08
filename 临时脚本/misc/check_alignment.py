#!/usr/bin/env python3
"""Check if lines and line_types arrays are aligned."""
import re

with open('/opt/hongloumeng/app/poems_data.py', 'r') as f:
    content = f.read()

start = content.find('    # 17. 芙蓉女儿诔')
end = content.find('    # 18. 杂篇')
section = content[start:end]

lines_match = re.search(r'\"lines\": \[(.*?)\],\n', section, re.DOTALL)
types_match = re.search(r'\"line_types\": \[(.*?)\],\n', section, re.DOTALL)

if lines_match and types_match:
    lines_str = lines_match.group(1)
    types_str = types_match.group(1)

    # Count all entries (including empty strings)
    lines_entries = re.findall(r'"[^"]*"', lines_str)
    types_entries = re.findall(r'"[^"]*"', types_str)

    ln = len(lines_entries)
    tn = len(types_entries)

    print(f"Lines count: {ln}")
    print(f"Line_types count: {tn}")
    print(f"Match: {'YES' if ln == tn else 'MISMATCH!'}")

    if ln != tn:
        print(f"Difference: lines has {ln - tn} more than types")

        # Show the entries from the point of divergence
        for i in range(min(ln, tn)):
            if lines_entries[i] != types_entries[i] or True:
                pass  # just show if different

        # Show last few entries of each
        print("\nLast 10 lines entries:")
        for e in lines_entries[-10:]:
            s = e[:50] + "..." if len(e) > 50 else e
            print(f"  {s}")
        print("\nLast 10 types entries:")
        for e in types_entries[-10:]:
            print(f"  {e}")
