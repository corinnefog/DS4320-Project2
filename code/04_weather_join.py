import os
import time
import logging
import pandas as pd
import numpy as np
import xarray as xr


# Logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("logs/04_weather_join.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


# Config
DATA_DIR = "data"
IN_PATH = os.path.join(DATA_DIR, "wildfires_merged.csv")
OUT_PATH = os.path.join(DATA_DIR, "wildfires_weather.csv")
CHECKPOINT_PATH = os.path.join(DATA_DIR, "weather_checkpoint.csv")

VARIABLES = ["tmmx", "vs", "rmin", "vpd", "pr"]

VAR_MAP = {
    "tmmx": "air_temperature",
    "vs": "wind_speed",
    "rmin": "relative_humidity",
    "vpd": "mean_vapor_pressure_deficit",
    "pr": "precipitation_amount",
}

CHECKPOINT_EVERY = 50
PAUSE_SEC = 0.02


# Load data
df = pd.read_csv(
    IN_PATH,
    parse_dates=["discovery_date"],
    dtype={"id": str},
    low_memory=False
)

# Use sample so script doesn't take too long
df = df.sample(3000, random_state=42).reset_index(drop=True)

print(f"Loaded {len(df):,} fire records.")


def query_gridmet_xarray(lat, lon, date_str, var):
    """
    Query one gridMET variable for one fire record.
    Returns the value or NaN if it fails.
    """
    year = date_str[:4]
    url = f"https://thredds.northwestknowledge.net/thredds/dodsC/MET/{var}/{var}_{year}.nc"

    try:
        ds = xr.open_dataset(url)
        ds_var = VAR_MAP[var]

        val = ds[ds_var].sel(
            day=np.datetime64(date_str),
            lat=lat,
            lon=lon,
            method="nearest"
        ).values.item()

        ds.close()

        return round(float(val), 3)

    except Exception as e:
        print(f"Failed for {var}, {date_str}, {lat}, {lon}: {e}")
        return np.nan


# Resume from checkpoint if it exists
if os.path.exists(CHECKPOINT_PATH):
    done = pd.read_csv(CHECKPOINT_PATH, dtype={"id": str})
    start_idx = len(done)
    print(f"Resuming from checkpoint at row {start_idx}.")
else:
    done = pd.DataFrame()
    start_idx = 0


# Main loop
for i, row in df.iloc[start_idx:].iterrows():
    processed = i - start_idx + 1
    total_remaining = len(df) - start_idx

    if processed % 10 == 0:
        print(f"Processing row {processed}/{total_remaining}...")

    date_str = str(row["discovery_date"])[:10]
    lat = row["latitude"]
    lon = row["longitude"]

    record = {"id": str(row["id"])}

    for var in VARIABLES:
        val = query_gridmet_xarray(lat, lon, date_str, var)
        record[var] = val
        time.sleep(PAUSE_SEC)

    done = pd.concat([done, pd.DataFrame([record])], ignore_index=True)

    if processed % CHECKPOINT_EVERY == 0:
        done.to_csv(CHECKPOINT_PATH, index=False)
        print(f"Checkpoint saved at {len(done)} records processed.")


# Save final checkpoint
done.to_csv(CHECKPOINT_PATH, index=False)


# Rename columns
done = done.rename(columns={
    "tmmx": "temp_max_c",
    "vs": "wind_speed_ms",
    "rmin": "relative_humidity",
    "vpd": "vpd_kpa",
    "pr": "precip_mm",
})


# Make sure merge ids match
df["id"] = df["id"].astype(str)
done["id"] = done["id"].astype(str)


# Merge back
result = df.merge(done, on="id", how="left")


print("\nWeather join complete.")
print(f"Records with temperature data: {result['temp_max_c'].notna().sum():,}")
print(f"Records missing temperature data: {result['temp_max_c'].isna().sum():,}")

print("\nWeather preview:")
print(result[[
    "id",
    "temp_max_c",
    "wind_speed_ms",
    "relative_humidity",
    "vpd_kpa",
    "precip_mm"
]].head())


# Save output
result.to_csv(OUT_PATH, index=False)
print(f"\nSaved to {OUT_PATH}")

