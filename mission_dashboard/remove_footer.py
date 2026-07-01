import glob
import re

html_files = glob.glob("*.html")

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Remove the lines containing these strings
    content = re.sub(r'<div class="f-copy">CHANDRAYAAN-2 // LUNAR ICE DETECTION</div>\n', '', content)
    content = re.sub(r'<div class="f-isro">ISRO × HACK2SKILL</div>\n', '', content)
    
    # Also just in case they have spaces
    content = re.sub(r'<div class="f-copy">.*?</div>\n?', '', content)
    content = re.sub(r'<div class="f-isro">.*?</div>\n?', '', content)

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Footer lines removed.")
