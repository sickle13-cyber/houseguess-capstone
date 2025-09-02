from __future__ import annotations
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Tuple

@dataclass
class Photo:
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    attributions: Optional[str] = None

@dataclass
class Place:
    id: str
    name: str
    country: str
    lat: float
    lon: float
    address: Optional[str] = None
    categories: List[str] = field(default_factory=list)
    photos: List[Photo] = field(default_factory=list)
    source: str = "api"

    def coords(self) -> Tuple[float, float]:
        return (self.lat, self.lon)

    def label(self) -> str:
        return f"{self.name}{f' - {self.country}' if self.country else ''}"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
