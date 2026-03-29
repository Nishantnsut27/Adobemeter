import json
import time
import os
import random
import requests
import ee
import geopy.distance
import config
from generate_grids import create_raw_grids
import fetch_b3_rapidapi as b3

try:
    ee.Initialize()
except Exception as e:
    print(f"ee auth failed: {e}")
    print("run 'earthengine authenticate' first")
    exit(1)

def load_raw_grids():
    create_raw_grids()
    with open("raw_grids_5km.json", "r") as f:
        return json.load(f)

import pygeohash

def get_landuse_classification(min_lat, min_lon, max_lat, max_lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    query = f'''
    [out:json][timeout:25];
    (
      way["landuse"="residential"]({bbox});
      way["landuse"="commercial"]({bbox});
      way["landuse"="retail"]({bbox});
      way["landuse"="industrial"]({bbox});
      way["amenity"="university"]({bbox});
    );
    out tags;
    '''
    counts = {"residential": 0, "commercial": 0, "retail": 0, "industrial": 0, "institutional": 0}
    try:
        res = requests.post(overpass_url, data={'data': query})
        if res.status_code == 200:
            for el in res.json().get('elements', []):
                tags = el.get('tags', {})
                lu = tags.get('landuse')
                if lu == 'residential': counts['residential'] += 1
                elif lu == 'commercial': counts['commercial'] += 1
                elif lu == 'retail': counts['retail'] += 1
                elif lu == 'industrial': counts['industrial'] += 1
                elif tags.get('amenity') == 'university': counts['institutional'] += 1
    except: pass
    
    if counts['commercial'] + counts['retail'] > counts['residential'] + 1:
        return "Commercial"
    elif counts['institutional'] > counts['residential']:
        return "Institutional"
    else:
        return "Residential"

def get_b1_metrics_from_overpass(min_lat, min_lon, max_lat, max_lon):
    overpass_url = "http://overpass-api.de/api/interpreter"
    bbox = f"{min_lat},{min_lon},{max_lat},{max_lon}"
    overpass_query = f'''
    [out:json][timeout:25];
    (
      node["amenity"="school"]({bbox});
      way["amenity"="school"]({bbox});
      node["amenity"="clinic"]({bbox});
      way["amenity"="clinic"]({bbox});
      node["amenity"="hospital"]({bbox});
      way["amenity"="hospital"]({bbox});
      node["amenity"="cafe"]({bbox});
      way["amenity"="cafe"]({bbox});
      node["leisure"="fitness_centre"]({bbox});
      way["leisure"="fitness_centre"]({bbox});
      node["shop"="mall"]({bbox});
      way["shop"="mall"]({bbox});
      node["railway"="station"]({bbox});
      way["railway"="station"]({bbox});
      node["amenity"="university"]({bbox});
      way["amenity"="university"]({bbox});
      node["office"]({bbox});
      way["office"]({bbox});
    );
    out center;
    '''
    counts = {
        "schools": 0, "clinics": 0, "cafes": 0, "gyms": 0, 
        "malls": 0, "metro_stations": 0, "universities": 0, "corporate_offices": 0
    }
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        if response.status_code == 200:
            data = response.json()
            for element in data.get('elements', []):
                tags = element.get('tags', {})
                if tags.get('amenity') == 'school': counts['schools'] += 1
                elif tags.get('amenity') in ['clinic', 'hospital']: counts['clinics'] += 1
                elif tags.get('amenity') == 'cafe': counts['cafes'] += 1
                elif tags.get('leisure') == 'fitness_centre': counts['gyms'] += 1
                elif tags.get('shop') == 'mall': counts['malls'] += 1
                elif 'station' in tags.get('railway', ''): counts['metro_stations'] += 1
                elif tags.get('amenity') == 'university': counts['universities'] += 1
                elif 'office' in tags: counts['corporate_offices'] += 1
    except Exception:
         pass
    return counts

def get_b2_distances_from_overpass(center_lat, center_lon, radius_km=4.0):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f'''
    [out:json][timeout:25];
    (
      node["shop"="mall"](around:{int(radius_km * 1000)},{center_lat},{center_lon});
      way["shop"="mall"](around:{int(radius_km * 1000)},{center_lat},{center_lon});
      node["railway"="station"](around:{int(radius_km * 1000)},{center_lat},{center_lon});
      node["station"="subway"](around:{int(radius_km * 1000)},{center_lat},{center_lon});
    );
    out center;
    '''
    dist_mall = None
    dist_metro = None
    try:
        response = requests.post(overpass_url, data={'data': overpass_query})
        if response.status_code == 200:
            data = response.json()
            for element in data.get('elements', []):
                lat = element.get('lat') or element.get('center', {}).get('lat')
                lon = element.get('lon') or element.get('center', {}).get('lon')
                if lat and lon:
                    dist = geopy.distance.geodesic((center_lat, center_lon), (lat, lon)).km
                    tags = element.get('tags', {})
                    if tags.get('shop') == 'mall':
                        if dist_mall is None or dist < dist_mall: dist_mall = dist
                    if 'station' in tags.get('railway', '') or 'subway' in tags.get('station', ''):
                        if dist_metro is None or dist < dist_metro: dist_metro = dist
    except Exception:
        pass
    return round(dist_mall, 2) if dist_mall else None, round(dist_metro, 2) if dist_metro else None

def get_b2_nightlight_nasa(center_lat, center_lon):
    try:
        dataset = (ee.ImageCollection('NOAA/VIIRS/DNB/MONTHLY_V1/VCMSLCFG')
                  .filterDate('2023-01-01', '2023-12-31')
                  .select('avg_rad').median())
        point = ee.Geometry.Point([center_lon, center_lat])
        radiance = dataset.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=500
        ).get('avg_rad').getInfo()
        return round(radiance, 2) if radiance else 0.0
    except Exception as e:
        print(f"Earth Engine Error: {e}")
        return None

def run_pipeline():
    print("starting data extraction for grids...")
    grids = load_raw_grids()
    
    count = 1
    total = len(grids)
    for g in grids:
        print(f"processing grid {count}/{total}...")
        
        g['id'] = pygeohash.encode(g['center_lat'], g['center_lon'], precision=6)
        
        metrics = get_b1_metrics_from_overpass(g['min_lat'], g['min_lon'], g['max_lat'], g['max_lon'])
        for k, v in metrics.items():
            g[k] = v
            
        g['grid_type'] = get_landuse_classification(g['min_lat'], g['min_lon'], g['max_lat'], g['max_lon'])
        
        time.sleep(1.5)
        
        g['night_light_intensity'] = get_b2_nightlight_nasa(g['center_lat'], g['center_lon'])
        
        mall_dist, metro_dist = get_b2_distances_from_overpass(g['center_lat'], g['center_lon'])
        g['dist_nearest_mall_km'] = mall_dist
        g['dist_nearest_metro_km'] = metro_dist
        
        g['avg_rent'] = None
        
        g.pop('b1_metrics', None)
        g.pop('b2_environment', None)
        g.pop('b3_real_estate', None)
        
        count += 1
        
    output_file = "dwarka_5km_pilot.json"
    with open(output_file, "w") as f:
        json.dump(grids, f, indent=2)
        
    print(f"done. saved {len(grids)} grids to {output_file}")

run_pipeline()
