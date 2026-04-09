import geopandas as gpd
import pandas as pd
import json
import os
import sys

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/src')))
from application.analysis.urban_eda_service import UrbanEdaService

def generate_stats():
    # Base paths
    CACHE_DIR = "backend/cache"
    DATA_PROCESSED = "data/processed"
    OUTPUT_PATH = "frontend/public/data/eda_stats.json"
    
    eda = UrbanEdaService()
    
    print("Loading expanded data from cache...")
    buildings_gdf = gpd.read_file(f"{CACHE_DIR}/colombo_north_buildings.geojson")
    schools_gdf = gpd.read_file(f"{CACHE_DIR}/schools.geojson")
    waterways_gdf = gpd.read_file(f"{CACHE_DIR}/waterways.geojson")
    flood_gdf = gpd.read_file(f"{CACHE_DIR}/flood_zones_clipped.geojson")
    
    print("Analyzing geometric patterns for buildings...")
    geo_stats = eda.analyze_geometric_patterns(buildings_gdf)
    
    print("Analyzing risk intersection...")
    # Standardize CRS for area calculations
    buildings_metric = buildings_gdf.to_crs("EPSG:3857")
    flood_metric = flood_gdf.to_crs("EPSG:3857")
    schools_metric = schools_gdf.to_crs("EPSG:3857")
    
    # Buildings at risk
    buildings_at_risk = gpd.sjoin(buildings_metric, flood_metric, predicate='intersects')
    
    risk_stats = {
        "total_buildings": len(buildings_gdf),
        "buildings_at_risk": len(buildings_at_risk),
        "risk_percentage": (len(buildings_at_risk) / len(buildings_gdf)) * 100 if len(buildings_gdf) > 0 else 0,
        "flood_area_sqkm": flood_metric.geometry.area.sum() / 1e6
    }
    
    # Schools analysis
    schools_at_risk = gpd.sjoin(schools_metric, flood_metric, predicate='intersects')
    school_stats = {
        "total_schools": len(schools_gdf),
        "schools_at_risk": len(schools_at_risk),
        "risk_percentage": (len(schools_at_risk) / len(schools_gdf)) * 100 if len(schools_gdf) > 0 else 0,
        "school_types": schools_gdf['type'].value_counts().to_dict()
    }
    
    # Waterways analysis
    waterway_stats = {
        "total_segments": len(waterways_gdf),
        "total_water_area_sqkm": waterways_gdf.to_crs("EPSG:3857").geometry.area.sum() / 1e6
    }
    
    # Combined stats
    final_stats = {
        "geometric": geo_stats,
        "risk": risk_stats,
        "schools": school_stats,
        "waterways": waterway_stats,
        "infrastructure": {
            "total_road_length_km": geo_stats.get('total_road_length_km', 1029) # Fallback to base value
        },
        "metadata": {
            "study_area": "Colombo Expanded (Kelaniya & Angoda)",
            "last_updated": pd.Timestamp.now().isoformat()
        }
    }
    
    # Save to JSON
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(final_stats, f, indent=2)
    
    print(f"Stats successfully exported to {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_stats()
