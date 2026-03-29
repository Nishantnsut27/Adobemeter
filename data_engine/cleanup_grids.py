import json

with open("dwarka_grid_enriched.json", "r") as f:
    grids = json.load(f)

original_count = len(grids)

# list of keys that represent actual content/data
data_keys = [
    "schools", "clinics", "cafes", "gyms", "malls", 
    "metro_stations", "universities", "corporate_offices",
    "listing_count", "listing_count_sale"
]

def is_empty(g):
    # a grid is empty if all counts are 0 and real estate prices are null
    if any(g.get(k, 0) > 0 for k in data_keys):
        return False
    
    # extra check for median prices
    if g.get("median_rent_price") is not None or g.get("median_sale_price") is not None:
        return False
        
    return True

# filter out empty ones
cleaned_grids = [g for g in grids if not is_empty(g)]

with open("dwarka_grid_enriched.json", "w") as f:
    json.dump(cleaned_grids, f, indent=2)

print(f"cleaned up grids. original: {original_count}, remaining: {len(cleaned_grids)}")
print(f"removed {original_count - len(cleaned_grids)} empty tiles.")
