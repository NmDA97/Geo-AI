import geopandas as gpd
from geoalchemy2 import Geometry
from geoalchemy2.shape import from_shape
from sqlalchemy import insert, Table, MetaData
import os

class GisAdapter:
    @staticmethod
    def load_and_convert(file_path, target_crs="EPSG:4326"):
        gdf = gpd.read_file(file_path)
        if gdf.crs != target_crs:
            gdf = gdf.to_crs(target_crs)
        return gdf

    @staticmethod
    def save_geojson(gdf, output_path):
        gdf.to_file(output_path, driver="GeoJSON")

    @staticmethod
    def to_postgis(gdf, table_name, engine, chunksize=1000):
        """
        Ingest GeoDataFrame into PostGIS using direct SQLAlchemy CORE (no ORM) 
        to avoid class identity/mapping issues in complex environments.
        """
        # Clean GDF: remove empty/invalid geometries
        gdf = gdf[gdf.geometry.notnull()]
        gdf = gdf[~gdf.is_empty]
        
        if gdf.empty:
            print(f"No valid records to ingest into {table_name}.")
            return

        # Load table metadata dynamically from DB
        metadata = MetaData()
        # Ensure postgis extension is already there or we might get errors on geometry cols
        table = Table(table_name, metadata, autoload_with=engine)
        
        srid = gdf.crs.to_epsg() if gdf.crs else 4326
        table_columns = [c.name for c in table.columns]
        
        # Prepare records using direct dicts for SQLAlchemy CORE
        records = []
        for _, row in gdf.iterrows():
            record = {}
            for col in table_columns:
                if col in row:
                    val = row[col]
                    if col == 'geometry' and val is not None:
                        try:
                            # Force conversion to MultiPolygon if the table expects it
                            # and the current geometry is a single Polygon
                            from shapely.geometry import MultiPolygon, Polygon, Point
                            if table_name in ['buildings', 'waterways', 'flood_zones']:
                                if isinstance(val, Polygon):
                                    val = MultiPolygon([val])
                            
                            # Convert to WKBElement with correct SRID for GeoAlchemy2
                            val = from_shape(val, srid=srid)
                        except Exception as ge:
                            print(f"Geometry conversion error at index {_} for table {table_name}: {ge}")
                            continue
                    record[col] = val
            records.append(record)
        
        # Perform bulk insert in chunks via direct engine execution (Core)
        if records:
            from sqlalchemy import text
            try:
                with engine.begin() as conn:
                    # Clean existing records for a fresh start
                    conn.execute(text(f"TRUNCATE TABLE {table_name};"))
                    
                    for i in range(0, len(records), chunksize):
                        chunk = records[i:i + chunksize]
                        conn.execute(insert(table), chunk)
                print(f"Successfully ingested {len(records)} records into {table_name} table via SQLAlchemy Core.")
            except Exception as e:
                print(f"Error during core ingestion: {e}")
                raise e
        else:
            print(f"No records prepared for {table_name}.")
