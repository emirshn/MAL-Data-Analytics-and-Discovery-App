import pandas as pd

# Input / output CSV paths
INPUT_CSV = "manga_jikan_all_new.csv"
OUTPUT_CSV = "manga_jikan_all_new.csv"

# Load CSV
df = pd.read_csv(INPUT_CSV)

# Inspect possible hentai indicators
print("Available columns:", df.columns.tolist())

# Common columns: "genres", "explicit_genres", "themes", "demographics"
# Drop rows that contain hentai in genres/explicit_genres
def is_hentai(value):
    if pd.isna(value):
        return False
    return "hentai" in str(value).lower()

# Apply filter
mask = df.apply(lambda row: is_hentai(row.get("genres", "")) 
                            or is_hentai(row.get("explicit_genres", "")), axis=1)

print(f"Found {mask.sum()} hentai rows, removing...")

# Keep only non-hentai
df_clean = df[~mask].reset_index(drop=True)

# Save to new CSV
df_clean.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")

print(f"✅ Saved cleaned dataset to {OUTPUT_CSV}, total rows: {len(df_clean)}")
