# System Architecture & Physics Whitepaper: Project Deep Ice
## Autonomous Subsurface Ice Prospecting and Rover Routing in Lunar South Polar Regions (LSPR)

**Author:** Lead Planetary Data Scientist & Systems Architect  
**Version:** 1.0.0-RELEASE  
**Classification:** Production-Grade Engineering Documentation  
**Target Hardware:** 16GB System RAM / Python 3.10 / Rasterio-GDAL Stack

---

## 1. System Overview & Sensor Fusion Architecture

Project Deep Ice is a high-fidelity sensor fusion pipeline designed to overcome the "Black Box" problem of the Lunar South Pole. The objective is to identify high-yield subsurface water-ice deposits within "doubly shadowed craters" and compute a mathematically safe, battery-optimized traverse for a robotic explorer.

### 1.1 Multi-Modal Data Ingestion
The system ingest three distinct, unaligned planetary datasets:
- **DFSAR (Dual Frequency Synthetic Aperture Radar):** Full-polarimetric (FP) L-Band ($\sim 1.2\text{ GHz}$) and S-Band ($\sim 3.2\text{ GHz}$) data. These provide the subsurface "X-ray" capabilities.
- **OHRC (Orbiter High Resolution Camera):** 0.3m resolution optical imagery. This provides the high-frequency physical terrain context (boulders, crater rims).
- **NASA LOLA DEM:** 5m-per-pixel (mpp) Digital Elevation Model. This provides the topological foundation and slope gradients.

### 1.2 The Fusion Pipeline
The core architecture transforms these disjointed arrays into a unified **Cost Grid**. The flow is:
`Raw PDS-4` $\rightarrow$ `S-Matrix Synthesis` $\rightarrow$ `Polarimetric Filtering` $\rightarrow$ `L/S Band Differential Masking` $\rightarrow$ `LOLA Alignment` $\rightarrow$ `A* Graph Traversal`.

---

## 2. Quantum Polarimetry & Subsurface Ice Detection

### 2.1 Stokes Parameters and Volumetric Scattering
The pipeline treats the lunar surface not as a set of pixels, but as a complex scattering medium. We construct a $2 \times 2$ complex scattering matrix $\mathbf{S}$:
$$\mathbf{S} = \begin{pmatrix} S_{HH} & S_{HV} \\ S_{VH} & S_{VV} \end{pmatrix}$$

To isolate ice, we analyze the **volumetric scattering**—where radar waves penetrate the regolith and bounce off subsurface ice crystals. This is captured via the **Stokes Vector** $\mathbf{S}_{vec} = [S_0, S_1, S_2, S_3]^T$:
- $S_0 = |S_{HH}|^2 + |S_{HV}|^2 + |S_{VH}|^2 + |S_{VV}|^2$
- $S_1 = |S_{HH}|^2 - |S_{VV}|^2$
- $S_2 = 2\text{Re}(S_{HH}S_{VV}^* - S_{HV}S_{VH}^*)$
- $S_3 = 2\text{Im}(S_{HH}S_{VV}^* - S_{HV}S_{VH}^*)$

### 2.2 Circular Polarization Ratio (CPR) and DOP
Ice causes a specific phase shift that converts Right-Circular (RC) waves to Left-Circular (LC). We synthesize the Circular bases:
$$\mathbf{S}_{RL} = \frac{\mathbf{S}_{HH} + \mathbf{S}_{VV}}{2}, \quad \mathbf{S}_{RR} = \frac{\mathbf{S}_{HH} - \mathbf{S}_{VV} + i 2 \mathbf{S}_{HV}}{2}$$

The **Circular Polarization Ratio (CPR)** is defined as:
$$\text{CPR} = \frac{|\mathbf{S}_{RR}|^2}{|\mathbf{S}_{RL}|^2}$$
And the **Degree of Polarization (DOP)**:
$$\text{DOP} = \frac{\sqrt{S_1^2 + S_2^2 + S_3^2}}{S_0}$$
**Ice Detection Criteria**: $\text{CPR} > 1.0$ AND $\text{DOP} < 0.13$.

### 2.3 Multi-Look Speckle Filtering
Raw SAR data suffers from speckle (coherent interference). To prevent "salt-and-pepper" noise in the ice mask, we implement **Power-First Boxcar Filtering**. Instead of filtering the complex matrix, we compute the power $|\mathbf{S}|^2$ and apply a $5 \times 5$ spatial `uniform_filter`. This multi-looking suppresses noise while preserving the volumetric signature of the ice.

---

## 3. Depth Profiling & The Looyenga Dielectric Mixing Model

### 3.1 S-Band vs. L-Band Differential
We utilize the frequency-dependent penetration depth of microwaves. S-band ($\sim 3.2\text{ GHz}$) has a shallow penetration ($\sim 2\text{m}$), while L-band ($\sim 1.2\text{ GHz}$) penetrates deeper ($\sim 5\text{m}$).
- **Deep Ice Logic**: $\text{Deep\_Ice} = (\text{L-Band\_Mask} == 1) \text{ AND } (\text{S-Band\_Mask} == 0)$.
This boolean operation isolates ice deposits that are buried too deep for S-band to detect, effectively profiling the regolith's vertical composition.

### 3.2 The Looyenga Dielectric Mixing Model
To estimate the actual volumetric yield, we use the Looyenga model for a three-component mixture (Ice, Regolith, Void). The effective dielectric constant $\epsilon_{mix}$ is given by:
$$\epsilon_{mix}^{1/3} = V_{reg}\epsilon_{reg}^{1/3} + V_{ice}\epsilon_{ice}^{1/3} + V_{void}\epsilon_{void}^{1/3}$$

**Constants Used:**
- $\epsilon_{reg} = 2.7$ (Dry Lunar Regolith)
- $\epsilon_{ice} = 3.1$ (Water Ice)
- $\epsilon_{void} = 1.0$ (Vacuum/Air)
- $V_{void} = 0.4$ (Standard lunar porosity)

**Isolating Volume Fraction ($V_{ice}$):**
Given $V_{reg} = 1.0 - V_{void} - V_{ice}$, we solve for $V_{ice}$:
$$V_{ice} = \frac{\epsilon_{mix}^{1/3} - \epsilon_{reg}^{1/3} + V_{void}(\epsilon_{reg}^{1/3} - \epsilon_{void}^{1/3})}{\epsilon_{ice}^{1/3} - \epsilon_{reg}^{1/3}}$$

**Total Volume Calculation:**
$$\text{Total Volume (m}^3) = \sum (\text{Pixels} \times 25\text{m}^2 \times 5\text{m Depth} \times V_{ice})$$

---

## 4. Shadow-Resilient Computer Vision (The Hazard Engine)

### 4.1 The "Shadow Trap" and LCN
In the LSPR, the sun is nearly parallel to the horizon. Standard binary thresholding identifies deep shadows as boulders. To solve this, we implement **Local Contrast Normalization (LCN)**, which rescales the image based on local neighborhood variance, effectively "brightening" shadows relative to their local surroundings.

### 4.2 Morphological Top-Hat Filtering
We use a **White Top-Hat Transform** to isolate physical anomalies:
$$\text{Top-Hat}(f) = f - (\text{Opening}(f, B))$$
where $B$ is a $15 \times 15$ rectangular structuring element. This removes all low-frequency structures (large shadows) and retains only high-frequency bright "peaks" (boulders).

### 4.3 Adaptive Thresholding
Final hazard extraction is performed via **Adaptive Gaussian Thresholding**:
$$\text{Pixel}(x,y) = \begin{cases} 1 & \text{if } I(x,y) > \text{local\_mean} - C \\ 0 & \text{otherwise} \end{cases}$$
This ensures that a boulder in a dimly lit area is detected relative to its immediate surroundings, not a global average.

---

## 5. Geospatial Metadata & The 1.6-Billion-Pixel Bottleneck

### 5.1 Hardware Reality & Memory Crash
The NASA LOLA DEM is a $40,000 \times 40,000$ pixel matrix. Storing this as a float32 array requires $\sim 6.4\text{GB}$. When applying A* search, the priority queue and `came_from` maps can balloon to $>20\text{GB}$ of RAM, causing immediate crashes on 16GB machines.

### 5.2 Metadata-Driven Localized Windowing
To maintain performance, we implement **Dynamic Windowing**.
1. **Footprint Analysis**: Read the raw DFSAR `_gri` metadata to find the physical center $(X, Y)$ of the radar footprint.
2. **Pixel Mapping**: Convert $(X, Y)$ to DEM pixel coordinates $(row, col)$ using the `src.index()` method.
3. **Window Extraction**: Define a $1000 \times 1000$ `rasterio.windows.Window` centered on the target.
4. **Sparsity Reduction**: Only this $1\text{M}$ pixel subset is loaded into RAM, reducing the memory footprint by $99.99\%$.

### 5.3 Coordinate Reference Systems (CRS)
To avoid "Slippage" in QGIS, we reject `EPSG:4326`. We define a custom **Lunar Geographic CRS** (`+proj=longlat +R=1737400 +no_defs`) and warp all la-band, S-band, and OHRC masks to the `Moon2000_spole` projection using **Nearest Neighbor** resampling to preserve binary mask integrity.

---

## 6. Admissible Pathfinding & Mission Control Optimization

### 6.1 Landing Site Selection
A landing site is valid only if it satisfies a $5 \times 5$ pixel window of:
- $\text{Slope} < 5^\circ$
- $\text{HazardMask} = 0$ (Zero boulders)
- Situated outside the target crater (to ensure solar power) but within $10\text{km}$ of the ice target.

### 6.2 A* Graph Traversal & Cost Function
We use an **Admissible A* Algorithm**. To prevent infinite loops and ensure a guaranteed shortest path, the edge costs must be strictly positive ($g(n) > 0$).

**Corrected Cost Formulation:**
$$\text{Cost} = 1 + \alpha(\text{Slope\_Penalty}) + \beta(\text{Shadow\_Penalty})$$
- **Base Cost**: $1$ (unit distance).
- **$\alpha$ (Slope)**: Linear penalty for increasing incline.
- **$\beta$ (Shadow)**: Penalty for traversing PSRs (battery drain).
- **No-Go Zones**: $\text{Slope} > 15^\circ \text{ OR } \text{Hazard} = 1 \rightarrow \text{Cost} = \infty$.

### 6.3 Presentation Fallback Logic
In test tiles where the strict CPR/DOP thresholds yield an empty mask, the system automatically switches to **Prospecting Mode**, targeting $\text{argmax}(\text{CPR})$. This ensures the routing geometry can be validated even in the absence of confirmed ice.
