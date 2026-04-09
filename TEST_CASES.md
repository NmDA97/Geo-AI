# Golden Test Cases

## Phase 1: Environment & Data
**Test ID:** `TEST-01-NAV`
**Goal:** Verify Environment & Data Ingestion
**Procedure:**
1. Run `docker-compose up -d db`
2. Run `python src/etl/fetch_data.py`
**Success Criteria:**
- PostGIS container is running (`docker ps` shows healthy).
- `data/raw/colombo_roads.gpkg` exists.
- `data/raw/colombo_buildings.gpkg` exists.
- No "Architecture mismatch" errors on Apple Silicon.

## Phase 2: The Baseline (Marks Security)
**Test ID:** `TEST-02-BASELINE`
**Goal:** Verify Deterministic Weighted Overlay (No AI)
**Procedure:**
1. Run `pytest tests/test_baseline.py`
**Success Criteria:**
- **Input:** Coordinate `(6.97, 79.86)` (Kelani River mouth / High Flood Zone).
- **Expected Output:** `Suitability Score < 0.3` (Low Suitability) OR `Risk Score > 0.8` (High Risk).
- **Constraint:** Function must run fast (< 100ms) and strictly use Rasterio/Geopandas.

## Phase 3: The Geo-AI Backend
**Test ID:** `TEST-03-AGENT`
**Goal:** Verify Agent Reasoning & RAG
**Procedure:**
1. Send API Request: `POST /query { "question": "What is the minimum lot size for a seamless warehouse in Zone 2?" }`
**Success Criteria:**
- **Response:** Contains "6 perches" (or specific value from UDA docs).
- **Citations:** Response includes `Source: UDA_Zone2_Regulations.pdf, Page 12`.
- **Latency:** < 15 seconds (local LLM/quantized).

## Phase 4: Professional UI
**Test ID:** `TEST-04-UI`
**Goal:** Verify Split-Screen & Interactions
**Procedure:**
1. Open `http://localhost:3000`
2. Click on the Map at `(6.9, 79.9)`.
3. Verify Chat window updates context to "Selected Location: 6.9, 79.9".
**Success Criteria:**
- Map renders specific "Colombo North" tiles.
- Chat input is accessible.
- No React hydration errors.
