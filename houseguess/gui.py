"""
Project: HouseGuess
Authors: Preeth Vijay, Haytham Moussa, Connor Pollack, Victor Ortiz Nazario, Sam Appiah, Collin Poag
Date: 9/21/2025
Description: This file contains initialization functionality for HouseGuess
"""

# Libraries (Requires: pip install pillow tkintermapview)
import math
import os
import tkinter as tk
from .api_client import rapidapi_search
from .models import Place, Photo, RapidAPIConfig
from .util import haversine_km
from __future__ import annotations
from PIL import Image, ImageTk
from tkinter import ttk, messagebox
from tkintermapview import TkinterMapView
from typing import Optional, Tuple

# Windows DPI fix (MUST run before creating Tk)
try:
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)  # per-monitor DPI awareness
except Exception:
    pass

# ---------------- Theme ----------------
# Preeth: Consider renaming colors based on semantic purpose vs actual color.
DARK_BLUE = "#0B2638"
CARD_BG = "#0f3550"
CREAM = "#F5E6C8"
LIGHT_GREEN = "#6FCF97"   # Connor: Switched from orange to green since it's my wife and my wedding colors. :)
TEAL = "#4CA6A8"
GRAY = "#333333"

# ---------------- Widgets ----------------
class PhotoPanel(ttk.Frame):
    """Left panel that displays the current round image with safe resizing."""
    
    def __init__(self, master):
        """Initiate Photo Panel (left panel)"""
        super().__init__(master)
        self.canvas = tk.Canvas(self, bg="#101010", highlightthickness=1, highlightbackground=GRAY)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Configure>", lambda e: self._redraw())
        self._pil: Optional[Image.Image] = None
        self._tk: Optional[ImageTk.PhotoImage] = None
        self._last_size: Tuple[int, int] = (0, 0)
        self._error: Optional[str] = None

    def set_image_path(self, path: str):
        """Set path to find image for left panel"""
        self._pil = None
        self._tk = None
        self._error = None
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(path)
            img = Image.open(path).convert("RGB")
            self._pil = img
        except Exception as e:
            self._error = f"Image error:\n{e}"
        
        self._last_size = (0, 0)
        
        self._redraw()

    def _redraw(self):
    """Refresh left panel"""
        c = self.canvas
        c.delete("all")
        w, h = max(1, c.winfo_width()), max(1, c.winfo_height())
        c.create_rectangle(0, 0, w, h, fill=DARK_BLUE, outline="")
        c.create_rectangle(4, 4, w - 4, h - 4, outline=GRAY)
        if self._error:
            c.create_text(w//2, h//2, text=self._error, fill=CREAM, font=("Segoe UI", 16), justify="center")
            return
        if self._pil is None:
            c.create_text(w//2, h//2, text="(No image)", fill=CREAM, font=("Segoe UI", 16))
            return
        if (w, h) != self._last_size:
            img = self._pil.copy()
            img.thumbnail((w - 12, h - 12))
            self._tk = ImageTk.PhotoImage(img)
            self._last_size = (w, h)
        c.create_image(w // 2, h // 2, image=self._tk)

class ZoomMap(ttk.Frame):
    """Pan/zoom map using OpenStreetMap tiles. Accurate click marker with enable/disable."""

    def __init__(self, master, on_guess, start_center=(20.0, 0.0), start_zoom=2):
        """Initiate ZoomMap panel (right panel)"""
        super().__init__(master)
        self.on_guess = on_guess
        self._marker = None
        self._enabled = True  #Connor: block clicks when disabled

        self.map = TkinterMapView(self, corner_radius=0)
        self.map.pack(fill="both", expand=True)
        self.map.set_position(start_center[0], start_center[1])  # lat, lon
        self.map.set_zoom(start_zoom)

        # Connor: Uses geo-click callback PTL for no pixel math amrite?
        self.map.add_left_click_map_command(self._on_left_click)

    def set_enabled(self, value: bool):
        """Enable or disable reacting to clicks."""
        self._enabled = bool(value)

    def reset_pin(self):
        """Reset user-selected position on map"""
        if self._marker:
            try:
                self.map.delete(self._marker)
            except Exception:
                pass
            self._marker = None

    def _on_left_click(self, coords):
        """records guess and updates game state"""
        if not self._enabled:
            return
        try:
            lat, lon = float(coords[0]), float(coords[1])
        except Exception:
            return
        if self._marker:
            try:
                self.map.delete(self._marker)
            except Exception:
                pass
        self._marker = self.map.set_marker(lat, lon, text=f"{lat:.2f}, {lon:.2f}")
        self.on_guess(lat, lon)

class ControlPanel(ttk.Frame):
    """Right-side control stack: coords, big buttons, feedback."""
    
    def __init__(self, master, on_submit, on_next):
        """Initiate ControlPanel (right panel functionality)"""
        super().__init__(master)

        #Connor: Full-height stack (gets half of the right column)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)  # coords label
        self.rowconfigure(1, weight=1)  # buttons container
        self.rowconfigure(2, weight=0)  # feedback

        # Coordinates
        self.coords = tk.StringVar(value="Lat: —   Lon: —")
        ttk.Label(self, textvariable=self.coords, font=("Segoe UI", 20, "bold")).grid(
            row=0, column=0, sticky="w", pady=(8, 12)
        )

        # Big buttons (stacked)
        btns = ttk.Frame(self)
        btns.grid(row=1, column=0, sticky="nsew")
        btns.columnconfigure(0, weight=1)

        self.submit_btn = ttk.Button(btns, text="Submit Guess", command=on_submit)
        self.submit_btn.grid(row=0, column=0, sticky="ew", pady=(8, 8))
        self.next_btn = ttk.Button(btns, text="Next", command=on_next)
        self.next_btn.grid(row=1, column=0, sticky="ew", pady=(8, 8))

        # Feedback
        self.feedback = tk.StringVar(value="Distance: — km    |    Score: —")
        ttk.Label(self, textvariable=self.feedback, font=("Segoe UI", 20)).grid(
            row=2, column=0, sticky="w", pady=(8, 0)
        )

        # State
        self.last_distance_km: Optional[float] = None
        self.last_score: Optional[int] = None
        self.submit_btn.configure(state="disabled")

    def set_coords(self, lat: float, lon: float):
        """"""
        self.coords.set(f"Lat: {lat:.2f}   Lon: {lon:.2f}")
        self.submit_btn.configure(state="normal")

    def set_feedback(self, distance_km: float, score: int):
        """Set values to be displayed after guess is submitted"""
        self.last_distance_km = distance_km
        self.last_score = score
        self.feedback.set(f"Distance: {distance_km:.0f} km    |    Score: {score}")

    def reset_round(self):
        """Reset game variables for next round"""
        self.coords.set("Lat: —   Lon: —")
        self.feedback.set("Distance: — km    |    Score: —")
        self.submit_btn.configure(state="disabled")
        self.last_distance_km = None
        self.last_score = None

# ---------------- Screens ----------------
class MainMenu(ttk.Frame):
    def __init__(self, parent, controller: "App"):
        super().__init__(parent, style="TFrame")
        self.controller = controller

        box = ttk.Frame(self, style="Card.TFrame")
        box.place(relx=0.5, rely=0.5, anchor="center")

        title = ttk.Label(box, style="Card.TLabel", text="HouseGuess", font=("Segoe UI", 56, "bold"))
        start_btn = ttk.Button(box, text="Start", command=lambda: controller.start_session())
        #Connor: Difficulty is kept on the main menu (placeholder)
        diff_btn = ttk.Button(box, text="Difficulty", command=self._set_difficulty)
        info_btn = ttk.Button(box, text="Info", command=lambda: controller.show("InfoScreen"))

        title.grid(row=0, column=0, pady=(48, 28), padx=32)
        start_btn.grid(row=1, column=0, sticky="ew", padx=32, pady=18)
        diff_btn.grid(row=2, column=0, sticky="ew", padx=32, pady=18)
        info_btn.grid(row=3, column=0, sticky="ew", padx=32, pady=(18, 48))

    def _set_difficulty(self):
        messagebox.showinfo("Difficulty", "In the final version, choose Easy/Medium/Hard before starting.")

class InfoScreen(ttk.Frame):
    def __init__(self, parent, controller: "App"):
        super().__init__(parent, style="TFrame")
        self.controller = controller
        box = ttk.Frame(self, style="Card.TFrame")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(box,  style="Card.TLabel", text="About HouseGuess", font=("Segoe UI", 36, "bold"), foreground=CREAM)\
            .grid(row=0, column=0, pady=(24, 8), padx=24)
        info = ("HouseGuess is a simple guessing game where you look at a house "
                "and try to guess its location on the map. You earn more points "
                "the closer your guess is to the real spot.")
        ttk.Label(box,  style="Card.TLabel", text=info, wraplength=640, font=("Segoe UI", 18), foreground=CREAM)\
            .grid(row=1, column=0, padx=24, pady=(0, 16))

        back_btn = ttk.Button(box, text="Back", command=lambda: controller.show("MainMenu"))
        back_btn.grid(row=2, column=0, pady=(0, 24))

class GameScreen(ttk.Frame):
    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller

        #Connor: Layout: left photo, right column split 60/40 (map top, controls bottom)
        self.columnconfigure(0, weight=3)  # left photo
        self.columnconfigure(1, weight=2)  # right column
        self.rowconfigure(0, weight=1)

        # Connor: Left side: Photo
        self.image = PhotoPanel(self)
        self.image.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Connor: Right side: split into two equal rows
        right = ttk.Frame(self)
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=2)  # map takes up a lil more than half
        right.rowconfigure(1, weight=1)  # controls = <half

        #Connor: Map fills the top half
        self.map = ZoomMap(right, on_guess=self.on_map_guess, start_center=(20.0, 0.0), start_zoom=2)
        self.map.grid(row=0, column=0, sticky="nsew")

        #Connor: Controls fill the bottom half
        self.controls = ControlPanel(right, on_submit=self.on_submit, on_next=self.on_next)
        self.controls.grid(row=1, column=0, sticky="nsew", pady=(12, 0))

        #Connor: round state
        self._round_idx = 0
        self._pending_guess: Optional[Tuple[float, float]] = None
        self._answer: Tuple[float, float] = (0.0, 0.0)
        self._submitted: bool = False  # <-- lock after submit

    def new_round(self):
        # Preeth: Get the next available Place info and Photo.
        place = self.controller.places[self._round_idx]
        image = place.photos[0]
        self.image.set_image_path(image.file_path)
        self._answer = (place.lat, place.lon)
        self._pending_guess = None
        self._submitted = False
        self.controls.reset_round()
        self.map.reset_pin()
        self.map.set_enabled(True)  # re-enable map for the new round

     # Connor: Optional center map near the target (not exact) I couldn't remember how to do a multi line comment at this moment lol
     #   lat, lon = self._answer
     #   try:
     #       self.map.map.set_position(lat, lon)
     #       self.map.map.set_zoom(3)
     #   except Exception:
     #       pass

    def on_map_guess(self, lat: float, lon: float):
        if self._submitted:
            return  #Connor: ignore clicks after submission
        self._pending_guess = (lat, lon)
        self.controls.set_coords(lat, lon)

    def on_submit(self):
        if self._submitted:
            return  #Connor: prevent multiple submissions
        #Connor: If no guess yet, treat as 0 points
        if not self._pending_guess:
            self.controls.set_feedback(distance_km=0.0, score=0)
            #Connor: still mark as submitted to keep "one try"
            self._submitted = True
            self.controls.submit_btn.configure(state="disabled")
            self.map.set_enabled(False)
            return

        g_lat, g_lon = self._pending_guess
        t_lat, t_lon = self._answer
        d = haversine_km(g_lat, g_lon, t_lat, t_lon)
        score = int(5000 * math.exp(-d / 750.0))
        self.controls.set_feedback(distance_km=d, score=score)

        #Connor: lock the round,disable submit, disable map (no more guesses)
        self._submitted = True
        self.controls.submit_btn.configure(state="disabled")
        self.map.set_enabled(False)

    def on_next(self):
        #Connor: If no submit, record 0 pts
        if self.controls.last_score is None:
            self.controller.record_result(distance_km=0.0, score=0)
        else:
            self.controller.record_result(
                distance_km=self.controls.last_distance_km or 0.0,
                score=self.controls.last_score
            )
        # Advance round index
        self._round_idx += 1
        if self._round_idx < len(self.places):
            self.new_round()

class ResultsScreen(ttk.Frame):
    def __init__(self, parent, controller: "App"):
        super().__init__(parent)
        self.controller = controller
        self.title = ttk.Label(self, text="Results", font=("Segoe UI", 36, "bold"))
        self.summary = ttk.Label(self, text="", font=("Segoe UI", 20))
        back_btn = ttk.Button(self, text="Back to Menu", command=lambda: controller.show("MainMenu"))

        self.title.pack(pady=(24, 8))
        self.summary.pack(pady=(0, 16))
        back_btn.pack()

    def set_summary(self, rounds: int, total: int):
        self.summary.config(text=f"Rounds Played: {rounds}\nTotal Score: {total}")

# ---------------- App Shell ----------------
class App(tk.Tk):
    def __init__(self, config: RapidAPIConfig):
        super().__init__()
        try:
            self.tk.call('tk', 'scaling', 1.0)
        except Exception:
            pass

        self.config = config
        self.title("HouseGuess")
        self.geometry("1366x860")
        self.minsize(1100, 700)
        self.configure(bg=DARK_BLUE)

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        #Connor: Base styles
        style.configure("TFrame", background=DARK_BLUE)
        style.configure("TLabel", background=DARK_BLUE,foreground=CREAM)

        #Connor: Large, green buttons everywhere
        style.configure(
            "TButton",
            background=LIGHT_GREEN,
            foreground="black",
            font=("Segoe UI", 22, "bold"),
            padding=18
        )
        style.map("TButton",
                  background=[("active", TEAL)],
                  foreground=[("active", "white")])

        style.configure("Card.TFrame", background=CARD_BG)
        style.configure("Card.TLabel", background=CARD_BG)

        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (MainMenu, GameScreen, ResultsScreen, InfoScreen):
            frame = F(self.container, controller=self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show("MainMenu")

        #Connor: game session state
        # self._places = []
        # self._rounds = len(self._places)
        # self._round_index = 0
        # self._total_score = 0

    def show(self, name: str):
        self.frames[name].tkraise()

    def start_fixed_images_session(self):
        #Connor: Reset and start with the fixed images
        # self._rounds = len(self._places)
        # self._round_index = 0
        # self._total_score = 0
        self.places = []
        self._rounds = len(self.places)
        self._round_index = 0
        self._total_score = 0
        game: GameScreen = self.frames["GameScreen"]  # type: ignore
        game._round_idx = 0
        game.new_round()
        self.show("GameScreen")

    def start_session(self):
        self.places = rapidapi_search(self.config, "places", country="USA")
        self._rounds = len(self.places)
        self._round_index = 0
        self._total_score = 0
        game: GameScreen = self.frames["GameScreen"]  # type: ignore
        game._round_idx = 0
        game.new_round()
        self.show("GameScreen")

    def record_result(self, distance_km: float, score: int):
        self._total_score += score
        self._round_index += 1
        if self._round_index >= self._rounds:
            self.frames["ResultsScreen"].set_summary(rounds=self._rounds, total=self._total_score)
            self.show("ResultsScreen")

