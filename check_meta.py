"""
DIAGNOSTIC PHASE 4: Deep inspection of where actual radar data exists,
what values it contains, and what CPR/DOP thresholds produce ice detections.
"""
import numpy as np
import rasterio
from rasterio.windows import Window
import sys

print("="*60)
print("PHASE 4: Deep inspection of actual radar data extent + values")
print("="*60)

ICE_L_PATH = "work_data/interim/aligned_ice_mask_L.tif"
ICE_S_PATH = "work_data/interim/aligned_ice_mask_S.tif"
DEM_PATH   = "data/ldem_87s_5mpp.tif"

# Data is in rows 16700-19950, cols unknown. Find exact centroid.
DATA_ROW_MID = 18325
STEP = 10

with rasterio.open(ICE_L_PATH) as src:
    nodata = src.nodata
    print(f"\nICE_L nodata={nodata}")

    # Scan row 18325 to find col extents
    win = Window(0, DATA_ROW_MID, src.width, 1)
    row = src.read(1, window=win)[0]
    valid_cols = np.where(row != nodata)[0]
    print(f"Row {DATA_ROW_MID} valid col range: {valid_cols.min()} to {valid_cols.max()}")
    center_c = int(np.median(valid_cols))
    print(f"Col centroid: {center_c}")
    print(f"Unique values in that row: {np.unique(row[row != nodata])}")
    
    # Scan a patch of rows to get full extent and value distribution
    print(f"\nFull value distribution in data region (rows 16700-19950, sample step={STEP}):")
    all_vals = []
    for r in range(16700, 19950, STEP):
        win_row = Window(0, r, src.width, 1)
        row_data = src.read(1, window=win_row)[0]
        vals = row_data[row_data != nodata]
        all_vals.extend(vals.tolist())
    
    all_vals = np.array(all_vals)
    unique, counts = np.unique(all_vals, return_counts=True)
    for v, c in zip(unique, counts):
        print(f"  value={v}: {c:,} pixels ({100*c/len(all_vals):.2f}%)")
    
    # Find BEST window: centered on data, fully within DEM valid region
    r_start = max(0, DATA_ROW_MID - 500)
    c_start = max(0, center_c - 500)
    window = Window(c_start, r_start, 1000, 1000)
    
    print(f"\n--- OPTIMAL Window ---")
    print(f"r_start={r_start}, c_start={c_start}")
    
    # Check ice values in this window
    ice_patch = src.read(1, window=window)
    ice_valid = ice_patch[ice_patch != nodata]
    ice_ones = np.sum(ice_patch == 1)
    ice_zeros = np.sum(ice_patch == 0)
    print(f"Window ice_l: nodata={np.sum(ice_patch == nodata):,}, zeros={ice_zeros:,}, ones={ice_ones:,}")

# Check DEM at this window
with rasterio.open(DEM_PATH) as src:
    r_start_local = max(0, DATA_ROW_MID - 500)
    c_start_local = max(0, center_c - 500)
    window = Window(c_start_local, r_start_local, 1000, 1000)
    dem_patch = src.read(1, window=window).astype(np.float32)
    valid_dem = dem_patch[~np.isnan(dem_patch)]
    wt = src.window_transform(window)
    print(f"\nDEM at this window:")
    print(f"  valid pixels: {len(valid_dem):,}")
    if len(valid_dem):
        print(f"  elevation: {valid_dem.min():.1f}m to {valid_dem.max():.1f}m")
    print(f"  window_transform: {wt}")

# Also check the raw ice mask (pre-alignment) for ice pixels
print("\n\nChecking raw (pre-alignment) ice mask for value distribution:")
RAW_ICE_L = "work_data/interim/raw_ice_mask_L.tif"
try:
    with rasterio.open(RAW_ICE_L) as src:
        raw = src.read(1)
        unique, counts = np.unique(raw, return_counts=True)
        print(f"  shape: {src.shape}")
        for v, c in zip(unique, counts):
            print(f"  value={v}: {c:,} pixels")
except Exception as e:
    print(f"  Error: {e}")
