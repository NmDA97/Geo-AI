import osmnx as ox
import geopandas as gpd
import os

def fetch_urban_features():
    # Increase the query size limit to avoid unnecessary subdivision
    ox.settings.max_query_area_size = 1000 * 1000 * 1000 * 1000 # 1,000,000 sq km
    
    # Bounding Box: (north, south, east, west) for Colombo North
    bbox = (6.975, 6.935, 79.89, 79.85)
    
    # Target OSM Tags
    tags = {
        "leisure": ["playground", "park", "pitch", "garden"],
        "amenity": ["school", "hospital", "clinic", "place_of_worship", "marketplace", "kindergarten"],
        "landuse": ["grass", "forest", "meadow", "greenfield", "brownfield", "construction"],
        "natural": ["water", "scrub"]
    }
    
    print(f"Fetching urban features from OSM for bbox: {bbox}")
    try:
        # Fetch features
        gdf = ox.features.features_from_bbox(bbox=bbox, tags=tags)
        
        # Keep relevant columns and reset index
        # Result is indexed by (type, osmid). Let's flatten it.
        gdf = gdf.reset_index()
        
        # Standardize columns: tag name and value
        print(f"Total features fetched: {len(gdf)}")
        
        # Save output
        output_dir = "data/raw"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "osm_features_colombo_north.geojson")
        
        # Clean columns to ensure JSON compatibility (some attributes might be lists)
        for col in gdf.columns:
            if col != 'geometry':
                gdf[col] = gdf[col].astype(str)
                
        gdf.to_file(output_path, driver='GeoJSON')
        print(f"✅ Successfully saved features to {output_path}")
        
        # Summary counts
        summary = gdf[['element_type', 'osmid']].groupby('element_type').count()
        print("\nFeatures Summary:")
        print(summary)

    except Exception as e:
        print(f"❌ Failed to fetch features: {e}")

if __name__ == "__main__":
    fetch_urban_features()
