
import random
import requests
from io import BytesIO
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from PIL import Image, ImageTk

from .data import load_houses
from .api_client import get_random_house
from .geo import haversine_km, score_by_distance_km

ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets" / "images"

class HouseGuessApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("HouseGuess (starter)")
        self.geometry("900x640")  # basic size

        # State
        self.houses = None
        self.score = 0
        self.round = 0
        self.current = None
        self.current_image_tk = None

        # UI
        self._build_ui()
        self.next_round()

    def _build_ui(self):
        # Top: score + round
        top = ttk.Frame(self, padding=10)
        top.pack(side=tk.TOP, fill=tk.X)
        self.score_var = tk.StringVar(value="Score: 0")
        self.round_var = tk.StringVar(value="Round: 0")
        ttk.Label(top, textvariable=self.score_var).pack(side=tk.LEFT)
        ttk.Label(top, text="  |  ").pack(side=tk.LEFT)
        ttk.Label(top, textvariable=self.round_var).pack(side=tk.LEFT)

        # Center: image
        center = ttk.Frame(self, padding=10)
        center.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(center, width=800, height=400, bg="#222222")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bottom: input
        bottom = ttk.Frame(self, padding=10)
        bottom.pack(side=tk.BOTTOM, fill=tk.X)

        ttk.Label(bottom, text="Guess Country:").pack(side=tk.LEFT)
        self.entry = ttk.Entry(bottom, width=30)
        self.entry.pack(side=tk.LEFT, padx=8)
        self.entry.bind("<Return>", lambda e: self.check_guess())

        ttk.Button(bottom, text="Submit", command=self.check_guess).pack(side=tk.LEFT, padx=4)
        ttk.Button(bottom, text="Next", command=self.next_round).pack(side=tk.LEFT, padx=4)

        self.feedback_var = tk.StringVar(value="Welcome! Type a country and press Enter.")
        ttk.Label(self, textvariable=self.feedback_var, padding=10).pack(side=tk.BOTTOM, fill=tk.X)

    def _load_image(self, path: Path, max_w=800, max_h=400):
        img = Image.open(path).convert("RGB")
        img.thumbnail((max_w, max_h))
        return ImageTk.PhotoImage(img)

    def next_round(self):
        self.round += 1
        self.round_var.set(f"Round: {self.round}")
        self.entry.delete(0, tk.END)
        self.feedback_var.set("Fetching a new house...")

        try:
            self.current = get_random_house()
            resp = requests.get(self.current["image_url"], timeout=10)
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img.thumbnail((800, 400))
            self.current_image_tk = ImageTk.PhotoImage(img)

            self.canvas.delete("all")
            self.canvas.create_image(10, 10, anchor=tk.NW, image=self.current_image_tk)
            self.feedback_var.set("Make a guess!")
        except Exception as e:
            self.feedback_var.set(f"Error fetching house: {e}")
            self.canvas.delete("all")

    def check_guess(self):
        if not self.current:
            return
        guess = self.entry.get().strip().lower()
        correct = self.current.country.strip().lower()

        if not guess:
            self.feedback_var.set("Please enter a country.")
            return

        if guess == correct:
            self.score += 1000  # full points for exact country match (starter rule)
            self.feedback_var.set(f"Correct! +1000 pts. It was {self.current.country}. {self.current.notes}")
        else:
            # Starter: simple penalty. If you later accept lat/lon guesses or a map-click,
            # replace this with distance scoring using haversine_km((gLat,gLon),(trueLat,trueLon)).
            # Example with a fixed penalty for wrong country:
            self.score += 100  # consolation points
            self.feedback_var.set(f"Not quite. It was {self.current.country}. +100 pts. {self.current.notes}")

        self.score_var.set(f"Score: {self.score}")

if __name__ == "__main__":
    app = HouseGuessApp()
    app.mainloop()
