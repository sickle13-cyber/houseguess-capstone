from __future__ import annotations
import os, time, requests
from typing import Any, Dict, List, Optional, Tuple
from .models import Place, Photo
import re  # haytham: for address parsing fallback

# Config (override via .env)
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "maps-data.p.rapidapi.com")
RAPIDAPI_BASE = os.getenv("RAPIDAPI_BASE", f"https://{RAPIDAPI_HOST}")
# maps-data search endpoint
RAPIDAPI_SEARCH_PATH = os.getenv("RAPIDAPI_SEARCH_PATH", "/searchmaps.php")

DEFAULT_TIMEOUT = (5, 20)

def _pick(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def _extract_lat_lon(j: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    # common shapes across providers
    if "lat" in j and ("lon" in j or "lng" in j):
        return float(j["lat"]), float(j.get("lon", j.get("lng")))
    if "latitude" in j and "longitude" in j:
        return float(j["latitude"]), float(j["longitude"])
    g = j.get("geometry") or {}
    loc = g.get("location") or {}
    if "lat" in loc and ("lon" in loc or "lng" in loc):
        return float(loc["lat"]), float(loc.get("lon", loc.get("lng")))
    c = j.get("coordinates") or {}
    if "lat" in c and ("lon" in c or "lng" in c):
        return float(c["lat"]), float(c.get("lon", c.get("lng")))
    return None

# RapidAPI: maps-data search
def rapidapi_search(query: str, country: Optional[str] = None, limit: int = 5, extra_params: Optional[dict] = None) -> List[Place]:
    # haytham: maps-data search endpoint
    endpoint = f"{RAPIDAPI_BASE}{RAPIDAPI_SEARCH_PATH}"
    params: Dict[str, Any] = {"query": query, "limit": limit}
    if country:
        params["country"] = country
    if extra_params:
        params.update(extra_params)

    headers = {"X-RapidAPI-Key": RAPIDAPI_KEY, "X-RapidAPI-Host": RAPIDAPI_HOST}

    # haytham: debug (disable later if noisy)
    print(f"[DEBUG] GET {endpoint}")
    print(f"[DEBUG] params={params}")
    print(f"[DEBUG] host={headers['X-RapidAPI-Host']}, key_present={bool(RAPIDAPI_KEY)}")

    r = requests.get(endpoint, headers=headers, params=params, timeout=DEFAULT_TIMEOUT)
    if r.status_code >= 400:
        print(f"[DEBUG] status={r.status_code} body={r.text[:500]}")
        if r.status_code == 403:
            raise RuntimeError("RapidAPI 403: Not subscribed or wrong app/key for maps-data.")
        r.raise_for_status()

    data = r.json()
    items = data.get("results") or data.get("items") or data.get("data") or data.get("result") or []
    if isinstance(items, dict):
        items = items.get("items", [])
    if not isinstance(items, list):
        items = []

    out: List[Place] = []

    for it in items:
        coords = _extract_lat_lon(it)
        if not coords:
            continue
        lat, lon = coords

        pid = str(_pick(it, "place_id", "id", "ref", default=f"rapidapi:{lat},{lon}:{int(time.time())}"))
        name = _pick(it, "name", "title", default="Unknown")
        addr = _pick(it, "formatted_address", "address", "vicinity", default="") or ""

        # primary keys from payload
        country_val = _pick(it, "country", "country_code", "country_name", default="") or ""

        # haytham: fallback — try to infer country from the last component of the address
        if not country_val and addr:
            parts = [s.strip() for s in addr.split(",") if s.strip()]
            if parts:
                last = parts[-1]
                # strip trailing postal codes and extra tokens (very naive, good enough)
                country_guess = re.sub(r"\b\d[\dA-Za-z \-]*$", "", last).strip()
                # don't accept a pure number/empty
                if country_guess and not re.fullmatch(r"[\d \-]+", country_guess):
                    country_val = country_guess

        cats = it.get("types") or it.get("categories") or []
        if isinstance(cats, str):
            cats = [cats]
        photos: List[Photo] = []
        for ph in (it.get("photos") or [])[:3]:
            url = _pick(ph, "url", "photo_url", default=None)
            if url:
                photos.append(Photo(url=url, width=ph.get("width"), height=ph.get("height")))

        out.append(Place(pid, name, str(country_val), float(lat), float(lon), addr, cats, photos, "rapidapi"))
    return out

def rapidapi_details(place_id: str) -> Place:
    """
    Placeholder until you locate the maps-data details endpoint on RapidAPI.
    """
    raise NotImplementedError("rapidapi_details not implemented yet")
