import json
import os
import sys
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import shape, MultiPolygon, Polygon

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../backend/src'))
from infrastructure.database.setup import get_engine, FloodZone

def seed_flood_data():
    engine = get_engine()
    db = Session(engine)
    
    # Check if already seeded
    if db.query(FloodZone).count() > 0:
        print("Flood zones already exist in database. Skipping seed.")
        return

    geojson_path = 'frontend/public/data/flood_clean_wgs84.geojson'
    if not os.path.exists(geojson_path):
        print(f"File {geojson_path} not found.")
        return

    with open(geojson_path, 'r') as f:
        data = json.load(f)

    print(f"Seeding {len(data['features'])} flood zones...")
    
    for feature in data['features']:
        geom = shape(feature['geometry'])
        
        # Ensure it's a MultiPolygon for the DB model
        if isinstance(geom, Polygon):
            geom = MultiPolygon([geom])
            
        risk_level = feature['properties'].get('risk_level', 'unknown')
        
        zone = FloodZone(
            risk_level=risk_level,
            geometry=from_shape(geom, srid=4326)
        )
        db.add(zone)
    
    db.commit()
    print("Seeding complete.")
    db.close()

if __name__ == "__main__":
    seed_flood_data()
