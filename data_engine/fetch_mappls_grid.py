import requests
import json
import pygeohash
import time
from config import MAPPLS_CLIENT_ID, MAPPLS_CLIENT_SECRET, POI_CATEGORIES

def get_mappls_token():
    url = "https://outpost.mapmyindia.com/api/security/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MAPPLS_CLIENT_ID,
        "client_secret": MAPPLS_CLIENT_SECRET
    }
    response = requests.post(url, data=params)
    return response.json().get("access_token")

def fetch_poi_count(token, keyword, center_lat, center_lon, radius_m=354):
    url = "https://atlas.mappls.com/api/places/nearby/json"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "keywords": keyword,
        "refLocation": f"{center_lat},{center_lon}",
        "radius": int(radius_m)
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        if res.status_code == 200:
            time.sleep(0.05)
            return len(res.json().get("suggestedLocations", []))
        return 0
    except Exception as e:
        print(f"Error fetching {keyword}: {e}")
        return 0

def process_grids():
    print("Getting Mappls token...")
    token = get_mappls_token()
    if not token:
        print("Failed to get token!")
        return
        
    print("Loading raw grids...")
    with open("data_engine/raw_grids_5km.json", "r") as f:
        grids = json.load(f)
        
    enriched = []
    total = len(grids)
    print(f"Processing {total} grids...")
    
    # Process just a pilot first or all? The user wants the dataset.
    for i, g in enumerate(grids):
        # Calculate geohash as ID as seen in the dataset
        grid_id = pygeohash.encode(g['center_lat'], g['center_lon'], precision=6)
        
        print(f"[{i+1}/{total}] Processing Grid: {grid_id} (Center: {g['center_lat']}, {g['center_lon']})")
        
        grid_data = {
            "id": grid_id,
            "center_lat": g["center_lat"],
            "center_lon": g["center_lon"],
            "min_lat": g["min_lat"],
            "min_lon": g["min_lon"],
            "max_lat": g["max_lat"],
            "max_lon": g["max_lon"],
        }
        
        # We query the center of the grid with a radius that roughly covers the 500x500 cell.
        # Diagonal from center to corner of 500x500 is ~353.5 meters
        for cat, kw in POI_CATEGORIES.items():
            count = fetch_poi_count(token, kw, g["center_lat"], g["center_lon"], radius_m=354)
            grid_data[cat] = count
            
        enriched.append(grid_data)
        # Avoid rate limiting
        time.sleep(0.1)
        
    output_file = "data_engine/mappls_dwarka_grid.json"
    with open(output_file, "w") as f:
        json.dump(enriched, f, indent=2)
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    process_grids()
