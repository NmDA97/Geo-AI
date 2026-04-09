import json
import os
import sys
from sqlalchemy.orm import Session
from sqlalchemy import text
import geopandas as gpd

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), "../backend/src"))
from infrastructure.database.setup import get_engine, FloodZone, init_db

def import_flood_data():
    print("🌊 Re-importing flood zones...")
    engine = get_engine()
    init_db()
    
    with Session(engine) as session:
        # 1. Clear existing flood zones
        session.query(FloodZone).delete()
        
        # 2. Load from GeoJSON
        geojson_path = os.path.join(os.path.dirname(__file__), "../frontend/public/data/flood_clean_wgs84.geojson")
        if os.path.exists(geojson_path):
            gdf = gpd.read_file(geojson_path)
            if gdf.crs != "EPSG:4326": gdf = gdf.to_crs("EPSG:4326")
            
            # 3. Add features
            for _, row in gdf.iterrows():
                risk = row.get('risk_level', 'High')
                fz = FloodZone(
                    risk_level=str(risk),
                    geometry=f'SRID=4326;{row.geometry.wkt}'
                )
                session.add(fz)
            
            session.commit()
            print(f"✅ Successfully imported {len(gdf)} flood zones.")
            
            # 4. Check one entry
            res = session.query(FloodZone).first()
            if res:
                print(f"🔍 Sample entry: ID={res.id}, Risk={res.risk_level}")
        else:
            print(f"⚠️ Flood GeoJSON not found at {geojson_path}")

if __name__ == "__main__":
    import_flood_data()
