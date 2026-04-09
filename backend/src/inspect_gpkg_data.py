import geopandas as gpd
import os

# Paths
GPKG_PATH = "/Users/nadunhettiarachchi/MDSAI/Semester-03/Capstone_project/GeoAI/data/raw/planetscope_srilanka_11_30_buildings_clipped_predictions.gpkg"
PROCESSED_BUILDINGS = "/Users/nadunhettiarachchi/MDSAI/Semester-03/Capstone_project/GeoAI/data/processed/processed_buildings_risk.geojson"

def inspect():
    # 1. Raw GPKG Check
    print("--- RAW GPKG INSPECTION ---")
    if os.path.exists(GPKG_PATH):
        print(f"Loading GPKG: {GPKG_PATH}")
        gdf_raw = gpd.read_file(GPKG_PATH, rows=5) # Load only first 5 rows for speed
        print(f"Columns in GPKG: {gdf_raw.columns.tolist()}")
        print("\nFirst 5 rows of GPKG:")
        print(gdf_raw.head())
    else:
        print(f"Error: GPKG not found at {GPKG_PATH}")

    # 2. Processed Data Check
    print("\n--- PROCESSED DATA INSPECTION ---")
    if os.path.exists(PROCESSED_BUILDINGS):
        print(f"Loading Processed Data: {PROCESSED_BUILDINGS}")
        # The file is large (255MB), so we load only the first few rows to avoid memory overhead
        gdf_proc = gpd.read_file(PROCESSED_BUILDINGS, rows=5)
        print(f"Columns in Processed Data: {gdf_proc.columns.tolist()}")
        print("\nFirst 5 rows of Processed Data (Risk Classification):")
        print(gdf_proc[['id', 'risk_status', 'risk_level', 'geometry']].head())
        
        # Count total rows (this might take a bit - better to check file size first)
        print(f"\nProcessed data file size: {os.path.getsize(PROCESSED_BUILDINGS) / (1024*1024):.2f} MB")
    else:
        print(f"Error: Processed file not found at {PROCESSED_BUILDINGS}")

if __name__ == "__main__":
    inspect()
