import glob

html_files = glob.glob("*.html")

replacements = {
    "DEEP ICE — INITIALIZING": "SHISHIR — INITIALIZING",
    "DEEP ICE // LUNAR MISSION": "SHISHIR // LUNAR MISSION",
    "DEEP <b>ICE</b>": "SHIS<b>HIR</b>",
    "DEEP ICE": "SHISHIR",
    "Deep Ice — Real-Time Monitoring Dashboard": "Shishir — Real-Time Monitoring Dashboard",
    "Deep Ice — Multi-Sensor Fusion": "Shishir — Multi-Sensor Fusion",
    "Deep Ice — Lunar Ice Detection Mission Control": "Shishir — Lunar Ice Detection Mission Control",
    "Deep Ice — Radar Polarimetry": "Shishir — Radar Polarimetry",
    "Deep Ice — Rover AI Pathfinder": "Shishir — Rover AI Pathfinder",
    "Deep Ice — Terrain & Subsurface Analysis": "Shishir — Terrain & Subsurface Analysis",
    "Deep Ice — Team": "Shishir — Team",
    "Project Deep Ice": "Project Shishir",
}

for file_path in html_files:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    for old, new in replacements.items():
        content = content.replace(old, new)
        
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Renamed to Shishir successfully.")
