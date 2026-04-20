"""
04_weather_join.py
Extracts gridMET weather variables at each fire's ignition point and date.
Uses the gridMET REST API (climatologylab.org) to avoid requiring Google
Earth Engine authentication.

Variables extracted:
  - tmmx  : max air temperature (K, converted to C)
  - vs    : wind speed at 10m (m/s)
  - rmin  : min relative humidity (%)
  - vpd   : mean vapor pressure deficit (kPa)
  - pr    : precipitation (mm)

Outputs /data/wildfires_weather.csv
"""

import os
import time
import requests
import pandas as pd
import numpy as np

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR  = "data"
IN_PATH   = os.path.join(DATA_DIR, "wildfires_merged.csv")
OUT_PATH  = os.path.join(DATA_DIR, "wildfires_weather.csv")

GRIDMET_BASE = "https://www.reacchpna.org/thredds/ncss/grid/MET"
VARIABLES    = ["tmmx", "vs", "rmin", "vpd", "pr"]
PAUSE_SEC    = 0.3   # be polite to the API

# ── Load ──────────────────────────────────────────────────────────────────────
df = pd.read_csv(IN_PATH, parse_dates=["discovery_date"])
print(f"Loaded {len(df):,} fire records.")

# ── gridMET point query ───────────────────────────────────────────────────────
def query_gridmet(lat, lon, date_str, var):
    """
    Query a single gridMET variable at a point and date via the THREDDS
    NetCDF Subset Service. Returns the float value or NaN on failure.
    """
    year  = date_str[:4]
    url   = f"{GRIDMET_BASE}/{var}/{var}_{year}.nc"
    params = {
        "var":         var,
        "latitude":    lat,
        "longitude":   lon,
        "time":        f"{date_str}T00:00:00Z",
        "accept":      "csv",
        "point":       "true",
    }
    try:
        r = requests.get(url, params=params, timeout=30)
        if r.status_code == 200:
            lines = r.text.strip().split("\n")
            # CSV response: header row + data row
            if len(lines) >= 2:
                val = float(lines[-1].split(",")[-1])
                return val
    except Exception:
        pass
    return np.nan

# ── Alternative: use the climatologylab.org API ───────────────────────────────
def query_gridmet_clim(lat, lon, start_date, end_date, var):
    """
    Climatology Lab gridMET API — simpler and more reliable for point queries.
    Returns a single float (the value on start_date) or NaN.
    """
    url = "https://www.climatologylab.org/wget-gridmet.html"
    # Direct download URL format for climatologylab gridMET
    # Format: https://climate.northwestknowledge.net/METDATA/data/{var}/{var}_{year}.nc
    # We use the OpenDAP/REST endpoint instead
    api_url = (
        f"https://climate.northwestknowledge.net/METDATA/data/"
        f"{var}/{var}_{start_date[:4]}.nc"
        f"?var={var}&lat={lat}&lon={lon}"
        f"&start={start_date}&end={end_date}&type=gridmet"
    )
    try:
        r = requests.get(api_url, timeout=30)
        if r.status_code == 200:
            lines = [l for l in r.text.strip().split("\n") if l and not l.startswith("#")]
            if len(lines) >= 2:
                return float(lines[-1].split(",")[-1])
    except Exception:
        pass
    return np.nan

# ── Main loop ─────────────────────────────────────────────────────────────────
# For large datasets, process in batches and checkpoint periodically.
# If the API is slow or rate-limited, consider downloading full-year
# NetCDF files and using xarray for local extraction instead.

weather_cols = {
    "tmmx": [],   # max temp (K -> C)
    "vs":   [],   # wind speed m/s
    "rmin": [],   # min relative humidity %
    "vpd":  [],   # vapor pressure deficit kPa
    "pr":   [],   # precipitation mm
}

CHECKPOINT_EVERY = 500
checkpoint_path  = os.path.join(DATA_DIR, "weather_checkpoint.csv")

# Resume from checkpoint if it exists
if os.path.exists(checkpoint_path):
    done = pd.read_csv(checkpoint_path)
    start_idx = len(done)
    print(f"Resuming from checkpoint at row {start_idx}.")
else:
    done      = pd.DataFrame()
    start_idx = 0

for i, row in df.iloc[start_idx:].iterrows():
    date_str = str(row["discovery_date"])[:10]
    lat, lon = row["latitude"], row["longitude"]
    record   = {"id": row["id"]}

    for var in VARIABLES:
        val = query_gridmet_clim(lat, lon, date_str, date_str, var)
        record[var] = val
        time.sleep(PAUSE_SEC)

    # Convert temperature from Kelvin to Celsius
    if not np.isnan(record.get("tmmx", np.nan)):
        record["tmmx"] = round(record["tmmx"] - 273.15, 2)

    done = pd.concat([done, pd.DataFrame([record])], ignore_index=True)

    if (i - start_idx + 1) % CHECKPOINT_EVERY == 0:
        done.to_csv(checkpoint_path, index=False)
        print(f"  Checkpoint saved at {i - start_idx + 1} records processed.")

# ── Rename columns and merge back ─────────────────────────────────────────────
done = done.rename(columns={
    "tmmx": "temp_max_c",
    "vs":   "wind_speed_ms",
    "rmin": "relative_humidity",
    "vpd":  "vpd_kpa",
    "pr":   "precip_mm",
})

result = df.merge(done, on="id", how="left")

print(f"\nWeather join complete.")
print(f"Records with full weather data: {result['temp_max_c'].notna().sum():,}")
print(f"Records missing weather data:   {result['temp_max_c'].isna().sum():,}")

result.to_csv(OUT_PATH, index=False)
print(f"Saved to {OUT_PATH}")

# Clean up checkpoint
if os.path.exists(checkpoint_path):
    os.remove(checkpoint_path)
