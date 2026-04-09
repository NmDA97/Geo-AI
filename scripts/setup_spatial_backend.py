import json
import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text
import geopandas as gpd
from shapely.geometry import shape

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend/src"))
from infrastructure.database.setup import get_engine, Base, Road, FloodZone, init_db

def setup_spatial_backend():
    print("🚀 Initializing spatial backend...")
    engine = get_engine()
    
    # 1. Create tables
    print("📋 Ensuring tables exist...")
    init_db()
    
    # 2. Import Roads
    with Session(engine) as session:
        road_count = session.query(Road).count()
        if road_count == 0:
            print("🛣️ Importing roads from GeoJSON...")
            geojson_path = os.path.join(os.path.dirname(__file__), "../frontend/public/data/processed_roads_cleaned.geojson")
            if os.path.exists(geojson_path):
                gdf = gpd.read_file(geojson_path)
                if gdf.crs != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
                roads_to_add = [Road(name=row.get('name', 'Unnamed Road'), highway=row.get('highway', 'road'), geometry=f'SRID=4326;{row.geometry.wkt}') for _, row in gdf.iterrows()]
                session.add_all(roads_to_add)
                session.commit()
                print(f"✅ Imported {len(roads_to_add)} roads.")
        else:
            print(f"✅ Roads already present ({road_count}).")

    # 3. Import Flood Zones
    with Session(engine) as session:
        print("🌊 Refreshing flood zones from GeoJSON...")
        geojson_path = os.path.join(os.path.dirname(__file__), "../frontend/public/data/flood_clean_wgs84.geojson")
        if os.path.exists(geojson_path):
            gdf = gpd.read_file(geojson_path)
            if gdf.crs != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
            
            # Clear existing safely
            session.execute(text("TRUNCATE TABLE flood_zones RESTART IDENTITY CASCADE;"))
            
            flood_zones_to_add = []
            for _, row in gdf.iterrows():
                # Get risk level safely
                risk = row.get('risk_level', 'High')
                flood_zones_to_add.append(FloodZone(risk_level=str(risk), geometry=f'SRID=4326;{row.geometry.wkt}'))
            
            session.add_all(flood_zones_to_add)
            session.commit()
            print(f"✅ Imported {len(flood_zones_to_add)} flood zones.")
        else:
            print(f"⚠️ Flood GeoJSON not found at {geojson_path}")

    # 4. Create Spatial Indexes
    print("⚡ Creating spatial indexes...")
    with engine.connect() as conn:
        try: conn.execute(text("CREATE INDEX idx_buildings_geom ON buildings USING GIST (geometry);")); conn.commit()
        except Exception: pass
        try: conn.execute(text("CREATE INDEX idx_roads_geom ON roads USING GIST (geometry);")); conn.commit()
        except Exception: pass
        try: conn.execute(text("CREATE INDEX idx_flood_zones_geom ON flood_zones USING GIST (geometry);")); conn.commit()
        except Exception: pass
    print("✅ Spatial indexes checked.")

if __name__ == "__main__":
    setup_spatial_backend()
