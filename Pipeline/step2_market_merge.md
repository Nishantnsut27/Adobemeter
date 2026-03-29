# Step 2: Market Data Integration

This module takes the "skeleton" grid from Step 1 and populates it with real-estate pricing and inventory data (Rent/Sale) from any provided external source.

### Tasks:
1.  **Multi-Source Merging**: Ingests multiple market data formats (Rent from MagicBricks, Sale from 99acres, etc.).
2.  **Universal Matching**:
    *   **Geohash Match**: Uses the encoded cell ID for 1:1 precision mapping.
    *   **Spatial Fallback**: If a property is not exactly at a cell's geohash center, it uses a **Haversine Distance (1km)** radius scan to snap it to the nearest center.
3.  **Aggregation Logic**:
    *   **Median Price Calculation**: Avoids skewing data by using Medians instead of Averages for pricing.
    *   **Primary Property Classifier**: Dynamically identifies the most common property type (e.g., "Builder Floor" vs. "Apartment") in a given tile.
4.  **Portfolio Portability**: All data is merged into a single standardized object for easy delivery to the recommendation engine.

### Data Inputs:
*   Expected folder structure: `/data`
*   Expected format: JSON or CSV containing `lat`, `lon`, and `price/sale_price`.

### Goal:
Builds a market-driven layer for the ad engine, allowing us to see where high-rental (HNI) vs. economy (Student) populations reside.
