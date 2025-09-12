from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class RapidAPIConfig:
    key: str
    host: str
    endpoint: str
    search_path: str
    timeout: tuple

@dataclass
class Photo:
    url: str
    width: Optional[int] = None
    height: Optional[int] = None

@dataclass
class Place:
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
        return (self.lat, self.lon)

    def label(self) -> str:
        return f"{self.name}{f' - {self.country}' if self.country else ''}"

    def addUserScore(self, reviews: int, rating: float):
        self.reviews = reviews
        self.rating = rating
   
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
