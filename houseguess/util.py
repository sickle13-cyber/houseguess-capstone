"""
Project: HouseGuess
Authors: Preeth Vijay, Haytham Moussa, Connor Pollack, Victor Ortiz Nazario, Sam Appiah, Collin Poag
Date: 9/21/2025
Description: This file contains functionality to take API data and use it in HouseGuess operation
"""

# Libraries
import os
import requests
import shutil
from datetime import datetime
from math import radians, sin, cos, asin, sqrt

def haversine_km(a_lat: float, a_lon: float, b_lat: float, b_lon: float) -> float:
    """Great-circle distance in kilometers."""
    R = 6371.0088
    dlat = radians(b_lat - a_lat)
    dlon = radians(b_lon - a_lon)
    la1, la2 = radians(a_lat), radians(b_lat)
    h = sin(dlat / 2) ** 2 + cos(la1) * cos(la2) * sin(dlon / 2) ** 2
    return 2 * R * asin(sqrt(h))

def download_img(url: str) -> str:
    """ Returns filename for an image after downloading it, if successful."""
    prefix = "assets/images"
    if not os.path.isdir(prefix):
        os.makedirs(prefix)

    try:
        response = requests.get(url, stream=True)

        # Verifies status == 200.
        response.raise_for_status() 

        # Generate date based filename for image.
        now = datetime.now()
        formatted_string = now.strftime("%Y_%m_%d-%H_%M_%S")
        count = len(os.listdir(prefix))
        file_name = f"{formatted_string}_{count + 1}.png"

        # Save image.
        save_path = f"assets/images/{file_name}"
        with open(save_path, 'wb') as out_file:
            shutil.copyfileobj(response.raw, out_file)

        print(f"[DEBUG] Image successfully downloaded to: {save_path}")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"[DEBUG] Error downloading image: {e}")
    except IOError as e:
        print(f"[DEBUG] Error saving image to file: {e}")

    return ""
