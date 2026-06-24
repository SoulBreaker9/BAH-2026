# Project Deep Ice: End-to-End Lunar South Pole Prospecting & Autonomous Routing Pipeline

## 1. Executive Summary
**The Mission**
Project Deep Ice is a specialized software framework designed to detect and characterize subsurface water-ice deposits in the Lunar South Polar Region (LSPR), specifically targeting "doubly shadowed craters." By fusing dual-frequency Synthetic Aperture Radar (DFSAR) data from Chandrayaan-2 with ultra-high-resolution optical imagery (OHRC) and NASA LOLA topographic models, the pipeline transforms raw planetary data into a scientifically validated ice-probability map and a safe, optimized rover traverse.

**The Challenge**
The Lunar South Pole presents an extreme engineering environment. Most traditional geospatial tools fail due to:
- **Extreme Illumination**: Low solar angles create massive shadows that "trick" standard computer vision into seeing obstacles where there are only voids.
- **Coordinate Distortion**: Raw radar data is captured in Slant Range (time-delay), creating significant geometric distortions compared to the flat ground.
- **Data Fragmentation**: Space-agency PDS4 formats are non-standard, often separating raw binaries from their geometric labels and metadata.
- **Scale**: The target 5m-per-pixel (mpp) NASA DEM represents a massive computational grid (e.g., 40,000 x 40,000 pixels), challenging standard pathfinding memory allocations.

**The Achievement**
This pipeline implements a modular, "geometry-aware" architecture. It successfully navigates the PDS4 data structure, synthesizes a custom Lunar Geographic Coordinate Reference System (CRS) to fix projection errors, applies rigorous polarimetric physics to isolate volumetric scattering (ice), and utilizes an admissible A* search to route a rover safely from a flat landing site to the target ice deposit.

---

## 2. High-Level Pipeline Architecture

```text
[Raw ISRO PDS4 Data] 
       |
       v
[Modular Processing Engines]
   ├── Deep Radar Engine (L-Band FP)  ---> [Stokes Vector] ---> [Speckle Filter] ---> [CPR/DOP Mask]
   ├── Shallow Radar Engine (S-Band FP) ---> [Dielectric Analysis] ---> [Layer Depth Map]
   └── Optical Hazard Engine (OHRC)    ---> [Top-Hat Filter] ---> [Adaptive Threshold] ---> [Hazard Mask]
       |
       v
[Spatial Co-Registration Engine]
   └── Alignment of GRI/OHRC data to NASA LOLA DEM (Moon2000_spole) using Resampling.nearest
       |
       v
[Unified Cost Grid Synthesis]
   └── Fusion of Slope (DEM) + Hazards (OHRC) + Ice Targets (DFSAR)
       |
       v
[A* Pathfinding & Volume Estimation]
   └── Optimal Traverse Generation + Looyenga Volume Calculation
```

---

## 3. Deep-Dive Engineering & Data Components

### A. Dual-Frequency Radar Engine (`polarimetry.py`)
**Mathematical Ingestion**
The pipeline avoids "intensity-only" approximations and treats the DFSAR data as complex-valued scattering matrices. To identify ice, it synthesizes Circular Polarimetric bases from Linear bases:
- **Opposite-Sense Circular (OC):** $\mathbf{S}_{RL} = \frac{\mathbf{S}_{HH} + \mathbf{S}_{VV}}{2}$
- **Same-Sense Circular (SC):** $\mathbf{S}_{RR} = \frac{\mathbf{S}_{HH} - \mathbf{S}_{VV} + i 2 \mathbf{S}_{HV}}{2}$

The **Circular Polarization Ratio (CPR)** is then computed as:
$$\text{CPR} = \frac{|\mathbf{S}_{RR}|^2}{|\mathbf{S}_{RL}|^2}$$

**Speckle Mitigation**
To prevent "salt-and-pepper" noise in the binary masks, a power-first spatial averaging approach is used. Instead of filtering the complex matrix, the pipeline computes the raw power $|S|^2$ and applies a $5 \times 5$ **Boxcar Multi-look Filter** using `scipy.ndimage.uniform_filter`. This stabilizes the variance of the polarimetric signatures before the non-linear ratio division.

**Threshold Logic & Target Reconnaissance**
The pipeline implements a tiered confidence strategy:
1. **Strict Mode**: $\text{CPR} > 1.0$ AND $\text{DOP} < 0.13$ (High-confidence subsurface ice).
2. **Relaxed Mode**: $\text{DOP} < 0.2$ (Used if strict mode returns no results).
3. **Prospecting Mode**: Target $\text{argmax}(\text{CPR})$ (Used for demo/reconnaissance to ensure the rover has a destination even in low-signal regions).

### B. Optical Hazard Engine (`optical_hazard.py`)
**PDS4 Data Access**
The pipeline bypasses `rasterio`'s inability to read raw `.img` files by using `pds4_tools`. It reads the `.xml` label, navigates the `StructureList`, and extracts the raw 2D array from the base structural element (typically `ARRAY_0`), casting it to `float32` for processing.

**Illumination Resilience (The "Shadow-as-Obstacle" Trap)**
Standard global thresholding fails at the South Pole because shadows are darker than the physical boulders. The pipeline implements:
- **Local Contrast Normalization (LCN)**: Scales local pixel intensity to standardize the image across extreme lighting gradients.
- **White Top-Hat Transform**: $\text{Top-Hat}(f) = f - \text{Opening}(f)$. This operation removes any structures larger than the $15 \times 15$ kernel, effectively "deleting" the massive, low-frequency shadows and leaving only the high-frequency, bright "peaks" (boulders and crater rims).
- **Adaptive Thresholding**: Uses `cv2.adaptiveThreshold` with a Gaussian window, evaluating pixels against their local mean rather than a global value.

### C. Co-Registration & Coordinate Geometry Engine
**The CRS Mapping Fix**
A critical failure in planetary mapping is using Earth's `EPSG:4326` (WGS84). The pipeline implements a custom **Lunar Geographic CRS**:
`+proj=longlat +R=1737400 +no_defs` (where $R$ is the lunar radius).

**Geometry Synthesis**
Since OHRC products are non-orthorectified, the pipeline:
1. Parses the `_g_grd_d18.csv` geographic grid file.
2. Extracts the absolute `min/max` Longitude and Latitude.
3. Uses `rasterio.transform.from_bounds` to instantiate the affine transform.
4. Warps the data to the **Moon2000_spole** (Polar Stereographic) grid using `Resampling.nearest` to preserve the binary integrity of the hazard masks.

---

## 4. Pathfinding & Mission Control Synthesis (`mission_control.py`)

### A. Admissible Unified Cost Matrix
To prevent infinite loops and guarantee the shortest path, the edge costs are strictly non-negative ($g(n) \ge 0$).

**The Cost Equation:**
$$\text{Cost} = 1 + \alpha(\text{Slope\_Penalty}) + \beta(\text{Shadow\_Penalty})$$
- **Base Cost**: $1$ (unit distance).
- **Slope Penalty ($\alpha$)**: Linear increase based on NASA LOLA slope.
- **Shadow Penalty ($\beta$)**: Penalty for traversing PSRs to account for battery drain.
- **No-Go Zones**: If $\text{Slope} > 15^\circ$ or $\text{HazardMask} = 1$, $\text{Cost} = \infty$.

**The Heuristic:**
An admissible Euclidean distance $h(n)$ is used to pull the rover toward the nearest target pixel in the L-Band Ice Mask.

### B. Landing Site Selection Logic
The pipeline scans the NASA DEM for a $5 \times 5$ pixel cluster meeting these criteria:
1. **Flatness**: $\text{max}(\text{Slope}) < 5^\circ$.
2. **Safety**: $\text{sum}(\text{HazardMask}) = 0$.
3. **Illumination**: Located at an elevation above the target crater's floor.
4. **Proximity**: Minimized distance to the ice target.

---

## 5. Ice Volume Estimation Model
The pipeline integrates the **Looyenga Dielectric Mixing Model** to estimate the volume of ice in the top 5 meters of regolith.

**Volume Calculation:**
$$\text{Volume} = \sum_{i=1}^{N} (\text{PixelArea} \times \text{Depth} \times \text{Volumetric\_Fraction} \times \text{Porosity})$$
- **Pixel Area**: $5\text{m} \times 5\text{m} = 25\text{ m}^2$.
- **Depth**: $5.0\text{ m}$.
- **Porosity**: $0.45$ (Standard lunar regolith).
- **Volumetric Fraction**: Derived from the processed S-band dielectric constant relative to the L-band penetration.

---

## 6. Technical Debt & Scaling Limitations

**The 1.6-Billion-Pixel Grid Limitation**
Processing a $40,000 \times 40,000$ grid with standard A* causes memory exhaustion and timeouts. Current implementation uses a stepped-sampling approach for landing site search and a localized window for pathfinding.

**Production Scaling Strategy**
To scale this to the entire Lunar South Pole, we recommend:
- **HPA* (Hierarchical Pathfinding)**: Breaking the map into clusters and routing between cluster-portals.
- **Quadtree Decomposition**: Using a sparse grid for flat areas and high-resolution grids for complex crater rims.
- **GPU Acceleration**: Moving the `S-matrix` and `Top-Hat` operations to PyTorch/CuPy to handle multi-gigabyte TIFFs in parallel.

---

## 7. Problem Statement Objective Mapping

| Objective | Implementation Module | Technique Used | Status |
|---|---|---|---|
| **1. Identify/Map Ice** | `polarimetry.py` | la-band GRI $\rightarrow$ CPR/DOP thresholds | ✅ COMPLETE |
| **2. Radar Signatures** | `polarimetry.py` | complex S-matrix $\rightarrow$ circular synthesis | ✅ COMPLETE |
| **3. Landing Site** | `mission_control.py` | DEM Slope < 5° + Hazard-Free check | ✅ COMPLETE |
| **4. Rover Path** | `mission_control.py` | Admissible A* on unified cost matrix | ✅ COMPLETE |
| **5. Ice Volume** | `mission_control.py` | Looyenga mix $\times$ 25m² pixel area | ✅ COMPLETE |
