import rasterio
from rasterio.warp import reproject
from rasterio.enums import Resampling
import numpy as np
from pathlib import Path
from typing import Union

class CoRegistrationEngine:
    """
    Handles the spatial alignment of multiple lunar datasets.
    Warps source rasters (Radar/Optical) to match the Reference Raster (NASA DEM).
    """
    def __init__(self, reference_path: str):
        self.reference_path = Path(reference_path)
        with rasterio.open(self.reference_path) as ref:
            self.ref_meta = ref.meta.copy()
            self.ref_crs = ref.crs
            self.ref_transform = ref.transform
            self.ref_width = ref.width
            self.ref_height = ref.height

    def align_to_reference(self, source_path: str, output_path: str, is_mask: bool = False):
        """
        Reprojects and resamples source_path to match the reference_path.
        
        RESAMPLING CONSTRAINT:
        - Continuous data (backscatter/intensity): Bilinear interpolation.
        - Binary/Categorical data (masks): Nearest Neighbor interpolation.
        """
        with rasterio.open(source_path) as src:
            # Select resampling mode based on data type
            resampling_method = Resampling.nearest if is_mask else Resampling.bilinear
            
            # Prepare the output metadata
            out_meta = src.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": self.ref_height,
                "width": self.ref_width,
                "transform": self.ref_transform,
                "crs": self.ref_crs
            })

            # Create the output file and warp the data
            with rasterio.open(output_path, "w", **out_meta) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=self.ref_transform,
                        dst_crs=self.ref_crs,
                        resampling=resampling_method
                    )
        return output_path

if __name__ == "__main__":
    # Test the engine
    try:
        ref_file = "data/ldem_87s_5mpp.tif"
        from pathlib import Path
        matches = list(Path("data").glob("**/*_gri_xx_fp_hh_d18.tif"))
        if not matches:
            print("Source GRI file not found for test.")
        else:
            actual_src = str(matches[0])
            out_file = "work_data/test_aligned_gri.tif"
            
            engine = CoRegistrationEngine(ref_file)
            # Testing as continuous data
            engine.align_to_reference(actual_src, out_file, is_mask=False)
            print(f"SUCCESS: Aligned {actual_src} to DEM using Bilinear resampling.")
            
            # Testing as mask
            out_mask_file = "work_data/test_aligned_mask.tif"
            engine.align_to_reference(actual_src, out_mask_file, is_mask=True)
            print(f"SUCCESS: Aligned {actual_src} to DEM using Nearest Neighbor resampling.")

    except Exception as e:
        print(f"FAILURE: Co-registration test failed: {e}")
        import traceback
        traceback.print_exc()
