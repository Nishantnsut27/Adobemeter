import requests
import json
import os
import time
from config import MAPPLS_CLIENT_ID, MAPPLS_CLIENT_SECRET, POI_CATEGORIES, CENTER_LAT, CENTER_LON, RADIUS_KM

def get_mappls_token():
    url = "https://outpost.mapmyindia.com/api/security/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": MAPPLS_CLIENT_ID,
        "client_secret": MAPPLS_CLIENT_SECRET
    }
    try:
        response = requests.post(url, data=params)
        response.raise_for_status()
        return response.json().get("access_token")
    except Exception as e:
        print(f"Error fetching token: {e}")
        return None

def fetch_nearby_pois(token, keyword, lat, lon, radius_m):
    url = "https://atlas.mappls.com/api/places/nearby/json"
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "keywords": keyword,
        "refLocation": f"{lat},{lon}",
        "radius": radius_m
    }
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json().get("suggestedLocations", [])
    except Exception as e:
        print(f"Error fetching POIs for {keyword}: {e}")
        return []

def resolve_poi_details(token, eloc):
    # Using the verified working O2O Entity endpoint
    url = f"https://explore.mappls.com/apis/O2O/entity/{eloc}"
    headers = {"Authorization": f"Bearer {token}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        # The coordinates are nested in the response
        return {
            "lat": data.get("latitude"),
            "lon": data.get("longitude")
        }
    except Exception as e:
        print(f"Error resolving eLoc {eloc}: {e}")
        return None

def main():
    print("Starting MapmyIndia (Mappls) POI extraction with coordinate resolution...")
    token = get_mappls_token()
    if not token:
        print("Failed to obtain Mappls access token. Exiting.")
        return

    radius_m = int(RADIUS_KM * 1000)
    enriched_pois = {}
    total_found = 0
    total_resolved = 0

    for category, keyword in POI_CATEGORIES.items():
        print(f"\nCategory: {category} (Keyword: {keyword})")
        raw_results = fetch_nearby_pois(token, keyword, CENTER_LAT, CENTER_LON, radius_m)
        print(f"  Found {len(raw_results)} potential POIs.")
        
        category_pois = []
        for item in raw_results:
            eloc = item.get("eLoc")
            if not eloc: continue
            
            print(f"    Resolving: {item.get('placeName')}...", end=" ", flush=True)
            coords = resolve_poi_details(token, eloc)
            
            if coords and coords.get("lat") and coords.get("lon"):
                poi_data = {
                    "name": item.get("placeName"),
                    "address": item.get("placeAddress"),
                    "category": category,
                    "keyword": keyword,
                    "lat": float(coords["lat"]),
                    "lon": float(coords["lon"]),
                    "eloc": eloc,
                    "distance": item.get("distance")
                }
                category_pois.append(poi_data)
                total_resolved += 1
                print("OK")
            else:
                print("Failed")
            
            time.sleep(0.2) # Avoid aggressive rate limiting
        
        enriched_pois[category] = category_pois
        total_found += len(raw_results)

    output_file = "data_engine/mappls_enriched_pois.json"
    with open(output_file, "w") as f:
        json.dump(enriched_pois, f, indent=4)

    print(f"\nMappls POI resolution complete.")
    print(f"Total POIs Found in Search: {total_found}")
    print(f"Total POIs Resolved with Coordinates: {total_resolved}")
    print(f"Data saved to: {output_file}")

if __name__ == "__main__":
    main()
