from dataclasses import dataclass
from typing import List
from pathlib import Path

@dataclass
class House:
    filename: str = ""
    country: str = ""
    lat: float = 0.0
    lon: float = 0.0
    notes: str = ""
    name: str = ""

def load_houses() -> List[House]:
    img_dir = Path(__file__).resolve().parents[2] / "assets" / "images"
    houses: List[House] = []
    if img_dir.exists():
        for p in img_dir.glob("*.*"):
            if p.is_file():
                stem = p.stem
                houses.append(House(filename=p.name, name=stem, notes=stem))
    return houses
