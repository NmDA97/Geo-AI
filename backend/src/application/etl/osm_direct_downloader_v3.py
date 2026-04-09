import requests
import json
import os
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
import pandas as pd

def download_osm_features():
    # Bounding Box: (south, west, north, east) for Overpass QL
    s, w, n, e = 6.935, 79.85, 6.975, 79.89
    bbox_str = f"{s},{w},{n},{e}"
    
    # Combined Overpass QL Query
    query = f"""
    [out:json][timeout:300];
    (
      nwr["leisure"~"playground|park|pitch|garden"]({bbox_str});
      nwr["amenity"~"school|hospital|clinic|place_of_worship|marketplace|kindergarten"]({bbox_str});
      nwr["landuse"~"grass|forest|meadow|greenfield|brownfield|construction"]({bbox_str});
      nwr["natural"~"water|scrub"]({bbox_str});
    );
    out center;
    """
    
    url = "https://overpass-api.de/api/interpreter"
    print(f"🚀 Sending direct Overpass query for Colombo North ({bbox_str})...")
    
    try:
        # Use a long timeout for potentially large queries
        response = requests.post(url, data={"data": query}, timeout=300)
        response.raise_for_status()
        data = response.json()
        
        elements = data.get('elements', [])
        print(f"✅ Received {len(elements)} elements from Overpass.")
        
        features = []
        for el in elements:
            # We use 'center' if available for ways/relations, or 'lat'/'lon' for nodes
            lat = el.get('lat') or (el.get('center', {}).get('lat'))
            lon = el.get('lon') or (el.get('center', {}).get('lon'))
            
            if lat and lon:
                tags = el.get('tags', {})
                # Flatten the feature
                feature = {
                    'osmid': el.get('id'),
                    'type': el.get('type'),
                    'geometry': Point(lon, lat)
                }
                feature.update(tags)
                features.append(feature)
        
        if not features:
            print("⚠️ No valid features extracted.")
            return

        # Create GeoDataFrame (using centroids for now to ensure speed and consistency)
        gdf = gpd.GeoDataFrame(features, crs="EPSG:4326")
        
        output_path = "data/raw/osm_features_centroids.geojson"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Clean columns
        for col in gdf.columns:
            if col != 'geometry':
                gdf[col] = gdf[col].astype(str)
                
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"✨ Successfully saved {len(gdf)} features (centroids) to {output_path}")
        
        # Summary
        print("\nFeatures Summary by Primary Tags:")
        for tag in ['leisure', 'amenity', 'landuse', 'natural']:
            if tag in gdf.columns:
                print(f"  {tag}: {gdf[tag].value_counts().sum()}")

    except Exception as e:
        print(f"❌ Failed to download OSM data: {e}")

if __name__ == "__main__":
    download_osm_features()
