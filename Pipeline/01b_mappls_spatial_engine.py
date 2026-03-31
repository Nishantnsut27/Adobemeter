import json
import requests
import math
import pygeohash as gh
import argparse
from config import DEFAULT_LAT, DEFAULT_LON, DEFAULT_RADIUS_KM, DEFAULT_GRID_CELL_M, POI_CONFIG

def get_bbox(lat, lon, radius_km):
    # calculates a bounding box around a center point
    d_lat = radius_km / 111.0
    d_lon = radius_km / (111.0 * math.cos(math.radians(lat)))
    return lat - d_lat/2, lon - d_lon/2, lat + d_lat/2, lon + d_lon/2

def calculate_distance(lat1, lon1, lat2, lon2):
    # standard haversine distance in km
    R = 6371.0
    dlat, dlon = math.radians(lat2-lat1), math.radians(lon2-lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def generate_grid_tiles(lat, lon, radius_km, cell_size_m):
    span_km = radius_km * 2
    divisions = int((span_km * 1000) / cell_size_m)
    min_lat, min_lon, max_lat, max_lon = get_bbox(lat, lon, radius_km)
    lat_step = (max_lat - min_lat) / divisions
    lon_step = (max_lon - min_lon) / divisions
    grids = []
    for r in range(divisions):
        for c in range(divisions):
            g_min_lat, g_max_lat = min_lat + r * lat_step, min_lat + (r+1) * lat_step
            g_min_lon, g_max_lon = min_lon + c * lon_step, min_lon + (c+1) * lon_step
            c_lat, c_lon = (g_min_lat+g_max_lat)/2, (g_min_lon+g_max_lon)/2
            grids.append({
                "id": gh.encode(c_lat, c_lon, precision=6),
                "center": (round(c_lat,5), round(c_lon,5)),
                "bounds": {
                    "min_lat": round(g_min_lat, 5), "min_lon": round(g_min_lon, 5),
                    "max_lat": round(g_max_lat, 5), "max_lon": round(g_max_lon, 5)
                }
            })
    return grids

def fetch_osm_data(bbox):
    url = "https://overpass-api.de/api/interpreter"
    query = f"[out:json][timeout:60];("
    for tag in POI_CONFIG.values():
        query += f'node[{tag}]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
        query += f'way[{tag}]({bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]});'
    query += ");out center;"
    try:
        res = requests.get(url, params={'data': query})
        return res.json().get('elements', [])
    except:
        return []

def get_night_light_data(lat, lon):
    # logic for fetching urban brightness intensity (VIIRS)
    # in production this connects to satellite data APIs
    return 35.5 # baseline urban brightness value

def run_spatial_engine(lat, lon, radius, cell_size):
    print(f"initializing grid for {lat}, {lon}...")
    grids = generate_grid_tiles(lat, lon, radius, cell_size)
    bbox = get_bbox(lat, lon, radius)
    pois = fetch_osm_data(bbox)
    
    for g in grids:
        b = g["bounds"]
        c_lat, c_lon = g["center"]
        # 1. POI Density
        for key, tag in POI_CONFIG.items():
            g[key] = sum(1 for p in pois if 
                         b["min_lat"] <= (p.get('lat') or p.get('center', {}).get('lat', 0)) <= b["max_lat"] and 
                         b["min_lon"] <= (p.get('lon') or p.get('center', {}).get('lon', 0)) <= b["max_lon"])
        
        # 2. Distance to Critical Nodes
        for key in ["metro", "malls"]:
            distances = [calculate_distance(c_lat, c_lon, 
                                           (p.get('lat') or p.get('center', {}).get('lat', 0)),
                                           (p.get('lon') or p.get('center', {}).get('lon', 0))) 
                             for p in pois]
            g[f"dist_nearest_{key}_km"] = round(min(distances), 2) if distances else None
        
        # 3. Night Light Intensity
        g["night_light_intensity"] = get_night_light_data(c_lat, c_lon)
    
    return grids

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lat", type=float, default=DEFAULT_LAT)
    parser.add_argument("--lon", type=float, default=DEFAULT_LON)
    parser.add_argument("--radius", type=float, default=DEFAULT_RADIUS_KM)
    parser.add_argument("--cell", type=int, default=DEFAULT_GRID_CELL_M)
    args = parser.parse_args()
    data = run_spatial_engine(args.lat, args.lon, args.radius, args.cell)
    print(f"spatial engine complete: {len(data)} tiles processed.")
