import os
from infrastructure.gis.adapter import GisAdapter

class EtlProcessor:
    def __init__(self, data_dir, output_dir):
        self.data_dir = data_dir
        self.output_dir = output_dir
        self.gis = GisAdapter()
        os.makedirs(self.output_dir, exist_ok=True)

    def process_buildings(self, filename):
        input_path = os.path.join(self.data_dir, filename)
        print(f"Loading Buildings from {input_path}...")
        
        gdf = self.gis.load_and_convert(input_path)
        
        # Risk classification (Business Rule)
        gdf['risk_status'] = gdf['damage_pct_0m'].apply(lambda x: 'At Risk' if x > 0 else 'Not at Risk')
        
        def get_risk_level(pct):
            if pct > 0.5: return 'High'
            if pct > 0.2: return 'Medium'
            if pct > 0: return 'Low'
            return 'None'
        
        gdf['risk_level'] = gdf['damage_pct_0m'].apply(get_risk_level)
        
        clean_gdf = gdf[['id', 'damage_pct_0m', 'damaged', 'risk_status', 'risk_level', 'geometry']].copy()
        
        output_path = os.path.join(self.output_dir, "processed_buildings_risk.geojson")
        self.gis.save_geojson(clean_gdf, output_path)
        print(f"Saved Buildings to {output_path}")

    def process_roads(self, filename):
        input_path = os.path.join(self.data_dir, filename)
        print(f"Loading Roads from {input_path}...")
        
        gdf = self.gis.load_and_convert(input_path)
        
        # Road type cleaning
        gdf['road_type'] = gdf['highway'].apply(lambda x: x[0] if isinstance(x, list) else x)
        
        clean_gdf = gdf[['u', 'v', 'osmid', 'road_type', 'oneway', 'length', 'geometry']].copy()
        
        output_path = os.path.join(self.output_dir, "processed_roads_cleaned.geojson")
        self.gis.save_geojson(clean_gdf, output_path)
        print(f"Saved Roads to {output_path}")
