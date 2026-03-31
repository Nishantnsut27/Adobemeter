import json

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return []

def calculate_density(grids):
    categories = ["schools", "clinics", "cafes", "gyms", "malls", "metro_stations", "universities", "corporate_offices"]
    total = 0
    breakdown = {cat: 0 for cat in categories}
    
    for g in grids:
        for cat in categories:
            val = g.get(cat, 0)
            if isinstance(val, int):
                total += val
                breakdown[cat] += val
                
    return total, breakdown

def print_comparison():
    osm_data = load_json("data_engine/osm_dwarka_grid.json")
    mappls_data = load_json("data_engine/mappls_dwarka_grid.json")
    ola_data = load_json("data_engine/ola_dwarka_grid.json")
    
    datasets = {
        "OpenStreetMap (Original)": osm_data,
        "MapmyIndia (Mappls)": mappls_data,
        "Ola Krutrim Maps": ola_data
    }
    
    print("\n" + "="*50)
    print("DWARKA 5KM POI DENSITY COMPARISON")
    print("="*50)
    
    winner_name = None
    max_density = -1
    
    for name, data in datasets.items():
        if not data:
             print(f"{name}: INCOMPLETE/MISSING DATA")
             continue
             
        total_pois, breakdown = calculate_density(data)
        print(f"\n{name} Total POIs: {total_pois}")
        print("-" * 30)
        for cat, cnt in breakdown.items():
            print(f"  {cat.capitalize()}: {cnt}")
            
        if total_pois > max_density:
             max_density = total_pois
             winner_name = name
             
    print("\n" + "="*50)
    print(f"WINNER (Highest Density): {winner_name} with {max_density} POIs")
    print("="*50)

if __name__ == "__main__":
    print_comparison()
