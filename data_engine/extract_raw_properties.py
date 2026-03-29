import json
import requests
import time
import random

# rapidapi config - magicbricks scraper
api_host = "magicbricks-api.p.rapidapi.com"
api_endpoint = "https://magicbricks-api.p.rapidapi.com/scrapers/api/magicbricks/property/listing-by-url"
api_keys = [
    "79a993ef0bmsh9e88405f32bcfe0p1455e8jsnd9550e55fbe6",
    "e307904984msh61a0bf98e12ab91p16a8c2jsn8df8fadeb444",
    "64760d4efamsh778c52d664f4989p1058e5jsnacb1fe8911a1"
]

def get_properties_for_sector(sector_num):
    target_url = f"https://www.magicbricks.com/property-for-rent/residential-real-estate?cityName=New-Delhi&Locality=Dwarka-Sector-{sector_num}"
    key = random.choice(api_keys)
    headers = {
        "Content-Type": "application/json",
        "x-rapidapi-host": api_host,
        "x-rapidapi-key": key
    }
    payload = {"url": target_url}
    
    print(f"scraping: dwarka sector {sector_num}...")
    try:
        res = requests.post(api_endpoint, json=payload, headers=headers)
        if res.status_code == 200:
            return res.json().get('data', [])
        elif res.status_code == 429:
            print("rate limited. sleeping 5s...")
            time.sleep(5)
            return []
    except Exception as e:
        print(f"failed for sector {sector_num}: {e}")
    return []

def extract_property(raw, sector_num):
    # pull exact lat/lon from location field "lat,lon"
    loc = raw.get('location', '')
    prop_lat, prop_lon = None, None
    if loc:
        try:
            parts = loc.split(',')
            prop_lat = float(parts[0].strip())
            prop_lon = float(parts[1].strip())
        except:
            pass

    desc = str(raw.get('description', '')).lower()
    amenities = str(raw.get('amenities', '')).lower()

    # infer furnishing from description text
    if 'fully furnished' in desc:
        furnishing = 'fully_furnished'
    elif 'semi furnished' in desc or 'semi-furnished' in desc:
        furnishing = 'semi_furnished'
    elif 'unfurnished' in desc:
        furnishing = 'unfurnished'
    else:
        furnishing = None

    # detect premium amenities
    has_premium = any(k in amenities for k in ['pool', 'gym', 'club', 'squash', 'tennis'])

    return {
        "mb_id": raw.get('id'),
        "sector": sector_num,
        "lat": prop_lat,          # precise lat for grid mapping later
        "lon": prop_lon,          # precise lon for grid mapping later
        "rent_price": raw.get('price'),
        "bedrooms": raw.get('bedrooms'),
        "bathrooms": raw.get('bathrooms'),
        "covered_area_sqft": raw.get('covered_area'),
        "carpet_area_sqft": raw.get('carpet_area'),
        "furnishing": furnishing,
        "has_premium_amenities": has_premium,
        "posted_date": raw.get('posted_date'),
        "name": raw.get('name')
    }

def run_extractor():
    all_cleaned = []

    for sec in range(1, 24):
        raw_props = get_properties_for_sector(sec)
        
        for r in raw_props:
            cleaned = extract_property(r, sec)
            # only store if we have a valid lat/lon (needed for grid mapping)
            if cleaned['lat'] and cleaned['lon']:
                all_cleaned.append(cleaned)
        
        time.sleep(1.5) # breather between calls

    print(f"\ntotal valid properties extracted: {len(all_cleaned)}")
    
    with open("raw_properties.json", "w") as f:
        json.dump(all_cleaned, f, indent=2)
    
    print("saved to raw_properties.json — ready for grid integration later.")

run_extractor()
