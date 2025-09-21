"""
Project: HouseGuess
Authors: Preeth Vijay, Haytham Moussa, Connor Pollack, Victor Ortiz Nazario, Sam Appiah, Collin Poag
Date: 9/21/2025
Description: This file contains initialization functionality for HouseGuess
"""

"""Libraries"""
import os
from dotenv import load_dotenv
from .gui import App
from .models import RapidAPIConfig

def HouseGuessMain():
    """Function to initialize API configuration from .env file and start HouseGuess"""
    try:
        load_dotenv()
    except Exception:
        print(".env file not found. Environment variables need to be set for HouseGuess to work properly.")

    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "maps-data.p.rapidapi.com")
    RAPIDAPI_BASE = os.getenv("RAPIDAPI_BASE", f"https://{RAPIDAPI_HOST}")
    RAPIDAPI_SEARCH_PATH = os.getenv("RAPIDAPI_SEARCH_PATH", "/searchmaps.php")
    DEFAULT_TIMEOUT = (5, 20)

    config = RapidAPIConfig(RAPIDAPI_KEY, RAPIDAPI_HOST, RAPIDAPI_BASE, RAPIDAPI_SEARCH_PATH, DEFAULT_TIMEOUT)

    app = App(config)
    app.mainloop()
