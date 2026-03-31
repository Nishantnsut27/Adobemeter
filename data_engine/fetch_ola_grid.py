import requests
import json
import pygeohash
import time
from config import OLA_MAPS_API_KEY

OLA_TYPE_MAP = {
    "schools": "school",
    "clinics": "hospital|clinic",
    "cafes": "cafe|restaurant",
    "gyms": "gym",
    "malls": "shopping_mall",
    "metro_stations": "subway_station|transit_station|train_station",
    "universities": "university",
    "corporate_offices": "office|business"
}

def fetch_ola_poi_count(types_string, center_lat, center_lon, radius_m=354):
    url = "https://api.olamaps.io/places/v1/nearbysearch"
    # Ola allows multiple types separated by pipe `|` in some APIs. We can just query them individually if piped fails,
    # but let's assume it accepts standard place types. To be safe, we will loop through split types.
    total_count = 0
    for t in types_string.split('|'):
        params = {
            "location": f"{center_lat},{center_lon}",
            "radius": int(radius_m),
            "types": t,
            "layers": "venue",
            "api_key": OLA_MAPS_API_KEY
        }
        try:
            res = requests.get(url, params=params)
            if res.status_code == 200:
                data = res.json()
                predictions = data.get("predictions", [])
                total_count += len(predictions)
        except Exception as e:
            pass
        # Rate limit protection
        time.sleep(0.05)
    
    return total_count

def process_ola_grids():
    print("Loading raw grids...")
    with open("data_engine/raw_grids_5km.json", "r") as f:
        grids = json.load(f)
        
    enriched = []
    total = len(grids)
    print(f"Processing {total} grids for Ola Maps (Krutrim)...")
    
    for i, g in enumerate(grids):
        grid_id = pygeohash.encode(g['center_lat'], g['center_lon'], precision=6)
        print(f"[{i+1}/{total}] Processing Grid: {grid_id}...")
        
        grid_data = {
            "id": grid_id,
            "center_lat": g["center_lat"],
            "center_lon": g["center_lon"],
            "min_lat": g["min_lat"],
            "min_lon": g["min_lon"],
            "max_lat": g["max_lat"],
            "max_lon": g["max_lon"],
        }
        
        for cat, types_str in OLA_TYPE_MAP.items():
            count = fetch_ola_poi_count(types_str, g["center_lat"], g["center_lon"], radius_m=354)
            grid_data[cat] = count
            
        enriched.append(grid_data)
        
    output_file = "data_engine/ola_dwarka_grid.json"
    with open(output_file, "w") as f:
        json.dump(enriched, f, indent=2)
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    process_ola_grids()
