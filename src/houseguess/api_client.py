import os
import requests

RAPIDAPI_INFO_HOST = "https://maps-data.p.rapidapi.com/place.php"  
RAPIDAPI_IMAGE_HOST = "https://maps-data.p.rapidapi.com/photos.php"  

# retrieves key from environment variable defined in run.sh
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY") 

def get_random_house():
    """
    Example stub — adjust to match the Maps Data API response format.
    Returns a dict with keys: {image_url, country, lat, lon, notes}
    """
    url = f"https://{RAPIDAPI_HOST}/houses/random"
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key": RAPIDAPI_KEY,
    }
    resp = requests.get(url, headers=headers, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    
    # Adapt this to your actual API response schema
    return {
        "image_url": data["house"]["image"],
        "country": data["house"]["country"],
        "lat": data["house"]["lat"],
        "lon": data["house"]["lon"],
        "notes": data["house"].get("style", "")
    }
