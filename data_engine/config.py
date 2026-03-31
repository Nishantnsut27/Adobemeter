# Configuration for the Data Pipeline
CENTER_LAT = 28.6044
CENTER_LON = 77.0388
RADIUS_KM = 2.5 # 5km diameter mapping area
GRID_SIZE_KM = 0.5

# RapidAPI Credentials (User needs to populate)
RAPID_API_KEY = "INSERT_KEY_HERE"
RAPID_API_HOST = "INSERT_HOST_HERE" # e.g. "magicbricks-property.p.rapidapi.com"

# MapmyIndia (Mappls) Credentials
MAPPLS_CLIENT_ID = "96dHZVzsAusPiud7RjBOuGZTdhI9rSqz9RBG23IXQ1QZoTml5PgyKMJh6MIz-QSGqGbl18BQ_qMfq2P-fQPIvw=="
MAPPLS_CLIENT_SECRET = "lrFxI-iSEg8R5qM5nGuPlWJCuqFhl5SqPuKfG_WUyDjMfxWk_RWyocG5G5XF9QMRD1cqVQma7y7Tv_A0us1bu974kiHRCPCy"
MAPPLS_REST_KEY = "9d64be86ae1637f4b6c24c1daf5313d8"

# POI Categories for Mappls
# Note: Using descriptive keywords often yields better results than codes.
POI_CATEGORIES = {
    "schools": "School",
    "clinics": "Clinic",
    "cafes": "Cafe",
    "gyms": "Gym",
    "malls": "Mall",
    "metro_stations": "Metro Station",
    "universities": "University",
    "corporate_offices": "Office"
}

# Ola Krutrim Maps API Credentials
OLA_MAPS_API_KEY = "GZFw8yQolbIrUvJWDCYbcpy48HCoT5iv9LaoPB9t"
OLA_CLIENT_ID = "13ff9810-e60a-4677-b247-2b3e155b5563"
OLA_CLIENT_SECRET = "565bf86a32ee49ba92f29189a99a15b3"
