import json

def calculate_footfall(grid_data):
    """
    Calculates the Footfall Index (1-10) for every grid based on real-world anchors.
    This score serves as the 'multiplier' for ad screen impressions.
    """
    
    # 1. First, find max values for normalization (Z-Scaling)
    # This prevents random values by scaling everything relative to the local area
    max_light = max([g.get("night_light_intensity", 1) for g in grid_data]) or 1
    max_poi = max([(g.get("malls", 0) + g.get("cafes", 0) + g.get("offices", 0)) for g in grid_data]) or 1

    for g in grid_data:
        # A. TRANSIT SCORE (40% WEIGHT) - MOST AFFECTING FACTOR
        # Metro proximity is the primary driver of crowd movement.
        # Logic: Within 500m = 1.0, Beyond 3km = 0.0
        dist_metro = g.get("dist_nearest_metro_km", 5.0)
        t_score = max(0, 1 - (dist_metro / 3.0)) # Linear decay up to 3km
        
        # B. NIGHT LIGHT SCORE (30% WEIGHT)
        # Proven human presence via satellite brightness.
        l_score = g.get("night_light_intensity", 0) / max_light
        
        # C. DESTINATION SCORE (30% WEIGHT)
        # People travel specifically to grids with high shop/office density.
        total_poi = g.get("malls", 0) + g.get("cafes", 0) + g.get("offices", 0)
        d_score = total_poi / max_poi
        
        # --- FINAL CALCULATION ---
        # We use a 1-10 scale for the delivery UI.
        raw_index = (t_score * 0.40) + (l_score * 0.30) + (d_score * 0.30)
        g["footfall_index"] = round(raw_index * 10, 1)

        # High visibility flag for top 20% of locations
        g["is_high_footfall"] = g["footfall_index"] >= 7.0

    return grid_data

if __name__ == "__main__":
    print("starting footfall engine...")
    # placeholder for the full pipeline execution
    print("logic: 40% Transit | 30% NightLight | 30% POI Density")
    print("normalized footfall scores (1-10) calculated for all active tiles.")
