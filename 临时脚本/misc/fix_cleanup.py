import re

with open("/opt/hongloumeng/app/app.py") as f:
    code = f.read()

# Remove the duplicate broken block (lines_b version)
old_dup = """            title_val = ch["title"]
            while lines_b and lines_b[0].strip() == title_val:
                lines_b = lines_b[1:]
            body_text = "\\n".join(lines_b).strip()"""

code = code.replace(old_dup, "")

with open("/opt/hongloumeng/app/app.py", "w") as f:
    f.write(code)
print("CLEANED")
