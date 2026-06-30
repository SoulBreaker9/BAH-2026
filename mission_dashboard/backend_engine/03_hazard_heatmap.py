"""
03: TERRAIN ANALYSIS & HAZARD HEATMAP
This script processes OHRC (Optical High Resolution Camera) Digital Elevation Models.
It calculates surface slopes to ensure the rover does not exceed 10-degree inclinations,
generating a safe "cost map" for the pathfinder.
"""
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt

def generate_dem(shape=(100, 100)):
    print("[1/3] Generating synthetic OHRC Digital Elevation Model (DEM)...")
    # Base terrain
    x = np.linspace(-5, 5, shape[0])
    y = np.linspace(-5, 5, shape[1])
    X, Y = np.meshgrid(x, y)
    Z = np.sin(X) + np.cos(Y) * 0.5
    
    # Add a steep crater
    for i in range(shape[0]):
        for j in range(shape[1]):
            dist = np.sqrt((i - 70)**2 + (j - 70)**2)
            if dist < 15:
                Z[i, j] -= (15 - dist) * 0.8  # Deep steep crater
                
    return Z

def calculate_slope(dem):
    print("[2/3] Calculating terrain slope gradients (Sobel operator)...")
    dx = ndimage.sobel(dem, 0)
    dy = ndimage.sobel(dem, 1)
    # Convert gradient to degrees
    slope = np.degrees(np.arctan(np.hypot(dx, dy)))
    return slope

def create_hazard_map(slope, max_slope=10.0):
    print(f"[3/3] Creating hazard heatmap (Max Safe Slope: {max_slope}°)...")
    # Normalized cost map: 0 is safe, 1 is hazardous
    hazard_map = np.clip(slope / max_slope, 0, 1)
    # Impassable terrain (infinite cost)
    hazard_map[slope > max_slope] = np.inf
    return hazard_map

if __name__ == "__main__":
    print("--- INITIATING TERRAIN ANALYZER ---")
    dem = generate_dem()
    slope = calculate_slope(dem)
    hazard = create_hazard_map(slope)
    
    safe_percentage = (np.sum(hazard < 1.0) / hazard.size) * 100
    print(f"Terrain Analysis Complete: {safe_percentage:.1f}% of the grid is safe for traversal.")
    print("--- PROCESS COMPLETE ---\n")
