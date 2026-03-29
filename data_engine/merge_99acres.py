import json
from collections import defaultdict

def parse_val(val):
    if not val:
        return None
    try:
        if isinstance(val, str):
            # handle "1200 sq.ft." by taking first part
            return float(val.split()[0].replace(',', ''))
        return float(val)
    except:
        return None

with open("dwarka_grid_enriched.json", "r") as f:
    grids = json.load(f)

with open("99acres_raw_properties.json", "r") as f:
    props = json.load(f)

# BUCKET PROPERTIES INTO GRIDS (Strict bounding-box matching for 100% precision)
buckets = defaultdict(list)
for p in props:
    lat, lon = p.get("lat"), p.get("lon")
    if not lat or not lon:
        continue

    # Strict 500m precision matching
    for g in grids:
        if g["min_lat"] <= lat <= g["max_lat"] and g["min_lon"] <= lon <= g["max_lon"]:
            buckets[g["id"]].append(p)
            break

for g in grids:
    p_list = buckets.get(g["id"], [])
    
    prices = sorted([p["sale_price"] for p in p_list if p.get("sale_price")])
    beds = [parse_val(p.get("bedrooms")) for p in p_list if parse_val(p.get("bedrooms"))]
    baths = [parse_val(p.get("bathrooms")) for p in p_list if parse_val(p.get("bathrooms"))]
    carpet = [parse_val(p.get("carpet_area_sqft")) for p in p_list if parse_val(p.get("carpet_area_sqft"))]
    
    types = [p.get("property_type") for p in p_list if p.get("property_type")]
    primary_type = max(set(types), key=types.count) if types else None

    # Maintain strict original schema
    g["listing_count_sale"] = len(p_list)
    g["median_sale_price"] = prices[len(prices)//2] if prices else None
    g["avg_bedrooms_sale"] = round(sum(beds)/len(beds), 1) if beds else None
    g["avg_bathrooms_sale"] = round(sum(baths)/len(baths), 1) if baths else None
    g["avg_carpet_area_sale"] = round(sum(carpet)/len(carpet)) if carpet else None
    g["primary_property_type"] = primary_type

with open("dwarka_grid_enriched.json", "w") as f:
    json.dump(grids, f, indent=2)

print(f"combined {len(props)} 99acres properties into grids with zero guessing.")
