document.addEventListener('DOMContentLoaded', () => {
  // Initialize Leaflet Map
  const mapContainer = document.getElementById('mapContainer');
  if (mapContainer) {
    // Create map with simple CRS for image overlay
    const map = L.map('mapContainer', {
      crs: L.CRS.Simple,
      minZoom: -1,
      maxZoom: 3,
      zoomControl: false
    });

    // Dimensions of the mission traverse map
    const w = 2000, h = 2000;
    const bounds = [[0, 0], [h, w]];

    // Add base image overlay
    const overlay = L.imageOverlay('assets/mission_traverse_map.png', bounds).addTo(map);

    // Fit map to bounds
    map.fitBounds(bounds);
    
    // Add custom zoom controls
    L.control.zoom({ position: 'bottomright' }).addTo(map);

    // Add an interactive marker for the target landing site
    const targetSite = L.marker([h/2 + 200, w/2 - 100]).addTo(map);
    targetSite.bindPopup("<div style='color:black; font-family:monospace; text-align:center;'><b>TARGET: Faustini PSR</b><br>Safe Landing Site Found</div>");

    // Fix map issue when un-hidden or scrolled into view
    setTimeout(() => { map.invalidateSize(); }, 500);
  }
});
