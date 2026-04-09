import requests
import json
import geopandas as gpd
from shapely.geometry import shape, Point, LineString, Polygon
import pandas as pd
import os

def download_osm_features():
    # Bounding Box: (south, west, north, east) for Overpass QL
    # Colombo North: [79.85, 6.935, 79.89, 6.975]
    s, w, n, e = 6.935, 79.85, 6.975, 79.89
    bbox_str = f"{s},{w},{n},{e}"
    
    # Overpass QL Query
    # Targets: leisure, amenity, landuse, natural
    query = f"""
    [out:json][timeout:180];
    (
      node["leisure"]({bbox_str});
      way["leisure"]({bbox_str});
      relation["leisure"]({bbox_str});
      node["amenity"]({bbox_str});
      way["amenity"]({bbox_str});
      relation["amenity"]({bbox_str});
      node["landuse"]({bbox_str});
      way["landuse"]({bbox_str});
      relation["landuse"]({bbox_str});
      node["natural"]({bbox_str});
      way["natural"]({bbox_str});
      relation["natural"]({bbox_str});
    );
    out body;
    >;
    out skel qt;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    print(f"🚀 Sending direct Overpass query for Colombo North...")
    
    try:
        response = requests.post(url, data={"data": query})
        response.raise_for_status()
        data = response.json()
        
        # We'll use osmnx's internal parser if available as it handles geometry creation from nodes/ways/relations
        # But since we want to be independent of its subdivision logic, we'll use it just for parsing the JSON
        import osmnx as ox
        gdf = ox.features._create_gdf(data, None, None)
        
        if gdf.empty:
            print("⚠️ No features found.")
            return

        gdf = gdf.reset_index()
        
        # Filter for the specific tags we want (to clean up the metadata)
        # We'll keep the core tags
        important_tags = ['leisure', 'amenity', 'landuse', 'natural', 'name', 'geometry']
        existing_cols = [c for c in important_tags if c in gdf.columns]
        gdf_clean = gdf[existing_cols].copy()

        output_path = "data/raw/osm_features_direct.geojson"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Clean columns for GeoJSON
        for col in gdf_clean.columns:
            if col != 'geometry':
                gdf_clean[col] = gdf_clean[col].astype(str)

        gdf_clean.to_file(output_path, driver='GeoJSON')
        print(f"✨ Successfully saved {len(gdf_clean)} features to {output_path}")
        
    except Exception as e:
        print(f"❌ Failed to download OSM data: {e}")

if __name__ == "__main__":
    download_osm_features()
