import json
import matplotlib.pyplot as plt
import numpy as np

def load_json(filepath):
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return []

def get_total_pois(grid_obj):
    categories = ["schools", "clinics", "cafes", "gyms", "malls", "metro_stations", "universities", "corporate_offices"]
    return sum(grid_obj.get(cat, 0) for cat in categories)

# Load data
osm = load_json("data_engine/osm_dwarka_grid.json")
mappls = load_json("data_engine/mappls_dwarka_grid.json")
ola = load_json("data_engine/ola_dwarka_grid.json")

# Take first 20 grids
limit = 20
grid_ids = [g['id'] for g in osm[:limit]]
counts_osm = [get_total_pois(g) for g in osm[:limit]]
counts_mappls = [get_total_pois(g) for g in mappls[:limit]]
counts_ola = [get_total_pois(g) for g in ola[:limit]]

# Plotting
x = np.arange(len(grid_ids))
width = 0.25

fig, ax = plt.subplots(figsize=(16, 8))
rects1 = ax.bar(x - width, counts_osm, width, label='OSM', color='#1f77b4')
rects2 = ax.bar(x, counts_mappls, width, label='Mappls', color='#ff7f0e')
rects3 = ax.bar(x + width, counts_ola, width, label='Ola Krutrim', color='#2ca02c')

ax.set_ylabel('Total POIs (Aggregate Categories)', fontsize=12)
ax.set_title('Grid-Wise Density Comparison (First 20 Grids - Dwarka Pilot)', fontsize=16, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(grid_ids, rotation=45, ha="right")
ax.legend()

ax.grid(axis='y', linestyle='--', alpha=0.6)

def autolabel(rects):
    for rect in rects:
        height = rect.get_height()
        ax.annotate(f'{height}',
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center', va='bottom', fontsize=8)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

fig.tight_layout()

# Save image
output_img = r"C:\Users\Nishant Raj\.gemini\antigravity\brain\038a6b52-c635-4d94-bb11-f8e54cd3fe37\grid_wise_comparison.png"
plt.savefig(output_img, dpi=300)
print(f"Grid-wise plot saved to {output_img}")
