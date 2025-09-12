from dotenv import load_dotenv
from .gui import App

# haytham: load .env so RAPIDAPI_* vars are available without hardcoding
try:
    load_dotenv()
except Exception:
    print(".env file not found. Environment variables need to be set for HouseGuess to work properly.")

def HouseGuessMain():
    app = App()
    app.mainloop()
