from dataclasses import dataclass
from typing import Optional

@dataclass
class Building:
    id: str
    geometry: any  # Shapely object
    damage_pct: float
    is_damaged: bool
    risk_status: str
    risk_level: str

@dataclass
class Road:
    osmid: int
    geometry: any  # Shapely object
    road_type: str
    length: float
    oneway: bool
