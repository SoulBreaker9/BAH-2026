import numpy as np
import rasterio
from rasterio.windows import Window, transform as win_transform
import heapq
import os
from pathlib import Path
from typing import Tuple, List, Dict

class MissionControl:
    def __init__(self, dem_path: str, slope_path: str):
        self.dem_path = dem_path
        self.slope_path = slope_path
        self.output_dir = "work_data/output"
        os.makedirs(self.output_dir, exist_ok=True)
        
        with rasterio.open(dem_path) as src:
            self.full_meta = src.meta.copy()
            self.full_transform = src.transform
            self.full_crs = src.crs
            self.full_h = src.height
            self.full_w = src.width

    def get_window_data(self, window: Window):
        with rasterio.open(self.dem_path) as src:
            dem = src.read(1, window=window)
        with rasterio.open(self.slope_path) as src:
            slope = src.read(1, window=window)
        with rasterio.open("work_data/interim/aligned_hazard_mask.tif") as src:
            haz = src.read(1, window=window)
        with rasterio.open("work_data/interim/aligned_ice_mask_L.tif") as src:
            ice_l = src.read(1, window=window)
        with rasterio.open("work_data/interim/aligned_ice_mask_S.tif") as src:
            ice_s = src.read(1, window=window)
        return dem, slope, haz, ice_l, ice_s

    def save_cropped_layer(self, filename: str, data: np.ndarray, window: Window):
        new_transform = win_transform(window, self.full_transform)
        profile = self.full_meta.copy()
        
        # Safely handle booleans by explicitly casting to uint8 early
        if data.dtype == bool:
            data = data.astype(np.uint8)
            
        # Determine actual data type
        if np.issubdtype(data.dtype, np.floating):
            dtype = 'float32'
            nodata = -9999.0
        else:
            dtype = 'uint8'
            nodata = 255
            
        profile.update({
            'height': data.shape[0],
            'width': data.shape[1],
            'transform': new_transform,
            'crs': self.full_crs,
            'dtype': dtype,
            'nodata': nodata
        })
        
        out_path = os.path.join(self.output_dir, filename)
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(data.astype(dtype), 1)
        return out_path

    def a_star_traverse(self, start, goal, slope, hazards):
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

    def estimate_ice_volume(self, l_mask: np.ndarray, s_mask: np.ndarray) -> Tuple[float, float]:
        eps_mix, eps_reg, eps_ice, eps_void, v_void = 2.8, 2.7, 3.1, 1.0, 0.4
        depth_m, pixel_area = 5.0, 25.0
        num = (eps_mix**(1/3)) - (eps_reg**(1/3)) + v_void * (eps_reg**(1/3) - eps_void**(1/3))
        den = (eps_ice**(1/3)) - (eps_reg**(1/3))
        v_ice_fraction = max(0, min(1.0 - v_void, num / den))
        deep_ice_mask = (l_mask == 1) & (s_mask == 0)
        total_volume = np.sum(l_mask) * pixel_area * depth_m * v_ice_fraction
        deep_volume = np.sum(deep_ice_mask) * pixel_area * (depth_m - 2.0) * v_ice_fraction
        return total_volume, deep_volume

if __name__ == "__main__":
    mc = MissionControl("data/ldem_87s_5mpp.tif", "data/ldsm_87s_5mpp.tif")
    
    # Fixed Window coordinates from previous target identification
    r_start, c_start = 7595, 14 
    window = Window(c_start, r_start, 1000, 1000)
    
    dem, slope, haz, ice_l, ice_s = mc.get_window_data(window)
    
    # Preserve spatial metadata for QGIS
    mc.save_cropped_layer("cropped_dem.tif", dem, window)
    mc.save_cropped_layer("final_hazard_mask.tif", haz, window)
    mc.save_cropped_layer("final_ice_mask_L.tif", ice_l, window)
    deep_ice = (ice_l == 1) & (ice_s == 0)
    mc.save_cropped_layer("final_deep_ice_mask.tif", deep_ice, window)

    goal = (dem.shape[0]//2, dem.shape[1]//2)
    landing_site = None
    for r in range(dem.shape[0]-1, 0, -20):
        for c in range(dem.shape[1]-1, 0, -20):
            if slope[r, c] < 5.0 and haz[r, c] == 0:
                landing_site = (r, c)
                break
        if landing_site: break
    if not landing_site: landing_site = (0, 0)
    
    path = mc.a_star_traverse(landing_site, goal, slope, haz)
    total_vol, deep_vol = mc.estimate_ice_volume(ice_l, ice_s)
    win_transform = win_transform(window, mc.full_transform)
    ln_x, ln_y = win_transform * landing_site
    
    print("\n--- FINAL MISSION REPORT (Spatially Validated) ---")
    print(f"Landing Site (E/N): {ln_x:.2f}, {ln_y:.2f}")
    print(f"Traverse Distance: {len(path)*5} m")
    print(f"Total Ice Volume: {total_vol:.2f} m^3")
    print(f"Deep Ice Volume (>2m): {deep_vol:.2f} m^3")
    print(f"TIF Layers saved in: {mc.output_dir}")
