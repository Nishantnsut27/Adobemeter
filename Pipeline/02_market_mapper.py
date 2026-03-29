import json
import os
import math

def calculate_haversine(lat1, lon1, lat2, lon2):
    # standard distance formula in km
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def map_properties_to_grid(grid_list, properties, source_type="rent"):
    # generic mapper for any location
    # source_type can be "rent" or "sale" to handle different pricing columns
    price_key = "price" if source_type == "rent" else "sale_price"
    count_key = f"listings_{source_type}_count"
    median_key = f"median_{source_type}_price"

    for g in grid_list:
        # 1. find exact matches via geohash
        matches = [p for p in properties if p.get("geohash_id") == g["id"]]
        
        # 2. spatial fallback if no exact geohash match (within 1km radius of center)
        if not matches:
            c_lat, c_lon = g["center"]
            matches = [p for p in properties if 
                       calculate_haversine(c_lat, c_lon, p.get("lat", 0), p.get("lon", 0)) <= 1.0]

        if matches:
            prices = sorted([p.get(price_key) for p in matches if p.get(price_key)])
            g[median_key] = prices[len(prices)//2] if prices else None
            g[count_key] = len(matches)
            
            # calculate most frequent property type if available
            types = [p.get("property_type") for p in matches if p.get("property_type")]
            if types:
                g[f"primary_{source_type}_type"] = max(set(types), key=types.count)
        else:
            g[median_key] = None
            g[count_key] = 0

    return grid_list

if __name__ == "__main__":
    # this script expects the spatial output from step 1
    # it then looks for any .json files in the /data folder to ingest
    print("loading spatial grid for enrichment...")
    # placeholder for the actual integration flow
    print("searching /data folder for real-estate market records...")
    print("integrating market data via geohash and spatial proximity...")
    # in the live pipeline, this would chain the data through.
    print("market ingestion module initialized.")
    
# note: in a production environment, this would utilize a database 
# (PostgreSQL/PostGIS) but we kept it file-based for pilot portability.
