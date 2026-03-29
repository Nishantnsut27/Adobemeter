import math
import json
import config

DEG_LAT_PER_KM = 1.0 / 111.0 
DEG_LON_PER_KM = 1.0 / (111.0 * math.cos(math.radians(config.CENTER_LAT)))

def create_raw_grids():
    print(f"Generating {config.RADIUS_KM}km grids from center...")
    grids = []
    # 5km radius -> 10km diameter
    steps = int((config.RADIUS_KM * 2) / config.GRID_SIZE_KM)
    start_lat = config.CENTER_LAT - (config.RADIUS_KM * DEG_LAT_PER_KM)
    start_lon = config.CENTER_LON - (config.RADIUS_KM * DEG_LON_PER_KM)
    
    for i in range(steps):
        for j in range(steps):
            min_lat = start_lat + (i * config.GRID_SIZE_KM * DEG_LAT_PER_KM)
            max_lat = min_lat + (config.GRID_SIZE_KM * DEG_LAT_PER_KM)
            min_lon = start_lon + (j * config.GRID_SIZE_KM * DEG_LON_PER_KM)
            max_lon = min_lon + (config.GRID_SIZE_KM * DEG_LON_PER_KM)
            
            grids.append({
                "id": f"Grid_{i}_{j}",
                "center_lat": round((min_lat + max_lat) / 2, 5),
                "center_lon": round((min_lon + max_lon) / 2, 5),
                "min_lat": round(min_lat, 5),
                "min_lon": round(min_lon, 5),
                "max_lat": round(max_lat, 5),
                "max_lon": round(max_lon, 5),
                "b1_metrics": {"schools": 0, "clinics": 0, "cafes": 0},
                "b3_real_estate": {
                    "avg_rent": None, 
                    "proxy_income": None,
                    "night_light_intensity": None
                }
            })
            
    with open("raw_grids_5km.json", "w") as f:
        json.dump(grids, f, indent=2)
    print(f"Complete! Saved {len(grids)} pure raw grids to raw_grids_5km.json!")

if __name__ == "__main__":
    create_raw_grids()
