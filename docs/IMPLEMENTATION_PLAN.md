# BAH-2026 Hackathon: Implementation Plan
## Detection and Characterization of Subsurface Ice in Lunar South Polar Regions

---

## 📋 Team Structure & Role Distribution

| Role | Responsibilities | Primary Objectives |
|------|------------------|-------------------|
| **ML Guy (You)** | Deep/Shallow Radar engines, ice detection algorithms, dielectric volume estimation, path optimization | Objectives 1, 2, 5 |
| **Full Stack Guy** | Optical Hazard engine, Data pipeline (Co-registration), GIS visualization, Web dashboard, Landing site analysis | Objectives 3, 4 |

---

## 🎯 Objective Mapping

| Objective | Description | Owner | Dependencies |
|-----------|-------------|-------|--------------|
| **Obj 1** | Identify & map subsurface ice in PSRs (Doubly Shadowed Craters) | ML Guy | Deep Radar Engine (L-Band) |
| **Obj 2** | Use CPR/DOP to distinguish ice-rich regions from rocky terrain | ML Guy | L-Band & S-Band FP data |
| **Obj 3** | Propose viable landing site near target crater | Full Stack Guy | Optical Hazard Engine, NASA LOLA DEM |
| **Obj 4** | Design optimal rover traverse path | Full Stack Guy (viz), ML Guy (A* logic) | Hazard Map, NASA LOLA Slope Map |
| **Obj 5** | Estimate ice volume in top ~5m | ML Guy | Deep Radar Engine, Dielectric Models |

---

## 🏗️ Architecture: Modular Pipeline
To overcome spatiotemporal fragmentation in PRADAN data, we have pivoted from a "perfect overlap" search to a **Modular Engine Architecture**. We build independent engines on structurally perfect datasets, which will be dynamically fused during the competition.

### 1. Deep Radar Engine (L-Band FP)
- **Target**: Subsurface penetration up to 5m.
- **Goal**: Core ice detection via volumetric scattering.
- **Key Metrics**: CPR > 1, DOP < 0.13.

### 2. Shallow Radar Engine (S-Band FP)
- **Target**: Top-layer (1-2m) dielectric properties.
- **Goal**: Establish depth differential and confirm surface-level ice signatures.

### 3. Optical Hazard Engine (OHRC)
- **Target**: 0.3m resolution imagery.
- **Goal**: Computer vision for boulder detection and shadow gradient analysis.

### 4. Terrain Foundation (NASA LOLA)
- **Target**: 5mpp High-res DEM & Pre-computed Slope Map.
- **Goal**: 3D ground truth for landing site and pathfinding.

---

## 📊 Phase 1: Setup & Data Integration (Hours 0-4)

### 1.1 Data Inventory (Downloaded)
- [ ] **DFSAR S-Band FP**: `ch2_sar_ncls_20200317T233257583_d_fp_d18`
- [ ] **DFSAR L-Band FP**: `ch2_sar_ncxl_20200427T094025248_d_fp_d18`
- [ ] **OHRC Calibrated**: `ch2_ohr_ncp_20241122T2230467113_d_img_d18`
- [ ] **NASA LOLA DEM**: `ldem_87s_5mpp.tif` (3.3 GB)
- [ ] **NASA LOLA Slope**: `ldsm_87s_5mpp.tif` (4.9 GB)

### 1.2 Environment & Pipeline Setup
- [ ] **ML Guy**: Create Python environment (numpy, scipy, gdal, rasterio, pds4-tools, networkx).
- [ ] **Full Stack**: Set up QGIS with Moon_2000 / IAU 2000:49900.
- [ ] **Both**: Implement `src/shared/co_registration.py`
  - Develop dynamic resampling and tie-point alignment to fuse isolated datasets.
  - Use `rasterio` for warping and alignment of DFSAR/OHRC to the NASA DEM grid.

---

## 📡 Phase 2: Radar Engines & Ice Detection (Hours 4-12)

### 2.1 Deep Radar Engine (ML Guy)
- [ ] **Implementation**: `src/ml/deep_radar.py`
  - Process L-band FP data $\rightarrow$ 4x4 Stokes Matrix.
  - Compute **CPR** (|RR|² / |RL|²) and **DOP** ($\sqrt{S1^2 + S2^2 + S3^2} / S0$).
  - Apply thresholds: $\text{CPR} > 1.0$ AND $\text{DOP} < 0.13$.
  - Output: High-probability ice mask.

### 2.2 Shallow Radar Engine (ML Guy)
- [ ] **Implementation**: `src/ml/shallow_radar.py`
  - Process S-band FP data.
  - Analyze dielectric constant ($\epsilon$) for the top 1-2m.
  - Compare with L-band results to map ice-layer depth.

### 2.3 Validation
- [ ] **ML**: Cross-validate signatures against Sinha et al. (npj Space Exploration).

---

## 🗺️ Phase 3: Optical Hazard Engine & Terrain (Hours 10-16)

### 3.1 Optical Hazard Engine (Full Stack Guy)
- [ ] **Implementation**: `src/fs/optical_hazard.py`
  - Use OHRC (0.3m) imagery for boulder detection via computer vision.
  - Calculate extreme shadow gradients to identify steep walls.
  - Output: Binary boulder/hazard mask.

### 3.2 Terrain Analysis (Full Stack Guy)
- [ ] **Implementation**: `src/fs/terrain_analysis.py`
  - Integrate NASA LOLA DEM (`ldem_87s_5mpp.tif`).
  - Integrate NASA LOLA Slope Map (`ldsm_87s_5mpp.tif`) to bypass compute overhead.
  - Generate 3D mesh of the target doubly shadowed crater.

---

## 🛬 Phase 4: Landing Site Selection (Hours 14-20)

### 4.1 Constraints Engine (Full Stack Guy)
- [ ] **Implementation**: `src/fs/landing_site.py`
  - **Slope Constraint**: $\text{Slope} < 5^\circ$ (using LOLA Slope Map).
  - **Hazard Constraint**: Boulder-free zone (from Optical Hazard Engine).
  - **Illumination**: Solar model to ensure $\text{Light} > 70\%$.
  - **Proximity**: Optimal distance to ice targets identified in Phase 2.

---

## 🤖 Phase 5: Rover Traverse Planning (Hours 18-26)

### 5.1 Cost Matrix Generation (ML Guy $\rightarrow$ Full Stack)
- [ ] **Implementation**: `src/ml/path_cost.py`
  - Fuse: $\text{Cost} = \alpha(\text{Slope}) + \beta(\text{Roughness}) + \gamma(\text{Shadow Penalty}) - \delta(\text{Ice Proximity})$.
  - Use pre-computed LOLA slopes to speed up matrix generation.

### 5.2 Optimization (ML Guy)
- [ ] **Implementation**: `src/ml/path_planning.py`
  - Implement A* search over the fused cost matrix.
  - Constraints: Max slope $15^\circ$, energy budget for PSR duration.

---

## 🧊 Phase 6: Ice Volume Estimation (Hours 22-28)

### 6.1 Dielectric Modeling (ML Guy)
- [ ] **Implementation**: `src/ml/volume_est.py`
  - Use L-band backscatter $\sigma^0$ and S-band surface $\epsilon$ for depth profile.
  - Model subsurface ice concentration in the top 5m using Looyenga mixing.
  - Calculate total volume per pixel: $\sum (\text{Area} \times \text{Depth} \times \text{Fraction} \times \text{Porosity})$.

---

## 📈 Phase 7: Integration & Dashboard (Hours 26-30)

### 7.1 Unified Visualization (Full Stack Guy)
- [ ] **Implementation**: Streamlit/Plotly Dashboard.
  - Dynamic layers: NASA DEM $\rightarrow$ Ice Mask $\rightarrow$ Hazard Map $\rightarrow$ Optimal Path.
  - Interactive 3D view of the traverse.

---

## 🛠️ Updated Technology Stack

| Component | Tools / Libraries | Owner |
|------------|-------------------|-------|
| **Radar Engines** | `pds4_tools`, `numpy`, `scipy` | ML |
| **Optical Engine** | `opencv-python`, `scikit-image`, `rasterio` | FS |
| **Terrain/GIS** | `gdal`, `rasterio`, `geopandas`, QGIS | FS |
| **LOLA Integration** | TIF readers, `richdem` | FS |
| **Pathfinding** | `networkx`, custom A* implementation | ML |
| **Dashboard** | Streamlit, FastAPI, Plotly | FS |

---

## ⏰ Adjusted Timeline (30 Hours)

| Time Block | ML Guy (Engines & Math) | Full Stack (Pipeline & Viz) | Sync Points |
|------------|--------------------------|-----------------------------|-------------|
| **0-4h** | Env setup, DFSAR reader | Dynamic Co-registration, DEM load | Pipeline ready for data |
| **4-10h** | L-Band & S-Band FP processing | OHRC Hazard Engine, Slope Map load | Ice mask + Hazard map |
| **10-16h** | Cost function, Path logic | Landing site ranking | Candidate sites selected |
| **16-22h** | A* Optimization, Volume Est | Traverse viz, 3D pathing | Rover route finalized |
| **22-26h** | Uncertainty analysis, Final stats | Dashboard integration, API | All results unified |
| **26-30h** | Report writing | Demo video, final packaging | **SUBMISSION** |

---

## ✅ Quality Gates
- **G1**: Co-registration of L-band, S-band, and OHRC on NASA DEM successful.
- **G2**: CPR/DOP signatures correlate with known volumetric scattering.
- **G3**: Landing site slope $\le 5^\circ$ and boulder-free.
- **G4**: Rover traverse slope $\le 15^\circ$ and energy-feasible.

---

*This plan reflects our shift to a Modular Pipeline Architecture to ensure robustness against fragmented datasets. Update status in real-time.*
