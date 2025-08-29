import json
import math
import numpy as np
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
ANIME_CSV = BASE_DIR / "dataset" / "animes.csv"
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
            df['title_english'].str.contains(search, case=False, na=False) | 
            df['title_japanese'].str.contains(search, case=False, na=False)
        )
        df = df[search_mask]

    # --- Genre filter (works with cleaned array format) ---
    if genre:
        def has_genre(genres_field):
            if pd.isna(genres_field):
                return False
            genres_list = parse_array_field(genres_field)
            for genre_item in genres_list:
                if isinstance(genre_item, dict) and 'name' in genre_item:
                    genre_name = genre_item['name']
                    if genre_name and genre_name.lower() == genre.lower():
                        return True
                elif isinstance(genre_item, str) and genre_item.lower() == genre.lower():
                    return True
            return False
        
        df = df[df['genres'].apply(has_genre)]

    # --- Year filter (robust handling of year field) ---
    if year is not None:
        def matches_year(row):
            # First try the direct year column
            year_val = row.get('year')
            if pd.notna(year_val):
                try:
                    # Handle both string and numeric year values
                    if isinstance(year_val, str):
                        # Remove any non-numeric characters and try to parse
                        year_clean = ''.join(filter(str.isdigit, str(year_val)))
                        if year_clean:
                            return int(year_clean) == year
                    else:
                        return int(float(year_val)) == year
                except (ValueError, TypeError):
                    pass
            
            # Fallback: extract year from aired_from if year column is empty/invalid
            aired_from = row.get('aired_from')
            if pd.notna(aired_from):
                try:
                    if isinstance(aired_from, str):
                        import datetime
                        # Handle different date formats
                        aired_from_clean = aired_from.replace('Z', '+00:00')
                        parsed_date = datetime.datetime.fromisoformat(aired_from_clean)
                        return parsed_date.year == year
                except Exception as e:
                    # If datetime parsing fails, try to extract year with regex
                    try:
                        import re
                        year_match = re.search(r'\b(\d{4})\b', str(aired_from))
                        if year_match:
                            return int(year_match.group(1)) == year
                    except:
                        pass
            
            return False
        
        year_mask = df.apply(matches_year, axis=1)
        df = df[year_mask]
        
        # Debug: print how many results we got
        print(f"Year filter {year}: Found {len(df)} results")

    # --- Format (type) filter ---
    if format:
        def safe_type_compare(type_val):
            if pd.isna(type_val):
                return False
            return str(type_val).lower() == format.lower()
        df = df[df['type'].apply(safe_type_compare)]

    # --- Season filter ---
    if season:
        def safe_season_compare(season_val):
            if pd.isna(season_val):
                return False
            return str(season_val).lower() == season.lower()
        df = df[df['season'].apply(safe_season_compare)]

    # --- Status filter ---
    if status:
        def safe_status_compare(status_val):
            if pd.isna(status_val):
                return False
            return str(status_val).lower() == status.lower()
        df = df[df['status'].apply(safe_status_compare)]

    # --- Score filter ---
    if min_score is not None:
        df = df[df['score'] >= min_score]

    # --- Episode type filter (compute from episodes and type) ---
    if episode_type:
        def get_episode_type(row):
            episodes = row.get('episodes')
            anime_type_raw = row.get('type')
            anime_type = str(anime_type_raw).lower() if pd.notna(anime_type_raw) else ''
            
            if pd.isna(episodes) or episodes == 0:
                return 'unknown'
            
            try:
                ep_count = int(float(episodes))
                if anime_type == 'movie':
                    return 'movie'
                elif ep_count == 1:
                    return 'single'
                elif ep_count <= 12:
                    return 'short'
                else:
                    return 'long'
            except (ValueError, TypeError):
                return 'unknown'
        
        df['computed_episode_type'] = df.apply(get_episode_type, axis=1)
        df = df[df['computed_episode_type'] == episode_type.lower()]

    # --- Completed only filter (compute from status) ---
    if completed_only is not None:
        def is_completed(status_val):
            if pd.isna(status_val):
                return False
            status_lower = str(status_val).lower()
            return status_lower in ['finished airing', 'completed']
        
        df['computed_is_completed'] = df['status'].apply(is_completed)
        df = df[df['computed_is_completed'] == completed_only]

    # --- Sort by score (prioritizing items with scores) ---
    # Create computed columns for sorting
    df['score_filled'] = df['score'].fillna(0)
    df['has_score'] = df['score'].notna()
    df['has_score_int'] = df['has_score'].astype(int)
    
    # Sort by has_score first (items with scores), then by score value
    df = df.sort_values(by=['has_score_int', 'score_filled'], ascending=[False, False])

    # --- Build results ---
    results = []
    total_count = len(df)
    
    for _, row in df.iloc[offset:offset+limit].iterrows():
        # Parse streaming platforms - use 'streaming' column from CSV
        streaming_data = row.get('streaming', [])
        if pd.isna(streaming_data):
            streaming_platforms = []
        else:
            streaming_platforms = parse_array_field(streaming_data)
        
        # Parse genres for response - extract names from dictionaries
        genres_raw = parse_array_field(row.get('genres', []))
        genres = []
        for genre_item in genres_raw:
            if isinstance(genre_item, dict) and 'name' in genre_item:
                genres.append(genre_item['name'])
            elif isinstance(genre_item, str):
                genres.append(genre_item)
        
        # Extract image URL from images JSON
        images_data = row.get('images')
        image_url = None
        thumbnail_url = None
        
        if pd.notna(images_data):
            try:
                import json
                # Parse the JSON string directly
                if isinstance(images_data, str):
                    images_dict = json.loads(images_data)
                else:
                    images_dict = images_data
                
                if isinstance(images_dict, dict):
                    # Try webp first, then jpg
                    if 'webp' in images_dict and isinstance(images_dict['webp'], dict):
                        image_url = images_dict['webp'].get('large_image_url') or images_dict['webp'].get('image_url')
                        thumbnail_url = images_dict['webp'].get('small_image_url')
                    elif 'jpg' in images_dict and isinstance(images_dict['jpg'], dict):
                        image_url = images_dict['jpg'].get('large_image_url') or images_dict['jpg'].get('image_url')
                        thumbnail_url = images_dict['jpg'].get('small_image_url')
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing images for anime {row.get('mal_id')}: {e}")
                pass
        
        # Compute episode type for response
        episodes_val = row.get('episodes')
        anime_type_raw = row.get('type')
        anime_type = str(anime_type_raw).lower() if pd.notna(anime_type_raw) else ''
        episode_type_computed = 'unknown'
        
        if pd.notna(episodes_val) and episodes_val != 0:
            try:
                ep_count = int(float(episodes_val))
                if anime_type == 'movie':
                    episode_type_computed = 'movie'
                elif ep_count == 1:
                    episode_type_computed = 'single'
                elif ep_count <= 12:
                    episode_type_computed = 'short'
                else:
                    episode_type_computed = 'long'
            except (ValueError, TypeError):
                pass
        
        # Compute is_completed for response
        status_val = row.get('status')
        is_completed_computed = False
        if pd.notna(status_val):
            status_lower = str(status_val).lower()
            is_completed_computed = status_lower in ['finished airing', 'completed']
        
        # Create synopsis_short from synopsis if available
        synopsis = safe_value(row.get('synopsis'))
        synopsis_short = None
        if synopsis and len(synopsis) > 200:
            synopsis_short = synopsis[:197] + "..."
        elif synopsis:
            synopsis_short = synopsis
        
        # Parse studios from studios column
        studios_data = row.get('studios', [])
        studios = []
        if pd.notna(studios_data):
            studios_raw = parse_array_field(studios_data)
            for studio_item in studios_raw:
                if isinstance(studio_item, dict) and 'name' in studio_item:
                    studios.append(studio_item['name'])
                elif isinstance(studio_item, str):
                    studios.append(studio_item)
        
        studio_name = studios[0] if studios else None
        
        results.append({
            "id": safe_value(row.get('mal_id')),
            "title": safe_value(row.get('title')),
            "title_english": safe_value(row.get('title_english')),
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "year": safe_value(row.get('year')),
            "score": safe_value(row.get('score')),
            "episodes": safe_value(row.get('episodes')),
            "episode_type": episode_type_computed,
            "status": safe_value(row.get('status')),
            "type": safe_value(row.get('type')),
            "genres": genres,
            "is_completed": is_completed_computed,
            "has_score": safe_value(row.get('has_score', pd.notna(row.get('score')))),
            "url": safe_value(row.get('url')),
            "studio": studio_name,
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
        # Extract genre names from dictionaries
        for genre_item in genre_list:
            if isinstance(genre_item, dict) and 'name' in genre_item:
                genre_name = genre_item['name']
                if genre_name:  # Only add non-empty names
                    genres.add(genre_name)
            elif isinstance(genre_item, str) and genre_item:
                # Handle case where genres might be stored as strings
                genres.add(genre_item)
    
    genres = sorted([g for g in genres if g])  # Remove empty strings and sort

    # --- Years (robust extraction) ---
    years = set()
    
    # Extract from year column first
    for year_val in df['year'].dropna():
        try:
            year_int = int(float(year_val))
            if 1900 <= year_int <= 2030:  # Reasonable range
                years.add(year_int)
        except (ValueError, TypeError):
            pass
    
    # Fallback: extract from aired_from if year column has gaps
    for aired_from in df['aired_from'].dropna():
        try:
            if isinstance(aired_from, str):
                import datetime
                parsed_date = datetime.datetime.fromisoformat(aired_from.replace('Z', '+00:00'))
                if 1900 <= parsed_date.year <= 2030:
                    years.add(parsed_date.year)
        except:
            pass
    
    years = sorted(list(years), reverse=True)

    # --- Seasons ---
    seasons = sorted([s for s in df['season'].dropna().unique().tolist() if s])

    # --- Formats (Types) ---
    formats = sorted([f for f in df['type'].dropna().unique().tolist() if f])

    # --- Statuses ---
    statuses = sorted([s for s in df['status'].dropna().unique().tolist() if s])

    # --- Episode Types (if column exists) ---
    episode_types = []
    if 'episode_type' in df.columns:
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
    
import httpx
from fastapi.responses import JSONResponse

JIKAN_BASE_URL = "https://api.jikan.moe/v4"

@app.get("/anime/{anime_id}")
async def get_anime_detail(anime_id: int):
    async with httpx.AsyncClient() as client:
        detail_response = await client.get(f"{JIKAN_BASE_URL}/anime/{anime_id}/full")
        if detail_response.status_code != 200:
            raise HTTPException(status_code=detail_response.status_code, detail="Anime not found")

        detail_data = detail_response.json()

        rec_response = await client.get(f"{JIKAN_BASE_URL}/anime/{anime_id}/recommendations")
        rec_data = rec_response.json() if rec_response.status_code == 200 else {"data": []}

    result = {
        "anime": detail_data.get("data", {}),
        "recommendations": rec_data.get("data", []),
    }

    return JSONResponse(content=result)

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
    year: int = None,  # New year parameter
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

    # --- Year filter ---
    if year is not None:
        def matches_year(row):
            # Check published_from column first
            published_from = row.get('published_from')
            if pd.notna(published_from):
                try:
                    if isinstance(published_from, str):
                        import datetime
                        parsed_date = datetime.datetime.fromisoformat(published_from.replace('Z', '+00:00'))
                        return parsed_date.year == year
                except:
                    pass
            
            # Fallback: check if there's a published column (for compatibility)
            published = row.get('published')
            if pd.notna(published):
                published_data = safe_json_parse(published)
                
                if isinstance(published_data, dict):
                    from_date = published_data.get('from')
                    if from_date:
                        try:
                            if isinstance(from_date, str):
                                import datetime
                                parsed_date = datetime.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                                return parsed_date.year == year
                        except:
                            pass
                
                elif isinstance(published_data, str):
                    try:
                        import re
                        year_match = re.search(r'\b(\d{4})\b', published_data)
                        if year_match:
                            return int(year_match.group(1)) == year
                    except:
                        pass
            
            return False
        
        df = df[df.apply(matches_year, axis=1)]

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

    # --- Years ---
    years = set()
    
    # Extract years from published_from column
    for published_from in df['published_from'].dropna():
        try:
            if isinstance(published_from, str):
                import datetime
                parsed_date = datetime.datetime.fromisoformat(published_from.replace('Z', '+00:00'))
                years.add(parsed_date.year)
        except:
            pass
    
    # Fallback: if there's a published column, extract from there too
    if 'published' in df.columns:
        for published_field in df['published'].dropna():
            published_data = safe_json_parse(published_field)
            
            if isinstance(published_data, dict):
                from_date = published_data.get('from')
                if from_date:
                    try:
                        if isinstance(from_date, str):
                            import datetime
                            parsed_date = datetime.datetime.fromisoformat(from_date.replace('Z', '+00:00'))
                            years.add(parsed_date.year)
                    except:
                        pass
            
            elif isinstance(published_data, str):
                try:
                    import re
                    year_matches = re.findall(r'\b(\d{4})\b', published_data)
                    for year_match in year_matches:
                        year_val = int(year_match)
                        if 1900 <= year_val <= 2030:
                            years.add(year_val)
                except:
                    pass
    
    years = sorted([y for y in years if y], reverse=True)

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
        "years": years,  # New years array
        "score_ranges": score_ranges,
        "chapter_ranges": chapter_ranges,
        "volume_ranges": volume_ranges
    }
@app.get("/manga/{manga_id}")
async def get_manga_detail(manga_id: int):
    async with httpx.AsyncClient() as client:
        detail_response = await client.get(f"{JIKAN_BASE_URL}/manga/{manga_id}/full")
        if detail_response.status_code != 200:
            raise HTTPException(status_code=detail_response.status_code, detail="Manga not found")

        detail_data = detail_response.json()

        rec_response = await client.get(f"{JIKAN_BASE_URL}/manga/{manga_id}/recommendations")
        rec_data = rec_response.json() if rec_response.status_code == 200 else {"data": []}

    result = {
        "manga": detail_data.get("data", {}),
        "recommendations": rec_data.get("data", []),
    }

    return JSONResponse(content=result)

@app.get("/anime/{anime_id}/image")
async def get_anime_image(anime_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JIKAN_BASE_URL}/anime/{anime_id}/pictures")

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Anime not found")

    data = response.json()

    if "data" not in data or not data["data"]:
        raise HTTPException(status_code=404, detail="No images found for this anime")

    first_img = data["data"][0]["jpg"]

    return JSONResponse(content={
        "id": anime_id,
        "image_url": first_img.get("image_url"),
        "large_image_url": first_img.get("large_image_url"),
        "small_image_url": first_img.get("small_image_url"),
    })

@app.get("/manga/{manga_id}/image")
async def get_manga_image(manga_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{JIKAN_BASE_URL}/manga/{manga_id}/full")
    
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Manga not found")
    
    data = response.json().get("data", {})
    
    image_url = data.get("images", {}).get("jpg", {}).get("large_image_url")
    thumbnail_url = data.get("images", {}).get("jpg", {}).get("image_url")

    return JSONResponse(content={
        "id": manga_id,
        "image_url": image_url,
        "thumbnail_url": thumbnail_url
    })



def build_graph():
    nodes = {}
    links = []

    # Helper to add a node if it doesn't exist
    def add_node(mal_id, name, ntype, url=None):
        key = f"{ntype}_{mal_id}"
        if key not in nodes:
            nodes[key] = {
                "id": key,
                "mal_id": int(mal_id),
                "label": name,
                "type": ntype,
                "url": url
            }

    # Parse both anime + manga CSVs
    for df, ntype in [(anime_df, "anime"), (manga_df, "manga")]:
        for _, row in df.iterrows():
            mal_id = row["mal_id"]
            title = row.get("title", "")
            url = row.get("url", "")
            add_node(mal_id, title, ntype, url)

            if "relations" in row and pd.notna(row["relations"]):
                try:
                    rels = json.loads(row["relations"].replace("'", '"'))
                    for rel in rels:
                        relation_type = rel.get("relation", "")
                        for entry in rel.get("entry", []):
                            target_id = entry["mal_id"]
                            target_type = entry.get("type", "").lower()
                            target_name = entry.get("name", "")
                            target_url = entry.get("url", "")

                            # add the target node (anime or manga)
                            add_node(target_id, target_name, target_type, target_url)

                            # create link
                            links.append({
                                "source": f"{ntype}_{mal_id}",
                                "target": f"{target_type}_{target_id}",
                                "relation": relation_type
                            })
                except Exception as e:
                    # malformed JSON
                    continue

    return {"nodes": list(nodes.values()), "links": links}


@app.get("/graph")
async def get_graph():
    graph = build_graph()
    return JSONResponse(content=graph)

@app.get("/stats/")
def get_comprehensive_stats():
    """Get all comprehensive statistics in one endpoint"""
    
    # Helper functions for safe JSON parsing and array parsing
    def safe_json_parse(field):
        if pd.isna(field):
            return []
        try:
            if isinstance(field, str):
                return json.loads(field)
            return field if isinstance(field, list) else []
        except:
            return []
    
    def parse_array_field(field):
        if pd.isna(field):
            return []
        try:
            if isinstance(field, str):
                # Handle both JSON arrays and string representations
                if field.startswith('['):
                    return json.loads(field)
                else:
                    # Handle comma-separated values
                    return [{'name': item.strip()} for item in field.split(',') if item.strip()]
            return field if isinstance(field, list) else []
        except:
            return []
    
    # =============================================================================
    # BASIC STATS (Existing)
    # =============================================================================
    
    # Basic counts
    total_anime = len(anime_df)
    total_manga = len(manga_df)
    completed_anime = len(anime_df[anime_df['status'].str.contains('Finished', case=False, na=False)])
    completed_manga = len(manga_df[manga_df['status'].str.contains('Finished', case=False, na=False)])
    
    # Score distributions
    bins = list(range(0, 11))
    labels = [f"{i}-{i+1}" for i in range(0, 10)]
    
    anime_score_ranges = pd.cut(anime_df['score'], bins=bins, labels=labels, include_lowest=True, right=True).value_counts().sort_index()
    anime_score_ranges = {str(k): int(v) for k, v in anime_score_ranges.items()}
    
    manga_score_ranges = pd.cut(manga_df['score'], bins=bins, labels=labels, include_lowest=True, right=True).value_counts().sort_index()
    manga_score_ranges = {str(k): int(v) for k, v in manga_score_ranges.items()}
    
    # Average scores
    anime_avg_score = float(anime_df['score'].mean()) if not anime_df['score'].isna().all() else 0
    manga_avg_score = float(manga_df['score'].mean()) if not manga_df['score'].isna().all() else 0
    
    # =============================================================================
    # GENRE ANALYSIS
    # =============================================================================
    
    all_genres = {}
    
    # Anime genres
    for _, row in anime_df.dropna(subset=['genres']).iterrows():
        genres_list = parse_array_field(row['genres'])
        for genre_item in genres_list:
            if isinstance(genre_item, dict) and 'name' in genre_item:
                genre_name = genre_item['name']
                if genre_name:
                    all_genres[genre_name] = all_genres.get(genre_name, {'anime': 0, 'manga': 0})
                    all_genres[genre_name]['anime'] += 1
    
    # Manga genres
    for _, row in manga_df.dropna(subset=['genres']).iterrows():
        genres_list = safe_json_parse(row['genres'])
        for genre in genres_list:
            if isinstance(genre, dict) and genre.get('name'):
                genre_name = genre['name']
                all_genres[genre_name] = all_genres.get(genre_name, {'anime': 0, 'manga': 0})
                all_genres[genre_name]['manga'] += 1
    
    # Top combined genres
    top_combined_genres = {}
    for genre, counts in all_genres.items():
        total = counts['anime'] + counts['manga']
        top_combined_genres[genre] = {
            'total': total,
            'anime': counts['anime'],
            'manga': counts['manga']
        }
    
    top_10_genres = dict(sorted(top_combined_genres.items(), 
                               key=lambda x: x[1]['total'], reverse=True)[:15])
    
    # Genre combinations analysis
    genre_pairs = {}
    for _, row in anime_df.dropna(subset=['genres']).iterrows():
        genres_list = parse_array_field(row['genres'])
        genre_names = [g['name'] for g in genres_list if isinstance(g, dict) and 'name' in g]
        
        for i in range(len(genre_names)):
            for j in range(i+1, len(genre_names)):
                pair = tuple(sorted([genre_names[i], genre_names[j]]))
                genre_pairs[pair] = genre_pairs.get(pair, 0) + 1
    
    top_genre_pairs = [{"pair": " + ".join(pair), "count": count} 
                      for pair, count in sorted(genre_pairs.items(), key=lambda x: x[1], reverse=True)[:10]]
    
    # Genre performance analysis
    genre_scores = {}
    for _, row in anime_df.dropna(subset=['genres', 'score']).iterrows():
        genres_list = parse_array_field(row['genres'])
        score = float(row['score'])
        
        for genre_item in genres_list:
            if isinstance(genre_item, dict) and 'name' in genre_item:
                genre_name = genre_item['name']
                if genre_name not in genre_scores:
                    genre_scores[genre_name] = []
                genre_scores[genre_name].append(score)
    
    genre_avg_scores = {
        genre: sum(scores) / len(scores) 
        for genre, scores in genre_scores.items() 
        if len(scores) >= 10  # Only genres with 10+ entries
    }
    
    # =============================================================================
    # STUDIO & PRODUCER ANALYSIS
    # =============================================================================
    
    studio_counts = {}
    studio_scores = {}
    
    for _, row in anime_df.dropna(subset=['studios']).iterrows():
        studios_list = safe_json_parse(row['studios'])
        score = row.get('score', 0)
        
        for studio in studios_list:
            if isinstance(studio, dict) and studio.get('name'):
                name = studio['name']
                studio_counts[name] = studio_counts.get(name, 0) + 1
                if score and score > 0:
                    if name not in studio_scores:
                        studio_scores[name] = []
                    studio_scores[name].append(float(score))
    
    # Studio performance (min 5 anime)
    studio_performance = {}
    for studio, scores in studio_scores.items():
        if len(scores) >= 5:
            studio_performance[studio] = {
                'count': studio_counts[studio],
                'avg_score': sum(scores) / len(scores),
                'total_anime': len(scores)
            }
    
    top_studios = dict(sorted(studio_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    best_studios = dict(sorted(studio_performance.items(), 
                              key=lambda x: x[1]['avg_score'], reverse=True)[:10])
    
    # Producer analysis
    producer_counts = {}
    for _, row in anime_df.dropna(subset=['producers']).iterrows():
        producers_list = safe_json_parse(row['producers'])
        for producer in producers_list:
            if isinstance(producer, dict) and producer.get('name'):
                name = producer['name']
                producer_counts[name] = producer_counts.get(name, 0) + 1
    
    top_producers = dict(sorted(producer_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # =============================================================================
    # RATINGS & DEMOGRAPHICS
    # =============================================================================
    
    # Rating distribution
    rating_counts = anime_df['rating'].value_counts().to_dict()
    rating_scores = {}
    
    for rating in rating_counts.keys():
        rating_data = anime_df[anime_df['rating'] == rating]['score'].dropna()
        if len(rating_data) > 0:
            rating_scores[rating] = float(rating_data.mean())
    
    # Demographics
    anime_demo_counts = {}
    manga_demo_counts = {}
    
    for _, row in anime_df.dropna(subset=['demographics']).iterrows():
        demo_list = safe_json_parse(row['demographics'])
        for demo in demo_list:
            if isinstance(demo, dict) and demo.get('name'):
                name = demo['name']
                anime_demo_counts[name] = anime_demo_counts.get(name, 0) + 1
    
    for _, row in manga_df.dropna(subset=['demographics']).iterrows():
        demo_list = safe_json_parse(row['demographics'])
        for demo in demo_list:
            if isinstance(demo, dict) and demo.get('name'):
                name = demo['name']
                manga_demo_counts[name] = manga_demo_counts.get(name, 0) + 1
    
    # =============================================================================
    # SOURCE MATERIAL & TYPE ANALYSIS
    # =============================================================================
    
    # Source analysis
    source_counts = anime_df['source'].value_counts().to_dict()
    source_scores = {}
    
    for source in source_counts.keys():
        source_data = anime_df[anime_df['source'] == source]['score'].dropna()
        if len(source_data) >= 5:
            source_scores[source] = {
                'count': source_counts[source],
                'avg_score': float(source_data.mean()),
                'median_score': float(source_data.median())
            }
    
    # Type distributions
    anime_type_counts = anime_df['type'].value_counts().to_dict()
    manga_type_counts = manga_df['type'].value_counts().to_dict()
    
    # =============================================================================
    # TIME & BROADCAST ANALYSIS
    # =============================================================================
    
    # Year distribution
    year_counts = {}
    for year_val in anime_df['year'].dropna():
        try:
            year = int(float(year_val))
            if 1900 <= year <= 2025:
                year_counts[year] = year_counts.get(year, 0) + 1
        except:
            pass
    
    # Season analysis
    season_counts = anime_df['season'].value_counts().to_dict()
    season_scores = {}
    for season in ['spring', 'summer', 'fall', 'winter']:
        season_data = anime_df[anime_df['season'] == season]['score'].dropna()
        if len(season_data) > 0:
            season_scores[season] = {
                'count': len(season_data),
                'avg_score': float(season_data.mean())
            }
    
    # Broadcast timing
    broadcast_day_counts = anime_df['broadcast_day'].value_counts().to_dict()
    
    time_slots = {
        'Morning (06-12)': 0,
        'Afternoon (12-18)': 0, 
        'Evening (18-22)': 0,
        'Late Night (22-06)': 0
    }
    
    for time_str in anime_df['broadcast_time'].dropna():
        try:
            hour = int(time_str.split(':')[0])
            if 6 <= hour < 12:
                time_slots['Morning (06-12)'] += 1
            elif 12 <= hour < 18:
                time_slots['Afternoon (12-18)'] += 1
            elif 18 <= hour < 22:
                time_slots['Evening (18-22)'] += 1
            else:
                time_slots['Late Night (22-06)'] += 1
        except:
            pass
    
    # =============================================================================
    # POPULARITY & RANKING ANALYSIS
    # =============================================================================
    
    # Correlation data (limit to prevent huge responses)
    popularity_score_data = []
    rank_score_data = []
    members_score_data = []
    
    # Sample data for correlations (every 10th entry to reduce size)
    sample_anime = anime_df[::10]  # Every 10th row
    
    for _, row in sample_anime.dropna(subset=['popularity', 'score']).iterrows():
        popularity_score_data.append({
            'popularity': int(row['popularity']),
            'score': float(row['score']),
            'title': row['title'][:50]  # Truncate long titles
        })
    
    for _, row in sample_anime.dropna(subset=['rank', 'score']).iterrows():
        rank_score_data.append({
            'rank': int(row['rank']),
            'score': float(row['score']),
            'title': row['title'][:50]
        })
    
    for _, row in sample_anime.dropna(subset=['members', 'score']).iterrows():
        members_score_data.append({
            'members': int(row['members']),
            'score': float(row['score']),
            'title': row['title'][:50]
        })
    
    # Members distribution
    members_ranges = {
        '0-10K': len(anime_df[anime_df['members'] <= 10000]),
        '10K-50K': len(anime_df[(anime_df['members'] > 10000) & (anime_df['members'] <= 50000)]),
        '50K-100K': len(anime_df[(anime_df['members'] > 50000) & (anime_df['members'] <= 100000)]),
        '100K-500K': len(anime_df[(anime_df['members'] > 100000) & (anime_df['members'] <= 500000)]),
        '500K+': len(anime_df[anime_df['members'] > 500000])
    }
    
    # Top lists (limit to 20 items each)
    top_favorites = anime_df.nlargest(20, 'favorites')[['title', 'favorites', 'score']].to_dict('records')
    top_members = anime_df.nlargest(20, 'members')[['title', 'members', 'score']].to_dict('records')
    top_scored = anime_df.nlargest(20, 'score')[['title', 'score', 'members', 'favorites']].to_dict('records')
    
    # =============================================================================
    # AUTHOR & SERIALIZATION ANALYSIS (MANGA)
    # =============================================================================
    
    author_counts = {}
    author_scores = {}
    
    for _, row in manga_df.dropna(subset=['authors']).iterrows():
        authors_list = safe_json_parse(row['authors'])
        score = row.get('score', 0)
        
        for author in authors_list:
            if isinstance(author, dict) and author.get('name'):
                name = author['name']
                author_counts[name] = author_counts.get(name, 0) + 1
                if score and score > 0:
                    if name not in author_scores:
                        author_scores[name] = []
                    author_scores[name].append(float(score))
    
    top_authors = dict(sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    
    # Best authors by score (min 2 works)
    best_authors = {}
    for author, scores in author_scores.items():
        if len(scores) >= 2:
            best_authors[author] = {
                'count': len(scores),
                'avg_score': sum(scores) / len(scores)
            }
    
    best_authors_sorted = dict(sorted(best_authors.items(), 
                                    key=lambda x: x[1]['avg_score'], reverse=True)[:10])
    
    # Serializations
    serialization_counts = {}
    for _, row in manga_df.dropna(subset=['serializations']).iterrows():
        serial_list = safe_json_parse(row['serializations'])
        for serial in serial_list:
            if isinstance(serial, dict) and serial.get('name'):
                name = serial['name']
                serialization_counts[name] = serialization_counts.get(name, 0) + 1
    
    top_serializations = dict(sorted(serialization_counts.items(), key=lambda x: x[1], reverse=True)[:10])
    
    # =============================================================================
    # EPISODE & CHAPTER DISTRIBUTIONS
    # =============================================================================
    
    # Episode ranges
    episode_ranges = {
        '1 Episode': len(anime_df[anime_df['episodes'] == 1]),
        '2-12 Episodes': len(anime_df[(anime_df['episodes'] >= 2) & (anime_df['episodes'] <= 12)]),
        '13-26 Episodes': len(anime_df[(anime_df['episodes'] >= 13) & (anime_df['episodes'] <= 26)]),
        '27-52 Episodes': len(anime_df[(anime_df['episodes'] >= 27) & (anime_df['episodes'] <= 52)]),
        '53+ Episodes': len(anime_df[anime_df['episodes'] > 52])
    }
    
    # Chapter ranges
    chapter_ranges = {
        '1-50': len(manga_df[(manga_df['chapters'] >= 1) & (manga_df['chapters'] <= 50)]),
        '51-100': len(manga_df[(manga_df['chapters'] >= 51) & (manga_df['chapters'] <= 100)]),
        '101-200': len(manga_df[(manga_df['chapters'] >= 101) & (manga_df['chapters'] <= 200)]),
        '201-500': len(manga_df[(manga_df['chapters'] >= 201) & (manga_df['chapters'] <= 500)]),
        '500+': len(manga_df[manga_df['chapters'] > 500])
    }
    
    # Volume ranges
    volume_ranges = {
        '1-10': len(manga_df[(manga_df['volumes'] >= 1) & (manga_df['volumes'] <= 10)]),
        '11-25': len(manga_df[(manga_df['volumes'] >= 11) & (manga_df['volumes'] <= 25)]),
        '26-50': len(manga_df[(manga_df['volumes'] >= 26) & (manga_df['volumes'] <= 50)]),
        '51+': len(manga_df[manga_df['volumes'] > 50])
    }
    
    # =============================================================================
    # RETURN COMPREHENSIVE DATA
    # =============================================================================
    
    top_manga_scored = manga_df.nlargest(20, 'score')[['title', 'score', 'members', 'favorites']].to_dict('records')
    top_manga_favorites = manga_df.nlargest(20, 'favorites')[['title', 'favorites', 'score']].to_dict('records')
    top_manga_members = manga_df.nlargest(20, 'members')[['title', 'members', 'score']].to_dict('records')

    return {
        # Basic Overview
        "overview": {
            "total_anime": total_anime,
            "total_manga": total_manga,
            "total_items": total_anime + total_manga,
            "completed_anime": completed_anime,
            "completed_manga": completed_manga,
            "anime_avg_score": anime_avg_score,
            "manga_avg_score": manga_avg_score,
            "completion_rates": {
                "anime": (completed_anime / total_anime * 100) if total_anime > 0 else 0,
                "manga": (completed_manga / total_manga * 100) if total_manga > 0 else 0
            }
        },
        
        # Score Analysis
        "scores": {
            "anime_distribution": anime_score_ranges,
            "manga_distribution": manga_score_ranges
        },
        
        # Genre Analysis
        "genres": {
            "top_combined": top_10_genres,
            "combinations": top_genre_pairs,
            "performance": genre_avg_scores
        },
        
        # Studio & Production
        "studios": {
            "top_by_count": top_studios,
            "best_by_score": best_studios,
            "top_producers": top_producers
        },
        
        # Content Classification
        "classification": {
            "anime_types": anime_type_counts,
            "manga_types": manga_type_counts,
            "ratings": rating_counts,
            "rating_scores": rating_scores,
            "anime_demographics": anime_demo_counts,
            "manga_demographics": manga_demo_counts,
            "source_material": source_counts,
            "source_performance": source_scores
        },
        
        # Time & Broadcasting
        "timing": {
            "year_distribution": dict(sorted(year_counts.items())),
            "season_distribution": season_counts,
            "season_performance": season_scores,
            "broadcast_days": broadcast_day_counts,
            "broadcast_time_slots": time_slots
        },
        
        # Popularity & Community
        "popularity": {
            "members_ranges": members_ranges,
            "top_favorites": top_favorites,
            "top_members": top_members,
            "top_scored": top_scored,
            "top_manga_scored": top_manga_scored,
            "top_manga_favorites": top_manga_favorites, 
            "top_manga_members": top_manga_members,
            "correlations": {
                "popularity_score": popularity_score_data,
                "rank_score": rank_score_data,
                "members_score": members_score_data
            }
        },
        
        # Content Length
        "content_length": {
            "episode_distribution": episode_ranges,
            "chapter_distribution": chapter_ranges,
            "volume_distribution": volume_ranges
        },
        
        # Creators (Manga)
        "creators": {
            "top_authors": top_authors,
            "best_authors": best_authors_sorted,
            "top_serializations": top_serializations
        }
    }

import pickle
import gzip
import os
from typing import Optional

recommender = None

def load_recommender():
    global recommender
    if recommender is not None:
        return recommender
    
    model_files = [
        "anime_recommender_advanced.pkl.gz",
        "anime_recommender_advanced.pkl", 
        "dataset/anime_recommender_advanced.pkl.gz",
        "dataset/anime_recommender_advanced.pkl"
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            try:
                if model_file.endswith('.gz'):
                    with gzip.open(model_file, "rb") as f:
                        model_data = pickle.load(f)
                else:
                    with open(model_file, "rb") as f:
                        model_data = pickle.load(f)
                
                class SimpleRecommender:
                    def __init__(self, model_data):
                        self.df = model_data['df']
                        self.features = model_data['features']
                        self.model_info = model_data.get('model_info', {})
                    
                    def parse_list(self, x):
                        """Parse JSON-like strings to extract names"""
                        if pd.isna(x) or x == "":
                            return []
                        try:
                            if isinstance(x, str) and x.startswith("["):
                                parsed = ast.literal_eval(x)
                                if isinstance(parsed, list):
                                    return [d.get("name", "") for d in parsed if isinstance(d, dict) and "name" in d]
                            elif isinstance(x, list):
                                return x
                            return []
                        except:
                            return []
                    
                    def explain_similarity(self, source_anime, target_anime):
                        """Generate explanation for why anime are similar"""
                        source_genres = set(self.parse_list(source_anime.get('genres', '')))
                        target_genres = set(self.parse_list(target_anime.get('genres', '')))
                        source_themes = set(self.parse_list(source_anime.get('themes', '')))
                        target_themes = set(self.parse_list(target_anime.get('themes', '')))
                        
                        explanation_parts = []
                        
                        # Genre analysis
                        common_genres = source_genres & target_genres
                        if common_genres:
                            if len(common_genres) >= 3:
                                explanation_parts.append(f"Strong genre overlap: {', '.join(list(common_genres)[:3])}")
                            elif len(common_genres) == 2:
                                explanation_parts.append(f"Shared genres: {', '.join(common_genres)}")
                            else:
                                explanation_parts.append(f"Same genre: {list(common_genres)[0]}")
                        
                        # Theme analysis
                        common_themes = source_themes & target_themes
                        if common_themes:
                            if len(common_themes) >= 2:
                                explanation_parts.append(f"Similar themes: {', '.join(list(common_themes)[:2])}")
                            else:
                                explanation_parts.append(f"Shared theme: {list(common_themes)[0]}")
                        
                        # Format analysis
                        if source_anime.get('type') == target_anime.get('type'):
                            if source_anime.get('type') in ['TV', 'Movie']:
                                explanation_parts.append(f"Both {source_anime.get('type')} format")
                        
                        # Score tier analysis
                        source_score = source_anime.get('score', 0)
                        target_score = target_anime.get('score', 0)
                        if pd.notna(source_score) and pd.notna(target_score):
                            if source_score >= 8.5 and target_score >= 8.5:
                                explanation_parts.append("Both highly acclaimed")
                            elif source_score >= 8.0 and target_score >= 8.0:
                                explanation_parts.append("Both well-rated")
                            elif abs(source_score - target_score) <= 0.5:
                                explanation_parts.append("Similar rating levels")
                        
                        # Year proximity
                        source_year = source_anime.get('year')
                        target_year = target_anime.get('year')
                        if pd.notna(source_year) and pd.notna(target_year):
                            year_diff = abs(int(source_year) - int(target_year))
                            if year_diff <= 2:
                                explanation_parts.append(f"Same period ({int(target_year)})")
                            elif year_diff <= 5:
                                explanation_parts.append("Similar era")
                        
                        # Studio connection  
                        source_studios = set(self.parse_list(source_anime.get('studios', '')))
                        target_studios = set(self.parse_list(target_anime.get('studios', '')))
                        common_studios = source_studios & target_studios
                        if common_studios:
                            explanation_parts.append(f"Same studio: {list(common_studios)[0]}")
                        
                        # Combine explanation
                        if explanation_parts:
                            return "; ".join(explanation_parts[:4])  # Limit to 4 reasons
                        else:
                            return "Similar content profile and style"
                    
                    def recommend(self, anime_id, top_k=10, min_score=None, include_sequels=True, explain=False):
                        from sklearn.metrics.pairwise import cosine_similarity
                        import numpy as np
                        
                        if anime_id not in self.df['mal_id'].values:
                            return {"error": "Anime not found"}
                        
                        source_idx = self.df[self.df['mal_id'] == anime_id].index[0]
                        source_anime = self.df.iloc[source_idx]
                        
                        similarities = cosine_similarity([self.features[source_idx]], self.features)[0]
                        
                        # Fix NaN, inf, -inf values
                        similarities = np.nan_to_num(similarities, nan=0.0, posinf=1.0, neginf=0.0)
                        
                        # Create results dataframe
                        results_df = self.df.copy()
                        results_df['similarity'] = similarities
                        
                        # Remove source anime
                        results_df = results_df[results_df['mal_id'] != anime_id]
                        
                        # Apply min_score filter
                        if min_score is not None:
                            results_df = results_df[
                                (results_df['score'] >= min_score) &
                                results_df['score'].notna()
                            ]
                        
                        # Remove sequels if requested
                        if not include_sequels:
                            source_title_words = source_anime['title'].lower().split()
                            if len(source_title_words) > 0:
                                main_title = source_title_words[0]
                                if len(main_title) > 3:  # Only filter if title is meaningful
                                    mask = ~results_df['title'].str.lower().str.contains(
                                        main_title, na=False, regex=False
                                    )
                                    results_df = results_df[mask]
                        
                        # Ensure we have enough results
                        if len(results_df) == 0:
                            return {
                                'source': {
                                    'mal_id': int(source_anime['mal_id']),
                                    'title': source_anime['title'],
                                    'title_english': source_anime.get('title_english', ''),
                                    'score': float(source_anime['score']) if pd.notna(source_anime['score']) else None
                                },
                                'recommendations': [],
                                'filters_applied': {
                                    'min_score': min_score,
                                    'include_sequels': include_sequels,
                                    'explain': explain
                                }
                            }
                        
                        # Get top recommendations
                        sim_indices = results_df.nlargest(min(top_k, len(results_df)), 'similarity').index
                        
                        recommendations = []
                        for idx in sim_indices:
                            row = self.df.iloc[idx]
                            similarity_val = results_df.loc[idx, 'similarity']
                            
                            # Ensure similarity is a valid float
                            if not np.isfinite(similarity_val):
                                similarity_val = 0.0
                            
                            synopsis = row.get('synopsis', '')
                            synopsis = str(synopsis) if pd.notna(synopsis) else ''
                            rec_item = {
                                'mal_id': int(row['mal_id']),
                                'title': row['title'],
                                'title_english': row.get('title_english', ''),
                                'score': float(row['score']) if pd.notna(row['score']) else None,
                                'similarity': float(similarity_val),
                                'type': row.get('type', ''),
                                'episodes': int(row['episodes']) if pd.notna(row['episodes']) else None,
                                'year': int(row['year']) if pd.notna(row['year']) else None,
                                'synopsis': synopsis[:200] + "..." if synopsis and len(synopsis) > 200 else synopsis
                            }
                            
                            # Add explanation if requested
                            if explain:
                                rec_item['explanation'] = self.explain_similarity(source_anime, row)
                            
                            recommendations.append(rec_item)
                        
                        return {
                            'source': {
                                'mal_id': int(source_anime['mal_id']),
                                'title': source_anime['title'],
                                'title_english': source_anime.get('title_english', ''),
                                'score': float(source_anime['score']) if pd.notna(source_anime['score']) else None
                            },
                            'recommendations': recommendations,
                            'filters_applied': {
                                'min_score': min_score,
                                'include_sequels': include_sequels,
                                'explain': explain
                            }
                        }
                
                recommender = SimpleRecommender(model_data)
                print(f"✓ Recommender model loaded from {model_file}")
                return recommender
                
            except Exception as e:
                print(f"Failed to load {model_file}: {e}")
                continue
    
    print("Warning: No recommender model found")
    return None

@app.get("/anime/{anime_id}/recommend")
def get_anime_recommendations(
    anime_id: int,
    limit: int = 10,
    min_score: float = None,
    include_sequels: bool = True,
    explain: bool = False
):
    """Get anime recommendations based on trained model with configurable options"""
    
    def safe_float(value):
        """Convert value to safe float for JSON serialization"""
        if value is None:
            return None
        try:
            float_val = float(value)
            if not np.isfinite(float_val):
                return None
            return float_val
        except (ValueError, TypeError, OverflowError):
            return None
    
    def safe_int(value):
        """Convert value to safe int for JSON serialization"""
        if value is None or pd.isna(value):
            return None
        try:
            return int(value)
        except (ValueError, TypeError, OverflowError):
            return None
    
    rec = load_recommender()
    if rec is None:
        raise HTTPException(status_code=503, detail="Recommendation model not available")
    
    result = rec.recommend(
        anime_id, 
        top_k=limit,
        min_score=min_score,
        include_sequels=include_sequels,
        explain=explain
    )
    
    if "error" in result:
        if "not found" in result["error"].lower():
            raise HTTPException(status_code=404, detail=f"Anime with ID {anime_id} not found")
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    formatted_recommendations = []
    for rec_item in result['recommendations']:
        image_url = None
        thumbnail_url = None
        
        anime_row = anime_df[anime_df['mal_id'] == rec_item['mal_id']]
        if not anime_row.empty:
            images_data = anime_row.iloc[0].get('images')
            if pd.notna(images_data):
                try:
                    if isinstance(images_data, str):
                        images_dict = json.loads(images_data)
                    else:
                        images_dict = images_data
                    
                    if isinstance(images_dict, dict):
                        if 'webp' in images_dict and isinstance(images_dict['webp'], dict):
                            image_url = images_dict['webp'].get('large_image_url') or images_dict['webp'].get('image_url')
                            thumbnail_url = images_dict['webp'].get('small_image_url')
                        elif 'jpg' in images_dict and isinstance(images_dict['jpg'], dict):
                            image_url = images_dict['jpg'].get('large_image_url') or images_dict['jpg'].get('image_url')
                            thumbnail_url = images_dict['jpg'].get('small_image_url')
                except:
                    pass
        
        formatted_rec = {
            "id": safe_int(rec_item['mal_id']),
            "title": str(rec_item.get('title', '')),
            "title_english": str(rec_item.get('title_english', '')),
            "image_url": image_url,
            "thumbnail_url": thumbnail_url,
            "score": safe_float(rec_item.get('score')),
            "similarity": safe_float(rec_item.get('similarity')),
            "type": str(rec_item.get('type', '')),
            "episodes": safe_int(rec_item.get('episodes')),
            "year": safe_int(rec_item.get('year')),
            "synopsis": str(rec_item.get('synopsis', ''))
        }
        
        # Add explanation if available
        if rec_item.get('explanation'):
            formatted_rec['explanation'] = str(rec_item['explanation'])
        
        formatted_recommendations.append(formatted_rec)
    
    source_image_url = None
    source_thumbnail_url = None
    source_anime_row = anime_df[anime_df['mal_id'] == result['source']['mal_id']]
    if not source_anime_row.empty:
        images_data = source_anime_row.iloc[0].get('images')
        if pd.notna(images_data):
            try:
                if isinstance(images_data, str):
                    images_dict = json.loads(images_data)
                else:
                    images_dict = images_data
                
                if isinstance(images_dict, dict):
                    if 'webp' in images_dict and isinstance(images_dict['webp'], dict):
                        source_image_url = images_dict['webp'].get('large_image_url') or images_dict['webp'].get('image_url')
                        source_thumbnail_url = images_dict['webp'].get('small_image_url')
                    elif 'jpg' in images_dict and isinstance(images_dict['jpg'], dict):
                        source_image_url = images_dict['jpg'].get('large_image_url') or images_dict['jpg'].get('image_url')
                        source_thumbnail_url = images_dict['jpg'].get('small_image_url')
            except:
                pass
    
    return {
        "source": {
            "id": safe_int(result['source']['mal_id']),
            "title": str(result['source'].get('title', '')),
            "title_english": str(result['source'].get('title_english', '')),
            "image_url": source_image_url,
            "thumbnail_url": source_thumbnail_url,
            "score": safe_float(result['source'].get('score'))
        },
        "recommendations": formatted_recommendations,
        "count": len(formatted_recommendations),
        "filters_applied": result.get('filters_applied', {})
    }