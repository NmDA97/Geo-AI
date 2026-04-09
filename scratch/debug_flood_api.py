
import os
import sys
import json
from sqlalchemy.orm import Session
from sqlalchemy import func

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'backend/src'))
from infrastructure.database.setup import get_engine, FloodZone

def debug_flood_api():
    engine = get_engine()
    db = Session(engine)
    try:
        query = db.query(
            FloodZone.id,
            FloodZone.risk_level,
            func.ST_AsGeoJSON(FloodZone.geometry).label('geometry_json')
        ).limit(500)
        
        results = query.all()
        print(f"Results count: {len(results)}")
        
        features = []
        for res in results:
            print(f"ID: {res.id}, Risk: {res.risk_level}")
            geom = json.loads(res.geometry_json)
            print(f"Geometry type: {geom['type']}")
            features.append({
                "type": "Feature",
                "id": res.id,
                "properties": {
                    "risk_level": res.risk_level
                },
                "geometry": geom
            })
        
        fc = {
            "type": "FeatureCollection",
            "features": features
        }
        print("Successfully built FeatureCollection")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_flood_api()
