import re

with open("/opt/hongloumeng/app/app.py") as f:
    code = f.read()

old = "body_text = \"\\n\".join(body_lines).strip()\n            arabic_notes = []"

new = """body_text = "\\n".join(body_lines).strip()
            lines_b = body_text.split("\\n")
            while lines_b and lines_b[0].strip() and lines_b[0].strip().startswith(lines_b[0].strip().split(" ")[0]) and lines_b[0].strip() in lines_b[0].strip():
                # Just strip leading lines that match the chapter title pattern
                pass
            # Strip leading duplicated chapter title lines
            title_val = ch["title"]
            while lines_b and lines_b[0].strip() == title_val:
                lines_b = lines_b[1:]
            body_text = "\\n".join(lines_b).strip()
            arabic_notes = []"""

code = code.replace(old, new)

with open("/opt/hongloumeng/app/app.py", "w") as f:
    f.write(code)
print("OK")
