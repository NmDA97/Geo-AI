import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point
from rasterstats import zonal_stats
import rasterio
from typing import Dict, List, Optional
import warnings

warnings.filterwarnings('ignore')

class UrbanEdaService:
    def __init__(self, target_crs: str = "EPSG:5235"):
        """
        Initialize EDA Service.
        target_crs: Kandawala / Sri Lanka Grid (Metric) for accurate measurements.
        """
        self.target_crs = target_crs

    def validate_spatial_integrity(self, layers: Dict[str, gpd.GeoDataFrame]) -> Dict[str, bool]:
        """
        Point 1: Spatial Data Quality & Integrity.
        Checks CRS and missing geometries.
        """
        results = {}
        for name, gdf in layers.items():
            crs_ok = str(gdf.crs).upper() == self.target_crs.upper()
            missing_geom = gdf.geometry.isnull().sum()
            results[name] = {
                "crs_match": crs_ok,
                "current_crs": str(gdf.crs),
                "missing_geometries": missing_geom,
                "total_rows": len(gdf)
            }
        return results

    def analyze_geometric_patterns(self, buildings_gdf: gpd.GeoDataFrame) -> Dict:
        """
        Point 2: Geometric Analysis.
        Calculates footprints and identifies density.
        """
        df = buildings_gdf.copy()
        if df.crs != self.target_crs:
            df = df.to_crs(self.target_crs)
            
        df['area_sqm'] = df.geometry.area
        
        stats = {
            "mean_footprint": df['area_sqm'].mean(),
            "median_footprint": df['area_sqm'].median(),
            "total_built_area": df['area_sqm'].sum(),
            "large_buildings_count": len(df[df['area_sqm'] > 500])
        }
        return stats

    def calculate_amenity_proximity(self, at_risk_gdf: gpd.GeoDataFrame, osm_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Point 4: Correlation & Proximity.
        Calculates distance from risk buildings to the nearest school/hospital.
        """
        # Ensure metric CRS
        risk = at_risk_gdf.to_crs(self.target_crs)
        osm = osm_gdf.to_crs(self.target_crs)
        
        # Filter for critical amenities
        schools = osm[osm['amenity'].isin(['school', 'kindergarten'])]
        hospitals = osm[osm['amenity'].isin(['hospital', 'clinic'])]
        
        def min_dist(point, other_gdf):
            if other_gdf.empty: return np.nan
            return other_gdf.distance(point).min()

        risk['dist_to_school'] = risk.geometry.apply(lambda x: min_dist(x, schools))
        risk['dist_to_hospital'] = risk.geometry.apply(lambda x: min_dist(x, hospitals))
        
        return risk

    def get_zonal_indices(self, raster_path: str, zones_gdf: gpd.GeoDataFrame, prefix: str = "ndvi") -> gpd.GeoDataFrame:
        """
        Point 5: Remote Sensing Statistics.
        Calculates average index value (NDVI/NDBI) for each zone.
        """
        zones = zones_gdf.copy()
        # Zonal stats requires the same CRS
        with rasterio.open(raster_path) as src:
            if zones.crs != src.crs:
                zones = zones.to_crs(src.crs)
        
        stats = zonal_stats(zones, raster_path, stats=['mean', 'std', 'max'])
        
        df_stats = pd.DataFrame(stats)
        df_stats.columns = [f"{prefix}_{c}" for c in df_stats.columns]
        
        return pd.concat([zones.reset_index(drop=True), df_stats], axis=1)

    def identify_at_risk_amenities(self, flood_gdf: gpd.GeoDataFrame, osm_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Finds schools/hospitals located inside flood zones.
        """
        flood = flood_gdf.to_crs(self.target_crs)
        osm = osm_gdf.to_crs(self.target_crs)
        
        # Identify intersection
        critical_at_risk = gpd.sjoin(osm, flood, predicate='within')
        return critical_at_risk

if __name__ == "__main__":
    print("Urban EDA Service initialized.")
