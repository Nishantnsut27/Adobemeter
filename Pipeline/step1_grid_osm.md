# Step 1: Universal Spatial Mapping Engine

This module builds the **geographic skeleton** for any target location. It combines grid generation with urban intensity metrics.

### Key Tasks:
1.  **Dynamic Bounding Box**: Uses Haversine math to find the exact rectangular span for a given radius in km.
2.  **Adaptive Grid Generation**: Creates a matrix of sub-grids (N x N) covering the entire target area.
3.  **Cross-Category Extraction**: Connects to the Overpass API to pull data globally for all configured POI categories (Schools, Metro, Retail, Offices, etc.).
4.  **Night Light Intensity**: Integrates urban brightness data (VIIRS/NASA) to determine active nightlife and commercial zones.
5.  **Distance Indexing**: Calculates the exact distance in km from every grid center to critical nodes like the **Nearest Metro** and **Nearest Mall**.

### Usage:
Run for Dwarka (Default):
```bash
python 01_spatial_engine.py
```

Run for any other location (e.g., London):
```bash
python 01_spatial_engine.py --lat 51.5074 --lon -0.1278 --radius 5 --cell 500
```

### Purpose:
Provides the structural "skeleton" of the recommendation engine, populated with live urban density data, night-time activity levels, and proximity metrics.
