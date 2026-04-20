"""
01_acquire_usfs.py
Downloads the USFS Fire Occurrence Database (SQLite), filters to California
records, and exports a cleaned CSV to /data/usfs_california.csv.

Source: https://www.fs.usda.gov/rds/archive/Catalog/RDS-2013-0009.6
"""

import os
import sqlite3
import zipfile
import requests
import pandas as pd

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR   = "data"
ZIP_URL    = "https://www.fs.usda.gov/rds/archive/products/RDS-2013-0009.6/RDS-2013-0009.6_SQLITE.zip"
ZIP_PATH   = os.path.join(DATA_DIR, "usfs_fires.zip")
DB_PATH    = os.path.join(DATA_DIR, "FPA_FOD_20221014.sqlite")
OUT_PATH   = os.path.join(DATA_DIR, "usfs_california.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# ── Download ──────────────────────────────────────────────────────────────────
if not os.path.exists(DB_PATH):
    print("Downloading USFS Fire Occurrence Database (~175 MB)...")
    response = requests.get(ZIP_URL, stream=True)
    response.raise_for_status()
    with open(ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete. Extracting...")
    with zipfile.ZipFile(ZIP_PATH, "r") as z:
        z.extractall(DATA_DIR)
    print("Extraction complete.")
else:
    print(f"Database already exists at {DB_PATH}, skipping download.")

# ── Query ─────────────────────────────────────────────────────────────────────
print("Connecting to SQLite database...")
conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    FOD_ID                          AS id,
    FPA_ID                          AS fpa_id,
    FIRE_YEAR                       AS fire_year,
    DISCOVERY_DATE                  AS discovery_date,
    DISCOVERY_DOY                   AS discovery_doy,
    STAT_CAUSE_DESCR                AS cause,
    FIRE_SIZE                       AS size_acres,
    FIRE_SIZE_CLASS                 AS size_class_usfs,
    LATITUDE                        AS latitude,
    LONGITUDE                       AS longitude,
    STATE                           AS state,
    COUNTY                          AS county,
    FIPS_NAME                       AS county_name,
    OWNER_DESCR                     AS agency
FROM Fires
WHERE STATE = 'CA'
  AND FIRE_YEAR >= 2000
  AND LATITUDE IS NOT NULL
  AND LONGITUDE IS NOT NULL
  AND FIRE_SIZE IS NOT NULL
"""

print("Querying California fires from 2000 onward...")
df = pd.read_sql_query(query, conn)
conn.close()

print(f"Records retrieved: {len(df):,}")

# ── Assign size class labels ──────────────────────────────────────────────────
def assign_size_class(acres):
    if acres < 100:
        return "small"
    elif acres < 1000:
        return "medium"
    else:
        return "large"

df["size_class"] = df["size_acres"].apply(assign_size_class)
df["source"]     = "usfs"

# ── Convert discovery date from Julian to ISO ─────────────────────────────────
# USFS stores dates as Julian day numbers (days since 12/31/1899)
df["discovery_date"] = pd.to_datetime(
    df["discovery_date"] - 2415018.5, unit="D", origin="julian"
).dt.strftime("%Y-%m-%d")

# ── Export ────────────────────────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False)
print(f"Saved {len(df):,} California fire records to {OUT_PATH}")
print(df["size_class"].value_counts())
