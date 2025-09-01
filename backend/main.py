import ast
import json
import math
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import re
from pydantic import BaseModel
from dotenv import load_dotenv

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

import os
BASE_DIR = Path(__file__).parent
load_dotenv(BASE_DIR / '.env')

def load_dataframes():
    """Load dataframes from URLs or local files"""
    
    anime_url = os.getenv('ANIME_CSV_URL')
    manga_url = os.getenv('MANGA_CSV_URL')
    
    if anime_url and manga_url and anime_url.startswith('http'):
        try:
            print("Loading from configured URLs...")
            print(f"Anime URL: {anime_url}")
            print(f"Manga URL: {manga_url}")
            anime_df = pd.read_csv(anime_url)
            manga_df = pd.read_csv(manga_url)
            print("✓ Successfully loaded from URLs")
        except Exception as e:
            print(f"Failed to load from URLs: {e}")
    # Fallback to local files
    try:
        BASE_DIR = Path(__file__).parent.parent
        ANIME_CSV = BASE_DIR / "backend" / "animes.csv.gz"
        MANGA_CSV = BASE_DIR / "backend" / "mangas.csv.gz"
        anime_df = pd.read_csv(ANIME_CSV)
        manga_df = pd.read_csv(MANGA_CSV, compression='gzip')
        print("✓ Successfully loaded from local files")
        return anime_df, manga_df
    except Exception as e:
        print(f"Failed to load local files: {e}")
        raise Exception("No data source available")

anime_df, manga_df = load_dataframes()

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

    # --- Genre filter ---
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

    # --- Year filter  ---
    if year is not None:
        def matches_year(row):
            year_val = row.get('year')
            if pd.notna(year_val):
                try:
                    if isinstance(year_val, str):
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
                        aired_from_clean = aired_from.replace('Z', '+00:00')
                        parsed_date = datetime.datetime.fromisoformat(aired_from_clean)
                        return parsed_date.year == year
                except Exception as e:
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
        
    # --- Format filter ---
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

    # --- Episode type filter ---
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

    # --- Completed only filter  ---
    if completed_only is not None:
        def is_completed(status_val):
            if pd.isna(status_val):
                return False
            status_lower = str(status_val).lower()
            return status_lower in ['finished airing', 'completed']
        
        df['computed_is_completed'] = df['status'].apply(is_completed)
        df = df[df['computed_is_completed'] == completed_only]

    # --- Sort by score ---
    # Create computed columns for sorting
    df['score_filled'] = df['score'].fillna(0)
    df['has_score'] = df['score'].notna()
    df['has_score_int'] = df['has_score'].astype(int)
    
    # Sort by has_score first (items with scores), then by score value
    df = df.sort_values(by=['has_score_int', 'score_filled'], ascending=[False, False])

    results = []
    total_count = len(df)
    
    for _, row in df.iloc[offset:offset+limit].iterrows():
        # Parse genres for response
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
            except (json.JSONDecodeError, KeyError, TypeError) as e:
                print(f"Error parsing images for anime {row.get('mal_id')}: {e}")
                pass
        
        # Compute episode type 
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
        
        # Compute is_completed 
        status_val = row.get('status')
        is_completed_computed = False
        if pd.notna(status_val):
            status_lower = str(status_val).lower()
            is_completed_computed = status_lower in ['finished airing', 'completed']
        
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
                if genre_name:  
                    genres.add(genre_name)
            elif isinstance(genre_item, str) and genre_item:
                genres.add(genre_item)
    
    genres = sorted([g for g in genres if g]) 

    # --- Years ---
    years = set()
    
    # Extract from year column first
    for year_val in df['year'].dropna():
        try:
            year_int = int(float(year_val))
            if 1900 <= year_int <= 2030:  
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

    # --- Episode Types---
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
    year: int = None,  
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
            published_from = row.get('published_from')
            if pd.notna(published_from):
                try:
                    if isinstance(published_from, str):
                        import datetime
                        parsed_date = datetime.datetime.fromisoformat(published_from.replace('Z', '+00:00'))
                        return parsed_date.year == year
                except:
                    pass
            
            # Fallback: check if there's a published column 
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

    results = []
    total_count = len(df)
    
    for _, row in df.iloc[offset:offset+limit].iterrows():
        genres = safe_json_parse(row.get('genres', []))
        genre_names = [g.get('name', '') for g in genres if isinstance(g, dict)]
        
        authors = safe_json_parse(row.get('authors', []))
        author_names = [a.get('name', '') for a in authors if isinstance(a, dict)]
        
        demographics = safe_json_parse(row.get('demographics', []))
        demographic_names = [d.get('name', '') for d in demographics if isinstance(d, dict)]
        
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

    # --- Authors ---
    author_counts = {}
    for author_field in df['authors'].dropna():
        author_list = safe_json_parse(author_field)
        for author in author_list:
            if isinstance(author, dict) and author.get('name'):
                name = author['name']
                author_counts[name] = author_counts.get(name, 0) + 1
    
    top_authors = sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:50]
    authors = [name for name, _ in top_authors]

    # --- Serializations ---
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
    
    for published_from in df['published_from'].dropna():
        try:
            if isinstance(published_from, str):
                import datetime
                parsed_date = datetime.datetime.fromisoformat(published_from.replace('Z', '+00:00'))
                years.add(parsed_date.year)
        except:
            pass
    
    # Fallback
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
        "years": years,  
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

                            add_node(target_id, target_name, target_type, target_url)

                            links.append({
                                "source": f"{ntype}_{mal_id}",
                                "target": f"{target_type}_{target_id}",
                                "relation": relation_type
                            })
                except Exception as e:
                    continue

    return {"nodes": list(nodes.values()), "links": links}

@app.get("/graph")
async def get_graph():
    graph = build_graph()
    return JSONResponse(content=graph)

@app.get("/stats/")
def get_stats():
    """Get all statistics in one endpoint"""

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
                if field.startswith('['):
                    return json.loads(field)
                else:
                    return [{'name': item.strip()} for item in field.split(',') if item.strip()]
            return field if isinstance(field, list) else []
        except:
            return []
    
    # =============================================================================
    # BASIC STATS
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
        if len(scores) >= 10  
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
    sample_anime = anime_df[::10] 
    
    for _, row in sample_anime.dropna(subset=['popularity', 'score']).iterrows():
        popularity_score_data.append({
            'popularity': int(row['popularity']),
            'score': float(row['score']),
            'title': row['title'][:50] 
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
    # RETURN DATA
    # =============================================================================
    
    top_manga_scored = manga_df.nlargest(20, 'score')[['title', 'score', 'members', 'favorites']].to_dict('records')
    top_manga_favorites = manga_df.nlargest(20, 'favorites')[['title', 'favorites', 'score']].to_dict('records')
    top_manga_members = manga_df.nlargest(20, 'members')[['title', 'members', 'score']].to_dict('records')

    return {
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
class SearchRequest(BaseModel):
    q: str
    limit: int = 10

import json

@app.post("/anime/search")
def search_anime(request: SearchRequest):
    try:
        global anime_df
        if anime_df is None or anime_df.empty:
            raise HTTPException(status_code=503, detail="Anime database not loaded")
       
        if len(request.q.strip()) < 2:
            return {"data": [], "total": 0}
       
        df = anime_df
        query = request.q.lower().strip()
       
        mask = (
            df['title'].str.lower().str.contains(query, na=False, regex=False) |
            df['title_english'].str.lower().str.contains(query, na=False, regex=False)
        )
       
        total_results = mask.sum()
        results = df[mask].head(request.limit)
       
        search_results = []
        for _, row in results.iterrows():
            title_english = row.get('title_english', '')
            if pd.isna(title_english):
                title_english = ''
           
            score = row.get('score')
            if pd.isna(score):
                score = None
            else:
                score = float(score)
           
            year = row.get('year')
            if pd.isna(year):
                year = None
            else:
                year = int(year)
           
            episodes = row.get('episodes')
            if pd.isna(episodes):
                episodes = None
            else:
                episodes = int(episodes)
            
            image_url = None
            images = row.get('images')
            if pd.notna(images) and images:
                try:
                    if isinstance(images, str):
                        images_data = json.loads(images)
                    else:
                        images_data = images
                    
                    if 'webp' in images_data and 'large_image_url' in images_data['webp']:
                        image_url = images_data['webp']['large_image_url']
                    elif 'webp' in images_data and 'image_url' in images_data['webp']:
                        image_url = images_data['webp']['image_url']
                    elif 'jpg' in images_data and 'large_image_url' in images_data['jpg']:
                        image_url = images_data['jpg']['large_image_url']
                    elif 'jpg' in images_data and 'image_url' in images_data['jpg']:
                        image_url = images_data['jpg']['image_url']
                except (json.JSONDecodeError, KeyError, TypeError):
                    image_url = None
           
            search_results.append({
                'mal_id': int(row['mal_id']),
                'title': str(row['title']),
                'title_english': title_english,
                'score': score,
                'year': year,
                'type': str(row.get('type', '')),
                'episodes': episodes,
                'image_url': image_url
            })
       
        return {
            "data": search_results,
            "total": int(total_results),
            "query": request.q,
            "limit": request.limit
        }
       
    except Exception as e:
        print(f"Search error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import ast
import gzip
import pickle
import os
import json
from typing import Dict, Any 

class AnimeRecommender:
    def __init__(self, model_data):
        self.df = anime_df
        self.features = model_data['features']
        self.model_info = model_data.get('model_info', {})
        self.setup_enhanced_genre_groups()
    
    def setup_enhanced_genre_groups(self):
          self.genre_groups = {
                            # Core demographics and target audience
                            'shounen_action': ['Action', 'Adventure', 'Shounen', 'Super Power', 'Martial Arts', 'Tournament'],
                            'seinen_mature': ['Seinen', 'Psychological', 'Thriller', 'Adult Cast', 'Workplace'],
                            'shoujo_romance': ['Shoujo', 'Romance', 'School', 'Josei'],
                            'josei_adult': ['Josei', 'Romance', 'Drama', 'Adult Cast'],
                            
                            # Genre combinations
                            'dark_psychological': ['Horror', 'Thriller', 'Psychological', 'Gore', 'Supernatural'],
                            'comedy_lighthearted': ['Comedy', 'Slice of Life', 'School', 'Gag Humor', 'Parody'],
                            'sci_fi_tech': ['Sci-Fi', 'Mecha', 'Space', 'Cyberpunk', 'Technology'],
                            'fantasy_magic': ['Fantasy', 'Magic', 'Supernatural', 'Mythology', 'Isekai'],
                            
                            # Thematic groups
                            'sports_competition': ['Sports', 'Team Sports', 'Racing', 'Strategy Game'],
                            'music_arts': ['Music', 'Performing Arts', 'Idols (Female)', 'Idols (Male)'],
                            'historical_period': ['Historical', 'Samurai', 'Military'],
                            'slice_of_life': ['Slice of Life', 'Iyashikei', 'CGDCT'],
                            
                            # Advanced themes
                            'existential_deep': ['Philosophical', 'Psychological', 'Drama', 'Tragedy'],
                            'adventure_journey': ['Adventure', 'Survival', 'Travel'],
                            'mystery_detective': ['Mystery', 'Detective', 'Police'],
                            'war_conflict': ['Military', 'War', 'Combat Sports'],
                            
                            # SPORTS BRIDGE CATEGORIES
                            'psychological_sports': ['Sports', 'Psychological', 'Drama', 'Mental Health'],
                            'action_sports': ['Sports', 'Action', 'Tournament', 'Martial Arts'],
                            'supernatural_sports': ['Sports', 'Supernatural', 'Super Power', 'Fantasy'],
                            'comedy_sports': ['Sports', 'Comedy', 'School', 'Slice of Life'],
                            'romance_sports': ['Sports', 'Romance', 'School', 'Drama'],
                            'dark_sports': ['Sports', 'Thriller', 'Psychological', 'Tragedy'],
                            'team_drama': ['Sports', 'Drama', 'Friendship', 'Coming-of-Age'],
                            'competitive_mindset': ['Sports', 'Strategy Game', 'Psychological', 'Mind Games'],
                            
                            # ACTION BRIDGE CATEGORIES
                            'psychological_action': ['Action', 'Psychological', 'Thriller', 'Mind Games'],
                            'comedy_action': ['Action', 'Comedy', 'Parody', 'Adventure'],
                            'romance_action': ['Action', 'Romance', 'Adventure', 'Drama'],
                            'sci_fi_action': ['Action', 'Sci-Fi', 'Mecha', 'Space'],
                            'fantasy_action': ['Action', 'Fantasy', 'Magic', 'Supernatural'],
                            'historical_action': ['Action', 'Historical', 'Samurai', 'Military'],
                            'horror_action': ['Action', 'Horror', 'Supernatural', 'Gore'],
                            'school_action': ['Action', 'School', 'Shounen', 'Super Power'],
                            
                            # PSYCHOLOGICAL BRIDGE CATEGORIES
                            'psychological_horror': ['Psychological', 'Horror', 'Thriller', 'Supernatural'],
                            'psychological_romance': ['Psychological', 'Romance', 'Drama', 'Adult Cast'],
                            'psychological_sci_fi': ['Psychological', 'Sci-Fi', 'Cyberpunk', 'Philosophy'],
                            'psychological_fantasy': ['Psychological', 'Fantasy', 'Supernatural', 'Mystery'],
                            'psychological_mystery': ['Psychological', 'Mystery', 'Thriller', 'Detective'],
                            'psychological_slice_of_life': ['Psychological', 'Slice of Life', 'Drama', 'Adult Cast'],
                            'psychological_school': ['Psychological', 'School', 'Drama', 'Coming-of-Age'],
                            
                            # ROMANCE BRIDGE CATEGORIES
                            'dark_romance': ['Romance', 'Psychological', 'Thriller', 'Drama'],
                            'action_romance': ['Romance', 'Action', 'Adventure', 'Fantasy'],
                            'sci_fi_romance': ['Romance', 'Sci-Fi', 'Space', 'Drama'],
                            'fantasy_romance': ['Romance', 'Fantasy', 'Magic', 'Supernatural'],
                            'historical_romance': ['Romance', 'Historical', 'Drama', 'Period'],
                            'comedy_romance': ['Romance', 'Comedy', 'School', 'Slice of Life'],
                            'music_romance': ['Romance', 'Music', 'Drama', 'Performing Arts'],
                            'supernatural_romance': ['Romance', 'Supernatural', 'Fantasy', 'Drama'],
                            
                            # HORROR/THRILLER BRIDGE CATEGORIES
                            'action_horror': ['Horror', 'Action', 'Supernatural', 'Gore'],
                            'psychological_thriller': ['Thriller', 'Psychological', 'Mystery', 'Suspense'],
                            'sci_fi_horror': ['Horror', 'Sci-Fi', 'Thriller', 'Supernatural'],
                            'supernatural_thriller': ['Thriller', 'Supernatural', 'Mystery', 'Horror'],
                            'school_horror': ['Horror', 'School', 'Supernatural', 'Thriller'],
                            
                            # COMEDY BRIDGE CATEGORIES
                            'action_comedy': ['Comedy', 'Action', 'Adventure', 'Parody'],
                            'romantic_comedy': ['Comedy', 'Romance', 'School', 'Slice of Life'],
                            'fantasy_comedy': ['Comedy', 'Fantasy', 'Magic', 'Parody'],
                            'sci_fi_comedy': ['Comedy', 'Sci-Fi', 'Parody', 'Space'],
                            'school_comedy': ['Comedy', 'School', 'Slice of Life', 'Gag Humor'],
                            'supernatural_comedy': ['Comedy', 'Supernatural', 'Fantasy', 'Parody'],
                            
                            # SCI-FI BRIDGE CATEGORIES
                            'mecha_action': ['Sci-Fi', 'Mecha', 'Action', 'Military'],
                            'cyberpunk_thriller': ['Sci-Fi', 'Cyberpunk', 'Thriller', 'Psychological'],
                            'space_adventure': ['Sci-Fi', 'Space', 'Adventure', 'Action'],
                            'sci_fi_drama': ['Sci-Fi', 'Drama', 'Psychological', 'Philosophy'],
                            'time_travel': ['Sci-Fi', 'Drama', 'Romance', 'Mystery'],
                            
                            # FANTASY BRIDGE CATEGORIES
                            'dark_fantasy': ['Fantasy', 'Horror', 'Supernatural', 'Gore'],
                            'adventure_fantasy': ['Fantasy', 'Adventure', 'Action', 'Magic'],
                            'isekai_adventure': ['Fantasy', 'Isekai', 'Adventure', 'Comedy'],
                            'magical_girl': ['Fantasy', 'Magic', 'Shoujo', 'Action'],
                            'mythology_fantasy': ['Fantasy', 'Mythology', 'Historical', 'Supernatural'],
                            
                            # DRAMA BRIDGE CATEGORIES
                            'slice_of_life_drama': ['Drama', 'Slice of Life', 'Adult Cast', 'Workplace'],
                            'historical_drama': ['Drama', 'Historical', 'Period', 'Romance'],
                            'family_drama': ['Drama', 'Family', 'Slice of Life', 'Coming-of-Age'],
                            'music_drama': ['Drama', 'Music', 'Performing Arts', 'Romance'],
                            'workplace_drama': ['Drama', 'Workplace', 'Adult Cast', 'Seinen'],
                            
                            # SCHOOL/YOUTH BRIDGE CATEGORIES
                            'school_drama': ['School', 'Drama', 'Coming-of-Age', 'Slice of Life'],
                            'school_supernatural': ['School', 'Supernatural', 'Mystery', 'Horror'],
                            'school_romance': ['School', 'Romance', 'Comedy', 'Drama'],
                            'school_competition': ['School', 'Sports', 'Competition', 'Drama'],
                            
                            # MILITARY/WAR BRIDGE CATEGORIES
                            'military_action': ['Military', 'Action', 'War', 'Mecha'],
                            'military_drama': ['Military', 'Drama', 'Historical', 'Tragedy'],
                            'military_sci_fi': ['Military', 'Sci-Fi', 'Mecha', 'Space'],
                            'war_psychological': ['War', 'Psychological', 'Drama', 'Thriller'],
                            
                            # MUSIC/ARTS BRIDGE CATEGORIES
                            'music_drama': ['Music', 'Drama', 'Romance', 'Coming-of-Age'],
                            'music_school': ['Music', 'School', 'Drama', 'Competition'],
                            'performing_arts_drama': ['Performing Arts', 'Drama', 'Romance', 'Competition'],
                            'idol_comedy': ['Idols (Female)', 'Comedy', 'Music', 'Slice of Life'],
                            
                            # MYSTERY BRIDGE CATEGORIES
                            'mystery_horror': ['Mystery', 'Horror', 'Supernatural', 'Thriller'],
                            'mystery_psychological': ['Mystery', 'Psychological', 'Thriller', 'Detective'],
                            'mystery_supernatural': ['Mystery', 'Supernatural', 'Horror', 'Fantasy'],
                            'detective_action': ['Detective', 'Action', 'Mystery', 'Crime'],
                            'school_mystery': ['Mystery', 'School', 'Supernatural', 'Thriller'],
                            
                            # ADVENTURE BRIDGE CATEGORIES
                            'survival_adventure': ['Adventure', 'Survival', 'Thriller', 'Action'],
                            'fantasy_adventure': ['Adventure', 'Fantasy', 'Action', 'Magic'],
                            'space_adventure': ['Adventure', 'Space', 'Sci-Fi', 'Action'],
                            'historical_adventure': ['Adventure', 'Historical', 'Action', 'Drama'],
                            
                            # NICHE BRIDGE CATEGORIES
                            'competitive_gaming': ['Strategy Game', 'Competition', 'Psychological', 'Drama'],
                            'food_culture': ['Gourmet', 'Slice of Life', 'Comedy', 'Drama'],
                            'otaku_culture': ['Otaku Culture', 'Comedy', 'Parody', 'Romance'],
                            'coming_of_age': ['Coming-of-Age', 'Drama', 'School', 'Slice of Life'],
                            'philosophy_existential': ['Philosophy', 'Psychological', 'Drama', 'Existential'],
                            'tournament_battle': ['Tournament', 'Action', 'Competition', 'Super Power'],
                            'team_friendship': ['Team Sports', 'Friendship', 'Drama', 'Coming-of-Age'],
                            'artistic_expression': ['Art', 'Drama', 'Romance', 'Coming-of-Age']
                        }
    
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
    
    def safe_convert(self, value, convert_type=float):
        """Safely convert values handling NaN and invalid data"""
        if value is None or pd.isna(value):
            return None
        try:
            result = convert_type(value)
            if convert_type == float and not np.isfinite(result):
                return None
            return result
        except (ValueError, TypeError, OverflowError):
            return None
    
    def get_anime_tags(self, anime_data):
        """Get combined genres and themes as tags"""
        genres = set(self.parse_list(anime_data.get('genres', '')))
        themes = set(self.parse_list(anime_data.get('themes', '')))
        return genres.union(themes)
    
    def get_genre_groups_for_tags(self, tags):
        """Find which genre groups match the given tags"""
        groups = set()
        for group_name, group_tags in self.genre_groups.items():
            if any(tag in tags for tag in group_tags):
                groups.add(group_name)
        return groups
    
    def calculate_genre_bonus(self, candidate_row, source_anime_list):
        """Calculate genre group overlap bonus (replaces calculate_genre_group_bonus)"""
        candidate_tags = self.get_anime_tags(candidate_row)
        if not candidate_tags:
            return 0.0
        
        candidate_groups = self.get_genre_groups_for_tags(candidate_tags)
        total_bonus = 0.0
        source_group_sets = []
        
        for anime in source_anime_list:
            anime_data = anime['data'] if isinstance(anime, dict) and 'data' in anime else anime
            source_tags = self.get_anime_tags(anime_data)
            source_groups = self.get_genre_groups_for_tags(source_tags)
            source_group_sets.append(source_groups)
            
            # Direct group overlap bonus
            group_overlap = len(candidate_groups.intersection(source_groups))
            if group_overlap > 0:
                total_bonus += group_overlap * 0.1
        
        # Bridge bonus for pairs with different sources
        if len(source_anime_list) == 2:
            source1_groups, source2_groups = source_group_sets
            shared_groups = source1_groups.intersection(source2_groups)
            total_groups = source1_groups.union(source2_groups)
            
            if len(total_groups) > 0:
                dissimilarity = 1.0 - (len(shared_groups) / len(total_groups))
                if dissimilarity > 0.4:
                    connects_both = (len(candidate_groups.intersection(source1_groups)) > 0 and 
                                   len(candidate_groups.intersection(source2_groups)) > 0)
                    
                    if connects_both:
                        bridge_strength = min(len(candidate_groups.intersection(source1_groups)),
                                            len(candidate_groups.intersection(source2_groups)))
                        total_bonus += bridge_strength * 0.3 * dissimilarity
        
        return min(total_bonus, 0.6)  # Cap bonus
    
    def generate_explanation(self, candidate_row, source_anime_list, similarities=None):
        """Generate explanations (combines explain_similarity and generate_detailed_explanation)"""
        explanation_parts = []
        
        candidate_tags = self.get_anime_tags(candidate_row)
        candidate_studios = set(self.parse_list(candidate_row.get('studios', '')))
        candidate_year = candidate_row.get('year')
        candidate_score = candidate_row.get('score')
        candidate_type = candidate_row.get('type')
        
        if len(source_anime_list) > 1:
            # Multi-anime explanations
            source_matches = []
            all_common_tags = set()
            
            for i, anime in enumerate(source_anime_list):
                source_data = anime['data'] if isinstance(anime, dict) and 'data' in anime else anime
                source_tags = self.get_anime_tags(source_data)
                source_title = source_data.get('title', 'Unknown')
                
                common_tags = candidate_tags & source_tags
                
                if similarities and i < len(similarities) and similarities[i] > 0.2:
                    match_reasons = []
                    
                    if common_tags:
                        all_common_tags.update(common_tags)
                        if len(common_tags) >= 2:
                            match_reasons.append(f"shares {', '.join(list(common_tags)[:2])}")
                        else:
                            match_reasons.append(f"shares {list(common_tags)[0]}")
                    
                    source_studios = set(self.parse_list(source_data.get('studios', '')))
                    if candidate_studios & source_studios:
                        match_reasons.append("same studio")
                    
                    source_year = source_data.get('year')
                    if (pd.notna(candidate_year) and pd.notna(source_year) and 
                        abs(int(candidate_year) - int(source_year)) <= 3):
                        match_reasons.append("similar era")
                    
                    if match_reasons:
                        source_matches.append(f"matches {source_title[:20]} ({', '.join(match_reasons[:2])})")
            
            if len(source_matches) >= 2:
                explanation_parts.append(f"Appeals to multiple selections: {'; '.join(source_matches[:2])}")
            elif source_matches:
                explanation_parts.append(source_matches[0])
            
            if len(all_common_tags) >= 2:
                explanation_parts.append(f"Bridges {', '.join(list(all_common_tags)[:3])} themes across your selection")
            elif all_common_tags:
                explanation_parts.append(f"Common {list(all_common_tags)[0]} elements")
        else:
            # Single anime explanations
            source_data = source_anime_list[0]['data'] if source_anime_list else {}
            source_tags = self.get_anime_tags(source_data)
            source_studios = set(self.parse_list(source_data.get('studios', '')))
            
            # Genre/theme analysis
            common_tags = candidate_tags & source_tags
            if common_tags:
                if len(common_tags) >= 3:
                    explanation_parts.append(f"Shares {len(common_tags)} themes: {', '.join(list(common_tags)[:3])}")
                elif len(common_tags) == 2:
                    explanation_parts.append(f"Common themes: {', '.join(common_tags)}")
                else:
                    explanation_parts.append(f"Same {list(common_tags)[0]} theme")
            
            # Other connections
            common_studios = candidate_studios & source_studios
            if common_studios:
                explanation_parts.append(f"Same studio: {list(common_studios)[0]}")
            
            # Year proximity
            source_year = source_data.get('year')
            if pd.notna(candidate_year) and pd.notna(source_year):
                year_diff = abs(int(candidate_year) - int(source_year))
                if year_diff <= 2:
                    explanation_parts.append(f"Same period ({int(candidate_year)})")
                elif year_diff <= 5:
                    explanation_parts.append("Similar time period")
            
            # Score tier analysis
            source_score = source_data.get('score')
            if pd.notna(candidate_score) and pd.notna(source_score):
                if candidate_score >= 8.5 and source_score >= 8.5:
                    explanation_parts.append("Both highly acclaimed (8.5+)")
                elif candidate_score >= 8.0 and source_score >= 8.0:
                    explanation_parts.append("Both well-rated (8.0+)")
                elif abs(candidate_score - source_score) <= 0.5:
                    explanation_parts.append("Similar rating level")
            
            # Format similarity
            source_type = source_data.get('type')
            if candidate_type == source_type and candidate_type in ['Movie', 'TV', 'OVA']:
                explanation_parts.append(f"Both {candidate_type} format")
        
        return "; ".join(explanation_parts) if explanation_parts else "Similar content profile and viewing appeal"
    
    def get_image_urls(self, mal_id, anime_df):
        """Extract image URLs from anime dataframe"""
        anime_row = anime_df[anime_df['mal_id'] == mal_id]
        if anime_row.empty:
            return None, None
        
        images_data = anime_row.iloc[0].get('images')
        if pd.notna(images_data):
            try:
                images_dict = json.loads(images_data) if isinstance(images_data, str) else images_data
                
                if isinstance(images_dict, dict):
                    for format_type in ['webp', 'jpg']:
                        if format_type in images_dict and isinstance(images_dict[format_type], dict):
                            image_url = (images_dict[format_type].get('large_image_url') or 
                                       images_dict[format_type].get('image_url'))
                            thumbnail_url = images_dict[format_type].get('small_image_url')
                            return image_url, thumbnail_url
            except:
                pass
        return None, None
    
    def recommend(self, anime_id, top_k=10, min_score=None, include_sequels=True, explain=False):
        """Single anime recommendation"""
        if anime_id not in self.df['mal_id'].values:
            return {"error": "Anime not found"}
        
        source_idx = self.df[self.df['mal_id'] == anime_id].index[0]
        source_anime = self.df.iloc[source_idx]
        
        similarities = cosine_similarity([self.features[source_idx]], self.features)[0]
        similarities = np.nan_to_num(similarities, nan=0.0, posinf=1.0, neginf=0.0)
        
        # Filter candidates
        results_df = self.df.copy()
        results_df['similarity'] = similarities
        results_df = results_df[results_df['mal_id'] != anime_id]
        
        if min_score is not None:
            results_df = results_df[(results_df['score'] >= min_score) & results_df['score'].notna()]
        
        valid_anime = [{'data': source_anime}]
    
        if not include_sequels:
            filtered_indices = []
            for idx in results_df.index:
                row = self.df.iloc[idx]
                if not self.is_sequel_or_related(row, valid_anime):
                    filtered_indices.append(idx)
            results_df = results_df.loc[filtered_indices]
    
        if len(results_df) == 0:
            return {
                'source': self._format_source_anime(source_anime),
                'recommendations': [],
                'filters_applied': {'min_score': min_score, 'include_sequels': include_sequels, 'explain': explain}
            }
        
        sim_indices = results_df.nlargest(min(top_k, len(results_df)), 'similarity').index
        
        recommendations = []
        for idx in sim_indices:
            row = self.df.iloc[idx]
            similarity_val = results_df.loc[idx, 'similarity']
            
            if not np.isfinite(similarity_val):
                similarity_val = 0.0
            
            synopsis = str(row.get('synopsis', '')) if pd.notna(row.get('synopsis')) else ''
            rec_item = {
                'mal_id': self.safe_convert(row['mal_id'], int),
                'title': str(row['title']),
                'title_english': str(row.get('title_english', '')),
                'score': self.safe_convert(row['score']),
                'similarity': float(similarity_val),
                'type': str(row.get('type', '')),
                'episodes': self.safe_convert(row['episodes'], int),
                'year': self.safe_convert(row['year'], int),
                'synopsis': synopsis[:200] + "..." if synopsis and len(synopsis) > 200 else synopsis
            }
            
            if explain:
                rec_item['explanation'] = self.generate_explanation(row, [{'data': source_anime}])
            
            recommendations.append(rec_item)
        
        return {
            'source': self._format_source_anime(source_anime),
            'recommendations': recommendations,
            'filters_applied': {'min_score': min_score, 'include_sequels': include_sequels, 'explain': explain}
        }
        
    def is_sequel_or_related(self, candidate_row, source_anime_list):
        """Simple check: if candidate appears in any source anime's relations, filter it out"""
        candidate_mal_id = candidate_row.get('mal_id')
        if pd.isna(candidate_mal_id):
            return False
        
        try:
            candidate_mal_id = int(candidate_mal_id)
        except:
            return False
        
        for anime in source_anime_list:
            if isinstance(anime, dict) and 'data' in anime:
                source_data = anime['data']
            else:
                source_data = anime
            
            relations = source_data.get('relations')
            
            if relations is None or pd.isna(relations) or relations == '' or relations == '[]':
                continue
            
            try:
                relations_data = json.loads(relations)
                
                for relation in relations_data:
                    if 'entry' in relation:
                        for entry in relation['entry']:
                            entry_mal_id = entry.get('mal_id')
                            if entry_mal_id is not None:
                                try:
                                    if int(entry_mal_id) == candidate_mal_id:
                                        return True
                                except:
                                    continue
            except Exception as e:
                continue
        
        return False
    
    def multi_recommend(self, anime_ids, top_k=20, min_score=None, include_sequels=True, explain=False, diversity_weight=0.0):
        """Multi-anime recommendation"""
        if not anime_ids or len(anime_ids) > 20:
            return {"error": "Invalid anime IDs (must be 1-20)"}
        valid_anime = []
        for anime_id in anime_ids:
            if anime_id in self.df['mal_id'].values:
                source_idx = self.df[self.df['mal_id'] == anime_id].index[0]
                valid_anime.append({
                    'id': anime_id,
                    'data': self.df.iloc[source_idx],
                    'features': self.features[source_idx],
                    'index': source_idx
                })
        
        if not valid_anime:
            return {"error": "No valid anime found in selection"}
        
        selected_mal_ids = [anime['id'] for anime in valid_anime]
        
        individual_recs = {}
        
        for i, source_anime in enumerate(valid_anime):
            similarities = cosine_similarity([source_anime['features']], self.features)[0]
            similarities = np.nan_to_num(similarities, nan=0.0, posinf=1.0, neginf=0.0)
            
            candidate_indices = np.argsort(similarities)[::-1]
            
            rank = 0
            for idx in candidate_indices:
                if rank >= top_k * 3:
                    break
                
                mal_id = self.df.iloc[idx]['mal_id']
                
                if mal_id in selected_mal_ids:
                    continue
                
                row = self.df.iloc[idx]
                if min_score is not None and (pd.isna(row['score']) or row['score'] < min_score):
                    continue
                
                if not include_sequels:
                    if self.is_sequel_or_related(row, valid_anime):
                        continue
                
                similarity_score = similarities[idx]
                if similarity_score < 0.15:
                    continue
                
                if mal_id not in individual_recs:
                    individual_recs[mal_id] = {
                        'data': row,
                        'index': idx,
                        'source_similarities': {},
                        'source_ranks': {}
                    }
                
                individual_recs[mal_id]['source_similarities'][i] = similarity_score
                individual_recs[mal_id]['source_ranks'][i] = rank
                rank += 1
        
        # Score and rank final candidates
        final_candidates = []
        
        for mal_id, rec_data in individual_recs.items():
            similarities = []
            for i in range(len(valid_anime)):
                similarities.append(rec_data['source_similarities'].get(i, 0))
            
            avg_similarity = np.mean(similarities)
            min_similarity = min(similarities)
            max_similarity = max(similarities)
            strong_recommendations = sum(1 for s in similarities if s > 0.25)
            
            # Calculate genre bonus
            genre_bonus = self.calculate_genre_bonus(rec_data['data'], valid_anime)
            
            # Enhanced scoring
            if len(valid_anime) == 2:
                base_score = avg_similarity * 1.2
                if genre_bonus > 0.3:
                    final_score = base_score * 1.5 + genre_bonus
                elif genre_bonus > 0.15:
                    final_score = base_score * 1.3 + genre_bonus
                elif min_similarity > 0.2:
                    final_score = base_score * 1.4
                else:
                    final_score = (max_similarity * 0.8 + avg_similarity * 0.5) + genre_bonus
            else:
                proportion_recommending = strong_recommendations / len(valid_anime)
                base_score = avg_similarity * (0.7 + 0.5 * proportion_recommending)
                final_score = base_score + genre_bonus
            
            final_candidates.append({
                'mal_id': mal_id,
                'final_score': final_score,
                'avg_similarity': avg_similarity,
                'min_similarity': min_similarity,
                'max_similarity': max_similarity,
                'similarities': similarities,
                'strong_recommendations': strong_recommendations,
                'genre_bonus': genre_bonus,
                'data': rec_data['data'],
                'index': rec_data['index']
            })
        
        # Sort and balance results
        final_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Apply bridge content balancing for multiple sources
        if len(valid_anime) >= 2:
            bridge_candidates = [c for c in final_candidates if c['genre_bonus'] > 0.2]
            regular_candidates = [c for c in final_candidates if c['genre_bonus'] <= 0.2]
            
            bridge_count = min(len(bridge_candidates), int(top_k * 0.4))
            selected_recommendations = bridge_candidates[:bridge_count]
            
            remaining_slots = top_k - len(selected_recommendations)
            if remaining_slots > 0:
                source_groups = {i: [] for i in range(len(valid_anime))}
                taken_ids = {c['mal_id'] for c in selected_recommendations}
                
                for candidate in regular_candidates:
                    if candidate['mal_id'] not in taken_ids:
                        best_source_idx = candidate['similarities'].index(max(candidate['similarities']))
                        source_groups[best_source_idx].append(candidate)
                
                per_source = max(1, remaining_slots // len(valid_anime))
                remainder = remaining_slots % len(valid_anime)
                
                for i, candidates in source_groups.items():
                    take_count = per_source + (1 if i < remainder else 0)
                    selected_recommendations.extend(candidates[:take_count])
            
            final_candidates = selected_recommendations[:top_k]
        
        # Apply diversity penalty
        if diversity_weight > 0:
            for candidate in final_candidates:
                penalty = 0
                for anime in valid_anime:
                    if self.is_sequel_or_related(candidate['data'], [anime]):
                        penalty += diversity_weight
                candidate['final_score'] = max(0, candidate['final_score'] - penalty)
            
            final_candidates.sort(key=lambda x: x['final_score'], reverse=True)
        
        # Build response
        recommendations = []
        for candidate in final_candidates[:top_k]:
            row = candidate['data']
            synopsis = str(row.get('synopsis', '')) if pd.notna(row.get('synopsis')) else ''
            
            rec_item = {
                'mal_id': self.safe_convert(row['mal_id'], int),
                'title': str(row['title']),
                'title_english': str(row.get('title_english', '')),
                'score': self.safe_convert(row['score']),
                'similarity': self.safe_convert(candidate['final_score']),
                'avg_similarity': self.safe_convert(candidate['avg_similarity']),
                'min_similarity': self.safe_convert(candidate['min_similarity']),
                'max_similarity': self.safe_convert(candidate['max_similarity']),
                'individual_similarities': [self.safe_convert(s) for s in candidate['similarities']],
                'strong_recommendations': candidate['strong_recommendations'],
                'type': str(row.get('type', '')),
                'episodes': self.safe_convert(row['episodes'], int),
                'year': self.safe_convert(row['year'], int),
                'synopsis': synopsis[:200] + "..." if synopsis and len(synopsis) > 200 else synopsis
            }
            
            if explain:
                rec_item['explanation'] = self.generate_explanation(row, valid_anime, candidate['similarities'])
                rec_item['genre_bonus'] = self.safe_convert(candidate.get('genre_bonus', 0))
            
            recommendations.append(rec_item)
        
        source_anime_list = []
        for anime in valid_anime:
            source_anime_list.append({
                'mal_id': self.safe_convert(anime['data']['mal_id'], int),
                'title': str(anime['data']['title']),
                'score': self.safe_convert(anime['data']['score'])
            })
        
        return {
            'source_anime': source_anime_list,
            'recommendations': recommendations,
            'method': 'balanced_individual_recs',
            'total_candidates_considered': len(individual_recs),
            'filters_applied': {
                'min_score': min_score,
                'include_sequels': include_sequels,
                'explain': explain,
                'diversity_weight': diversity_weight
            }
        }
    
    def _format_source_anime(self, source_anime):
        """Format source anime data"""
        return {
            'mal_id': self.safe_convert(source_anime['mal_id'], int),
            'title': str(source_anime['title']),
            'title_english': str(source_anime.get('title_english', '')),
            'score': self.safe_convert(source_anime['score'])
        }

def load_recommender():
    global recommender
    if recommender is not None:
        return recommender
    
    model_files = [
        "anime_recommender_advanced.pkl.gz",
        "anime_recommender_advanced.pkl", 
        "backend/anime_recommender_advanced.pkl.gz",
        "backend/anime_recommender_advanced.pkl"
    ]
    
    for model_file in model_files:
        if os.path.exists(model_file):
            try:
                with (gzip.open(model_file, "rb") if model_file.endswith('.gz') else open(model_file, "rb")) as f:
                    model_data = pickle.load(f)
                
                recommender = AnimeRecommender(model_data)
                print(f"✓ Recommender model loaded from {model_file}")
                return recommender
                
            except Exception as e:
                print(f"Failed to load {model_file}: {e}")
                continue
    
    print("Warning: No recommender model found")
    return None

@app.get("/anime/{anime_id}/recommend")
def get_anime_recommendations(anime_id: int, limit: int = 10, min_score: float = None, 
                            include_sequels: bool = True, explain: bool = False):
    """Get anime recommendations based on trained model"""
    rec = load_recommender()
    if rec is None:
        raise HTTPException(status_code=503, detail="Recommendation model not available")
    
    result = rec.recommend(anime_id, top_k=limit, min_score=min_score, 
                          include_sequels=include_sequels, explain=explain)
    
    if "error" in result:
        status = 404 if "not found" in result["error"].lower() else 500
        raise HTTPException(status_code=status, detail=result["error"])
    
    # Add image URLs to recommendations
    for rec_item in result['recommendations']:
        image_url, thumbnail_url = rec.get_image_urls(rec_item['mal_id'], anime_df)
        rec_item.update({'image_url': image_url, 'thumbnail_url': thumbnail_url})
    
    # Add image URLs to source
    source_image_url, source_thumbnail_url = rec.get_image_urls(result['source']['mal_id'], anime_df)
    result['source'].update({'image_url': source_image_url, 'thumbnail_url': source_thumbnail_url})
    
    return {
        "source": result['source'],
        "recommendations": result['recommendations'],
        "count": len(result['recommendations']),
        "filters_applied": result.get('filters_applied', {})
    }

@app.post("/anime/multi-recommend")
def get_multi_anime_recommendations(request: Dict[str, Any]):
    """Generate balanced recommendations from multiple anime"""
    anime_ids = request.get('anime_ids', [])
    top_k = request.get('top_k', 20)
    min_score = request.get('min_score', None)
    include_sequels = request.get('include_sequels', True)
    explain = request.get('explain', False)
    diversity_weight = request.get('diversity_weight', 0.0)

    print(f"Multi-recommend request: include_sequels={include_sequels}, anime_ids={anime_ids}")

    rec = load_recommender()
    if not rec:
        return {"error": "Recommender not available"}
    
    try:
        result = rec.multi_recommend(anime_ids, top_k=top_k, min_score=min_score,
                                   include_sequels=include_sequels, explain=explain,
                                   diversity_weight=diversity_weight)
        
        if "error" in result:
            return result
        
        for rec_item in result['recommendations']:
            image_url, thumbnail_url = rec.get_image_urls(rec_item['mal_id'], anime_df)
            rec_item.update({'image_url': image_url, 'thumbnail_url': thumbnail_url})
        
        for source in result['source_anime']:
            image_url, thumbnail_url = rec.get_image_urls(source['mal_id'], anime_df)
            source.update({'image_url': image_url, 'thumbnail_url': thumbnail_url})
        
        return result
        
    except Exception as e:
        print(f"Multi-recommend error: {str(e)}")
        return {"error": f"Recommendation failed: {str(e)}"}