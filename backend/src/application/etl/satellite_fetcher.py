import pystac_client
import planetary_computer
import rasterio
from rasterio.windows import from_bounds
from pyproj import Transformer
import numpy as np
import os

def fetch_satellite_indices():
    # Bounding Box: (west, south, east, north) for Colombo North
    bbox_4326 = [79.85, 6.935, 79.89, 6.975]
    
    print(f"🚀 Searching Microsoft Planetary Computer for Sentinel-2 imagery...")
    catalog = pystac_client.Client.open(
        "https://planetarycomputer.microsoft.com/api/stac/v1",
        modifier=planetary_computer.sign_inplace,
    )
    
    search = catalog.search(
        collections=["sentinel-2-l2a"],
        bbox=bbox_4326,
        datetime="2024-01-01/2024-12-31",
        query={"eo:cloud_cover": {"lt": 5}},
        sortby=[{"field": "properties.eo:cloud_cover", "direction": "asc"}]
    )
    
    items = search.item_collection()
    if not items:
        print("❌ No cloud-free imagery found for 2024.")
        return
    
    item = items[0]
    print(f"✅ Found clear scene: {item.id} (Cloud cover: {item.properties['eo:cloud_cover']:.2f}%)")
    
    assets = {
        "red": item.assets["B04"].href,
        "nir": item.assets["B08"].href,
        "swir": item.assets["B11"].href
    }
    
    output_dir = "data/raw/satellite"
    os.makedirs(output_dir, exist_ok=True)
    
    def get_data(url):
        with rasterio.open(url) as src:
            # Project our geographic bbox to the raster's CRS
            transformer = Transformer.from_crs("EPSG:4326", src.crs, always_xy=True)
            west, south = transformer.transform(bbox_4326[0], bbox_4326[1])
            east, north = transformer.transform(bbox_4326[2], bbox_4326[3])
            
            # Read only the window of our projected bbox
            window = from_bounds(west, south, east, north, src.transform)
            data = src.read(1, window=window).astype(float)
            return data, src.window_transform(window), src.crs

    try:
        print("📥 Downloading bands (Red, NIR, SWIR) for the study area...")
        red, transform, crs = get_data(assets["red"])
        nir, _, _ = get_data(assets["nir"])
        swir, _, _ = get_data(assets["swir"])
        
        # Ensure they have the same shape (B11 is 20m, others are 10m)
        if swir.shape != red.shape:
            print("🔄 Resampling SWIR band to match 10m resolution...")
            import scipy.ndimage
            zoom_factors = [red.shape[0]/swir.shape[0], red.shape[1]/swir.shape[1]]
            swir = scipy.ndimage.zoom(swir, zoom_factors, order=1)
            # Clip if slightly off
            swir = swir[:red.shape[0], :red.shape[1]]

        # Calculate NDVI: (NIR - Red) / (NIR + Red)
        print("📊 Calculating NDVI (Vegetation Index)...")
        ndvi = (nir - red) / (nir + red + 1e-10)
        
        # Calculate NDBI: (SWIR - NIR) / (SWIR + NIR)
        print("📊 Calculating NDBI (Built-up Index)...")
        ndbi = (swir - nir) / (swir + nir + 1e-10)
        
        # Save results
        for name, data in [("ndvi", ndvi), ("ndbi", ndbi)]:
            path = os.path.join(output_dir, f"colombo_north_{name}.tif")
            with rasterio.open(
                path, 'w',
                driver='GTiff', height=data.shape[0], width=data.shape[1],
                count=1, dtype='float32', crs=crs, transform=transform
            ) as dst:
                dst.write(data.astype('float32'), 1)
            print(f"✨ Saved {name.upper()} to {path}")

    except Exception as e:
        print(f"❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fetch_satellite_indices()
