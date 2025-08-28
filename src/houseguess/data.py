import csv
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

@dataclass
class House:
    filename: str
    country: str
    lat: float
    lon: float
    notes: str = ""

