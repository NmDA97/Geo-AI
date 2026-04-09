from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func, text
import os
import json
import sys

# Add src to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from infrastructure.database.setup import get_engine, FloodZone, Building, Road
from application.analysis.urban_eda_service import UrbanEdaService

app = FastAPI(title="GeoAI Backend API")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database Session
engine = get_engine()
def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()

# Initialize services
eda_service = UrbanEdaService()

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "GeoAI Backend"}

@app.get("/api/spatial/flood-zones")
async def get_flood_zones(db: Session = Depends(get_db)):
    """
    Fetch flood zones from PostGIS.
    Returns GeoJSON format.
    """
    # Colombo North bounding box filtering (Optional, but good practice)
    # For now, fetching first 500 to keep it fast
    # ST_AsGeoJSON converts geometry to GeoJSON string
    
    query = db.query(
        FloodZone.id,
        FloodZone.risk_level,
        func.ST_AsGeoJSON(FloodZone.geometry).label('geometry_json')
    ).limit(500)
    
    results = query.all()
    
    features = []
    for res in results:
        features.append({
            "type": "Feature",
            "id": res.id,
            "properties": {
                "risk_level": res.risk_level
            },
            "geometry": json.loads(res.geometry_json)
        })
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

@app.get("/api/spatial/tiles/{layer}/{z}/{x}/{y}")
async def get_spatial_tiles(layer: str, z: int, x: int, y: int, db: Session = Depends(get_db)):
    """
    Generate Vector Tiles (MVT) for buildings, roads, or flood zones.
    """
    table_map = {
        "buildings": "buildings",
        "roads": "roads",
        "flood": "flood_zones"
    }
    
    table_name = table_map.get(layer)
    if not table_name:
        raise HTTPException(status_code=400, detail="Invalid layer")

    # SQL query for ST_AsMVT
    # 1. Transform geometry to Web Mercator (3857) if needed, but ST_TileEnvelope expects 3857 bounds
    # 2. Clip features to tile boundary
    # 3. Aggregate into MVT
    
    query = text(f"""
        WITH bounds AS (
            SELECT ST_TileEnvelope(:z, :x, :y) AS geom
        ),
        mvtgeom AS (
            SELECT ST_AsMVTGeom(ST_Transform(t.geometry, 3857), bounds.geom) AS geom, 
                   t.*
            FROM {table_name} t, bounds
            WHERE ST_Intersects(ST_Transform(t.geometry, 3857), bounds.geom)
        )
        SELECT ST_AsMVT(mvtgeom.*, :layer) FROM mvtgeom;
    """)
    
    try:
        result = db.execute(query, {"z": z, "x": x, "y": y, "layer": layer}).scalar()
        if not result:
            return Response(content=b"", media_type="application/x-protobuf")
        return Response(content=bytes(result), media_type="application/x-protobuf")
    except Exception as e:
        print(f"Error generating tile: {e}")
        return Response(content=b"", media_type="application/x-protobuf")


@app.get("/api/stats")
async def get_stats():
    """
    Returns the pre-calculated EDA statistics.
    """
    stats_path = os.path.join(os.path.dirname(__file__), "../../frontend/public/data/eda_stats.json")
    if not os.path.exists(stats_path):
        raise HTTPException(status_code=404, detail="Stats not found. Run scripts/generate_eda_stats.py")
    
    with open(stats_path, 'r') as f:
        return json.load(f)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
