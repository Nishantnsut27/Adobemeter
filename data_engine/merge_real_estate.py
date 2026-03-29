import json
import math
from collections import defaultdict

def haversine_km(lat1, lon1, lat2, lon2):
    r = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return r * 2 * math.asin(math.sqrt(a))

with open("final_dwarka_5km_pilot.json", "r") as f:
    grids = json.load(f)

with open("raw_properties.json", "r") as f:
    properties = json.load(f)

grid_index = {g["id"]: g for g in grids}
grid_centres = [(g["center_lat"], g["center_lon"], g["id"]) for g in grids]

buckets = defaultdict(list)
max_snap_dist_km = 2.0
skipped = 0

for p in properties:
    lat, lon = p.get("lat"), p.get("lon")
    if not lat or not lon:
        skipped += 1
        continue

    gh = __import__("pygeohash").encode(lat, lon, precision=6)

    if gh in grid_index:
        buckets[gh].append(p)
        continue

    nearest_id = None
    nearest_dist = float("inf")
    for clat, clon, gid in grid_centres:
        d = haversine_km(lat, lon, clat, clon)
        if d < nearest_dist:
            nearest_dist = d
            nearest_id = gid

    if nearest_dist <= max_snap_dist_km:
        buckets[nearest_id].append(p)
    else:
        skipped += 1

total_mapped = sum(len(v) for v in buckets.values())
print(f"mapped {total_mapped} properties | skipped {skipped}")

for g in grids:
    props = buckets.get(g["id"], [])
    total = len(props)

    rents = sorted([p["rent_price"] for p in props if p.get("rent_price")])
    beds = [p["bedrooms"] for p in props if p.get("bedrooms")]
    baths = [p["bathrooms"] for p in props if p.get("bathrooms")]
    carpet = [p["carpet_area_sqft"] for p in props if p.get("carpet_area_sqft")]
    covered = [p["covered_area_sqft"] for p in props if p.get("covered_area_sqft")]
    furnished = sum(1 for p in props if p.get("furnishing") == "fully_furnished")
    premium = sum(1 for p in props if p.get("has_premium_amenities"))

    g["listing_count"] = total
    g["median_rent_price"] = rents[len(rents) // 2] if rents else None
    g["avg_bedrooms"] = round(sum(beds) / len(beds), 1) if beds else None
    g["avg_bathrooms"] = round(sum(baths) / len(baths), 1) if baths else None
    g["avg_carpet_area_sqft"] = round(sum(carpet) / len(carpet)) if carpet else None
    g["avg_covered_area_sqft"] = round(sum(covered) / len(covered)) if covered else None
    g["pct_fully_furnished"] = round(furnished / total, 2) if total > 0 else None
    g["pct_with_premium_amenities"] = round(premium / total, 2) if total > 0 else None

with open("dwarka_grid_enriched.json", "w") as f:
    json.dump(grids, f, indent=2)

print("done. saved to dwarka_grid_enriched.json")
