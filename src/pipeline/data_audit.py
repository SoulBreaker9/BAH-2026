# pyrefly: ignore [missing-import]
import rasterio
import os
from pathlib import Path

def audit_raster(file_path):
    try:
        with rasterio.open(file_path) as src:
            print(f"File: {os.path.basename(file_path)}")
            print(f"  - Dimensions: {src.width}x{src.height}")
            print(f"  - CRS: {src.crs}")
            print(f"  - Bounds: {src.bounds}")
            print(f"  - Resolution: {src.res}")
            print(f"  - Count: {src.count} bands")
            print("-" * 30)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

def main():
    data_root = Path("data")
    
    # Target files to audit
    targets = [
        "ldem_87s_5mpp.tif",
        "ldsm_87s_5mpp.tif",
    ]
    
    # Search for OHRC .img files
    ohrc_files = list(data_root.glob("**/ch2_ohr_*.img"))
    
    # Search for SAR .tif files (Full Polarimetric)
    sar_files = list(data_root.glob("**/*.tif")) 
    # Filter out the NASA DEMs from SAR search
    sar_files = [f for f in sar_files if "ldem" not in f.name and "ldsm" not in f.name]

    print("--- Auditing NASA DEMs ---")
    for t in targets:
        audit_raster(data_root / t)

    print("\n--- Auditing OHRC Imagery ---")
    for f in ohrc_files:
        audit_raster(f)

    print("\n--- Auditing SAR Data ---")
    for f in sar_files:
        audit_raster(f)

if __name__ == "__main__":
    main()
