import json
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from pathlib import Path

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).parent.parent
ANIME_CSV = BASE_DIR / "dataset" / "animes.csv"

anime_df = pd.read_csv(ANIME_CSV)

@app.get("/anime")
def get_anime(
    limit: int = 20,
    offset: int = 0,
    search: str = None,
    genre: str = None,
    year: str = None,
    season: str = None,
    format: str = None,
    status: str = None,
):
    df = anime_df.copy()
    df = df.fillna("")

    # Search
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False)]

    # Genre filter (handle JSON list)
    if genre:
        def has_genre(entry):
            try:
                parsed = json.loads(entry) if isinstance(entry, str) and entry.startswith("[") else []
                return any(g.get("name","").strip().lower() == genre.lower() for g in parsed)
            except:
                return False
        df = df[df['genres'].apply(has_genre)]

    # Year filter
    if year:
        def parse_year(y):
            try:
                return int(float(y))
            except:
                return None
        df = df[df['year'].apply(parse_year) == int(year)]

    # Season filter
    if season:
        df = df[df['season'].str.lower() == season.lower()]

    if format:
        df = df[df['type'].str.lower() == format.lower()]

    if status:
        df = df[df['status'].str.lower() == status.lower()]

    if 'members' in df.columns:
        df['members_num'] = pd.to_numeric(df['members'], errors='coerce').fillna(0)
        df = df.sort_values(by='members_num', ascending=False)

    results = []
    for _, row in df.iloc[offset:offset+limit].iterrows():
        try:
            images = json.loads(row['images'])
            img_url = images.get('jpg', {}).get('image_url', '')
        except:
            img_url = ''

        try:
            year_val = int(float(row.get('year', 0))) if row.get('year') else ''
        except:
            year_val = ''

        results.append({
            "mal_id": row['mal_id'],
            "title": row['title'],
            "image_url": img_url,
            "year": year_val,
            "url": row.get('url', '')
        })

    return {"count": len(df), "results": results}

import json

@app.get("/anime/filters")
def get_anime_filters():
    df = anime_df.fillna("")

    genres = set()
    for entry in df['genres']:
        try:
            parsed = json.loads(entry) if isinstance(entry, str) and entry.startswith("[") else []
            for g in parsed:
                if "name" in g:
                    genres.add(g["name"].strip())
        except Exception:
            continue
    genres = sorted(genres)

    years = (
    pd.to_numeric(df['year'], errors="coerce")   
    .dropna()                                  
    .astype(int)                                 
    .unique()
    .tolist()
    )
    years = sorted(years, reverse=True)



    filters = {
        "genres": genres,
        "years": years,
        "seasons": sorted(df['season'].dropna().unique().tolist()),
        "formats": sorted(df['type'].dropna().unique().tolist()),
        "statuses": sorted(df['status'].dropna().unique().tolist()),
    }

    return filters


@app.get("/manga")
def get_manga(limit: int = 20, offset: int = 0, search: str = None, sort_by: str = "title"):
    df = manga_df.copy()
    df = df.fillna("") 
    if search:
        df = df[df['title'].str.contains(search, case=False, na=False)]
    if sort_by in df.columns:
        df = df.sort_values(by=sort_by)
    data = df.iloc[offset:offset+limit].to_dict(orient="records")
    return {"count": len(df), "results": data}
