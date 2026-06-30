"""
05: SUBSURFACE ICE VOLUME QUANTIFICATION
Uses dielectric mathematical models to estimate how deep the radar pulse penetrated
and calculates the total volumetric tons of water-ice trapped in the top 5 meters.
"""
import math

def calculate_ice_volume(area_sq_meters, depth_meters, dielectric_constant):
    print(f"[1/3] Analyzing target area: {area_sq_meters} m² at depth {depth_meters}m")
    
    # Pure ice has a dielectric constant of ~3.1
    # Dry lunar regolith is ~2.7
    # We estimate ice concentration based on the measured dielectric anomaly
    base_regolith_k = 2.7
    pure_ice_k = 3.1
    
    # Very simplified mixing model to find ice fraction
    if dielectric_constant <= base_regolith_k:
        ice_fraction = 0.0
    else:
        ice_fraction = (dielectric_constant - base_regolith_k) / (pure_ice_k - base_regolith_k)
        ice_fraction = min(ice_fraction, 1.0)
        
    print(f"[2/3] Dielectric inversion calculated ice fraction: {ice_fraction * 100:.1f}%")
    
    # Calculate volume
    total_volume_regolith = area_sq_meters * depth_meters
    ice_volume_cubic_meters = total_volume_regolith * ice_fraction
    
    # Density of ice is approx 917 kg/m^3
    ice_mass_kg = ice_volume_cubic_meters * 917
    ice_mass_tons = ice_mass_kg / 1000
    
    return ice_volume_cubic_meters, ice_mass_tons

if __name__ == "__main__":
    print("--- INITIATING SUBSURFACE QUANTIFICATION ---")
    crater_area = 50000 # 50,000 sq meters
    probe_depth = 5.0 # Analyzing top 5 meters
    measured_dielectric = 2.95 # Higher than dry dirt, indicates ice mix
    
    vol, tons = calculate_ice_volume(crater_area, probe_depth, measured_dielectric)
    
    print(f"[3/3] ESTIMATED ICE DEPOSIT: {vol:.1f} cubic meters ({tons:.1f} metric tons)")
    print("--- PROCESS COMPLETE ---\n")
