from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"
DATABASE_FILE = DATA_DIR / "database.csv"

DEBUG = os.getenv("DEBUG", "1") == "1"