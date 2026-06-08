import re

with open("/opt/hongloumeng/app/app.py") as f:
    code = f.read()

# Remove the broken while loop and keep only the proper dedup logic
old_block = """            body_text = "\\n".join(body_lines).strip()
            lines_b = body_text.split("\\n")
            while lines_b and lines_b[0].strip() and lines_b[0].strip().startswith(lines_b[0].strip().split(" ")[0]) and lines_b[0].strip() in lines_b[0].strip():
                # Just strip leading lines that match the chapter title pattern
                pass
            # Strip leading duplicated chapter title lines"""

new_block = """            body_text = "\\n".join(body_lines).strip()
            # Strip leading duplicated chapter title lines"""

code = code.replace(old_block, new_block)

# Now add the dedup logic after body_text = ... .strip()
old = "body_text = \"\\n\".join(body_lines).strip()\n            # Strip leading duplicated chapter title lines"
new = """body_text = "\\n".join(body_lines).strip()
            # Strip leading duplicated chapter title lines
            title_val = ch["title"]
            blines = body_text.split("\\n")
            while blines and blines[0].strip() == title_val:
                blines = blines[1:]
            body_text = "\\n".join(blines).strip()"""

code = code.replace(old, new)

with open("/opt/hongloumeng/app/app.py", "w") as f:
    f.write(code)
print("OK")
