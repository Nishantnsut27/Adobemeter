import json

def prune_empty_tiles(grid_data, min_listings=1, min_poi_count=0):
    # universal cleanup script to remove "voids" from the final recommendation data
    # it targets tiles that have zero urban significance
    
    original_size = len(grid_data)
    
    # define which counts we should check for "urban content"
    critical_poi_keys = ["schools", "clinics", "malls", "metro", "offices"]
    
    def has_content(g):
        # 1. check if it has any POIs (from OSM)
        if any(g.get(k, 0) > min_poi_count for k in critical_poi_keys):
            return True
        
        # 2. check if it has any real-estate listings (Rent or Sale)
        if g.get("listings_rent_count", 0) >= min_listings:
            return True
        if g.get("listings_sale_count", 0) >= min_listings:
            return True
        
        # 3. check for price data directly
        if g.get("median_rent_price") or g.get("median_sale_price"):
            return True
            
        return False

    # Perform the pruning
    cleaned_grid = [g for g in grid_data if has_content(g)]
    
    print(f"data cleanup finished for anyplace.")
    print(f"original: {original_size} tiles, remaining: {len(cleaned_grid)} active tiles.")
    print(f"pruned {original_size - len(cleaned_grid)} empty/void regions.")
    
    return cleaned_grid

if __name__ == "__main__":
    print("optimizing final recommendation engine data...")
    # placeholder for the full execution flow
    print("cleaning up empty/void areas...")
    print("final delivery object ready.")
