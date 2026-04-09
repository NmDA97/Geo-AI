# Setup Guide: Adaptive Geo-AI Agent

## Prerequisites
- **Computer**: MacBook Pro M4 (or Apple Silicon equivalent)
- **OS**: macOS Sonoma or later
- **Docker**: Docker Desktop for Mac (ensure "Use Rosetta for x86/amd64 emulation on Apple Silicon" is ON, though we aim for ARM64 native)
- **Git**

## 1. Environment Setup

### Clone and Directories
```bash
git clone <repo_url> geoai_agent
cd geoai_agent
```

### Docker
Start the PostGIS database:
```bash
docker-compose up -d db
```
Verify it is running:
```bash
docker ps
# Look for 'postgis/postgis' status 'Up'
```

## 2. Data Engineering (Phase 1)

### Install Dependencies (Local Python)
It is recommended to use a virtual environment for the ETL scripts if not running inside Docker.
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Fetch OpenStreetMap Data
Run the ETL script to download building and road signatures for Colombo:
```bash
# From backend directory
python src/etl/fetch_data.py
```
*Expected Output*: Should save `colombo_buildings.gpkg` and `colombo_roads.gpkg` to `data/raw`.

### Manual Data Ingestion
Due to proprietary licensing, you must manually place the following files:
1. **Flood Risk Raster**: Place the `.tif` file in `data/raw/flood_maps/`
2. **Legal Docs**: Place UDA Regulation PDFs in `data/raw/uda_pdfs/`

### Preprocessing and Database Ingestion
Run the preprocessing script to filter data for Colombo North and ingest it into PostGIS:
```bash
docker compose run --rm backend python3 preprocess_geoai.py
```
*Expected Output*: 
- Filtered GeoJSON at `backend/cache/colombo_north_buildings.geojson`.
- Data ingested into PostGIS `buildings` table.
- Summary stats at `backend/cache/colombo_north_stats.json`.

## 3. Running EDA and Backend
Once preprocessing is complete, you can run the full environment:
```bash
docker compose up -d
```
The backend API will be available at `http://localhost:8000`.

## 4. Troubleshooting
**Apple Silicon (M1/M2/M3/M4) Issues:**
- If you see `exec format error`, ensure you are building/pulling `linux/arm64` images.
- The provided `docker-compose.yml` uses `postgis/postgis:15-3.3` which supports ARM64.

**OSMnx Errors:**
- If SSL errors occur during download, ensure your Python environment has updated certificates: `pip install --upgrade certifi`.
