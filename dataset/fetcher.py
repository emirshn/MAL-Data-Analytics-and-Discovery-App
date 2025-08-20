import requests
import json

def fetch_anime_jikan(anime_id):
    url = f"https://api.jikan.moe/v4/anime/{anime_id}/full"  # full endpoint
    res = requests.get(url)
    if res.status_code != 200:
        raise Exception(f"Error fetching anime {anime_id}: {res.status_code}")
    data = res.json().get("data", {})

    # Flatten helper
    def flatten_list(items):
        return [{"mal_id": i.get("mal_id"), "type": i.get("type"), "name": i.get("name"), "url": i.get("url")} for i in items] if items else []

    # Flatten relations
    relations = []
    for r in data.get("relations") or []:
        relation_type = r.get("relation")
        entries = flatten_list(r.get("entry"))
        relations.append({"relation": relation_type, "entry": entries})

    result = {
        "mal_id": data.get("mal_id"),
        "url": data.get("url"),
        "images": data.get("images"),
        "trailer": data.get("trailer"),
        "titles": data.get("titles"),
        "title": data.get("title"),
        "title_english": data.get("title_english"),
        "title_japanese": data.get("title_japanese"),
        "title_synonyms": data.get("title_synonyms"),
        "type": data.get("type"),
        "source": data.get("source"),
        "episodes": data.get("episodes"),
        "status": data.get("status"),
        "airing": data.get("airing"),
        "aired": data.get("aired"),
        "duration": data.get("duration"),
        "rating": data.get("rating"),
        "score": data.get("score"),
        "scored_by": data.get("scored_by"),
        "rank": data.get("rank"),
        "popularity": data.get("popularity"),
        "members": data.get("members"),
        "favorites": data.get("favorites"),
        "synopsis": data.get("synopsis"),
        "background": data.get("background"),
        "season": data.get("season"),
        "year": data.get("year"),
        "broadcast": data.get("broadcast"),
        "producers": flatten_list(data.get("producers")),
        "licensors": flatten_list(data.get("licensors")),
        "studios": flatten_list(data.get("studios")),
        "genres": flatten_list(data.get("genres")),
        "explicit_genres": flatten_list(data.get("explicit_genres")),
        "themes": flatten_list(data.get("themes")),
        "demographics": flatten_list(data.get("demographics")),
        "relations": relations,
        "theme": {
            "openings": data.get("theme", {}).get("openings", []),
            "endings": data.get("theme", {}).get("endings", [])
        },
        "external": data.get("external"),
        "streaming": data.get("streaming")
    }

    return result

if __name__ == "__main__":
    anime_id = 5114  
    anime_data = fetch_anime_jikan(anime_id)
    print(json.dumps(anime_data, indent=2, ensure_ascii=False))
