# BAH-2026 Hackathon: Implementation Plan
## Detection and Characterization of Subsurface Ice in Lunar South Polar Regions

---

## 📋 Team Structure & Role Distribution

| Role | Responsibilities | Primary Objectives |
|------|------------------|-------------------|
| **ML Guy (You)** | Data processing, radar analysis, ice detection algorithms, volume estimation, path optimization algorithms | Objectives 1, 2, 5 |
| **Full Stack Guy** | Data pipeline, GIS visualization, web dashboard, API integration, deployment, presentation | Objectives 3, 4 |

---

## 🎯 Objective Mapping

| Objective | Description | Owner | Dependencies |
|-----------|-------------|-------|--------------|
| **Obj 1** | Identify & map potential subsurface ice bearing regions in PSRs, emphasis on doubly shadowed craters | ML Guy | DFSAR data, OHRC imagery, DEM |
| **Obj 2** | Utilize radar polarimetric signatures (CPR, DOP) to distinguish ice-rich regions from rocky terrain | ML Guy | DFSAR L-band & S-band data |
| **Obj 3** | Integrate terrain & illumination constraints to propose viable landing site near doubly shadowed crater | Full Stack Guy | Obj 1, 2 complete; DEM, illumination models |
| **Obj 4** | Design optimal rover traverse path from landing site to target crater | Full Stack Guy (path), ML Guy (cost function) | Obj 3 complete; DEM, slope, roughness |
| **Obj 5** | Estimate volume of subsurface ice within top ~5m at identified crater | ML Guy | Obj 1, 2 complete; dielectric models |

---

## 📊 Phase 1: Data Acquisition & Setup (Hours 0-4)

### 1.1 Account Setup & Data Access
- [ ] **Full Stack**: Register on PRADAN portal (https://pradan.issdc.gov.in/)
- [ ] **Full Stack**: Access CH2 Map Browse (https://chmapbrowse.issdc.gov.in)
- [ ] **Both**: Download target datasets for Faustini crater region:
  - DFSAR L-band (polarimetric) - `.IMG` + XML labels
  - DFSAR S-band (polarimetric) - `.IMG` + XML labels
  - OHRC calibrated products - `.IMG` + XML labels
  - Lunar South Pole DEM (SLDEM2015 or LOLA)

### 1.2 Environment Setup
- [ ] **ML Guy**: Create Python environment
```bash
conda create -n bah2026 python=3.10
conda activate bah2026
pip install numpy scipy gdal rasterio pds4-tools matplotlib opencv-python scikit-image networkx
pip install geopandas shapely pyproj rasterio[plot] tqdm
```
- [ ] **Full Stack**: Set up QGIS project with lunar coordinate system (Moon_2000 / IAU 2000:49900)
- [ ] **Both**: Install MIDAS (from VEDAS/SAC-ISRO) for radar processing validation
- [ ] **Full Stack**: Set up Git repo with structure:
```
bah2026/
├── data/              # Raw data (gitignored)
├── processed/         # Processed outputs
├── src/
│   ├── ml/           # ML Guy: radar, ice detection, volume
│   ├── fs/           # Full Stack: pipeline, viz, API
│   └── shared/       # Common utilities
├── notebooks/        # Exploration & validation
├── outputs/          # Final deliverables
└── docs/             # Documentation
```

---

## 📡 Phase 2: DFSAR Radar Processing & Ice Detection (Hours 4-12)

### 2.1 DFSAR Data Ingestion & Preprocessing (ML Guy)
- [ ] **ML**: Write `src/ml/radar_io.py` - PDS-4 reader using `pds4_tools`
  - Parse Stokes matrix components (S11, S12, S22, S33, S34, S44)
  - Handle L-band & S-band separately
  - Preserve geolocation metadata (lat/lon, incidence angle)
- [ ] **ML**: Write `src/ml/calibration.py` - Radiometric calibration
  - Apply calibration constants from XML labels
  - Noise correction (thermal noise subtraction)
  - Convert DN to sigma-nought (σ⁰)

### 2.2 Polarimetric Decomposition (ML Guy)
- [ ] **ML**: Write `src/ml/polarimetry.py` - Compute polarimetric parameters
  - **CPR (Circular Polarization Ratio)**: CPR = |RR|² / |RL|²
    - RR = Right-circular Receive, Right-circular Transmit
    - RL = Right-circular Receive, Left-circular Transmit
  - **DOP (Degree of Polarization)**: DOP = √(S1² + S2² + S3²) / S0
    - From Stokes vector [S0, S1, S2, S3]
  - **m-chi decomposition** (optional): Surface vs volume vs double-bounce
  - **Entropy/Alpha** (Cloude-Pottier) for scattering mechanism
- [ ] **ML**: Apply incidence angle normalization
  - CPR_norm = CPR × cos(θ) correction

### 2.3 Ice Detection Thresholding (ML Guy)
- [ ] **ML**: Write `src/ml/ice_detection.py` - Core detection logic
  - **Primary criterion**: CPR > 1.0 AND DOP < 0.13
  - **Secondary filters**:
    - S-band CPR > L-band CPR (penetration depth difference)
    - Low cross-pol ratio (volumetric scattering signature)
    - Exclude crater rims (high CPR from roughness)
  - Generate binary ice probability mask
  - Output: GeoTIFF with ice probability (0-1)

### 2.4 Validation & Visualization
- [ ] **ML**: Compare with PRL/ISRO published results (Sinha et al., npj Space Exploration)
- [ ] **Full Stack**: Load ice mask in QGIS, overlay on OHRC imagery
- [ ] **Both**: Create validation plots (CPR/DOP histograms, scatter plots)

---

## 🗺️ Phase 3: Terrain Analysis & Hazard Mapping (Hours 10-16)

### 3.1 OHRC Processing (Full Stack Guy)
- [ ] **FS**: Write `src/fs/ohrc_processing.py`
  - Orthorectify OHRC images using DEM
  - Co-register OHRC with DFSAR grid (sub-pixel accuracy)
  - Generate orthomosaic if multiple tiles

### 3.2 Hazard Mapping (Full Stack + ML)
- [ ] **FS**: Write `src/fs/hazard_mapping.py` in QGIS/Python
  - **Slope map**: From DEM (GDAL `gdaldem slope`)
  - **Roughness**: RMS height from DEM (3×3 or 5×5 window)
  - **Boulder detection**: 
    - ML: Train U-Net on OHRC patches (if time) or use template matching
    - FS: Manual digitization fallback
  - **Shadow mapping**: Solar illumination model for landing site analysis
- [ ] **Both**: Create composite hazard score:
  ```
  Hazard = w1×Slope + w2×Roughness + w3×Boulder_Density + w4×Permanent_Shadow
  Weights: w1=0.4, w2=0.3, w3=0.2, w4=0.1 (tunable)
  ```

---

## 🛬 Phase 4: Landing Site Selection (Hours 14-20)

### 4.1 Landing Site Criteria (Full Stack Guy)
- [ ] **FS**: Write `src/fs/landing_site.py`
  - **Hard constraints**:
    - Slope < 5° (ideally < 2°)
    - No boulders > 0.5m in 50×50m ellipse
    - Illumination > 70% (annual average)
    - Earth visibility (line-of-sight)
    - Distance to ice target: 2-10 km (rover range)
  - **Soft constraints**:
    - Proximity to multiple ice deposits
    - Scientific value of landing ellipse
    - Communication relay feasibility

### 4.2 Candidate Generation & Ranking
- [ ] **FS**: Grid search over illuminated region near target crater
- [ ] **FS**: Score each candidate, produce ranked list with trade-off analysis
- [ ] **FS**: Output: Top 3 landing sites with coordinates, hazard scores, illumination profiles

---

## 🤖 Phase 5: Rover Traverse Planning (Hours 18-26)

### 5.1 Cost Map Construction (ML Guy → Full Stack)
- [ ] **ML**: Write `src/ml/cost_map.py`
  - Input: Hazard map, ice probability map, DEM
  - Cost function: C = α×Slope + β×Roughness + γ×Shadow_Penalty - δ×Ice_Proximity
  - Shadow penalty: Exponential cost in PSR (battery drain model)
  - Ice proximity: Negative cost (attractive) near high-probability zones

### 5.2 Path Optimization (ML Guy)
- [ ] **ML**: Implement pathfinding in `src/ml/path_planning.py`
  - **Algorithm**: A* with heuristic (Euclidean + elevation)
  - **Alternative**: Dijkstra for guaranteed optimality
  - **Advanced**: RRT* for non-holonomic constraints (rover turning radius)
  - **Constraints**:
    - Max slope: 15° (rover limit)
    - Max step height: 0.3m
    - Battery budget: Calculate energy consumption per segment
    - Thermal: Survival time in shadow

### 5.3 Traverse Validation (Full Stack Guy)
- [ ] **FS**: Write `src/fs/traverse_viz.py`
  - 3D path visualization in QGIS/cesium
  - Energy profile along path (solar + battery)
  - Waypoint list with coordinates, slopes, estimated time
  - Contingency paths (Plan B, C)

---

## 🧊 Phase 6: Ice Volume Estimation (Hours 22-28)

### 6.1 Dielectric Modeling (ML Guy)
- [ ] **ML**: Write `src/ml/volume_estimation.py`
  - **Dielectric mixing model**: Looyenga / Polder-van Santen
    - ε_regolith ≈ 2.5-3.0 (dry)
    - ε_ice ≈ 3.15 (at radar frequencies)
    - ε_mix = f(ε_ice, ε_regolith, porosity, ice_fraction)
  - **Radar backscatter model**: 
    - IEM (Integral Equation Model) or Dubois model
    - Relate σ⁰ to ice concentration
  - **Penetration depth**: δ = λ / (2π√ε'' tanδ) ~ 5-10m at L-band

### 6.2 Volume Calculation
- [ ] **ML**: For each ice-probable pixel:
  - Invert backscatter to get ice volume fraction
  - Integrate over depth (0-5m) using exponential decay
  - Account for porosity (~0.4-0.5 for lunar regolith)
- [ ] **ML**: Total volume = Σ (area_pixel × depth × ice_fraction × porosity)
- [ ] **ML**: Uncertainty propagation (Monte Carlo on dielectric params)

---

## 📈 Phase 7: Integration, Visualization & Presentation (Hours 26-30)

### 7.1 Unified Dashboard (Full Stack Guy)
- [ ] **FS**: Build interactive web dashboard (Streamlit/Plotly Dash)
  - Layer toggle: Ice probability, Hazards, Landing sites, Rover path
  - 3D crater view with path
  - Metrics panel: Ice volume, traverse distance, energy budget
- [ ] **FS**: API endpoints for data serving (FastAPI)

### 7.2 Deliverables Package
- [ ] **Both**: Final report (PDF) with:
  - Methodology flowchart
  - Ice detection maps (CPR, DOP, combined)
  - Landing site analysis table
  - Rover traverse specs (distance, time, energy, risk)
  - Ice volume estimate with confidence intervals
  - Code repository (GitHub)
-ready)
- [ ] **Both**: 5-min presentation slides
- [ ] **Both**: Demo video (screen capture of dashboard)

---

## 🛠️ Technology Stack Summary

| Category | Tools/Libraries | Owner |
|----------|----------------|-------|
| **Radar Processing** | `pds4_tools`, `numpy`, `scipy`, MIDAS (validation) | ML |
| **Polarimetry** | Custom implementation (CPR, DOP, Stokes) | ML |
| **Geospatial** | `gdal`, `rasterio`, `geopandas`, `pyproj`, QGIS | Both |
| **DEM/Terrain** | `gdaldem`, `richdem`, `scikit-image` | FS |
| **ML/Pathfinding** | `networkx`, `scikit-learn` (if U-Net), custom A*/Dijkstra | ML |
| **Visualization** | `matplotlib`, `plotly`, `folium`, QGIS, CesiumJS | FS |
| **Web Dashboard** | Streamlit / Plotly Dash + FastAPI | FS |
| **Version Control** | Git + GitHub | Both |

---

## ⏰ Detailed Timeline (30 Hours)

| Time Block | ML Guy | Full Stack Guy | Sync Points |
|------------|--------|----------------|-------------|
| **0-2h** | Env setup, DFSAR reader | PRADAN download, QGIS project | Data download complete |
| **2-6h** | Calibration, polarimetry (CPR/DOP) | OHRC orthorectification, co-registration | Co-registered stacks ready |
| **6-10h** | Ice detection mask, validation | Hazard maps (slope, roughness, boulders) | Ice mask + hazard map ready |
| **10-14h** | Cost map, pathfinding algorithms | Landing site candidate generation | Landing sites selected |
| **14-18h** | Rover path optimization, energy model | Traverse viz, 3D path in QGIS | Path validated |
| **18-22h** | Dielectric modeling, volume estimation | Dashboard development | Volume estimate ready |
| **22-26h** | Uncertainty analysis, final metrics | Dashboard integration, API | All results integrated |
| **26-30h** | Report writing, slides | Demo video, final packaging | **SUBMISSION** |

---

## ✅ Quality Gates (Must Pass Before Next Phase)

| Gate | Criteria | Validation Method |
|------|----------|-------------------|
| **G1: Data Ready** | All 4 datasets downloaded, readable, co-registered | Visual overlay in QGIS |
| **G2: Ice Detection** | CPR/DOP match literature (Sinha et al.) | Histogram comparison, known crater test |
| **G3: Hazard Map** | Slope/roughness match DEM derivatives | Cross-check with LOLA profiles |
| **G4: Landing Site** | Meets all hard constraints | Automated constraint checker |
| **G5: Rover Path** | Energy budget positive, max slope < 15° | Path profile analysis |
| **G6: Volume Est** | Order-of-magnitude matches literature | Compare with PRL estimates |

---

## 🔄 Communication Protocol

- **Daily standup**: Every 6 hours (sync on progress, blockers)
- **Shared channel**: Discord/Slack for quick questions
- **Code review**: PR required for all `src/` changes
- **Data sharing**: Processed outputs in `processed/` (synced via Git LFS or shared drive)

---

## 🚨 Risk Mitigation

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| DFSAR data download fails | Medium | High | Pre-download sample data; have backup crater |
| MIDAS unavailable | High | Medium | Implement polarimetry in Python (validated) |
| Co-registration errors | Medium | High | Use tie-points + RPC refinement |
| Time overrun | High | Critical | Prioritize: Ice detection → Landing → Path → Volume |
| Battery model uncertainty | Medium | Medium | Conservative estimates, sensitivity analysis |

---

## 📝 Final Submission Checklist

- [ ] Ice probability map (GeoTIFF + PNG)
- [ ] Landing site analysis (3 candidates, ranked)
- [ ] Rover traverse (waypoints, energy profile, 3D viz)
- [ ] Ice volume estimate (with uncertainty)
- [ ] Methodology document (2-3 pages)
- [ ] Code repository (public/private GitHub)
- [ ] Dashboard demo (running or video)
- [ ] Presentation slides (10-12 slides)
- [ ] 5-min pitch ready

---

## 🎓 Key Scientific References (Must Cite)

1. **Sinha et al. (2024)** - "Subsurface ice in doubly shadowed craters..." *npj Space Exploration*
2. **Nozette et al. (1996)** - Clementine bistatic radar (CPR concept)
3. **Campbell (2012)** - "Radar remote sensing of planetary ice"
4. **Fa & Eke (2018)** - "Illumination conditions at lunar poles"
5. **ISRO DFSAR Handbook** - Technical specs for L/S band

---

*This plan is our contract. Every task has an owner, a tool, and a deadline. Update status in real-time. Let's win this.*