# Region: Dwarka, New Delhi (Default)
DEFAULT_LAT = 28.5921
DEFAULT_LON = 77.0460
DEFAULT_RADIUS_KM = 5.0
DEFAULT_GRID_CELL_M = 500

# API Configuration
# -----------------
# Overpass API (OSM) - Publicly available, no key required for basic use.
# RapidAPI Keys (Required for active property extraction)
RAPIDAPI_KEY = "YOUR_RAPIDAPI_KEY_HERE"
RAPIDAPI_HOST_MB = "magicbricks.p.rapidapi.com"
RAPIDAPI_HOST_HOUSING = "housing-api.p.rapidapi.com"

# Google Earth Engine (GEE) - Required for live Night Light Intensity (VIIRS)
# Requires a service account or user-level authentication.
GEE_PROJECT_ID = "YOUR_GEE_PROJECT_NAME"

# Metadata for POI extraction
POI_CATEGORIES = {
    "schools": "amenity=school",
    "clinics": "amenity=clinic",
    "cafes": "amenity=cafe",
    "gyms": "leisure=fitness_centre",
    "malls": "shop=mall",
    "metro_stations": "railway=station",
    "universities": "amenity=university",
    "corporate_offices": "office=company"
}
