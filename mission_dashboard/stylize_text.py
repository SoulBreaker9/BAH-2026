import glob
import os

html_files = glob.glob("*.html")

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # We want to replace standard Shishir with the stylized version with diacritics
    content = content.replace("SHISHIR", "SHÏSHỊR")
    content = content.replace("Shishir", "Shïshịr")
    content = content.replace("SHIS<b>HIR</b>", "SHÏS<b>HỊR</b>")
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Stylized font text applied.")
