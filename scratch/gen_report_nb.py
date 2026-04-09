import json
import os

notebook = {
    'cells': [
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': [
                '# Advanced Urban Resilience & Geo-AI Progress Report\n',
                '**Project:** Adaptive Geo-AI Agent for Multimodal Urban Planning and Risk Assessment  \n',
                '**Pilot Study Area:** Colombo North (Modara, Grandpass, Mattakkuliya)\n',
                '\n',
                '--- \n',
                '**Candidate Information**  \n',
                '**Name:** H A N M Hettiarachchi  \n',
                '**Index:** 258727X  \n',
                '--- \n',
                '\n',
                '## 🎯 Executive Summary\n',
                'Urban transformations in Sri Lanka often lack smart, data-driven planning, leading to construction in environmentally sensitive areas. In Colombo North—characterized by extreme building densities and Kelani River flood risks—this issue is critical. This notebook demonstrates the quantitative and spatial foundation for a **Geo-AI Agent** designed to automate site suitability assessments by integrating real-world geographic data with regulatory constraints.'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 1. Technological Infrastructure & Geospatial Environment\n', 'The Geo-AI backend leverages Python-based spatial libraries to process high-resolution vector and satellite data. CRS standardization ensures all computations are aligned with global WGS84 and local Sri Lankan grid standards.']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                'import os\n',
                'import geopandas as gpd\n',
                'import pandas as pd\n',
                'import matplotlib.pyplot as plt\n',
                'import seaborn as sns\n',
                'import folium\n',
                'from folium import plugins\n',
                'from shapely.geometry import Point\n',
                'import warnings\n',
                'warnings.filterwarnings("ignore")\n',
                '\n',
                '# Core Configurations\n',
                'WGS84 = "EPSG:4326"\n',
                'DATA_DIR = "../data"\n',
                'FLOOD_2025_PATH = "../data/raw/flood_maps/FL20251128LKA_SHP/Multisensors_20251126_20251202_FloodExtent_SriLanka.shp"\n',
                '\n',
                'sns.set_theme(style="whitegrid")\n',
                'print("✅ Geospatial environment initialized for H A N M Hettiarachchi (258727X).")'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 2. Multi-Modal Data Ingestion\n', 'Accurate reasoning requires access to primary sources. We ingest data from OpenStreetMap (building footprints, roads, amenities) and UNOSAT telemetry (flood extents).']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                '# Load standardized datasets\n',
                'buildings = gpd.read_file(f"{DATA_DIR}/processed/buildings_clean_wgs84.geojson")\n',
                'roads = gpd.read_file(f"{DATA_DIR}/processed/processed_roads_cleaned.geojson")\n',
                'osm_centroids = gpd.read_file(f"{DATA_DIR}/raw/osm_features_centroids.geojson")\n',
                'flood_2025 = gpd.read_file(FLOOD_2025_PATH)\n',
                '\n',
                '# Align Coordinate Reference Systems\n',
                'if flood_2025.crs != buildings.crs:\n',
                '    flood_2025 = flood_2025.to_crs(buildings.crs)\n',
                '\n',
                '# Filter for project-specific critical facilities\n',
                'critical_fac = osm_centroids[osm_centroids["amenity"].isin(["school", "hospital", "clinic", "university"])]\n',
                '\n',
                'print(f"📊 Dataset Integrity Summary:")\n',
                'print(f"- Total Urban Footprints (Colombo North Area): {len(buildings):,}")\n',
                'print(f"- Transportation Network Segments: {len(roads):,}")\n',
                'print(f"- Critical Life-Safety Amenities: {len(critical_fac):,}")'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 3. Urban Morphological Profiling: Modara, Grandpass & Mattakkuliya\n', 'We analyze the high building density of the study area to understand the socio-economic "Exposure Surface".']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                'fig, ax = plt.subplots(1, 2, figsize=(20, 8))\n',
                '\n',
                '# Plot 1: Amenity Distribution (Socio-Economic Infrastructure)\n',
                'amenity_counts = critical_fac["amenity"].value_counts()\n',
                'sns.barplot(x=amenity_counts.values, y=amenity_counts.index, ax=ax[0], palette="viridis")\n',
                'ax[0].set_title("Distribution of Critical Social Infrastructure")\n',
                'ax[0].set_xlabel("Count of Facilities")\n',
                '\n',
                '# Plot 2: Road Network Density Approximation\n',
                '# Using road length as a proxy for urban connectivity\n',
                'sns.histplot(roads["length"], bins=50, ax=ax[1], color="teal", kde=True)\n',
                'ax[1].set_title("Road Segment Length Distribution (Network Connectivity)")\n',
                'ax[1].set_xlabel("Length (meters)")\n',
                '\n',
                'plt.tight_layout()\n',
                'plt.show()'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 4. Problem Statement Context: Automated Risk Detection\n', 'Manual checking of UDA zoning and flood maps is slow and error-prone. The Geo-AI agent automates this by performing spatial intersections at millisecond speeds.']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                '# Automated spatial join for exposure detection\n',
                'vulnerable_buildings = gpd.sjoin(buildings, flood_2025, how="inner", predicate="intersects")\n',
                'vulnerable_amenities = gpd.sjoin(critical_fac, flood_2025, how="inner", predicate="intersects")\n',
                '\n',
                '# Quantitative Exposure Metrics for H A N M Hettiarachchi (258727X)\n',
                'exposure_percentage = (len(vulnerable_buildings) / len(buildings)) * 100\n',
                '\n',
                'print(f"🚨 EXPOSURE REPORT - NOVEMBER 2025 FLOOD EVENT:")\n',
                'print(f"- Total Households/Units Affected: {len(vulnerable_buildings):,}")\n',
                'print(f"- Study Area Impact Ratio: {exposure_percentage:.2f}% of monitored building stock.")\n',
                'print(f"- High-Risk Critical Facilities: {len(vulnerable_amenities)} Schools/Hospitals identified.")'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 5. Decision Support Visualization (Agentic View)\n', 'This visualization reflects what the Geo-AI Agent "sees" when determining site suitability. Red markers indicate areas where the agent would trigger an "Unsuitable Zone Report".']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                'fig, ax = plt.subplots(figsize=(15, 15))\n',
                '\n',
                '# Base map layers\n',
                'buildings.plot(ax=ax, color="#eceff1", edgecolor="#cfd8dc", linewidth=0.3, label="Base Urban Fabric")\n',
                'roads.plot(ax=ax, color="#90a4ae", linewidth=0.5, alpha=0.5)\n',
                '\n',
                '# Flood Context (UNOSAT November 2025)\n',
                'flood_2025.plot(ax=ax, color="#bbdefb", alpha=0.5, label="2025 Master Flood Layer")\n',
                '\n',
                '# Identified Risk Objects\n',
                'if not vulnerable_buildings.empty:\n',
                '    vulnerable_buildings.plot(ax=ax, color="#ef5350", markersize=0.5, label="High-Risk Footprints")\n',
                '\n',
                'if not vulnerable_amenities.empty:\n',
                '    vulnerable_amenities.plot(ax=ax, color="#b71c1c", markersize=120, marker="P", label="Critical Infrastructure Exposure")\n',
                '\n',
                'plt.title("GeoAI Diagnostic Overlay: Infrastructure Inundation Exposure Analysis", fontsize=16)\n',
                'plt.legend(loc="upper right", frameon=True)\n',
                'plt.axis("off")\n',
                'plt.show()'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 6. Interactive Ground-Truthing Dashboard\n', 'The dynamic map for field-level decision support allows for rapid verification of zoning and safety non-compliance.']
        },
        {
            'cell_type': 'code',
            'execution_count': None,
            'metadata': {},
            'outputs': [],
            'source': [
                'm = folium.Map(location=[buildings.centroid.y.mean(), buildings.centroid.x.mean()], zoom_start=14, tiles="cartodbpositron")\n',
                '\n',
                '# Risk Density Heatmap\n',
                'risk_points = [[row.geometry.centroid.y, row.geometry.centroid.x] for _, row in vulnerable_buildings.iterrows()]\n',
                'plugins.HeatMap(risk_points, radius=10, blur=15, name="Flood Risk Hotspots").add_to(m)\n',
                '\n',
                '# Critical Asset Layer with Risk Popups\n',
                'for _, row in vulnerable_amenities.iterrows():\n',
                '    folium.Marker(\n',
                '        location=[row.geometry.y, row.geometry.x],\n',
                '        popup=f"VULNERABLE ASSET: {row.get(\'name\', row[\'amenity\'])}",\n',
                '        icon=folium.Icon(color="red", icon="cloud")\n',
                '    ).add_to(m)\n',
                '\n',
                'folium.LayerControl().add_to(m)\n',
                'm'
            ]
        },
        {
            'cell_type': 'markdown',
            'metadata': {},
            'source': ['## 7. Conclusions and Technical Readiness\n', '1. **Study Area Complexity:** Modeling the Modara/Grandpass corridor successfully captures the interaction between urban density and hydrology.\n', '2. **Data-Driven Siting:** The automation shown here is a prerequisite for the GeoAI Agent to generate "legally sound and scientifically backed" recommendations.\n', '3. **Future Extension:** The modular architecture allows for the integration of RAG (Retrieval-Augmented Generation) to ingest UDA/NBRO safety guidelines, providing citations alongside these spatial results.']
        }
    ],
    'metadata': {
        'kernelspec': {'display_name': 'Python 3', 'language': 'python', 'name': 'python3'},
        'language_info': {'name': 'python', 'version': '3.12.0'}
    },
    'nbformat': 4,
    'nbformat_minor': 4
}

with open('notebooks/Project_Progress_Report_EDA.ipynb', 'w') as f:
    json.dump(notebook, f, indent=4)

print("✨ Successfully generated FINAL OFFICIAL notebooks/Project_Progress_Report_EDA.ipynb")
