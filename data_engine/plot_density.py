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

def aggregate(grids):
    categories = ["schools", "clinics", "cafes", "gyms", "malls", "metro_stations", "universities", "corporate_offices"]
    breakdown = {cat: 0 for cat in categories}
    for g in grids:
        for cat in categories:
            val = g.get(cat, 0)
            if isinstance(val, int):
                breakdown[cat] += val
    return breakdown

osm = load_json("data_engine/osm_dwarka_grid.json")
mappls = load_json("data_engine/mappls_dwarka_grid.json")
ola = load_json("data_engine/ola_dwarka_grid.json")

b_osm = aggregate(osm)
b_map = aggregate(mappls)
b_ola = aggregate(ola)

categories = list(b_osm.keys())
v_osm = [b_osm[c] for c in categories]
v_map = [b_map[c] for c in categories]
v_ola = [b_ola[c] for c in categories]

# Plotting
x = np.arange(len(categories))
width = 0.25

fig, ax = plt.subplots(figsize=(14, 7))
rects1 = ax.bar(x - width, v_osm, width, label='OSM', color='#1f77b4')
rects2 = ax.bar(x, v_map, width, label='MapmyIndia (Mappls)', color='#ff7f0e')
rects3 = ax.bar(x + width, v_ola, width, label='Ola Krutrim', color='#2ca02c')

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Total POI Count', fontsize=12)
ax.set_title('POI Density Comparison in Dwarka (500m x 500m Grid Analysis)', fontsize=14, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels([c.replace("_", " ").title() for c in categories], rotation=45, ha="right", fontsize=11)
ax.legend(fontsize=11)

ax.grid(axis='y', linestyle='--', alpha=0.7)

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        if height > 0:
            ax.annotate(f'{height}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

fig.tight_layout()

# Save directly to the Artifacts directory
output_img = r"C:\Users\Nishant Raj\.gemini\antigravity\brain\038a6b52-c635-4d94-bb11-f8e54cd3fe37\density_comparison.png"
plt.savefig(output_img, dpi=300)
print(f"Plot saved to {output_img}")
