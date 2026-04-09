
import os
import sys
import json
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add src to path
sys.path.append(os.path.join(os.getcwd(), 'backend/src'))
from infrastructure.database.setup import get_engine

def check_db():
    engine = get_engine()
    with engine.connect() as conn:
        # Check flood_zones
        result = conn.execute(text("SELECT count(*) FROM flood_zones"))
        count = result.scalar()
        print(f"Flood zones count: {count}")
        
        if count > 0:
            result = conn.execute(text("SELECT id, risk_level, ST_AsText(geometry) FROM flood_zones LIMIT 5"))
            for row in result:
                print(f"ID: {row[0]}, Risk: {row[1]}, Geom: {row[2][:100]}...")
        
        # Check buildings
        result = conn.execute(text("SELECT count(*) FROM buildings"))
        count = result.scalar()
        print(f"Buildings count: {count}")

        # Check for Kelaniya/Angoda areas
        # Kelaniya is roughly 6.95, 79.91
        # Angoda is roughly 6.93, 79.93
        print("\nChecking for data in Kelaniya/Angoda areas...")
        result = conn.execute(text("""
            SELECT count(*) FROM buildings 
            WHERE ST_Intersects(geometry, ST_MakeEnvelope(79.88, 6.90, 79.95, 7.00, 4326))
        """))
        print(f"Buildings in wider area (including Kelaniya/Angoda): {result.scalar()}")

if __name__ == "__main__":
    check_db()
