import json
import os

notebook = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# 📊 Milestone 2: Advanced Urban Planning EDA\n",
                "**Project:** Adaptive Geo-AI Agent for Multimodal Urban Planning and Risk Assessment  \n",
                "**Study Area:** Colombo North, Sri Lanka\n",
                "\n",
                "## 🎯 Objectives\n",
                "Perform a professional-grade Exploratory Data Analysis (EDA) using the 6-point Urban Planning framework:\n",
                "1. **Spatial Integrity:** CRS and geometry validation.\n",
                "2. **Geometric Analysis:** Building footprints and urban density.\n",
                "3. **Hotspot Detection:** Flood risk clusters.\n",
                "4. **Correlation Analysis:** Proximity to critical amenities (Schools/Hospitals).\n",
                "5. **Remote Sensing:** NDVI (Vegetation) and NDBI (Built-up) zonal stats.\n",
                "6. **Social Context:** Identifying high-priority buildings in risk zones."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 1. Environment Setup & Data Loading"]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "import geopandas as gpd\n",
                "import matplotlib.pyplot as plt\n",
                "import rasterio\n",
                "from rasterio.plot import show\n",
                "import warnings\n",
                "warnings.filterwarnings('ignore')\n",
                "\n",
                "# Path to Clean Architecture backend\n",
                "sys.path.append('../backend/src')\n",
                "from application.analysis.urban_eda_service import UrbanEdaService\n",
                "\n",
                "eda = UrbanEdaService()\n",
                "\n",
                "# Data Paths\n",
                "DATA_PROCESSED = \"../data/processed\"\n",
                "DATA_RAW = \"../data/raw\"\n",
                "DATA_SATELLITE = \"../data/raw/satellite\"\n",
                "\n",
                "# Load base layers\n",
                "flood_gdf = gpd.read_file(f\"{DATA_PROCESSED}/flood_clean_wgs84.geojson\")\n",
                "buildings_gdf = gpd.read_file(f\"{DATA_PROCESSED}/buildings_clean_wgs84.geojson\")\n",
                "osm_gdf = gpd.read_file(f\"{DATA_RAW}/osm_features_centroids.geojson\")\n",
                "ndvi_path = f\"{DATA_SATELLITE}/colombo_north_ndvi.tif\"\n",
                "\n",
                "print(f\"✅ Loaded {len(buildings_gdf)} buildings and {len(osm_gdf)} urban features.\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 2. Spatial Data Integrity (Point 1)\n", "We validate that all layers are in the correct CRS (Metric: EPSG:5235) for accurate measurements."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "layers = {\"buildings\": buildings_gdf, \"flood\": flood_gdf, \"osm\": osm_gdf}\n",
                "integrity_results = eda.validate_spatial_integrity(layers)\n",
                "\n",
                "for layer, stats in integrity_results.items():\n",
                "    print(f\"- {layer}: {stats['current_crs']} | Missing Geoms: {stats['missing_geometries']}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 3. Geometric Urban Analysis (Point 2)\n", "Analyzing building footprints (sqm) and density."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "geo_stats = eda.analyze_geometric_patterns(buildings_gdf)\n",
                "print(f\"Total Built Area: {geo_stats['total_built_area']/1e6:.2f} sqkm\")\n",
                "print(f\"Mean Footprint: {geo_stats['mean_footprint']:.2f} sqm\")\n",
                "\n",
                "# Plotting footprint distribution\n",
                "buildings_gdf_metric = buildings_gdf.to_crs(\"EPSG:5235\")\n",
                "buildings_gdf_metric['area'] = buildings_gdf_metric.geometry.area\n",
                "buildings_gdf_metric['area'].hist(bins=100, figsize=(10, 5), color='teal')\n",
                "plt.title(\"Building Footprint Distribution (Colombo North)\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 4. Proximity & Social Context (Point 4 & 6)\n", "Find schools and hospitals located directly in flood zones and calculate proximity for others."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Find critical amenities inside flood zone\n",
                "critical_risk = eda.identify_at_risk_amenities(flood_gdf, osm_gdf)\n",
                "print(f\"🚨 ALERT: Found {len(critical_risk)} critical facilities in flood-prone zones.\")\n",
                "\n",
                "# Visualize\n",
                "ax = flood_gdf.plot(color='blue', alpha=0.3, figsize=(12, 12))\n",
                "buildings_gdf.sample(5000).plot(ax=ax, color='gray', markersize=1, alpha=0.5)\n",
                "critical_risk.plot(ax=ax, color='red', markersize=50, label='Critical Facility at Risk')\n",
                "plt.title(\"Critical Urban Facilities in Flood Risk Areas\")\n",
                "plt.legend()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": ["## 5. Remote Sensing Context (Point 5)\n", "Comparing NDVI (Vegetation) of Safe vs Risk areas."]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "# Load NDVI\n",
                "with rasterio.open(ndvi_path) as src:\n",
                "    plt.figure(figsize=(10, 10))\n",
                "    show(src, cmap='RdYlGn', title=\"NDVI (Vegetation Index) Overlay\")\n",
                "    plt.show()"
            ]
        }
    ],
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {"name": "ipython", "version": 3},
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbconvert_exporter": "python",
            "pygments_lexer": "ipython3",
            "version": "3.12.0"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open('notebooks/02_Advanced_Urban_EDA.ipynb', 'w') as f:
    json.dump(notebook, f, indent=1)

print("✨ Successfully generated notebooks/02_Advanced_Urban_EDA.ipynb")
