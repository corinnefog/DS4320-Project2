
import os
import time
import math
import requests
import pandas as pd
import numpy as np

# Config 
DATA_DIR = "data"
IN_PATH  = os.path.join(DATA_DIR, "wildfires_weather.csv")
OUT_PATH = os.path.join(DATA_DIR, "wildfires_topo.csv")

ELEVATION_API = "https://epqs.nationalmap.gov/v1/json"
PAUSE_SEC     = 0.2

# Load 
df = pd.read_csv(IN_PATH)
print(f"Loaded {len(df):,} records.")

# USGS Elevation Point Query 
def get_elevation(lat, lon):
    """Query USGS EPQS for elevation in meters at a point."""
    params = {
        "x":      lon,
        "y":      lat,
        "units":  "Meters",
        "output": "json",
    }
    try:
        r = requests.get(ELEVATION_API, params=params, timeout=15)
        if r.status_code == 200:
            data = r.json()
            val  = data.get("value")
            if val is not None and str(val) not in ("-1000000", ""):
                return float(val)
    except Exception:
        pass
    return np.nan

def get_slope_aspect(lat, lon, delta_deg=0.001):
    """
    Approximate slope (degrees) and aspect (degrees from north) using
    a 3-point finite difference of elevations from USGS EPQS.
    delta_deg ~ 100m spacing at California latitudes.
    """
    e_center = get_elevation(lat, lon)
    e_east   = get_elevation(lat, lon + delta_deg)
    e_north  = get_elevation(lat + delta_deg, lon)

    if any(np.isnan(v) for v in [e_center, e_east, e_north]):
        return np.nan, np.nan

    # Approximate horizontal distance in meters
    meters_per_deg_lat = 111_320
    meters_per_deg_lon = 111_320 * math.cos(math.radians(lat))

    dz_dx = (e_east  - e_center) / (delta_deg * meters_per_deg_lon)
    dz_dy = (e_north - e_center) / (delta_deg * meters_per_deg_lat)

    slope_rad  = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
    slope_deg  = math.degrees(slope_rad)

    aspect_rad = math.atan2(-dz_dy, dz_dx)
    aspect_deg = (math.degrees(aspect_rad) + 360) % 360

    return round(slope_deg, 2), round(aspect_deg, 2)

# Main loop 
CHECKPOINT_EVERY = 200
checkpoint_path  = os.path.join(DATA_DIR, "topo_checkpoint.csv")

if os.path.exists(checkpoint_path):
    done      = pd.read_csv(checkpoint_path)
    start_idx = len(done)
    print(f"Resuming from checkpoint at row {start_idx}.")
else:
    done      = pd.DataFrame()
    start_idx = 0

for i, row in df.iloc[start_idx:].iterrows():
    lat, lon = row["latitude"], row["longitude"]
    record   = {"id": row["id"]}

    elev = get_elevation(lat, lon)
    time.sleep(PAUSE_SEC)

    slope, aspect = get_slope_aspect(lat, lon)
    time.sleep(PAUSE_SEC)

    record["elevation_m"] = elev
    record["slope_deg"]   = slope
    record["aspect_deg"]  = aspect

    done = pd.concat([done, pd.DataFrame([record])], ignore_index=True)

    if (i - start_idx + 1) % CHECKPOINT_EVERY == 0:
        done.to_csv(checkpoint_path, index=False)
        print(f"  Checkpoint at {i - start_idx + 1} records.")

#  Merge and export 
result = df.merge(done, on="id", how="left")

print(f"\nTopography join complete.")
print(f"Elevation available: {result['elevation_m'].notna().sum():,} records")
print(f"Slope available:     {result['slope_deg'].notna().sum():,} records")

result.to_csv(OUT_PATH, index=False)
print(f"Saved to {OUT_PATH}")

if os.path.exists(checkpoint_path):
    os.remove(checkpoint_path)
