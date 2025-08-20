import json
import math
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).parent.parent
ANIME_CSV = BASE_DIR / "dataset" / "processed_anime_data.csv"
anime_df = pd.read_csv(ANIME_CSV)

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

@app.get("/anime/{anime_id}")
def get_anime_detail(anime_id: int):
    """Get detailed information for a specific anime"""
    anime = anime_df[anime_df['id'] == anime_id]
    
    if anime.empty:
        return {"error": "Anime not found"}, 404
    
    row = anime.iloc[0]
    
    # Parse array fields
    genres = parse_array_field(row.get('genres', []))
    themes = parse_array_field(row.get('themes', []))
    demographics = parse_array_field(row.get('demographics', []))
    streaming_platforms = parse_array_field(row.get('streaming_platforms', []))
    
    return {
        "id": safe_value(row.get('id')),
        "title": safe_value(row.get('title')),
        "title_english": safe_value(row.get('title_english')),
        "title_japanese": safe_value(row.get('title_japanese')),
        "image_url": safe_value(row.get('image_url')),
        "thumbnail_url": safe_value(row.get('thumbnail_url')),
        "synopsis": safe_value(row.get('synopsis')),
        "synopsis_short": safe_value(row.get('synopsis_short')),
        "score": safe_value(row.get('score')),
        "episodes": safe_value(row.get('episodes')),
        "episode_type": safe_value(row.get('episode_type')),
        "year": safe_value(row.get('year')),
        "season": safe_value(row.get('season')),
        "status": safe_value(row.get('status')),
        "type": safe_value(row.get('type')),
        "aired_from": safe_value(row.get('aired_from')),
        "aired_to": safe_value(row.get('aired_to')),
        "genres": genres,
        "themes": themes,
        "demographics": demographics,
        "streaming_platforms": streaming_platforms,
        "is_completed": safe_value(row.get('is_completed')),
        "has_score": safe_value(row.get('has_score')),
        "url": safe_value(row.get('url'))
    }

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


@app.get("/anime/search/suggestions")
def get_search_suggestions(q: str, limit: int = 10):
    """Get search suggestions based on partial query"""
    if not q or len(q) < 2:
        return {"suggestions": []}
    
    df = anime_df.copy()
    
    # Search in titles
    mask = (
        df['title'].str.contains(q, case=False, na=False) |
        df['title_english'].str.contains(q, case=False, na=False)
    )
    
    matches = df[mask].head(limit)
    
    suggestions = []
    for _, row in matches.iterrows():
        title = safe_value(row.get('title'))
        title_english = safe_value(row.get('title_english'))
        
        # Use English title if available and different
        display_title = title_english if title_english and title_english != title else title
        
        suggestions.append({
            "id": safe_value(row.get('id')),
            "title": display_title,
            "year": safe_value(row.get('year')),
            "thumbnail_url": safe_value(row.get('thumbnail_url'))
        })
    
    return {"suggestions": suggestions}