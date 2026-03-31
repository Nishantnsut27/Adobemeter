import requests
import json
import pygeohash
import time

def get_b1_metrics_from_overpass(min_lat, min_lon, max_lat, max_lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    overpass_query = f'''
    [out:json][timeout:25];
    (
      node["amenity"="school"]({bbox});
      way["amenity"="school"]({bbox});
      node["amenity"="clinic"]({bbox});
      way["amenity"="clinic"]({bbox});
      node["amenity"="hospital"]({bbox});
      way["amenity"="hospital"]({bbox});
      node["amenity"="cafe"]({bbox});
      way["amenity"="cafe"]({bbox});
      node["leisure"="fitness_centre"]({bbox});
      way["leisure"="fitness_centre"]({bbox});
      node["shop"="mall"]({bbox});
      way["shop"="mall"]({bbox});
      node["railway"="station"]({bbox});
      way["railway"="station"]({bbox});
      node["amenity"="university"]({bbox});
      way["amenity"="university"]({bbox});
      node["office"]({bbox});
      way["office"]({bbox});
    );
    out center;
    '''
    counts = {
        "schools": 0, "clinics": 0, "cafes": 0, "gyms": 0, 
        "malls": 0, "metro_stations": 0, "universities": 0, "corporate_offices": 0
    }
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        if response.status_code == 200:
            data = response.json()
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                if tags.get('amenity') == 'school': counts['schools'] += 1
                elif tags.get('amenity') in ['clinic', 'hospital']: counts['clinics'] += 1
                elif tags.get('amenity') == 'cafe': counts['cafes'] += 1
                elif tags.get('leisure') == 'fitness_centre': counts['gyms'] += 1
                elif tags.get('shop') == 'mall': counts['malls'] += 1
                elif 'station' in tags.get('railway', ''): counts['metro_stations'] += 1
                elif tags.get('amenity') == 'university': counts['universities'] += 1
                elif 'office' in tags: counts['corporate_offices'] += 1
    except Exception:
         pass
    return counts

def process_osm_grids():
    print("Loading raw grids...")
    with open("data_engine/raw_grids_5km.json", "r") as f:
        grids = json.load(f)
        
    enriched = []
    total = len(grids)
    print(f"Processing {total} grids for OpenStreetMap (OSM)...")
    
    for i, g in enumerate(grids):
        grid_id = pygeohash.encode(g['center_lat'], g['center_lon'], precision=6)
        print(f"[{i+1}/{total}] Processing Grid: {grid_id}...")
        
        # Bounding box is already in the grid object
        counts = get_b1_metrics_from_overpass(g['min_lat'], g['min_lon'], g['max_lat'], g['max_lon'])
        
        grid_data = {
            "id": grid_id,
            "center_lat": g["center_lat"],
            "center_lon": g["center_lon"],
            "min_lat": g["min_lat"],
            "min_lon": g["min_lon"],
            "max_lat": g["max_lat"],
            "max_lon": g["max_lon"],
        }
        grid_data.update(counts)
        enriched.append(grid_data)
        
        # Overpass polite delay
        time.sleep(1.0)
        
    output_file = "data_engine/osm_dwarka_grid.json"
    with open(output_file, "w") as f:
        json.dump(enriched, f, indent=2)
    print(f"Done! Saved to {output_file}")

if __name__ == "__main__":
    process_osm_grids()
