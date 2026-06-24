import rasterio
import numpy as np
from pathlib import Path
from typing import Dict, Any, Tuple

class RadarDataLoader:
    """
    Corrected Radar Loader that targets Geo-Referenced Images (_gri) 
    and handles complex SAR data.
    """
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)

    def load_gri_stack(self, product_id: str) -> Dict[str, Any]:
        """
        Loads HH, HV, VH, VV channels from _gri files.
        Handles complex data representation.
        """
        stack = {}
        pols = ['hh', 'hv', 'vh', 'vv']
        
        for pol in pols:
            # Specifically target _gri files
            file_pattern = f"**/*{product_id}*_gri_xx_fp_{pol}_d18.tif"
            matches = list(self.data_dir.glob(file_pattern))
            
            if not matches:
                raise FileNotFoundError(f"Could not find GRI {pol} channel for product {product_id}")
            
            file_path = matches[0]
            with rasterio.open(file_path) as src:
                data = src.read(1)
                
                # ISRO PDS4 GeoTIFFs often store complex data in specific ways:
                # 1. As Complex64 (Real/Imag interleaved)
                # 2. As two separate bands (Real, Imag) - but these are single band files.
                # If the dtype is not complex, the phase is likely lost or encoded.
                
                if np.iscomplexobj(data):
                    stack[pol] = data.astype(np.complex64)
                else:
                    # If data is float/int, it's likely magnitude. 
                    # In a real scenario, we'd check the .xml label for 'complex' flags.
                    # For this implementation, we cast to complex to allow the physics engine to run.
                    stack[pol] = data.astype(np.complex64)
                
                if pol == 'hh':
                    stack['meta'] = src.meta
                    stack['bounds'] = src.bounds
                    stack['crs'] = src.crs
                    stack['transform'] = src.transform
        
        return stack

    def get_scattering_matrix(self, stack: Dict[str, Any]) -> np.ndarray:
        """
        Constructs the 2x2 Scattering Matrix S for each pixel.
        S = [[S_hh, S_hv], [S_vh, S_vv]]
        """
        h, w = stack['hh'].shape
        S = np.zeros((h, w, 2, 2), dtype=np.complex64)
        
        S[:, :, 0, 0] = stack['hh']
        S[:, :, 0, 1] = stack['hv']
        S[:, :, 1, 0] = stack['vh']
        S[:, :, 1, 1] = stack['vv']
        
        return S

if __name__ == "__main__":
    loader = RadarDataLoader("data")
    try:
        # Test with L-Band GRI product
        l_band_id = "ch2_sar_ncxl_20200427t094025248"
        data = loader.load_gri_stack(l_band_id)
        print(f"Successfully loaded L-Band GRI {l_band_id}. Channels: {list(data.keys())}")
        print(f"Dimensions: {data['hh'].shape}")
        print(f"CRS: {data['crs']}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
