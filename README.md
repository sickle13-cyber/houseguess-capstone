# HouseGuess

A simple Python 3 Tkinter GUI game where players see a house image and guess its origin.

## Features (MVP)
- Tkinter GUI
- Random image per round
- Guess country and get immediate feedback
- Score tracking (basic)
- Extensible structure for distance-based scoring and API integrations

## Quick Start (Linux / macOS)

First, set up the `.env.example` template file with a valid API key for the [Maps Data](https://rapidapi.com/alexanderxbx/api/maps-data) API. Then, rename it to `.env`

```bash
# Python 3.10+ recommended
python -m venv .venv
source .venv/source/activate
pip install -r requirements.txt
python3 -m houseguess
```

## Project Layout
```
run.sh             # Application entry point.
README.md          # Starter information.
TODO.txt           # Items to be completed.
src/houseguess/
  __init__.py
  app.py           # Tkinter GUI
  data.py          # House class definition + loading
  geo.py           # haversine distance + helpers
assets/images/     # Where to store and cache images
tests/             # Tests using pytest
```

## License
MIT
