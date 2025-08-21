import json
import math
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173", 
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8080", 
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


BASE_DIR = Path(__file__).parent.parent
ANIME_CSV = BASE_DIR / "dataset" / "processed_anime_data.csv"
MANGA_CSV = BASE_DIR / "dataset" / "mangas.csv"

anime_df = pd.read_csv(ANIME_CSV)
manga_df = pd.read_csv(MANGA_CSV)

def safe_value(val):
    """Handle NaN, None, and invalid values"""
    try:
        if pd.isna(val):
            return None
        if isinstance(val, (int, float)):
            if math.isnan(val) or math.isinf(val):
                return None
        return val
    except:
        return None

def parse_array_field(field_value):
    """Parse array fields that might be stored as strings"""
    if pd.isna(field_value) or field_value == "":
        return []
    
    if isinstance(field_value, str):
        try:
            parsed = json.loads(field_value)
            return parsed if isinstance(parsed, list) else []
        except:
            return [item.strip() for item in field_value.split(',') if item.strip()]
    
    return field_value if isinstance(field_value, list) else []

@app.get("/anime")
def get_anime(
    limit: int = 20,
    offset: int = 0,
    search: str = None,
    genre: str = None,
    year: int = None,
    season: str = None,
    format: str = None,
    status: str = None,
    min_score: float = None,
    episode_type: str = None,
    completed_only: bool = None,
):
    df = anime_df.copy()

    # --- Search filter (search in title and title_english) ---
    if search:
        search_mask = (
            df['title'].str.contains(search, case=False, na=False) |
            df['title_english'].str.contains(search, case=False, na=False) | df['title_japanese'].str.contains(search, case=False, na=False)
        )
        df = df[search_mask]

    # --- Genre filter (works with cleaned array format) ---
    if genre:
        def has_genre(genres_field):
            genres_list = parse_array_field(genres_field)
            return any(g.lower() == genre.lower() for g in genres_list)
        
        df = df[df['genres'].apply(has_genre)]

    # --- Year filter (using cleaned year field) ---
    if year:
        df = df[df['year'] == year]

    # --- Format (type) filter ---
    if format:
        df = df[df['type'].str.lower() == format.lower()]

    # --- Season filter ---
    if season:
        df = df[df['season'].str.lower() == season.lower()]

    # --- Status filter ---
    if status:
        df = df[df['status'].str.lower() == status.lower()]

    # --- Score filter ---
    if min_score is not None:
        df = df[df['score'] >= min_score]

    # --- Episode type filter (using computed field) ---
    if episode_type:
        df = df[df['episode_type'] == episode_type.lower()]

    # --- Completed only filter (using computed field) ---
    if completed_only is not None:
        df = df[df['is_completed'] == completed_only]

    # --- Sort by score (prioritizing items with scores) ---
    df['score_filled'] = df['score'].fillna(0)
    df['has_score_int'] = df['has_score'].astype(int)
    df = df.sort_values(by=['has_score_int', 'score_filled'], ascending=[False, False])

    # --- Build results ---
    results = []
    total_count = len(df)
    
    for _, row in df.iloc[offset:offset+limit].iterrows():
        # Parse streaming platforms
        streaming_platforms = parse_array_field(row.get('streaming_platforms', []))
        
        # Parse genres for response
        genres = parse_array_field(row.get('genres', []))
        
        results.append({
            "id": safe_value(row.get('id')),
            "title": safe_value(row.get('title')),
            "title_english": safe_value(row.get('title_english')),
            "image_url": safe_value(row.get('image_url')),
            "thumbnail_url": safe_value(row.get('thumbnail_url')),
            "year": safe_value(row.get('year')),
            "score": safe_value(row.get('score')),
            "episodes": safe_value(row.get('episodes')),
            "episode_type": safe_value(row.get('episode_type')),
            "status": safe_value(row.get('status')),
            "type": safe_value(row.get('type')),
            "genres": genres,
            "synopsis_short": safe_value(row.get('synopsis_short')),
            "streaming_platforms": streaming_platforms,
            "is_completed": safe_value(row.get('is_completed')),
            "has_score": safe_value(row.get('has_score')),
            "url": safe_value(row.get('url')),
            "studio": safe_value(row.get('studios')),
            "season": safe_value(row.get('season')),
        })

    return {
        "count": total_count,
        "results": results,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_count,
            "has_prev": offset > 0
        }
    }

@app.get("/anime/filters")
def get_anime_filters():
    """Get all available filter options"""
    df = anime_df.copy()

    # --- Genres ---
    genres = set()
    for genre_field in df['genres'].dropna():
        genre_list = parse_array_field(genre_field)
        genres.update(genre_list)
    genres = sorted([g for g in genres if g])  # Remove empty strings

    # --- Years ---
    years = sorted(df['year'].dropna().unique().tolist(), reverse=True)

    # --- Seasons ---
    seasons = sorted([s for s in df['season'].dropna().unique().tolist() if s])

    # --- Formats (Types) ---
    formats = sorted([f for f in df['type'].dropna().unique().tolist() if f])

    # --- Statuses ---
    statuses = sorted([s for s in df['status'].dropna().unique().tolist() if s])

    # --- Episode Types ---
    episode_types = sorted([et for et in df['episode_type'].dropna().unique().tolist() if et])

    # --- Score ranges ---
    score_ranges = [
        {"label": "9.0+", "min": 9.0},
        {"label": "8.0+", "min": 8.0},
        {"label": "7.0+", "min": 7.0},
        {"label": "6.0+", "min": 6.0},
    ]

    return {
        "genres": genres,
        "years": years,
        "seasons": seasons,
        "formats": formats,
        "statuses": statuses,
        "episode_types": episode_types,
        "score_ranges": score_ranges
    }

import json
from fastapi.responses import JSONResponse

def safe_json_parse(value):
    if pd.isna(value) or value in ["", "[]", "{}", None]:
        return []
    try:
        return json.loads(value)
    except Exception as e:
        print(f"JSON parse error: {value} — {e}")
        return []
    
@app.get("/anime/{anime_id}")
async def get_anime_detail(anime_id: int):
    anime_row = anime_df[anime_df["id"] == anime_id]
    if anime_row.empty:
        raise HTTPException(status_code=404, detail="Anime not found")

    row = anime_row.iloc[0]

    return JSONResponse(content={
        "id": int(row["id"]),
        "title": safe_value(row["title"]),
        "title_english": safe_value(row["title_english"]),
        "title_japanese": safe_value(row["title_japanese"]),
        "title_synonyms": safe_json_parse(row.get("title_synonyms")),
        "type": safe_value(row["type"]),
        "episodes": int(row["episodes"]) if not pd.isna(row["episodes"]) else None,
        "status": safe_value(row["status"]),
        "score": float(row["score"]) if not pd.isna(row["score"]) else None,
        "rank": int(row["rank"]) if not pd.isna(row["rank"]) else None,
        "popularity": int(row["popularity"]) if not pd.isna(row["popularity"]) else None,
        "members": int(row["members"]) if not pd.isna(row["members"]) else None,
        "favorites": int(row["favorites"]) if not pd.isna(row["favorites"]) else None,
        "scored_by": int(row["scored_by"]) if not pd.isna(row["scored_by"]) else None,
        "rating": safe_value(row["rating"]),
        "year": int(row["year"]) if not pd.isna(row["year"]) else None,
        "season": safe_value(row["season"]),
        "source": safe_value(row["source"]),
        "duration": safe_value(row["duration"]),
        "airing": bool(row["airing"]),
        "aired_from": safe_value(row["aired_from"]),
        "aired_to": safe_value(row["aired_to"]),
        "broadcast_day": safe_value(row["broadcast_day"]),
        "broadcast_time": safe_value(row["broadcast_time"]),
        "broadcast_timezone": safe_value(row["broadcast_timezone"]),
        "genres": safe_value(row["genres"]).split(",") if not pd.isna(row["genres"]) else [],
        "explicit_genres": safe_json_parse(row.get("explicit_genres")),
        "demographics": safe_json_parse(row.get("demographics")),
        "themes": safe_json_parse(row.get("themes")),
        "studios": safe_value(row["studios"]),
        "producers": safe_value(row["producers"]),
        "licensors": safe_json_parse(row.get("licensors")),
        "streaming_platforms": safe_value(row["streaming_platforms"]).split(",") if not pd.isna(row["streaming_platforms"]) else [],
        "synopsis": safe_value(row["synopsis"]),
        "synopsis_short": safe_value(row["synopsis_short"]),
        "background": safe_value(row["background"]),
        "relations": safe_json_parse(row.get("relations")),
        "openings": safe_json_parse(row.get("openings")),
        "endings": safe_json_parse(row.get("endings")),
        "image_url": safe_value(row["image_url"]),
        "thumbnail_url": safe_value(row["thumbnail_url"]),
        "trailer": safe_json_parse(row.get("trailer")),
        "external": safe_json_parse(row.get("external")),
        "has_score": bool(row["has_score"]),
        "is_completed": bool(row["is_completed"]),
        "episode_type": safe_value(row["episode_type"])
     })

@app.get("/anime/stats")
def get_anime_stats():
    """Get dataset statistics"""
    df = anime_df.copy()
    
    total_anime = len(df)
    with_scores = len(df[df['has_score'] == True])
    completed = len(df[df['is_completed'] == True])
    
    # Top genres
    genre_counts = {}
    for genre_field in df['genres'].dropna():
        genre_list = parse_array_field(genre_field)
        for genre in genre_list:
            if genre:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_anime": total_anime,
        "with_scores": with_scores,
        "completed": completed,
        "score_percentage": round((with_scores / total_anime) * 100, 1),
        "completed_percentage": round((completed / total_anime) * 100, 1),
        "top_genres": [{"name": name, "count": count} for name, count in top_genres],
        "year_range": {
            "min": int(df['year'].min()) if not df['year'].isna().all() else None,
            "max": int(df['year'].max()) if not df['year'].isna().all() else None
        }
    }

@app.get("/manga")
def get_manga(
    limit: int = 20,
    offset: int = 0,
    search: str = None,
    genre: str = None,
    type: str = None,
    status: str = None,
    min_score: float = None,
    demographic: str = None,
    theme: str = None,
    author: str = None,
    serialization: str = None,
    publishing: bool = None,
    min_chapters: int = None,
    max_chapters: int = None,
    min_volumes: int = None,
    max_volumes: int = None,
):
    df = manga_df.copy()

    # --- Search filter ---
    if search:
        search_mask = (
            df['title'].str.contains(search, case=False, na=False) |
            df['title_english'].str.contains(search, case=False, na=False) |
            df['title_japanese'].str.contains(search, case=False, na=False)
        )
        df = df[search_mask]

    # --- Genre filter ---
    if genre:
        def has_genre(genres_field):
            genres_list = safe_json_parse(genres_field)
            return any(g.get('name', '').lower() == genre.lower() for g in genres_list if isinstance(g, dict))
        
        df = df[df['genres'].apply(has_genre)]

    # --- Type filter ---
    if type:
        df = df[df['type'].str.lower() == type.lower()]

    # --- Status filter ---
    if status:
        df = df[df['status'].str.lower() == status.lower()]

    # --- Score filter ---
    if min_score is not None:
        df = df[df['score'] >= min_score]

    # --- Demographic filter ---
    if demographic:
        def has_demographic(demo_field):
            demo_list = safe_json_parse(demo_field)
            return any(d.get('name', '').lower() == demographic.lower() for d in demo_list if isinstance(d, dict))
        
        df = df[df['demographics'].apply(has_demographic)]

    # --- Theme filter ---
    if theme:
        def has_theme(theme_field):
            theme_list = safe_json_parse(theme_field)
            return any(t.get('name', '').lower() == theme.lower() for t in theme_list if isinstance(t, dict))
        
        df = df[df['themes'].apply(has_theme)]

    # --- Author filter ---
    if author:
        def has_author(author_field):
            author_list = safe_json_parse(author_field)
            return any(author.lower() in a.get('name', '').lower() for a in author_list if isinstance(a, dict))
        
        df = df[df['authors'].apply(has_author)]

    # --- Serialization filter ---
    if serialization:
        def has_serialization(serial_field):
            serial_list = safe_json_parse(serial_field)
            return any(serialization.lower() in s.get('name', '').lower() for s in serial_list if isinstance(s, dict))
        
        df = df[df['serializations'].apply(has_serialization)]

    # --- Publishing filter ---
    if publishing is not None:
        df = df[df['publishing'] == publishing]

    # --- Chapters filter ---
    if min_chapters is not None:
        df = df[df['chapters'] >= min_chapters]
    if max_chapters is not None:
        df = df[df['chapters'] <= max_chapters]

    # --- Volumes filter ---
    if min_volumes is not None:
        df = df[df['volumes'] >= min_volumes]
    if max_volumes is not None:
        df = df[df['volumes'] <= max_volumes]

    # --- Sort by score ---
    df = df.sort_values(by=['score'], ascending=False, na_position='last')

    # --- Build results ---
    results = []
    total_count = len(df)
    
    for _, row in df.iloc[offset:offset+limit].iterrows():
        # Parse genres
        genres = safe_json_parse(row.get('genres', []))
        genre_names = [g.get('name', '') for g in genres if isinstance(g, dict)]
        
        # Parse authors
        authors = safe_json_parse(row.get('authors', []))
        author_names = [a.get('name', '') for a in authors if isinstance(a, dict)]
        
        # Parse demographics
        demographics = safe_json_parse(row.get('demographics', []))
        demographic_names = [d.get('name', '') for d in demographics if isinstance(d, dict)]
        
        # Extract image URL from images JSON
        images = safe_json_parse(row.get('images', {}))
        image_url = None
        if isinstance(images, dict):
            jpg = images.get('jpg', {})
            if isinstance(jpg, dict):
                image_url = jpg.get('image_url') or jpg.get('large_image_url')
        
        results.append({
            "mal_id": safe_value(row.get('mal_id')),
            "url": safe_value(row.get('url')),
            "title": safe_value(row.get('title')),
            "title_english": safe_value(row.get('title_english')),
            "title_japanese": safe_value(row.get('title_japanese')),
            "type": safe_value(row.get('type')),
            "chapters": safe_value(row.get('chapters')),
            "volumes": safe_value(row.get('volumes')),
            "status": safe_value(row.get('status')),
            "publishing": safe_value(row.get('publishing')),
            "score": safe_value(row.get('score')),
            "rank": safe_value(row.get('rank')),
            "popularity": safe_value(row.get('popularity')),
            "members": safe_value(row.get('members')),
            "favorites": safe_value(row.get('favorites')),
            "genres": genre_names,
            "authors": author_names,
            "demographics": demographic_names,
            "image_url": image_url,
            "synopsis": safe_value(row.get('synopsis')),
        })

    return {
        "count": total_count,
        "results": results,
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_next": offset + limit < total_count,
            "has_prev": offset > 0
        }
    }

@app.get("/manga/filters")
def get_manga_filters():
    """Get all available manga filter options"""
    df = manga_df.copy()

    # --- Genres ---
    genres = set()
    for genre_field in df['genres'].dropna():
        genre_list = safe_json_parse(genre_field)
        for genre in genre_list:
            if isinstance(genre, dict) and genre.get('name'):
                genres.add(genre['name'])
    genres = sorted([g for g in genres if g])

    # --- Types ---
    types = sorted([t for t in df['type'].dropna().unique().tolist() if t])

    # --- Statuses ---
    statuses = sorted([s for s in df['status'].dropna().unique().tolist() if s])

    # --- Demographics ---
    demographics = set()
    for demo_field in df['demographics'].dropna():
        demo_list = safe_json_parse(demo_field)
        for demo in demo_list:
            if isinstance(demo, dict) and demo.get('name'):
                demographics.add(demo['name'])
    demographics = sorted([d for d in demographics if d])

    # --- Themes ---
    themes = set()
    for theme_field in df['themes'].dropna():
        theme_list = safe_json_parse(theme_field)
        for theme in theme_list:
            if isinstance(theme, dict) and theme.get('name'):
                themes.add(theme['name'])
    themes = sorted([t for t in themes if t])

    # --- Authors (top 50) ---
    author_counts = {}
    for author_field in df['authors'].dropna():
        author_list = safe_json_parse(author_field)
        for author in author_list:
            if isinstance(author, dict) and author.get('name'):
                name = author['name']
                author_counts[name] = author_counts.get(name, 0) + 1
    
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:50]
    authors = [name for name, _ in top_authors]

    # --- Serializations (top 30) ---
    serial_counts = {}
    for serial_field in df['serializations'].dropna():
        serial_list = safe_json_parse(serial_field)
        for serial in serial_list:
            if isinstance(serial, dict) and serial.get('name'):
                name = serial['name']
                serial_counts[name] = serial_counts.get(name, 0) + 1
    
    top_serials = sorted(serial_counts.items(), key=lambda x: x[1], reverse=True)[:30]
    serializations = [name for name, _ in top_serials]

    # --- Score ranges ---
    score_ranges = [
        {"label": "9.0+", "min": 9.0},
        {"label": "8.0+", "min": 8.0},
        {"label": "7.0+", "min": 7.0},
        {"label": "6.0+", "min": 6.0},
    ]

    # --- Chapter/Volume ranges ---
    chapter_ranges = [
        {"label": "1-50", "min": 1, "max": 50},
        {"label": "51-100", "min": 51, "max": 100},
        {"label": "101-200", "min": 101, "max": 200},
        {"label": "201+", "min": 201, "max": None},
    ]

    volume_ranges = [
        {"label": "1-10", "min": 1, "max": 10},
        {"label": "11-25", "min": 11, "max": 25},
        {"label": "26-50", "min": 26, "max": 50},
        {"label": "51+", "min": 51, "max": None},
    ]

    return {
        "genres": genres,
        "types": types,
        "statuses": statuses,
        "demographics": demographics,
        "themes": themes,
        "authors": authors,
        "serializations": serializations,
        "score_ranges": score_ranges,
        "chapter_ranges": chapter_ranges,
        "volume_ranges": volume_ranges
    }

@app.get("/manga/{manga_id}")
async def get_manga_detail(manga_id: int):
    manga_row = manga_df[manga_df["mal_id"] == manga_id]
    if manga_row.empty:
        raise HTTPException(status_code=404, detail="Manga not found")

    row = manga_row.iloc[0]

    return {
        "mal_id": int(row["mal_id"]),
        "url": safe_value(row["url"]),
        "title": safe_value(row["title"]),
        "title_english": safe_value(row["title_english"]),
        "title_japanese": safe_value(row["title_japanese"]),
        "title_synonyms": safe_json_parse(row.get("title_synonyms")),
        "type": safe_value(row["type"]),
        "chapters": int(row["chapters"]) if not pd.isna(row["chapters"]) else None,
        "volumes": int(row["volumes"]) if not pd.isna(row["volumes"]) else None,
        "status": safe_value(row["status"]),
        "publishing": bool(row["publishing"]),
        "published_from": safe_value(row["published_from"]),
        "published_to": safe_value(row["published_to"]),
        "score": float(row["score"]) if not pd.isna(row["score"]) else None,
        "scored_by": int(row["scored_by"]) if not pd.isna(row["scored_by"]) else None,
        "rank": int(row["rank"]) if not pd.isna(row["rank"]) else None,
        "popularity": int(row["popularity"]) if not pd.isna(row["popularity"]) else None,
        "members": int(row["members"]) if not pd.isna(row["members"]) else None,
        "favorites": int(row["favorites"]) if not pd.isna(row["favorites"]) else None,
        "synopsis": safe_value(row["synopsis"]),
        "background": safe_value(row["background"]),
        "authors": safe_json_parse(row.get("authors")),
        "serializations": safe_json_parse(row.get("serializations")),
        "genres": safe_json_parse(row.get("genres")),
        "explicit_genres": safe_json_parse(row.get("explicit_genres")),
        "themes": safe_json_parse(row.get("themes")),
        "demographics": safe_json_parse(row.get("demographics")),
        "relations": safe_json_parse(row.get("relations")),
        "external": safe_json_parse(row.get("external")),
        "images": safe_json_parse(row.get("images"))
    }

@app.get("/manga/stats")
def get_manga_stats():
    """Get manga dataset statistics"""
    df = manga_df.copy()
    
    total_manga = len(df)
    with_scores = len(df[df['score'].notna()])
    publishing = len(df[df['publishing'] == True])
    finished = len(df[df['status'] == 'Finished'])
    
    # Top genres
    genre_counts = {}
    for genre_field in df['genres'].dropna():
        genre_list = safe_json_parse(genre_field)
        for genre in genre_list:
            if isinstance(genre, dict) and genre.get('name'):
                name = genre['name']
                genre_counts[name] = genre_counts.get(name, 0) + 1
    
    top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Top authors
    author_counts = {}
    for author_field in df['authors'].dropna():
        author_list = safe_json_parse(author_field)
        for author in author_list:
            if isinstance(author, dict) and author.get('name'):
                name = author['name']
                author_counts[name] = author_counts.get(name, 0) + 1
    
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
    
    return {
        "total_manga": total_manga,
        "with_scores": with_scores,
        "publishing": publishing,
        "finished": finished,
        "score_percentage": round((with_scores / total_manga) * 100, 1),
        "publishing_percentage": round((publishing / total_manga) * 100, 1),
        "finished_percentage": round((finished / total_manga) * 100, 1),
        "top_genres": [{"name": name, "count": count} for name, count in top_genres],
        "top_authors": [{"name": name, "count": count} for name, count in top_authors],
        "avg_chapters": round(df['chapters'].mean(), 1) if not df['chapters'].isna().all() else None,
        "avg_volumes": round(df['volumes'].mean(), 1) if not df['volumes'].isna().all() else None,
    }
