"""
Project: HouseGuess
Authors: Preeth Vijay, Haytham Moussa, Connor Pollack, Victor Ortiz Nazario, Sam Appiah, Collin Poag
Date: 9/21/2025
Description: This file allows HouseGuess to make requests to the Maps Data API hosted on RapidAPI
"""

"""Libraries""""
import os
import time
import requests
import re
from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from .models import Place, Photo
from .models import RapidAPIConfig
from .util import download_img

def _pick(d: Dict[str, Any], *keys, default=None):
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return default

def _extract_lat_lon(j: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """Extract Longitude and Latitude from API response for later use"""
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

def rapidapi_search(config: RapidAPIConfig, query: str, country: Optional[str] = None, limit: int = 5, extra_params: Optional[dict] = None) -> list[Place]:
    """Function to create and send search to Maps Data API"""
    endpoint = f"{config.endpoint}{config.search_path}"
    params: Dict[str, Any] = {"query": query, "limit": limit}
    if country:
        params["country"] = country
    if extra_params:
        params.update(extra_params)

    headers = {"x-rapidapi-key": config.key, "x-rapidapi-host": config.host}

    # haytham: debug (disable later if noisy)
    print(f"[DEBUG] GET {endpoint}")
    print(f"[DEBUG] params={params}")
    print(f"[DEBUG] host={config.host}, key_present={bool(config.key)}")

    r = requests.get(endpoint, headers=headers, params=params, timeout=config.timeout)
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

    out: list[Place] = []

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
        photos: list[Photo] = []
        for ph in (it.get("photos") or [])[:3]:
            url = _pick(ph, "url", "src", default=None)
            if url:
                max_width = ph.get("max_size")[0]
                max_height = ph.get("max_size")[1]
                suffix = url.rindex("=")
                url = f"{url[:suffix + 1]}w{max_width}-h{max_height}"
                if file_path := download_img(url):
                    photo = Photo(file_path=file_path, width=max_width, height=max_height)
                    print("[DEBUG] photo:", photo)
                    photos.append(photo)
                else:
                    print("[DEBUG] Failed to get image...")
    
        place_link = _pick(it, "place_link", "place_url", default="")
        place = Place(pid, name, str(country_val), float(lat), float(lon), place_link, address=addr, categories=cats, photos=photos)
        if phone := _pick(it, "phone_number", "phone", default=""):
            place.phone_number = str(phone)

        if website := _pick(it, "website_number", "website", default=""):
            place.website = str(website)

        out.append(place)
    print("[DEBUG] place count:", len(out))
    return out

def rapidapi_details(place_id: str) -> Place:
    """
    Placeholder until maps-data details endpoint is located on RapidAPI.
    """
    raise NotImplementedError("rapidapi_details not implemented yet")
