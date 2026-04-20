"""
03_merge_deduplicate.py
Joins USFS and CAL FIRE records on location + date to remove duplicates.
USFS record is treated as authoritative where conflicts exist.
Outputs /data/wildfires_merged.csv.

Deduplication tolerance:
  - Location: within 0.01 degrees (~1 km) in both lat and lon
  - Date: within 2 days of each other
"""

import os
import pandas as pd
import numpy as np
from scipy.spatial import cKDTree

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR   = "data"
USFS_PATH  = os.path.join(DATA_DIR, "usfs_california.csv")
CAL_PATH   = os.path.join(DATA_DIR, "calfire_incidents.csv")
OUT_PATH   = os.path.join(DATA_DIR, "wildfires_merged.csv")

# ── Load ──────────────────────────────────────────────────────────────────────
print("Loading USFS data...")
usfs = pd.read_csv(USFS_PATH, parse_dates=["discovery_date"])

print("Loading CAL FIRE data...")
cal  = pd.read_csv(CAL_PATH,  parse_dates=["discovery_date"])

print(f"USFS records:    {len(usfs):,}")
print(f"CAL FIRE records: {len(cal):,}")

# ── Standardize shared columns ────────────────────────────────────────────────
# Ensure both have lat, lon, discovery_date, size_acres, size_class, source
for df in [usfs, cal]:
    df["discovery_date"] = pd.to_datetime(df["discovery_date"], errors="coerce")
    df["discovery_doy"]  = df["discovery_date"].dt.dayofyear
    df["fire_year"]      = df["discovery_date"].dt.year

# Drop rows without coordinates in either dataset
usfs = usfs.dropna(subset=["latitude", "longitude", "discovery_date"])
cal  = cal.dropna(subset=["latitude", "longitude", "discovery_date"])

# ── Spatial deduplication using KD-tree ──────────────────────────────────────
LOC_TOL_DEG  = 0.01   # ~1 km
DATE_TOL_DAY = 2

print("Building spatial index for deduplication...")
usfs_coords = usfs[["latitude", "longitude"]].values
cal_coords  = cal[["latitude", "longitude"]].values

tree = cKDTree(usfs_coords)
distances, indices = tree.query(cal_coords, k=1)

is_duplicate = []
for i, (dist, idx) in enumerate(zip(distances, indices)):
    if dist <= LOC_TOL_DEG:
        date_diff = abs(
            (cal.iloc[i]["discovery_date"] - usfs.iloc[idx]["discovery_date"]).days
        )
        is_duplicate.append(date_diff <= DATE_TOL_DAY)
    else:
        is_duplicate.append(False)

cal["is_duplicate"] = is_duplicate

# Mark matched USFS records as appearing in both sources
matched_usfs_idx = [
    indices[i] for i, dup in enumerate(is_duplicate) if dup
]
usfs["source"] = "usfs"
usfs.iloc[matched_usfs_idx, usfs.columns.get_loc("source")] = "both"

# Keep only CAL FIRE records that are NOT duplicates of USFS records
cal_unique = cal[~cal["is_duplicate"]].copy()
cal_unique["source"] = "calfire"

print(f"Duplicate records removed from CAL FIRE: {cal['is_duplicate'].sum():,}")
print(f"Unique CAL FIRE records retained:        {len(cal_unique):,}")

# ── Align columns and concatenate ─────────────────────────────────────────────
shared_cols = [
    "id", "fire_year", "discovery_date", "discovery_doy",
    "cause", "size_acres", "size_class",
    "latitude", "longitude", "county", "agency", "source"
]

# Add missing columns with NaN so concat works cleanly
for col in shared_cols:
    if col not in usfs.columns:
        usfs[col] = np.nan
    if col not in cal_unique.columns:
        cal_unique[col] = np.nan

# Generate IDs for CAL FIRE records that don't have one
cal_unique["id"] = cal_unique.get("id", pd.Series(dtype=str))
mask = cal_unique["id"].isna()
cal_unique.loc[mask, "id"] = [f"CAL-{i:06d}" for i in range(mask.sum())]

merged = pd.concat(
    [usfs[shared_cols], cal_unique[shared_cols]],
    ignore_index=True
)

# ── Final cleanup ─────────────────────────────────────────────────────────────
merged = merged.dropna(subset=["size_acres", "latitude", "longitude"])
merged["size_class"] = merged["size_class"].fillna(
    merged["size_acres"].apply(
        lambda a: "small" if a < 100 else ("medium" if a < 1000 else "large")
    )
)

print(f"\nFinal merged dataset: {len(merged):,} records")
print(merged["source"].value_counts())
print(merged["size_class"].value_counts())

merged.to_csv(OUT_PATH, index=False)
print(f"\nSaved merged dataset to {OUT_PATH}")
