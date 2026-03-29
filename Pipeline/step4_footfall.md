# Step 4: Footfall Intelligence Engine (Multiplier)

This module calculates the **Footfall Multiplier (1–10)** for every grid. This score is critical because it tells an advertiser how many "impressions" their screen will get.

### Weighted Metrics:
We use a **40-30-30 Weighted Ratio** to ensure the most accurate density mapping:

1.  **Transit Accessibility (40% Weight)**: 
    *   **Reasoning**: Metro stations are the #1 source of mass footfall in Indian urban corridors (like Dwarka).
    *   **Logic**: High scores for grids within 500m of a station; exponential decay beyond 3km.
2.  **Night-Life & Activity Intensity (30% Weight)**:
    *   **Reasoning**: Uses NASA VIIRS Night-Light data as a direct proxy for human activity (street lighting, billboards, open stores).
    *   **Logic**: Proven scientific proof of human activity.
3.  **Commercial Destination Density (30% Weight)**:
    *   **Reasoning**: People travel specifically to grids with high concentrations of **Malls, Cafes, and Offices**.
    *   **Logic**: Aggregates POI counts to find "sticky" urban zones where people linger.

### Outcome:
Every grid is assigned a **`footfall_index`**. High-footfall areas are marked with an `is_high_footfall` flag for the recommendation UI.
