import re

with open('index_original.html', 'r') as f:
    html = f.read()

# 1. Add Leaflet CSS to head
html = html.replace('<link rel="stylesheet" href="style.css" />', 
                    '<link rel="stylesheet" href="style.css" />\n  <link rel="stylesheet" href="libs/leaflet.css" />')

# 2. Add Leaflet JS and script.js before app.js
html = html.replace('<script src="app.js"></script>', 
                    '<script src="libs/leaflet.js"></script>\n  <script src="script.js"></script>\n  <script src="app.js"></script>')

# 3. Replace the MISSION DOSSIER section with our new Solution, Map, Team sections
# Find the start and end of the mission section
start_marker = '<!-- 2. MISSION DOSSIER -->'
end_marker = '<!-- 3. TOOL NAVIGATION HUB -->'

# Regex to match everything between start_marker and end_marker
pattern = re.compile(rf'({re.escape(start_marker)}.*?)(?={re.escape(end_marker)})', re.DOTALL)

new_content = """<!-- 2. SOLUTION SHOWCASE -->
  <section class="sec" id="solution">
    <div class="sec-label">Solution Architecture</div>
    <h2 class="sec-h2">Interactive<br/><em>Lunar Map</em></h2>
    <p style="text-align:center; max-width:700px; margin: 0 auto 30px; font-family:var(--font-mono); color:rgba(255,255,255,0.5);">
      Explore the Faustini crater with high-resolution DFSAR overlays mapping subsurface ice and surface hazards for rover traversal.
    </p>
    
    <div id="mapContainer" style="height:600px; width:100%; max-width:1140px; margin: 0 auto 40px; border-radius:14px; border:1px solid rgba(255,255,255,0.1); overflow:hidden;"></div>
    
    <div style="text-align:center; margin-bottom: 80px;">
      <a href="docs/report.pdf" target="_blank" class="btn-p" style="text-decoration:none; display:inline-block; padding: 15px 30px; border-radius: 8px; background: rgba(0,255,136,0.1); border: 1px solid #00FF88; color: #00FF88; font-family: var(--font-mono); font-weight: bold; letter-spacing: 0.1em; text-transform: uppercase; transition: all 0.3s;">
        Download Full Report (PDF)
      </a>
    </div>
  </section>

  <div class="div"></div>

  <!-- 2.5 TEAM SECTION -->
  <section class="sec" id="team">
    <div class="sec-label">Mission Control</div>
    <h2 class="sec-h2">Our<br/><em>Team</em></h2>
    
    <div class="dash-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); padding-bottom:40px;">
      
      <div class="dash-card">
        <div class="dc-title" style="text-align:center; font-size:22px;">Team Member 1</div>
        <div class="dc-tag" style="display:block; text-align:center; margin-bottom:15px; color:#4FC3F7; border-color:rgba(79,195,247,0.3);">Project Lead</div>
        <div class="dc-desc" style="text-align:center;">AI & Radar Specialist</div>
      </div>

      <div class="dash-card">
        <div class="dc-title" style="text-align:center; font-size:22px;">Team Member 2</div>
        <div class="dc-tag" style="display:block; text-align:center; margin-bottom:15px; color:#00FF88; border-color:rgba(0,255,136,0.3);">Data Scientist</div>
        <div class="dc-desc" style="text-align:center;">Computer Vision & Mapping</div>
      </div>
      
      <div class="dash-card">
        <div class="dc-title" style="text-align:center; font-size:22px;">Team Member 3</div>
        <div class="dc-tag" style="display:block; text-align:center; margin-bottom:15px; color:#FFD700; border-color:rgba(255,215,0,0.3);">Rover Engineer</div>
        <div class="dc-desc" style="text-align:center;">Pathfinding & Robotics</div>
      </div>
      
    </div>
  </section>

  <div class="div"></div>

  """

html = pattern.sub(new_content, html)

# 4. Fix the "Explore Mission" button in the hero section to point to #solution
html = html.replace("document.getElementById('mission').scrollIntoView", "document.getElementById('solution').scrollIntoView")

with open('index.html', 'w') as f:
    f.write(html)

print("index.html rewritten successfully.")
