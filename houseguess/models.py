"""
Project: HouseGuess
Authors: Preeth Vijay, Haytham Moussa, Connor Pollack, Victor Ortiz Nazario, Sam Appiah, Collin Poag
Date: 9/21/2025
Description: This file contains classes that assist in HouseGuess operation
"""

# Libraries
from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class RapidAPIConfig:
    """Class to hold API config data""" 
   
    # Instance variables
    key: str
    host: str
    endpoint: str
    search_path: str
    timeout: tuple

@dataclass
class Photo:
    """"Class to represent image to be utilized by HouseGuess"""
    
    # Instance variables
    file_path: str
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class Place:
    """Class to represent location"""
    
    # Instance Variables
    id: str
    name: str
    country: str
    lat: float
    lon: float
    place_link: str
    address: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    photos: List[Photo] = field(default_factory=list)
    phone_number: Optional[str] = None
    website: Optional[str] = None
    reviews: Optional[int] = None
    rating: Optional[float] = None

    def coords(self) -> Tuple[float, float]:
        """Return coordinates of location"""
        return (self.lat, self.lon)

    def label(self) -> str:
        """Return name of location"""
        return f"{self.name}{f' - {self.country}' if self.country else ''}"

    def addUserScore(self, reviews: int, rating: float):
        """Add information about place to be displayed as part of score feedback"""
        self.reviews = reviews
        self.rating = rating
   
    def to_dict(self) -> Dict[str, Any]:
        """Return place object as dictionary"""
        return asdict(self)
