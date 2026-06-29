import rasterio
from glob import glob

print("Checking output TIFs:")
for f in glob('work_data/output/*.tif'):
    try:
        with rasterio.open(f) as src:
            print(f"File: {f}")
            print(f"  CRS: {src.crs}")
            print(f"  Transform: {src.transform}")
            print(f"  Dtype: {src.dtypes[0]}")
            print(f"  Nodata: {src.nodata}")
            print(f"  Shape: {src.shape}")
    except Exception as e:
        print(f"Error opening {f}: {e}")
