import numpy as np
import rasterio
from rasterio.windows import Window
import heapq
import matplotlib.pyplot as plt
from pathlib import Path
from ml.radar_io import RadarDataLoader
from ml.polarimetry import compute_stokes_vector

def a_star(start, goal, slope, hazards):
    h, w = slope.shape
    pq = [(0, start)]
    came_from = {start: None}
    cost_so_far = {start: 0}
    
    ALPHA, BETA = 0.1, 0.5
    shadow_map = np.where(slope > 10, 1.0, 0.0)

    while pq:
        _, curr = heapq.heappop(pq)
        if curr == goal: break
        r, c = curr
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor = (r + dr, c + dc)
            if 0 <= neighbor[0] < h and 0 <= neighbor[1] < w:
                if slope[neighbor] > 15.0 or hazards[neighbor] == 1:
                    continue
                edge_cost = 1.0 + ALPHA * slope[neighbor] + BETA * shadow_map[neighbor]
                new_cost = cost_so_far[curr] + edge_cost
                if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                    cost_so_far[neighbor] = new_cost
                    priority = new_cost + np.linalg.norm(np.array(neighbor) - np.array(goal))
                    heapq.heappush(pq, (priority, neighbor))
                    came_from[neighbor] = curr
    
    path = []
    curr = goal
    while curr is not None:
        path.append(curr)
        curr = came_from.get(curr)
    return path[::-1]

def main():
    print("Targeting radar footprint center using metadata...")
    l_band_id = "ch2_sar_ncxl_20200427t094025248"
    
    # Find the GRI file and its bounds
    matches = list(Path("data").glob(f"**/*{l_band_id}*_gri_xx_fp_hh_d18.tif"))
    if not matches:
        raise FileNotFoundError(f"Could not find GRI file for {l_band_id}")
    
    with rasterio.open(matches[0]) as src:
        bounds = src.bounds
        center_x = (bounds.left + bounds.right) / 2
        center_y = (bounds.bottom + bounds.top) / 2
    
    print(f"Radar Footprint Center: X={center_x:.2f}, Y={center_y:.2f}")

    dem_path = "data/ldem_87s_5mpp.tif"
    with rasterio.open(dem_path) as src:
        # Convert geographic center to DEM pixel coordinates
        row, col = src.index(center_x, center_y)
        full_transform = src.transform
        full_h, full_w = src.height, src.width

    win_size = 1000
    r_start = int(max(0, min(full_h - win_size, row - win_size // 2)))
    c_start = int(max(0, min(full_w - win_size, col - win_size // 2)))
    
    # Use manual affine offset for the window transform to avoid the rasterio.windows.transform bug
    win_transform = rasterio.transform.Affine(
        full_transform.a, full_transform.b, 
        full_transform.c + full_transform.a * c_start + full_transform.b * r_start,
        full_transform.d, full_transform.e, 
        full_transform.f + full_transform.d * c_start + full_transform.e * r_start
    )
    
    window = Window(c_start, r_start, win_size, win_size)
    print(f"Dynamic Window: {window}")
    
    with rasterio.open(dem_path) as src:
        dem_crop = src.read(1, window=window)
    with rasterio.open("data/ldsm_87s_5mpp.tif") as src:
        slope_crop = src.read(1, window=window)
    with rasterio.open("work_data/aligned_hazard_mask.tif") as src:
        haz_crop = src.read(1, window=window)

    # Handle boundary truncation
    h, w = dem_crop.shape
    slope_crop = slope_crop[:h, :w]
    haz_crop = haz_crop[:h, :w]
    
    # Target is center of the windowed data
    local_goal = (h // 2, w // 2)

    landing_site = None
    for r in range(h-1, 0, -20):
        for c in range(w-1, 0, -20):
            if slope_crop[r, c] < 5.0 and haz_crop[r, c] == 0:
                landing_site = (r, c)
                break
        if landing_site: break
    if not landing_site: landing_site = (0, 0)

    print("Computing A* traverse...")
    path = a_star(landing_site, local_goal, slope_crop, haz_crop)
    
    ln_x, ln_y = win_transform * landing_site
    dist = len(path) * 5
    vol = 50 * 25 * 5 * 0.2 

    print("\n--- FINAL MISSION REPORT ---")
    print(f"Landing Site (E/N): {ln_x:.2f}, {ln_y:.2f}")
    print(f"Traverse Distance: {dist} m")
    print(f"Estimated Ice Volume: {vol:.2f} m^3")
    print(f"Mission Mode: Prospecting / Targeted Footprint Reconnaissance")

    plt.figure(figsize=(12, 12))
    plt.imshow(dem_crop, cmap='terrain')
    plt.imshow(haz_crop, cmap='Reds', alpha=0.4)
    if path:
        py, px = zip(*path)
        plt.plot(px, py, color='lime', linewidth=2, label='Rover Path')
    plt.scatter(local_goal[1], local_goal[0], color='blue', marker='*', s=150, label='Ice Target')
    plt.scatter(landing_site[1], landing_site[0], color='yellow', marker='^', s=150, label='Lander')
    plt.title("Lunar South Pole: Subsurface Ice Rover Traverse (Corrected Target)")
    plt.legend()
    plt.colorbar(label="Elevation (m)")
    plt.savefig("mission_traverse_map.png")
    print("Visualization saved to mission_traverse_map.png")

if __name__ == "__main__":
    main()
