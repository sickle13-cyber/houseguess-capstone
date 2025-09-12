from dotenv import load_dotenv
import os

from .gui import App
from .models import RapidAPIConfig

def HouseGuessMain():
    # haytham: load .env so RAPIDAPI_* vars are available without hardcoding
    try:
        load_dotenv()
    except Exception:
        print(".env file not found. Environment variables need to be set for HouseGuess to work properly.")

    # Config (override via .env)
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "maps-data.p.rapidapi.com")
    RAPIDAPI_BASE = os.getenv("RAPIDAPI_BASE", f"https://{RAPIDAPI_HOST}")
    RAPIDAPI_SEARCH_PATH = os.getenv("RAPIDAPI_SEARCH_PATH", "/searchmaps.php")
    DEFAULT_TIMEOUT = (5, 20)

    config = RapidAPIConfig(RAPIDAPI_KEY, RAPIDAPI_HOST, RAPIDAPI_BASE, RAPIDAPI_SEARCH_PATH, DEFAULT_TIMEOUT)

    app = App(config)
    app.mainloop()
