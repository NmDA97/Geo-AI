import pytest
import sys
import os
from pathlib import Path

# Add the src directory to the python path so modules can be imported
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.baseline.overlay import calculate_risk_score

def test_high_risk_zone_kelani_river():
    """
    TEST-02-BASELINE: Verify a known high-risk coordinate results in High Risk.
    Using a valid centroid from the 2014 shapefile (in Eastern Province / Uva, based on actual shapefile extent).
    """
    result = calculate_risk_score(7.0321, 81.8415)
    
    # We expect high risk
    assert result["risk_level"] == "High"
    assert result["risk_score"] == 1.0

def test_low_risk_zone_city_center():
    """
    Verify Coordinate (6.90, 79.85) results in Low Risk.
    This coordinate is further south in the city center.
    """
    result = calculate_risk_score(6.90, 79.85)
    
    # We expect low risk
    assert result["risk_level"] == "Low"
    assert result["risk_score"] == 0.0
