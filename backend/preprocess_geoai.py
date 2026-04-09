import geopandas as gpd
import os
import sys
import json
from shapely.geometry import box
from sqlalchemy import text

# Standardize path to project root (at /app in container)
if os.getcwd() not in sys.path:
    sys.path.insert(0, os.getcwd())

# Force imports from the canonical path relative to /app
from src.infrastructure.gis.adapter import GisAdapter
from src.infrastructure.database.setup import get_engine, init_db, Building
print(f"DEBUG: Preprocess Building class ID: {id(Building)}")

def preprocess_colombo_north():
    """
    Isolate, clean, and ingest geospatial data for Colombo North.
    """
    # Use Docker mount path /data, fallback to local data/
    DATA_DIR = os.getenv("DATA_DIR", "/data")
    DATA_RAW_BUILDINGS = os.path.join(DATA_DIR, "data/raw/planetscope_srilanka_11_30_buildings_clipped_predictions.gpkg")
    OUTPUT_DIR = "backend/cache"
    
    STUDY_AREA_BBOX = [79.85, 6.92, 79.96, 6.99] # Expanded to include Kelaniya and Angoda
    boundary_geom = box(*STUDY_AREA_BBOX)
    boundary_gdf = gpd.GeoDataFrame({'geometry': [boundary_geom]}, crs="EPSG:4326")

    print(f"Starting expanded preprocessing for Study Area: {STUDY_AREA_BBOX}")
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    engine = get_engine()
    
    # Drop existing tables to ensure schema matches the models exactly
    with engine.connect() as conn:
        print("Dropping existing tables for clean ingestion...")
        conn.execute(text("DROP TABLE IF EXISTS buildings, infrastructure, flood_zones, waterways CASCADE;"))
        conn.commit()
    
    init_db() # Recreate them

    # 1. Buildings
    if os.path.exists(DATA_RAW_BUILDINGS):
        print(f"Loading building footprints from {DATA_RAW_BUILDINGS}...")
        buildings = gpd.read_file(DATA_RAW_BUILDINGS)
        if buildings.crs != boundary_gdf.crs: buildings = buildings.to_crs(boundary_gdf.crs)
        buildings_clipped = gpd.clip(buildings, boundary_gdf)
        # Simplify geometry to reduce file size and improve rendering performance
        buildings_clipped.geometry = buildings_clipped.geometry.simplify(0.00001)
        print(f"Ingesting {len(buildings_clipped)} buildings...")
        GisAdapter.to_postgis(buildings_clipped, "buildings", engine)
        buildings_clipped.to_file(os.path.join(OUTPUT_DIR, "colombo_north_buildings.geojson"), driver='GeoJSON')
    
    # 2. Schools (from OSM centroids)
    DATA_OSM = os.path.join(DATA_DIR, "data/raw/osm_features_centroids.geojson")
    if os.path.exists(DATA_OSM):
        print(f"Extracting schools from {DATA_OSM}...")
        osm_data = gpd.read_file(DATA_OSM)
        if osm_data.crs != boundary_gdf.crs: osm_data = osm_data.to_crs(boundary_gdf.crs)
        schools = osm_data[osm_data['amenity'].isin(['school', 'college', 'university'])]
        schools_clipped = gpd.clip(schools, boundary_gdf)
        
        # Prepare for DB
        schools_clipped = schools_clipped[['name', 'amenity', 'geometry']].rename(columns={'amenity': 'type'})
        print(f"Ingesting {len(schools_clipped)} schools...")
        GisAdapter.to_postgis(schools_clipped, "infrastructure", engine)
        schools_clipped.to_file(os.path.join(OUTPUT_DIR, "schools.geojson"), driver='GeoJSON')

    # 3. Waterways (from Water Extent SHP)
    DATA_WATER = os.path.join(DATA_DIR, "data/raw/flood_maps/FL20251128LKA_SHP/Multisensors_20251126_20251202_WaterExtent_SriLanka.shp")
    if os.path.exists(DATA_WATER):
        print(f"Extracting waterways from {DATA_WATER}...")
        water_data = gpd.read_file(DATA_WATER)
        if water_data.crs != boundary_gdf.crs: water_data = water_data.to_crs(boundary_gdf.crs)
        water_clipped = gpd.clip(water_data, boundary_gdf)
        
        # Filter for significant water bodies / canals
        water_clipped['type'] = 'canal' # Default classification for this urban analysis
        water_clipped['name'] = 'Unnamed Canal/Waterway'
        print(f"Ingesting {len(water_clipped)} waterway segments...")
        GisAdapter.to_postgis(water_clipped[['name', 'type', 'geometry']], "waterways", engine)
        water_clipped.to_file(os.path.join(OUTPUT_DIR, "waterways.geojson"), driver='GeoJSON')

    # 4. Flood Zones
    DATA_FLOOD = "frontend/public/data/flood_clean_wgs84.geojson"
    if os.path.exists(DATA_FLOOD):
        print(f"Ingesting flood zones from {DATA_FLOOD}...")
        flood_data = gpd.read_file(DATA_FLOOD)
        if flood_data.crs != boundary_gdf.crs: flood_data = flood_data.to_crs(boundary_gdf.crs)
        flood_clipped = gpd.clip(flood_data, boundary_gdf)
        
        # Ingest via GisAdapter
        print(f"Ingesting {len(flood_clipped)} flood zone features...")
        GisAdapter.to_postgis(flood_clipped, "flood_zones", engine)
        flood_clipped.to_file(os.path.join(OUTPUT_DIR, "flood_zones_clipped.geojson"), driver='GeoJSON')

    # 5. Roads
    DATA_ROADS = os.path.join(DATA_DIR, "data/raw/colombo_roads.gpkg")
    if os.path.exists(DATA_ROADS):
        print(f"Loading road network from {DATA_ROADS}...")
        roads = gpd.read_file(DATA_ROADS)
        if roads.crs != boundary_gdf.crs: roads = roads.to_crs(boundary_gdf.crs)
        roads_clipped = gpd.clip(roads, boundary_gdf)
        print(f"Saving {len(roads_clipped)} roads...")
        roads_clipped.to_file(os.path.join(OUTPUT_DIR, "processed_roads_clipped.geojson"), driver='GeoJSON')

    # Update summary stats
    stats = {
        "region": "Colombo Expanded (Kelaniya/Angoda)",
        "building_count": len(buildings_clipped) if 'buildings_clipped' in locals() else 0,
        "school_count": len(schools_clipped) if 'schools_clipped' in locals() else 0,
        "waterway_count": len(water_clipped) if 'water_clipped' in locals() else 0,
        "flood_zone_count": len(flood_clipped) if 'flood_clipped' in locals() else 0,
        "road_count": len(roads_clipped) if 'roads_clipped' in locals() else 0,
        "boundary": STUDY_AREA_BBOX
    }
    
    stats_path = os.path.join(OUTPUT_DIR, "colombo_north_stats.json")
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=4)
    print(f"Summary stats saved to {stats_path}")

    # 6. Synchronize with Frontend
    print("Synchronizing data with frontend...")
    import shutil
    mapping = {
        "colombo_north_buildings.geojson": "buildings_clean_wgs84.geojson",
        "processed_roads_clipped.geojson": "processed_roads_cleaned.geojson",
        "flood_zones_clipped.geojson": "flood_clean_wgs84.geojson"
    }
    for src, dst in mapping.items():
        src_path = os.path.join(OUTPUT_DIR, src)
        dst_path = os.path.join("frontend/public/data", dst)
        if os.path.exists(src_path):
            shutil.copy(src_path, dst_path)
            print(f"Updated {dst}")

if __name__ == "__main__":
    try:
        init_db()
        preprocess_colombo_north()
    except Exception as e:
        print(f"Failure in preprocessing: {e}")
        import traceback
        traceback.print_exc()
