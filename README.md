# HouseGuess (starter)

A simple Python 3 Tkinter GUI game (college capstone starter) where players see a house image and guess its origin.
This starter focuses on the GUI loop and data loading, with a stub for distance-based scoring you can extend.

## Features (MVP)
- Tkinter GUI
- Random image per round
- Guess country and get immediate feedback
- Score tracking (basic)
- Extensible structure for distance-based scoring and API integrations

## Quick Start (Linux)
```bash
# Python 3.10+ recommended
./run.sh
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
