"""
FOOTFALL CALCULATION METHODOLOGY
--------------------------------
1. TRANSIT PROXIMITY (40%) - MOST INFLUENTIAL
   - Proximity to Metro Stations is the primary driver of crowds in Dwarka.
2. URBAN INTENSITY (30%)
   - Proven by Night Light (VIIRS) brightness measurements.
3. DESTINATION DENSITY (30%)
   - Concentration of Malls, Cafes, and Corporate Offices.
"""

import json

def apply_real_footfall():
    with open("dwarka_grid_enriched.json", "r") as f:
        grids = json.load(f)

    print(f"processing {len(grids)} real dwarka grids...")

    # helper for normalization (0 to 1)
    def normalize(val, max_v):
        return min(1.0, val / max_v) if max_v > 0 else 0

    # find max values for scaling
    max_light = max([g.get("night_light_intensity", 0) for g in grids]) or 1
    max_poi = max([(g.get("malls", 0) + g.get("cafes", 0) + g.get("offices", 0)) for g in grids]) or 1

    for g in grids:
        # A. TRANSIT SCORE (40% Weight)
        # Handle None distances (assign large default)
        metro_dist = g.get("dist_nearest_metro_km")
        if metro_dist is None: metro_dist = 10.0
        transit_score = max(0, 1 - (metro_dist / 3.0))

        # B. NIGHT LIGHT SCORE (30% Weight)
        # Proven scientific proxy for street activity
        light_score = normalize(g.get("night_light_intensity", 0), max_light)

        # C. POI DENSITY SCORE (30% Weight)
        total_poi = g.get("malls", 0) + g.get("cafes", 0) + g.get("corporate_offices", 0)
        poi_score = normalize(total_poi, max_poi)

        # FINAL CALCULATION (1-10 Scale)
        # Weights: 40% Transit, 30% Light, 30% POI
        raw_index = (transit_score * 0.40) + (light_score * 0.30) + (poi_score * 0.30)
        
        # Rounding for clean UI delivery
        g["footfall_index"] = round(raw_index * 10, 1)
        
        # High intensity flag for heat-mapping
        g["is_high_footfall"] = g["footfall_index"] >= 6.5

    with open("dwarka_grid_enriched.json", "w") as f:
        json.dump(grids, f, indent=2)

    print("successfully updated dwarka_grid_enriched.json with real footfall scores.")

if __name__ == "__main__":
    apply_real_footfall()
