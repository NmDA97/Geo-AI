import os
import sys

# Add src to python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from application.etl.processor import EtlProcessor

def main():
    data_dir = "/Users/nadunhettiarachchi/MDSAI/Semester-03/Capstone_project/GeoAI/data/raw"
    output_dir = "/Users/nadunhettiarachchi/MDSAI/Semester-03/Capstone_project/GeoAI/data/processed"
    
    buildings_file = "planetscope_srilanka_11_30_buildings_clipped_predictions.gpkg"
    roads_file = "colombo_roads.gpkg"
    
    processor = EtlProcessor(data_dir, output_dir)
    
    print("--- Starting Preprocessing ---")
    processor.process_buildings(buildings_file)
    processor.process_roads(roads_file)
    print("--- Preprocessing Complete ---")

if __name__ == "__main__":
    main()
