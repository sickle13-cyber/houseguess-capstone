# HouseGuess

A simple Python 3 Tkinter GUI game where players see an image of a commercial building or place and try to guess its location.

## Features (MVP)
- Tkinter GUI
- Maps Data API integration via RapidAPI
- Random images per round
- Guess approximate radius of origin and get immediate feedback
- Score tracking (basic leaderboard)
- Extensible structure for distance-based scoring

## Quick Start (Linux / macOS)

This project requires Linux or macOS to run.

First, set up the `.env.example` template file with a valid API key for the [Maps Data](https://rapidapi.com/alexanderxbx/api/maps-data) API. Then, rename it to `.env`

Afterwards, paste the following into your terminal.

```bash
# Python 3.10+ recommended
python3 -m venv .venv
source .venv/source/activate
pip install -r requirements.txt
python3 -m houseguess
```

## Project Layout
```
README.md          # Starter information.
TODO.txt           # Items to be completed.
src/houseguess/
  __init__.py
  app.py           # Application entry point
  gui.py           # Tkinter GUI
  models.py        # Main component definitions
  api_client.py    # Makes queries to RapidAPI
  util.py          # Haversine distance + helpers
assets/images/     # Where to store and cache images
tests/             # Tests using pytest
```

## License
MIT
