
from houseguess.geo import haversine_km, score_by_distance_km

def test_haversine_zero():
    assert abs(haversine_km((0,0),(0,0))) < 1e-6

def test_score_bounds():
    assert score_by_distance_km(0) == 1000
    assert score_by_distance_km(10000) == 0
    assert score_by_distance_km(20000) == 0  # clamped
