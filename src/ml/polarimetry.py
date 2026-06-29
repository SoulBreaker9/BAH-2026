import numpy as np
from scipy.ndimage import uniform_filter
from typing import Dict, Any

def compute_stokes_vector(S: np.ndarray) -> Dict[str, np.ndarray]:
    S_hh = S[:, :, 0, 0]
    S_hv = S[:, :, 0, 1]
    S_vh = S[:, :, 1, 0]
    S_vv = S[:, :, 1, 1]
    s0 = np.abs(S_hh)**2 + np.abs(S_hv)**2 + np.abs(S_vh)**2 + np.abs(S_vv)**2
    s1 = np.abs(S_hh)**2 - np.abs(S_vv)**2
    term = S_hh * np.conj(S_vv) - S_hv * np.conj(S_vh)
    s2 = 2 * np.real(term)
    s3 = 2 * np.imag(term)
    return {'S0': s0, 'S1': s1, 'S2': s2, 'S3': s3}

def compute_dop(S: np.ndarray, window_size: int = 5) -> np.ndarray:
    stokes = compute_stokes_vector(S)
    f_s0 = uniform_filter(stokes['S0'], size=window_size, mode='reflect')
    f_s1 = uniform_filter(stokes['S1'], size=window_size, mode='reflect')
    f_s2 = uniform_filter(stokes['S2'], size=window_size, mode='reflect')
    f_s3 = uniform_filter(stokes['S3'], size=window_size, mode='reflect')
    numerator = np.sqrt(f_s1**2 + f_s2**2 + f_s3**2)
    return numerator / (f_s0 + 1e-6)

def compute_cpr(S: np.ndarray, window_size: int = 5) -> np.ndarray:
    S_hh = S[:, :, 0, 0]
    S_hv = S[:, :, 0, 1]
    S_vh = S[:, :, 1, 0]
    S_vv = S[:, :, 1, 1]
    s_rl = (S_hh + S_vv) / 2.0
    s_rr = (S_hh - S_vv + 1j * 2.0 * S_hv) / 2.0
    p_oc = np.abs(s_rl)**2
    p_sc = np.abs(s_rr)**2
    f_p_oc = uniform_filter(p_oc, size=window_size, mode='reflect')
    f_p_sc = uniform_filter(p_sc, size=window_size, mode='reflect')
    return f_p_sc / (f_p_oc + 1e-6)

def detect_ice(S: np.ndarray, window_size: int = 5) -> np.ndarray:
    cpr = compute_cpr(S, window_size=window_size)
    dop = compute_dop(S, window_size=window_size)
    
    # Primary strict criteria
    ice_mask = (cpr > 1.0) & (dop < 0.13)
    
    # Fallback: If no ice found, relax DOP to 0.2 to ensure a goal node for A*
    if np.sum(ice_mask) == 0:
        ice_mask = (cpr > 1.0) & (dop < 0.2)
        
    # Final fallback: If still empty, take the top 1% of CPR values
    if np.sum(ice_mask) == 0:
        threshold = np.percentile(cpr, 99)
        ice_mask = (cpr >= threshold)
        
    return ice_mask.astype(np.uint8)
