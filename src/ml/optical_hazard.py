import numpy as np
import cv2
import rasterio
from rasterio.transform import from_bounds
from pathlib import Path
from typing import Tuple
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.shared.co_registration import CoRegistrationEngine
import pds4_tools

class OpticalHazardEngine:
    def __init__(self, reference_dem_path: str):
        self.ref_engine = CoRegistrationEngine(reference_dem_path)

    def load_pds4_img(self, img_path: str) -> np.ndarray:
        label_path = img_path.replace('.img', '.xml')
        if not Path(label_path).exists():
            raise FileNotFoundError(f"Label file not found at {label_path}")
        handles = pds4_tools.read(label_path)
        img = np.array(handles[0].data).astype(np.float32)
        if img.ndim > 2:
            img = img.squeeze()
        return img

    def get_transform_from_csv(self, img_path: str) -> Tuple[float, float, float, float]:
        csv_path = Path(img_path).parent.parent.parent.parent / "geometry" / "calibrated" / "20241122" / "ch2_ohr_ncp_20241122T2230467113_g_grd_d18.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"Grid CSV not found at {csv_path}")
        
        import pandas as pd
        df = pd.read_csv(csv_path)
        cols = df.columns
        lon_col = [c for c in cols if 'lon' in c.lower()][0]
        lat_col = [c for c in cols if 'lat' in c.lower()][0]
        return df[lon_col].min(), df[lat_col].min(), df[lon_col].max(), df[lat_col].max()

    def process_hazards(self, img: np.ndarray) -> np.ndarray:
        img_norm = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        tophat = cv2.morphologyEx(img_norm, cv2.MORPH_TOPHAT, kernel)
        hazard_mask = cv2.adaptiveThreshold(
            tophat, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 21, 2
        )
        return (hazard_mask > 0).astype(np.uint8)

    def generate_aligned_hazard_map(self, img_path: str, output_path: str):
        img = self.load_pds4_img(img_path)
        h, w = img.shape
        west, south, east, north = self.get_transform_from_csv(img_path)
        
        # USE LUNAR GEOGRAPHIC CRS instead of Earth EPSG:4326
        lunar_crs = '+proj=longlat +R=1737400 +no_defs'
        transform = from_bounds(west, south, east, north, w, h)
        
        mask = self.process_hazards(img)
        raw_mask_path = "work_data/interim/raw_hazard_mask.tif"
        with rasterio.open(
            raw_mask_path, 'w', 
            driver='GTiff', height=h, width=w, 
            count=1, dtype=rasterio.uint8, nodata=255,
            crs=lunar_crs, transform=transform
        ) as dst:
            dst.write(mask, 1)
        
        self.ref_engine.align_to_reference(raw_mask_path, output_path, is_mask=True)
        return output_path

if __name__ == "__main__":
    ohrc_file = "data/ch2_ohr_ncp_20241122T2230467113_d_img_d18/data/calibrated/20241122/ch2_ohr_ncp_20241122T2230467113_d_img_d18.img"
    ref_dem = "data/ldem_87s_5mpp.tif"
    out_map = "work_data/interim/aligned_hazard_mask.tif"
    try:
        engine = OpticalHazardEngine(ref_dem)
        engine.generate_aligned_hazard_map(ohrc_file, out_map)
        print(f"SUCCESS: Hazard map aligned to DEM: {out_map}")
    except Exception as e:
        print(f"FAILURE: Optical Engine error: {e}")
        import traceback
        traceback.print_exc()
