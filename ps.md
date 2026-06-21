# Comprehensive Guide: Detection and Characterization of Subsurface Ice in Lunar South Polar Regions

This document provides an extremely detailed, beginner-friendly breakdown of the hackathon problem statement. It covers everything from understanding the core science to finding the datasets and using the right tools.

## 1. The Core Concept (Explained Simply)

**Why are we looking at the Moon's South Pole?**
The Moon doesn't have an atmosphere to protect it, and the sun shines on it differently than on Earth. At the Moon's poles, the sun is always very low on the horizon. Because of this, deep craters at the poles have areas inside them that *never* see sunlight. We call these **Permanently Shadowed Regions (PSRs)**. They are some of the coldest places in our solar system (around -248°C or 25 Kelvin). 

**What is a "Doubly Shadowed Crater"?**
Imagine a dark room (the Permanently Shadowed Region). Now imagine a deep freezer inside that dark room. That freezer is a "doubly shadowed crater." It's a smaller crater located *inside* a larger permanently shadowed crater. These spots are shielded not only from direct sunlight but also from the heat that bounces off the surrounding crater walls. Because it's so incredibly cold, if water molecules land there, they freeze instantly and stay there perfectly preserved over geological timescales.

**The Mission:**
Your goal is to use data from India's **Chandrayaan-2** spacecraft to prove that water ice is buried just beneath the surface (subsurface ice) in a specific doubly shadowed crater (like the Faustini crater). Then, you need to plan a safe route for a robotic rover to drive there and investigate it.

---

## 2. Breaking Down the Objectives (What you need to do)

1. **Find the Ice:** Identify the exact spots inside these doubly shadowed craters where ice is most likely buried under the lunar dirt (regolith).
2. **Use Radar like X-Ray Vision:** Use radar data to tell the difference between "rough, rocky ground" and "ground filled with ice."
3. **Pick a Landing Spot:** Find a safe, flat place for a spacecraft to land nearby. It needs sunlight (for solar panels to charge) and a clear line of sight to communicate with Earth.
4. **Drive the Rover:** Draw the safest and most efficient path for a robotic rover to drive from the landing spot down into the dark, icy crater.
5. **Calculate the Amount of Ice:** Estimate how much ice is hiding in the top 5 meters of dirt at the target spot using mathematical models.

---

## 3. The Datasets (Where to get them and what they are)

You will use two main cameras/sensors from the Chandrayaan-2 Orbiter:

### A. DFSAR (Dual Frequency Synthetic Aperture Radar)
*   **What it does:** It shoots microwave beams (L-band and S-band) at the Moon and measures how they bounce back. Unlike normal cameras, radar can "see" through total darkness and slightly under the dirt (penetrating up to a few meters deep).
*   **Why it's important:** Ice changes the way radar signals bounce back in a very specific way compared to dry rocks. This phenomenon is called *volumetric scattering*.

### B. OHRC (Orbiter High-Resolution Camera)
*   **What it does:** It takes incredibly sharp, high-definition black-and-white photos of the Moon's surface. 
*   **Why it's important:** You need OHRC imagery to map out the physical terrain. You have to see boulders, steep slopes, and rough terrain so you don't crash the lander or get the rover stuck.

### 📥 How to Download the Datasets
The data is completely free and public, but you must access it through the official Indian Space Research Organisation (ISRO) data portals.

1. **The Primary Portal:** Go to the **ISRO Science Data Archive (ISDA)** via the **PRADAN** portal: [https://pradan.issdc.gov.in/](https://pradan.issdc.gov.in/)
2. **Registration Required:** You must create an account and log in to download data.
3. **Finding the Specific Data:**
    * Access the **CH2 Map Browse application** ([https://chmapbrowse.issdc.gov.in](https://chmapbrowse.issdc.gov.in/)).
    * Set the map projection to look directly at the **Lunar South Pole**.
    * Under the instrument footprints, select `CH2_OHR_Calibrated_Product` for camera images and the respective `DFSAR` products for radar data.
    * Click on the footprints over your target crater (e.g., Faustini crater) to download the data files.
4. **Data Format:** The files are provided in the internationally recognized **PDS-4 (Planetary Data System)** standard. The image files usually end in `.IMG`. You will need special Python libraries (like `pds4_tools`) or advanced GIS software to open and read these files.

---

## 4. Tools & Technologies You Will Need

*   **GIS Platforms (QGIS / ArcGIS):** These are professional map-making software. You will load the lunar images here to draw your rover paths, analyze slopes, and measure distances. QGIS is highly recommended as it is free and open-source.
*   **Programming (Python):** You will use Python to do the heavy mathematical lifting.
    *   *NumPy / SciPy:* For matrix calculations and scientific computing.
    *   *GDAL / Rasterio:* Critical libraries for opening, reading, and processing massive geospatial/PDS-4 map files.
*   **MIDAS (Microwave Data Analysis Software):** 
    *   **What it is:** This is a highly specialized, indigenous software developed by the Space Applications Centre (SAC), ISRO, designed specifically to process complex radar data like DFSAR. 
    *   **Why you need it:** It contains the specific algorithms needed to calculate polarimetric features from the raw radar data.
    *   **Where to get it:** It is made available through the **VEDAS** portal (Visualisation of Earth Observation Data and Archival System) operated by SAC-ISRO, or via direct academic request to ISRO.
*   **Image Processing (ENVI):** A powerful commercial software for analyzing remote sensing imagery (though open-source Python alternatives can achieve similar results).
*   **Digital Elevation Models (DEM tools):** These are 3D topological maps showing the hills, rims, and valleys. You need this to calculate slopes and ensure your rover doesn't try to traverse a cliff.

---

## 5. Detailed Step-by-Step Workflow

Here is exactly how you should approach solving the problem from start to finish:

### Step 1: Mapping the Shadows
First, take the OHRC images and combine them with solar illumination models. Your goal is to figure out exactly where the Permanently Shadowed Regions are located. Once you have the PSRs mapped, look inside them to pinpoint the deeper, doubly shadowed craters.

### Step 2: The Magic Radar Formula (Finding the Ice)
You need to process the DFSAR radar data to compute two specific mathematical parameters that act as a signature for buried ice:
*   **CPR (Circular Polarization Ratio):** If this ratio is **greater than 1 (> 1)**, it implies the radar signal is bouncing around multiple times inside something transparent (like ice crystals) before returning to the satellite.
*   **DOP (Degree of Polarization):** If this value is **less than 0.13 (< 0.13)**, it further confirms the signal is undergoing volumetric scattering (ice) rather than surface scattering (bouncing off a hard, rough rock).
*   **Actionable Task:** Write a Python script to scan the radar data and highlight all pixels on your map where **CPR > 1 AND DOP < 0.13**. This highlighted area is your high-probability buried ice deposit!

### Step 3: Checking the Terrain Danger Zones
Now switch to the high-resolution OHRC camera images. Look closely at the icy spots you just highlighted. What does the surface look like? Are there huge boulders? Are the crater walls too steep? You need to map out "danger zones" based on surface roughness and slope.

### Step 4: Selecting the Landing Site
Find a spot safely outside the doubly shadowed crater for the spacecraft to land. 
*   **Landing Constraints:** It must be flat (slope < 5 degrees), have no large boulders or deep craters (hazard-free), receive good sunlight (> 70% illumination for solar panels), and have a direct line of sight to Earth for communication.

### Step 5: Drawing the Rover Path
Draw a line representing the path the rover will take from your landing site down to the ice deposit inside the dark crater.
*   **Traverse Constraints:** The rover runs on solar power but relies on batteries when entering the dark crater. It needs to drive quickly and efficiently through the dark zones before the battery dies. It must avoid steep hills (high slope) and rough rocky areas. 
*   **Recommendation:** Use AI-based pathfinding optimization algorithms (like A* search or Dijkstra's algorithm), assigning high "cost" to steep or rocky pixels, to calculate the absolute safest and shortest route.

### Step 6: How Much Ice is Actually There?
Using radar backscatter models based on the dielectric constant of water ice (how it interacts with microwave radiation), estimate the concentration of ice. Calculate the total volume of ice hidden in the top 5 meters of lunar soil within the target area. 

---

## 6. Background Research & Important Scientific Papers

To build a robust, winning solution, your methodology must be grounded in real science. The exact premise of this problem statement is based on recent, cutting-edge research conducted by ISRO scientists.

**Key Research Reference to Study:**
*   **Who:** Researchers from the **Physical Research Laboratory (PRL), Ahmedabad** (led by scientists like Dr. Rishitosh K. Sinha).
*   **Where:** Published recently in the prestigious journal ***npj Space Exploration*** (a Nature Portfolio journal).
*   **What they found:** They used Chandrayaan-2 DFSAR data to prove that doubly shadowed craters inside the Faustini crater at the Lunar South Pole show distinct volumetric scattering (CPR > 1, DOP < 0.13). They also observed a distinct "lobate-rim" morphology (shape), which implies that an ancient impact hit a layer of ice, causing the dirt to flow somewhat like mud.
*   **Why it matters:** This research provided some of the first definitive radar evidence of subsurface ice in these specific, ultra-cold traps, proving they are prime targets for future ISRU (In-Situ Resource Utilization) where astronauts could potentially mine the ice for drinking water and rocket fuel.

**Search Terms to read more online:** 
*   *"Chandrayaan-2 DFSAR subsurface ice Faustini crater"*
*   *"Rishitosh K. Sinha npj Space Exploration lunar south pole"*
*   *"Circular Polarization Ratio Degree of Polarization lunar ice detection"*

---

## 7. Evaluation Parameters (How to Win the Hackathon)

Judges will evaluate your project based on the following:
1.  **Scientific Robustness:** Did you actually use the CPR and DOP formulas correctly based on physics?
2.  **Accuracy:** Did you process the raw PDS-4 data correctly without corrupting the geospatial coordinates?
3.  **Feasibility:** Is your landing site realistic? Could a real lander survive landing at your chosen spot?
4.  **Rover Safety:** Is your traverse path optimized? Will your rover get stuck on a steep slope or run out of battery in the dark?
5.  **Innovation:** Did you use advanced AI algorithms for pathfinding, or create an impressive 3D visualization of the crater?
6.  **Presentation:** Is your final report clear, well-documented, mathematically sound, and easy for the judges to understand?
