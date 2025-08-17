import aiohttp
import asyncio
import pandas as pd
import json
import os
import random
import re

ANIME_CSV = "anime_jikan_all_new.csv"
MANGA_CSV = "manga_jikan_all_new.csv"
BASE_URL = "https://api.jikan.moe/v4/manga"
MAX_ID = 70000
BATCH_SIZE = 50
MAX_CONCURRENT = 5
RETRY_LIMIT = 5

# --- Utils ---
def flatten(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# --- Mapping function for manga ---
def parse_manga(data):
    return {
        "mal_id": data.get("mal_id"),
        "url": data.get("url"),
        "title": data.get("title"),
        "title_english": data.get("title_english"),
        "title_japanese": data.get("title_japanese"),
        "title_synonyms": json.dumps(data.get("title_synonyms", []), ensure_ascii=False),
        "type": data.get("type"),
        "chapters": data.get("chapters"),
        "volumes": data.get("volumes"),
        "status": data.get("status"),
        "publishing": data.get("publishing"),
        "published_from": data.get("published", {}).get("from"),
        "published_to": data.get("published", {}).get("to"),
        "score": data.get("score"),
        "scored_by": data.get("scored_by"),
        "rank": data.get("rank"),
        "popularity": data.get("popularity"),
        "members": data.get("members"),
        "favorites": data.get("favorites"),
        "synopsis": flatten(data.get("synopsis")),
        "background": flatten(data.get("background")),
        "authors": json.dumps(data.get("authors", []), ensure_ascii=False),
        "serializations": json.dumps(data.get("serializations", []), ensure_ascii=False),
        "genres": json.dumps(data.get("genres", []), ensure_ascii=False),
        "explicit_genres": json.dumps(data.get("explicit_genres", []), ensure_ascii=False),
        "themes": json.dumps(data.get("themes", []), ensure_ascii=False),
        "demographics": json.dumps(data.get("demographics", []), ensure_ascii=False),
        "relations": json.dumps(data.get("relations", []), ensure_ascii=False),
        "external": json.dumps(data.get("external", []), ensure_ascii=False),
        "images": json.dumps(data.get("images", {}), ensure_ascii=False),
    }

# --- CSV utilities ---
def save_to_csv(manga_list, csv_file=MANGA_CSV):
    if not manga_list:
        return
    df = pd.DataFrame(manga_list)
    write_header = not os.path.exists(csv_file)
    df.to_csv(csv_file, mode="a", header=write_header, index=False, encoding="utf-8-sig")

def load_existing_ids():
    anime_ids, manga_ids = set(), set()
    if os.path.exists(ANIME_CSV):
        df_anime = pd.read_csv(ANIME_CSV, usecols=["mal_id"])
        anime_ids.update(df_anime["mal_id"].dropna().astype(int).tolist())
    if os.path.exists(MANGA_CSV):
        df_manga = pd.read_csv(MANGA_CSV, usecols=["mal_id"])
        manga_ids.update(df_manga["mal_id"].dropna().astype(int).tolist())
    return anime_ids, manga_ids

# --- Async fetch function ---
async def fetch_manga(session, sem, manga_id):
    url = f"{BASE_URL}/{manga_id}/full"
    retries = 0
    async with sem:
        while retries < RETRY_LIMIT:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = (await resp.json()).get("data")
                        if data:
                            print(f"✅ ID {manga_id}: {data.get('title')}")
                            return parse_manga(data)
                        return None
                    elif resp.status == 404:
                        return None
                    elif resp.status == 429:
                        wait_time = min(60, 2 ** retries + random.random())
                        print(f"⏳ Rate limited ID {manga_id}, retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                    else:
                        wait_time = 3 + random.random()
                        print(f"⚠ HTTP {resp.status} for ID {manga_id}, retry in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
            except Exception as e:
                wait_time = 3 + random.random()
                print(f"❌ Exception on ID {manga_id}: {e}, retry in {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            retries += 1
    print(f"❌ Failed ID {manga_id} after {RETRY_LIMIT} retries")
    return None

# --- Main crawler ---
async def crawl_all_manga():
    anime_ids, manga_ids = load_existing_ids()
    print(f"🔄 Already have {len(anime_ids)} anime and {len(manga_ids)} manga entries")

    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        for batch_start in range(1, MAX_ID + 1, BATCH_SIZE):
            batch_end = min(batch_start + BATCH_SIZE - 1, MAX_ID)

            tasks = []
            for manga_id in range(batch_start, batch_end + 1):
                if manga_id in anime_ids:
                    print(f"⏭️ Skipping ID {manga_id} (already in anime)")
                    continue
                if manga_id in manga_ids:
                    print(f"⏭️ Skipping ID {manga_id} (already in manga)")
                    continue
                tasks.append(fetch_manga(session, sem, manga_id))

            results = []
            for task in asyncio.as_completed(tasks):
                res = await task
                if res:
                    results.append(res)

            if results:
                save_to_csv(results)
                manga_ids.update([r["mal_id"] for r in results])
                print(f"💾 Saved {len(results)} entries (up to ID {batch_end})")

if __name__ == "__main__":
    asyncio.run(crawl_all_manga())
