import numpy as np
from pathlib import Path
import rasterio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.ml.radar_io import RadarDataLoader
from src.ml.polarimetry import detect_ice
from src.shared.co_registration import CoRegistrationEngine

def run_radar_pipeline(product_id: str, label: str, date_str: str):
    print(f"Processing {label} (Target Date: {date_str})...")
    loader = RadarDataLoader("data")
    
    # Robust matching using the date string and GRI pattern
    matches = list(Path("data").glob(f"**/*{date_str}*_gri_xx_fp_hh_d18.tif"))
    if not matches:
        raise FileNotFoundError(f"Could not find GRI files for date {date_str}")
    
    actual_id = matches[0].name.split('_gri')[0]
    print(f"Matched to product ID: {actual_id}")
    stack = loader.load_gri_stack(actual_id)

    S = loader.get_scattering_matrix(stack)
    ice_mask = detect_ice(S, window_size=5)
    
    raw_mask_path = f"work_data/interim/raw_ice_mask_{label}.tif"
    meta = stack['meta'].copy()
    meta.update(dtype=rasterio.uint8, nodata=255, count=1)
    with rasterio.open(raw_mask_path, 'w', **meta) as dst:
        dst.write(ice_mask.astype(rasterio.uint8), 1)
    
    engine = CoRegistrationEngine("data/ldem_87s_5mpp.tif")
    output_path = f"work_data/interim/aligned_ice_mask_{label}.tif"
    engine.align_to_reference(raw_mask_path, output_path, is_mask=True)
    
    print(f"SUCCESS: Aligned mask saved to {output_path}")
    return output_path

if __name__ == "__main__":
    # Mapping of label to target date from audit
    products = {
        "L": "20200427",
        "S": "20200317"
    }
    
    results = {}
    for label, date in products.items():
        try:
            results[label] = run_radar_pipeline("", label, date)
        except Exception as e:
            print(f"FAILURE: {label} error: {e}")
            import traceback
            traceback.print_exc()

    print("\nRadar Pipeline Results:")
    for k, v in results.items():
        print(f"{k}: {v}")
