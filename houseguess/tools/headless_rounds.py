from __future__ import annotations
import os, random, time
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from houseguess.api_client import rapidapi_search
from houseguess.models import Place

API_DEFAULT_PARAMS = {
    "country": "us",
    "lang": "en",
    "lat": "51.5072",
    "lng": "0.12",
    "offset": "0",
    "zoom": "13",
}

def one_round(q="restaurant") -> Place:
    places = rapidapi_search(q, limit=20, extra_params=API_DEFAULT_PARAMS)
    if not places:
        raise RuntimeError("No places from API")
    p = random.choice(places)
    cats = ",".join(p.categories) if p.categories else "-"
    print(f"[ROUND] {p.name} - {p.country} @ {p.lat:.5f},{p.lon:.5f} cats={cats}")
    return p

if __name__ == "__main__":
    for i in range(3):
        one_round()
        time.sleep(0.2)
