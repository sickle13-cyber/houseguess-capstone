# haytham: load .env so RAPIDAPI_* vars are available without hardcoding
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    print(".env file not found. Environment variables need to be set for HouseGuess to work properly.")

