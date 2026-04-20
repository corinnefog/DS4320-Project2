"""
02_acquire_calfire.py
Downloads and cleans the CAL FIRE incident history dataset.
Outputs /data/calfire_incidents.csv.

Source: https://www.fire.ca.gov/stats-events
CAL FIRE publishes incident data as a CSV download from their stats portal.
"""

import os
import requests
import pandas as pd
from io import StringIO

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR = "data"
OUT_PATH = os.path.join(DATA_DIR, "calfire_incidents.csv")

os.makedirs(DATA_DIR, exist_ok=True)

# CAL FIRE public incident CSV endpoint
# If this URL changes, visit https://www.fire.ca.gov/stats-events and
# right-click the CSV download button to get the updated link.
CALFIRE_URL = "https://www.fire.ca.gov/umbraco/Api/IncidentApi/GetCsv?inactive=true"

# ── Download ──────────────────────────────────────────────────────────────────
print("Downloading CAL FIRE incident data...")
headers = {"User-Agent": "Mozilla/5.0"}
response = requests.get(CALFIRE_URL, headers=headers, timeout=60)

if response.status_code != 200:
    print(f"Direct download failed (status {response.status_code}).")
    print("Please manually download the CSV from https://www.fire.ca.gov/stats-events")
    print("and save it to data/calfire_raw.csv, then re-run this script.")
    # Try to read manually downloaded file as fallback
    manual_path = os.path.join(DATA_DIR, "calfire_raw.csv")
    if os.path.exists(manual_path):
        print(f"Found manual download at {manual_path}, using that.")
        df = pd.read_csv(manual_path)
    else:
        raise FileNotFoundError("No CAL FIRE data found. Please download manually.")
else:
    df = pd.read_csv(StringIO(response.text))
    print(f"Downloaded {len(df):,} raw CAL FIRE records.")

# ── Inspect columns ───────────────────────────────────────────────────────────
print("Columns:", df.columns.tolist())

# ── Standardize column names ──────────────────────────────────────────────────
# CAL FIRE column names vary by export version; map to standard names
col_map = {
    "IncidentName":      "incident_name",
    "Name":              "incident_name",
    "County":            "county",
    "Location":          "location_desc",
    "AcresBurned":       "size_acres",
    "Acres":             "size_acres",
    "Started":           "discovery_date",
    "StartedDateOnly":   "discovery_date",
    "Contained":         "containment_date",
    "Latitude":          "latitude",
    "Longitude":         "longitude",
    "StructuresDamaged": "structures_damaged",
    "StructuresDestroyed":"structures_destroyed",
    "Fatalities":        "fatalities",
    "Active":            "active",
}
df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

# ── Filter and clean ──────────────────────────────────────────────────────────
# Keep only columns we have
keep = [c for c in ["incident_name", "county", "discovery_date", "containment_date",
                     "size_acres", "latitude", "longitude",
                     "structures_damaged", "structures_destroyed", "fatalities"] if c in df.columns]
df = df[keep].copy()

# Parse dates
for col in ["discovery_date", "containment_date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

# Filter to 2000+ and records with coordinates and acreage
df = df[df["discovery_date"] >= "2000-01-01"]
df = df.dropna(subset=["size_acres"])
if "latitude" in df.columns and "longitude" in df.columns:
    df = df.dropna(subset=["latitude", "longitude"])

# Assign size class
def assign_size_class(acres):
    if acres < 100:
        return "small"
    elif acres < 1000:
        return "medium"
    else:
        return "large"

df["size_class"] = df["size_acres"].apply(assign_size_class)
df["source"]     = "calfire"

# ── Export ────────────────────────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False)
print(f"Saved {len(df):,} cleaned CAL FIRE records to {OUT_PATH}")
print(df["size_class"].value_counts())
