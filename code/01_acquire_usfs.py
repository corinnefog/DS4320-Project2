import sqlite3
import pandas as pd

DB_PATH  = "/Users/corinnefogarty/DS4320/Project-2/data/Data/FPA_FOD_20221014.sqlite"
OUT_PATH = "/Users/corinnefogarty/DS4320/Project-2/data/usfs_california.csv"

conn = sqlite3.connect(DB_PATH)

query = """
SELECT
    FOD_ID                  AS id,
    FIRE_YEAR               AS fire_year,
    DISCOVERY_DATE          AS discovery_date,
    DISCOVERY_DOY           AS discovery_doy,
    NWCG_GENERAL_CAUSE      AS cause,
    FIRE_SIZE               AS size_acres,
    FIRE_SIZE_CLASS         AS size_class_usfs,
    LATITUDE                AS latitude,
    LONGITUDE               AS longitude,
    STATE                   AS state,
    COUNTY                  AS county,
    FIPS_NAME               AS county_name,
    OWNER_DESCR             AS agency
FROM Fires
WHERE STATE = 'CA'
  AND FIRE_YEAR >= 2000
  AND LATITUDE IS NOT NULL
  AND LONGITUDE IS NOT NULL
  AND FIRE_SIZE IS NOT NULL
"""

df = pd.read_sql_query(query, conn)
conn.close()
print(f"Records retrieved: {len(df):,}")

def assign_size_class(acres):
    if acres < 100:    return "small"
    elif acres < 1000: return "medium"
    else:              return "large"

df["size_class"] = df["size_acres"].apply(assign_size_class)
df["source"]     = "usfs"

df.to_csv(OUT_PATH, index=False)
print(f"Saved {len(df):,} records to {OUT_PATH}")
print(df["size_class"].value_counts())
