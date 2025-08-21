import pandas as pd
import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
RAW_CSV = BASE_DIR / "dataset" / "animes.csv"
CLEAN_CSV = BASE_DIR / "dataset" / "animes_cleaned.csv"

def extract_year(date_str):
    try:
        dt = pd.to_datetime(date_str, errors='coerce')
        return dt.year if not pd.isna(dt) else None
    except:
        return None

def parse_genres(genres_str):
    try:
        genres = json.loads(genres_str)
        return [g.get("name", "").strip().lower() for g in genres]
    except:
        return []

def extract_image_url(images_str):
    try:
        images = json.loads(images_str)
        return images.get("jpg", {}).get("image_url", "")
    except:
        return ""

df = pd.read_csv(RAW_CSV)

df["aired_from_year"] = df["aired_from"].apply(extract_year)

df.to_csv(CLEAN_CSV, index=False)
