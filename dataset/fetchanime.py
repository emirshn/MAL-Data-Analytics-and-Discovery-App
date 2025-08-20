import aiohttp
import asyncio
import pandas as pd
import json
import os
import random
import re

ANIME_CSV = "anime_jikan_all_new.csv"
LIST_URL = "https://api.jikan.moe/v4/anime"
DETAIL_URL = "https://api.jikan.moe/v4/anime/{id}/full"
PAGE_SIZE = 25  
MAX_CONCURRENT = 5
RETRY_LIMIT = 5

ANIME_FIELDS = [
    "mal_id","url","title","title_english","title_japanese","title_synonyms",
    "type","source","episodes","status","airing","aired_from","aired_to",
    "duration","rating","score","scored_by","rank","popularity","members","favorites",
    "synopsis","background","season","year",
    "broadcast_day","broadcast_time","broadcast_timezone",
    "producers","licensors","studios","genres","explicit_genres","themes","demographics",
    "relations","openings","endings","external","streaming","images","trailer"
]

def flatten(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[\r\n]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def parse_anime(data):
    return {
        "mal_id": data.get("mal_id"),
        "url": data.get("url"),
        "title": data.get("title"),
        "title_english": data.get("title_english"),
        "title_japanese": data.get("title_japanese"),
        "title_synonyms": json.dumps(data.get("title_synonyms", []), ensure_ascii=False),
        "type": data.get("type"),
        "source": data.get("source"),
        "episodes": data.get("episodes"),
        "status": data.get("status"),
        "airing": data.get("airing"),
        "aired_from": data.get("aired", {}).get("from"),
        "aired_to": data.get("aired", {}).get("to"),
        "duration": data.get("duration"),
        "rating": data.get("rating"),
        "score": data.get("score"),
        "scored_by": data.get("scored_by"),
        "rank": data.get("rank"),
        "popularity": data.get("popularity"),
        "members": data.get("members"),
        "favorites": data.get("favorites"),
        "synopsis": flatten(data.get("synopsis")),
        "background": flatten(data.get("background")),
        "season": data.get("season"),
        "year": data.get("year"),
        "broadcast_day": data.get("broadcast", {}).get("day"),
        "broadcast_time": data.get("broadcast", {}).get("time"),
        "broadcast_timezone": data.get("broadcast", {}).get("timezone"),
        "producers": json.dumps(data.get("producers", []), ensure_ascii=False),
        "licensors": json.dumps(data.get("licensors", []), ensure_ascii=False),
        "studios": json.dumps(data.get("studios", []), ensure_ascii=False),
        "genres": json.dumps(data.get("genres", []), ensure_ascii=False),
        "explicit_genres": json.dumps(data.get("explicit_genres", []), ensure_ascii=False),
        "themes": json.dumps(data.get("themes", []), ensure_ascii=False),
        "demographics": json.dumps(data.get("demographics", []), ensure_ascii=False),
        "relations": json.dumps(data.get("relations", []), ensure_ascii=False),
        "openings": json.dumps(data.get("theme", {}).get("openings", []), ensure_ascii=False),
        "endings": json.dumps(data.get("theme", {}).get("endings", []), ensure_ascii=False),
        "external": json.dumps(data.get("external", []), ensure_ascii=False),
        "streaming": json.dumps(data.get("streaming", []), ensure_ascii=False),
        "images": json.dumps(data.get("images", {}), ensure_ascii=False),
        "trailer": json.dumps(data.get("trailer", {}), ensure_ascii=False),
    }

def save_to_csv(anime_list, csv_file=ANIME_CSV):
    if not anime_list:
        return
    df = pd.DataFrame(anime_list, columns=ANIME_FIELDS)
    file_exists = os.path.exists(csv_file)
    file_nonempty = file_exists and os.path.getsize(csv_file) > 0
    df.to_csv(
        csv_file,
        mode="a" if file_exists else "w",
        header=not file_nonempty,
        index=False,
        encoding="utf-8-sig",
    )

def read_ids(csv_path: str) -> set[int]:
    if not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0:
        return set()
    try:
        df = pd.read_csv(csv_path, usecols=["mal_id"])
        return set(pd.to_numeric(df["mal_id"], errors="coerce").dropna().astype(int))
    except Exception:
        df = pd.read_csv(csv_path, header=None, usecols=[0])
        col = df.columns[0]
        return set(pd.to_numeric(df[col], errors="coerce").dropna().astype(int))

# --- Async fetch functions ---
async def fetch_detail(session, sem, anime_id):
    url = DETAIL_URL.format(id=anime_id)
    retries = 0
    async with sem:
        while retries < RETRY_LIMIT:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        data = (await resp.json()).get("data")
                        if data:
                            print(f"✅ {anime_id}: {data.get('title')}")
                            return parse_anime(data)
                        return None
                    elif resp.status == 404:
                        return None
                    elif resp.status == 429:
                        wait_time = min(60, 2 ** retries + random.random())
                        print(f"⏳ Rate limited ID {anime_id}, retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
                    else:
                        wait_time = 3 + random.random()
                        print(f"⚠ HTTP {resp.status} for ID {anime_id}, retrying in {wait_time:.1f}s")
                        await asyncio.sleep(wait_time)
            except Exception as e:
                wait_time = 3 + random.random()
                print(f"❌ Exception on ID {anime_id}: {e}, retrying in {wait_time:.1f}s")
                await asyncio.sleep(wait_time)
            retries += 1
    return None

async def fetch_list_page(session, page, retries=0):
    url = f"{LIST_URL}?page={page}&limit={PAGE_SIZE}&order_by=mal_id&sort=asc"
    try:
        async with session.get(url) as resp:
            if resp.status == 200:
                return await resp.json()
            elif resp.status == 429:
                if retries < RETRY_LIMIT:
                    wait = min(60, 2 ** retries + random.random())
                    print(f"⏳ Rate limited on page {page}, retrying in {wait:.1f}s")
                    await asyncio.sleep(wait)
                    return await fetch_list_page(session, page, retries + 1)
                else:
                    print(f"❌ Page {page} failed after {RETRY_LIMIT} retries (429)")
            else:
                print(f"⚠ HTTP {resp.status} on page {page}, retrying in 3s")
                await asyncio.sleep(3 + random.random())
                if retries < RETRY_LIMIT:
                    return await fetch_list_page(session, page, retries + 1)
    except Exception as e:
        print(f"❌ Exception fetching page {page}: {e}, retrying in 3s")
        await asyncio.sleep(3 + random.random())
        if retries < RETRY_LIMIT:
            return await fetch_list_page(session, page, retries + 1)
    return None

async def crawl_all_anime():
    existing_ids = read_ids(ANIME_CSV)
    print(f"🔄 Already have {len(existing_ids)} anime entries")

    sem = asyncio.Semaphore(MAX_CONCURRENT)

    async with aiohttp.ClientSession() as session:
        page = 1
        while True:
            payload = await fetch_list_page(session, page)
            if not payload:
                print("❌ Failed to fetch page, stopping crawler")
                break

            data = payload.get("data", [])
            if not data:
                print("✅ No more data, finished crawling")
                break

            ids_to_fetch = [a["mal_id"] for a in data if a["mal_id"] not in existing_ids]
            if not ids_to_fetch:
                print(f"⏭️ Page {page}: all {len(data)} already in CSV")
                page += 1
                continue

            tasks = [fetch_detail(session, sem, aid) for aid in ids_to_fetch]
            results = []
            for task in asyncio.as_completed(tasks):
                res = await task
                if res:
                    results.append(res)

            if results:
                save_to_csv(results)
                existing_ids.update([r["mal_id"] for r in results])
                print(f"💾 Saved {len(results)} entries from page {page}")

            page += 1
            await asyncio.sleep(random.uniform(0.5, 1.5)) 

if __name__ == "__main__":
    asyncio.run(crawl_all_anime())
