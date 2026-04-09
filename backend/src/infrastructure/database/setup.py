from sqlalchemy import Column, Integer, String, Float, Boolean, text
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine
from geoalchemy2 import Geometry
import os

Base = declarative_base()

class Building(Base):
    __tablename__ = 'buildings'
    
    id = Column(String, primary_key=True)
    damage_pct_0m = Column(Float)
    damage_pct_10m = Column(Float)
    damage_pct_20m = Column(Float)
    built_pct_0m = Column(Float)
    damaged = Column(Boolean)
    unknown_pct = Column(Float)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))
    

class FloodZone(Base):
    __tablename__ = 'flood_zones'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    risk_level = Column(String)
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))

class Infrastructure(Base):
    __tablename__ = 'infrastructure'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String) # school, hospital, etc.
    geometry = Column(Geometry('POINT', srid=4326))

class Waterway(Base):
    __tablename__ = 'waterways'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    type = Column(String) # canal, river, etc.
    geometry = Column(Geometry('MULTIPOLYGON', srid=4326))

class Road(Base):
    __tablename__ = 'roads'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    highway = Column(String)
    geometry = Column(Geometry('LINESTRING', srid=4326))

def get_engine():
    # Priority 1: Environment variable
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        return create_engine(db_url)
        
    # Priority 2: Try 'localhost' (direct execution on mac)
    # The docker-compose maps 5433:5432
    try:
        engine = create_engine("postgresql://geoai:geoai_password@localhost:5433/geodb")
        # Quick check
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return engine
    except Exception:
        # Priority 3: Try 'db' (inside docker network)
        return create_engine("postgresql://geoai:geoai_password@db:5432/geodb")

def init_db():
    engine = get_engine()
    # Ensure PostGIS extension is enabled
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        conn.commit()
    
    Base.metadata.create_all(engine)
    print("Database tables initialized.")

if __name__ == "__main__":
    init_db()
