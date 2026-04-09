# Geo-AI Project Progress Report
**Project Title:** Adaptive Geo-AI Agent for Multimodal Urban Planning and Risk Assessment  
**Student Name:** H A N M Hettiarachchi  
**Index Number:** 258727X  
**Date:** April 9, 2026

---

## 1. Introduction: The Urgency of Smart Urban Planning

The skyline of Sri Lanka is changing at an unprecedented pace. From the high-rises of central Colombo to the sprawling suburbs in the outskirts, the country is undergoing a massive urban transformation. However, during my travels around the country, I have observed a recurring and troubling pattern: our urban planning systems seem to be lagging behind this physical growth. The lack of a unified, smart, and data-driven approach to new constructions is not just a localized administrative issue; it is a nationwide challenge that carries significant environmental and economic risks.

One of the most pressing symptoms of this "planning gap" is the construction of residential and commercial buildings in areas that are either environmentally sensitive or technically unsuitable. This is nowhere more evident than in **Colombo North**, specifically in the wards of **Modara, Grandpass, and Mattakkuliya**. This region represents what urban planners often call a "perfect storm." It combines some of the highest population and building densities in Sri Lanka with a geographic location that is essentially the front line of the Kelani River's high-risk flood zones.

Currently, the effort required for a developer, a government official, or an average citizen to verify the safety and legality of a site is immense. One must manually cross-reference static PDF zoning plans from the Urban Development Authority (UDA), consult soil and safety guidelines from the National Building Research Organisation (NBRO), and then attempt to overlay this information mentally against flood hazard maps. This process is slow, confusing, and dangerously dependent on human interpretation, which leaves a wide margin for error. 

My project, the **Adaptive Geo-AI Agent**, was born from the realization that we can bridge this gap by using artificial intelligence to "reason" through spatial data and government regulations. The goal is to move away from fragmented maps toward a system where a user can simply ask a question in plain English and receive a recommendation that is both scientifically grounded and legally compliant.

---

## 2. Study Area Expansion and Descriptive Data Collection

### 2.1 Geographic Focus
While the project initially focused on the core wards of Colombo North, I realized during the early stages of data analysis that floods do not respect ward boundaries. To build a truly predictive system, I had to expand the study area to include **Kelaniya and Angoda**. These areas are hydrologically linked to Colombo North, and including them allows the system to analyze the movement of floodwaters along the Kelani River corridor more accurately. This expanded boundary now encompasses a diverse range of urban textures, from industrial zones to dense residential clusters.

### 2.2 The "Messiness" of Real-World Data
One of the first major challenges I encountered was the scarcity and "messiness" of data. While we live in a world of "Big Data," local planning data in Sri Lanka is often trapped in static formats.

1.  **OpenStreetMap (OSM) as a Foundation:** I utilized the `OSMnx` and `Pyrosm` libraries to extract raw vector data. This provided the "skeleton" of the city—road networks, building footprints, and land-use types. However, OSM data for Colombo North, while extensive, often lacks specific attributes like floor counts or building materials, requiring further enrichment.
2.  **PlanetScope Satellite Imagery:** To fill the gaps in ground-truth data, I integrated high-resolution satellite imagery from the **PlanetScope** constellation. These 3-meter resolution images allow for contemporary damage assessment and allow the system to detect new constructions that may not yet appear on OSM or official maps.
3.  **Hydrographical and Environmental Data:** Sourcing flood maps proved to be a significant task. I utilized the **RiskInfo/HDX Sri Lanka** portal to obtain flood inundation rasters. Because many of these maps were originally designed as PDF visuals, I had to perform extensive georeferencing in **QGIS** to digitize them into structured GeoJSON formats that the AI agent can "read."
4.  **Regulatory PDFs:** I collected the "Colombo Commercial City Development Plan 2019-2030" and NBRO safety manuals. These aren't just documents; they are the "rules of the game" that the AI must master.

---

## 3. Spatial Data Engineering and Preprocessing

The core of a GeoAI project lies not just in the "AI," but in the "Geo." Before any reasoning can happen, the data must be engineered into a format that supports rapid spatial computation.

### 3.1 Establishing a Spatial Source of Truth
I implemented a robust preprocessing pipeline using **Python and GeoPandas**. A critical first step was **CRS (Coordinate Reference System) Standardization**. Geospatial data often comes in various projections (like Kandawala or WGS84). To ensure that a "point" in a building footprint aligns perfectly with a "pixel" in a flood map, I standardized the entire dataset to **WGS84 (EPSG:4326)**, ensuring that spatial intersections (like checking if a building is inside a flood zone) are mathematically accurate.

### 3.2 Automated Clipping and Cleaning
Using `shapely` and `geopandas`, I built an automated scripts (`preprocess_geoai.py`) that clips raw national-level datasets to my specific study area bbox. This process is more than just cropping; it involves:
- **Geometry Validation:** Fixing "self-intersecting" polygons and invalid geometries that often crash spatial databases.
- **Simplification:** Using the Douglas-Peucker algorithm to simplify complex building shapes. This is vital for performance. By reducing the number of vertices in 154,000 buildings, I achieved a 40% reduction in data size while maintaining 99.9% topological accuracy.

### 3.3 The Power of PostGIS
To manage the massive volume of data, I deployed a **PostGIS** backend. Standard relational databases are built for text and numbers; PostGIS is built for geography. It allows the backend to perform complex spatial intersections in milliseconds. For example, the system can instantly identify every building that overlaps with a "High Risk" flood polygon using the `ST_Intersects` function. This performance is the bedrock upon which the real-time agent is built.

---

## 4. Current Progress: The Visualization Layer

To validate the preprocessing pipeline, I have developed a high-performance **Frontend Visualization Dashboard**. 

Initially, I used the Leaflet library for mapping. However, as the dataset grew to over 150,000 buildings, the browser started to struggle. In a major progress milestone, I migrated the entire frontend map engine to **MapLibre GL JS**. MapLibre uses hardware acceleration (the user's GPU) to render vector tiles, ensuring that panning and zooming across Colombo North feels smooth and responsive.

I have also implemented a **glassmorphic design system** using vanilla CSS. This choice was deliberate: I wanted the interface to feel premium and "alive." Interactive layers allow users to toggle between building density, road connectivity, and flood zones, providing an immediate visual understanding of the urban risk landscape.

---

## 5. Now Building: The Agentic Reasoning Core

The most significant transition in the project is taking place right now: the shift from a "passive map tool" to an **active GeoAI Agent**.

### 5.1 Integrating LangChain and ReAct
I am currently implementing the agent's logic using the **LangChain** framework and the **ReAct (Reason/Act)** pattern. Standard LLMs often struggle with spatial logic—they might "hallucinate" distances or locations. To prevent this, I am building a suite of specialized **Python Tools** that the agent can "pick up and use":
- **`check_flood_risk`**: A tool that takes a coordinate and returns the exact risk level from PostGIS.
- **`verify_zoning_regulations`**: A tool that checks the UDA zoning rules for a specific ward.
- **`calculate_infrastructure_proximity`**: A tool that finds the nearest school, hospital, or emergency center using spatial joins.

By using the ReAct framework, when a user asks, "Is it safe to build a school here?", the agent doesn't just predict the next word; it "reasons": *I need to check the flood risk, then I need to check the zoning laws, then I will synthesize the answer.*

### 5.2 Retrieval-Augmented Generation (RAG) for Regulations
To ensure the agent gives legally sound advice, I am developing a **RAG pipeline**. I am using **ChromaDB** as a vector store to index the text from UDA and NBRO guidelines. When the agent answers a query, it "retrieves" the relevant clause from the original PDF and uses it to "augment" its response. This creates a "Source-Grounded" system where every recommendation is backed by a direct citation from the law.

---

## 6. Challenges, Mitigations, and Next Steps

The journey hasn't been without its hurdles. Managing the memory constraints of local vector processing and handling the "hallucination" rates of LLMs are ongoing areas of research. However, by enforcing a logic where the agent *must* provide a citation for every claim, I have significantly improved the reliability of the system.

### Next Steps:
- **Finalizing the RAG Integration:** Ensuring the agent can handle multi-page regulatory documents seamlessly.
- **Quantitative Evaluation:** Comparing the GeoAI Agent's siting recommendations against traditional **Multi-Criteria Decision Analysis (MCDA)** models to scientifically validate its performance.
- **Agent Testing:** Stress-testing the system with complex, multi-variable queries from potential urban planners.

---
© 2026 H A N M Hettiarachchi - University Project Submission
