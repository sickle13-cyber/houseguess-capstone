
import math
from typing import Tuple

# Simple haversine function (no external deps)
# Returns great-circle distance in kilometers between (lat1,lon1) and (lat2,lon2)
def haversine_km(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    R = 6371.0088  # mean Earth radius in km
    lat1, lon1 = map(math.radians, p1)
    lat2, lon2 = map(math.radians, p2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def score_by_distance_km(distance_km: float) -> int:
    """Example scoring: closer => more points.
    0 km: 1000 points, 10000 km: 0 points (clamped)
    Modify as desired.
    """
    max_dist = 10000.0
    distance_km = max(0.0, min(distance_km, max_dist))
    return int(round(1000 * (1.0 - (distance_km / max_dist))))
