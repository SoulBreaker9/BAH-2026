import os
import glob
import re

html_files = glob.glob("*.html")

replacements = {
    "BAH 2026 — Real-Time Monitoring Dashboard": "Deep Ice — Real-Time Monitoring Dashboard",
    "BAH 2026 — Multi-Sensor Fusion": "Deep Ice — Multi-Sensor Fusion",
    "BAH 2026 — Lunar Ice Detection Mission Control": "Deep Ice — Lunar Ice Detection Mission Control",
    "BAH 2026 — Radar Polarimetry": "Deep Ice — Radar Polarimetry",
    "BAH 2026 — Rover AI Pathfinder": "Deep Ice — Rover AI Pathfinder",
    "BAH 2026 — Terrain & Subsurface Analysis": "Deep Ice — Terrain & Subsurface Analysis",
    "BAH 2026 — INITIALIZING": "DEEP ICE — INITIALIZING",
    "BAH-2026 // CHL-08": "DEEP ICE // LUNAR MISSION",
    "BAH <b>2026</b>": "DEEP <b>ICE</b>",
    "BAH 2026": "DEEP ICE",
    "Bharatiya Antariksh Hackathon 2026": "Project Deep Ice",
    "ISRO Challenge": "Lunar South Pole",
    "CHALLENGE 08 // ": "",
}

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    # Remove team section if exists (using regex to remove the <section id="team">...</section>)
    content = re.sub(r'<!-- TEAM SECTION -->\s*<section id="team" class="sec">.*?</section>', '', content, flags=re.DOTALL)
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

# Also update style.css for Lunar Ice text visibility
with open("style.css", "r", encoding="utf-8") as f:
    css = f.read()

# Change .l1 and .l2 to be more visible
css = css.replace('.l1 { color: transparent; -webkit-text-stroke: 1px rgba(255,255,255,0.5); }', 
                  '.l1 { color: var(--ice); text-shadow: 0 0 20px rgba(79,195,247,0.5); }')
css = css.replace('.l2 { color: #fff; text-shadow: 0 0 40px rgba(255,255,255,0.3); }', 
                  '.l2 { color: #fff; text-shadow: 0 0 20px rgba(255,255,255,0.8); }')

with open("style.css", "w", encoding="utf-8") as f:
    f.write(css)

print("Replacements completed successfully.")
