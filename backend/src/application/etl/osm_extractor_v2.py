import osmnx as ox
import geopandas as gpd
import os
import pandas as pd

def fetch_urban_features():
    # Fix: Set huge query size limit to avoid subdivision overhead
    ox.settings.max_query_area_size = 10**14 
    ox.settings.overpass_settings = '[out:json][timeout:180]'
    ox.settings.overpass_rate_limit = False # Disable rate limit wait if we are in a hurry (optional)
    
    # Bounding Box: (north, south, east, west) for Colombo North
    bbox = (6.975, 6.935, 79.89, 79.85)
    
    # Target OSM Tags broken down for individual fetching
    target_tags = [
        {"leisure": ["playground", "park", "pitch", "garden"]},
        {"amenity": ["school", "hospital", "clinic", "place_of_worship", "marketplace", "kindergarten"]},
        {"landuse": ["grass", "forest", "meadow", "greenfield", "brownfield", "construction"]},
        {"natural": ["water", "scrub"]}
    ]
    
    all_features = []
    
    print(f"🚀 Starting optimized OSM fetch for Colombo North: {bbox}")
    
    for tag_dict in target_tags:
        key = list(tag_dict.keys())[0]
        values = tag_dict[key]
        print(f"  Fetching {key}={values}...")
        
        try:
            # Fetch one category at a time
            gdf = ox.features.features_from_bbox(bbox=bbox, tags=tag_dict)
            if not gdf.empty:
                gdf = gdf.reset_index()
                # Track the main tag for summary
                gdf['feature_category'] = key
                all_features.append(gdf)
                print(f"    ✅ Found {len(gdf)} features.")
            else:
                print(f"    ⚠️ No features found for {key}.")
        except Exception as e:
            print(f"    ❌ Error fetching {key}: {e}")

    if not all_features:
        print("❌ No features found at all.")
        return

    # Combine all GeoDataFrames
    final_gdf = pd.concat(all_features, ignore_index=True)
    
    # Clean columns for GeoJSON
    for col in final_gdf.columns:
        if col != 'geometry':
            final_gdf[col] = final_gdf[col].astype(str)
            
    # Save output
    output_path = "data/raw/osm_features_colombo_north_v2.geojson"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_gdf.to_file(output_path, driver='GeoJSON')
    
    print(f"\n✨ Successfully saved {len(final_gdf)} features to {output_path}")
    
    # Summary
    if 'feature_category' in final_gdf.columns:
        print("\nFeatures Summary by Category:")
        print(final_gdf['feature_category'].value_counts())

if __name__ == "__main__":
    fetch_urban_features()
