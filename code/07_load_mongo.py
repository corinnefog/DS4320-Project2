"""
07_load_mongo.py
Loads the final enriched wildfire dataset into MongoDB Atlas.
Each row becomes one document in the 'wildfires' collection of the
'wildfire_project' database.

Documents follow the schema defined in the project metadata:
{
    id, source, fire_year, discovery_date, discovery_doy,
    cause, size_acres, size_class, agency,
    location: { latitude, longitude, county },
    weather:  { temp_max_c, wind_speed_ms, relative_humidity, vpd_kpa, precip_mm },
    topography: { elevation_m, slope_deg, aspect_deg },
    proximity: { dist_road_m, dist_structure_m }
}

Usage:
    Set MONGO_URI environment variable or paste URI directly (do not commit).
    python 07_load_mongo.py
"""

import os
import math
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR   = "data"
IN_PATH    = os.path.join(DATA_DIR, "wildfires_proximity.csv")
DB_NAME    = "wildfire_project"
COLLECTION = "wildfires"
CHUNK_SIZE = 500

# Load URI from environment variable (recommended) or paste here
MONGO_URI = os.environ.get("MONGO_URI", "YOUR_MONGO_URI_HERE")

# ── Connect ───────────────────────────────────────────────────────────────────
print("Connecting to MongoDB Atlas...")
client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
try:
    client.admin.command("ping")
    print("Connected successfully.")
except Exception as e:
    raise ConnectionError(f"Could not connect to MongoDB: {e}")

db  = client[DB_NAME]
col = db[COLLECTION]

# ── Load data ─────────────────────────────────────────────────────────────────
df = pd.read_csv(IN_PATH)
print(f"Loaded {len(df):,} records from {IN_PATH}")

# ── Convert rows to documents ─────────────────────────────────────────────────
def safe_float(val):
    """Return float or None (never NaN — Mongo doesn't accept NaN)."""
    try:
        f = float(val)
        return None if math.isnan(f) else round(f, 4)
    except (TypeError, ValueError):
        return None

def safe_str(val):
    return str(val) if pd.notna(val) else None

def row_to_doc(row):
    return {
        "id":             safe_str(row.get("id")),
        "source":         safe_str(row.get("source")),
        "fire_year":      int(row["fire_year"]) if pd.notna(row.get("fire_year")) else None,
        "discovery_date": safe_str(row.get("discovery_date")),
        "discovery_doy":  int(row["discovery_doy"]) if pd.notna(row.get("discovery_doy")) else None,
        "cause":          safe_str(row.get("cause")),
        "size_acres":     safe_float(row.get("size_acres")),
        "size_class":     safe_str(row.get("size_class")),
        "agency":         safe_str(row.get("agency")),
        "location": {
            "latitude":  safe_float(row.get("latitude")),
            "longitude": safe_float(row.get("longitude")),
            "county":    safe_str(row.get("county")),
        },
        "weather": {
            "temp_max_c":         safe_float(row.get("temp_max_c")),
            "wind_speed_ms":      safe_float(row.get("wind_speed_ms")),
            "relative_humidity":  safe_float(row.get("relative_humidity")),
            "vpd_kpa":            safe_float(row.get("vpd_kpa")),
            "precip_mm":          safe_float(row.get("precip_mm")),
        },
        "topography": {
            "elevation_m": safe_float(row.get("elevation_m")),
            "slope_deg":   safe_float(row.get("slope_deg")),
            "aspect_deg":  safe_float(row.get("aspect_deg")),
        },
        "proximity": {
            "dist_road_m":      safe_float(row.get("dist_road_m")),
            "dist_structure_m": safe_float(row.get("dist_structure_m")),
        },
    }

docs = [row_to_doc(row) for _, row in df.iterrows()]
print(f"Converted {len(docs):,} rows to documents.")

# ── Drop existing collection and reload ───────────────────────────────────────
existing = col.count_documents({})
if existing > 0:
    print(f"Dropping existing collection ({existing:,} documents)...")
    col.drop()

# ── Insert in chunks ──────────────────────────────────────────────────────────
print(f"Inserting {len(docs):,} documents in chunks of {CHUNK_SIZE}...")
inserted_total = 0

for i in range(0, len(docs), CHUNK_SIZE):
    chunk = docs[i : i + CHUNK_SIZE]
    result = col.insert_many(chunk, ordered=False)
    inserted_total += len(result.inserted_ids)
    if (i // CHUNK_SIZE + 1) % 10 == 0:
        print(f"  {inserted_total:,} documents inserted...")

print(f"\nDone. Total documents in collection: {col.count_documents({}):,}")

# ── Create indexes for common query fields ────────────────────────────────────
print("Creating indexes...")
col.create_index("id",           unique=True)
col.create_index("size_class")
col.create_index("fire_year")
col.create_index("cause")
col.create_index([("location.latitude", 1), ("location.longitude", 1)])
print("Indexes created.")

# ── Quick sanity check ────────────────────────────────────────────────────────
print("\nSample document:")
import pprint
pprint.pprint(col.find_one({}, {"_id": 0}))

print("\nSize class distribution:")
pipeline = [{"$group": {"_id": "$size_class", "count": {"$sum": 1}}},
            {"$sort":  {"count": -1}}]
for doc in col.aggregate(pipeline):
    print(f"  {doc['_id']:<10} {doc['count']:>8,}")
