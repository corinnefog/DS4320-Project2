import os
import pandas as pd

DATA_DIR = "data"
OUT_PATH = os.path.join(DATA_DIR, "calfire_incidents.csv")

df = pd.read_csv(os.path.join(DATA_DIR, "calfire_raw.csv"))
print(f"Loaded {len(df):,} raw CAL FIRE records.")
print("Columns:", df.columns.tolist())

# Rename using actual column names from mapdatall.csv
df = df.rename(columns={
    "incident_name":            "incident_name",
    "incident_county":          "county",
    "incident_acres_burned":    "size_acres",
    "incident_dateonly_created":"discovery_date",
    "incident_dateonly_extinguished": "containment_date",
    "incident_latitude":        "latitude",
    "incident_longitude":       "longitude",
})

# Keep only what we need
keep = [c for c in ["incident_name", "county", "discovery_date", "containment_date",
                     "size_acres", "latitude", "longitude"] if c in df.columns]
df = df[keep].copy()

# Parse dates
for col in ["discovery_date", "containment_date"]:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce").dt.strftime("%Y-%m-%d")

# Filter
df = df[df["discovery_date"] >= "2000-01-01"]
df = df.dropna(subset=["size_acres"])
df = df.dropna(subset=["latitude", "longitude"])

def assign_size_class(acres):
    if acres < 100:    return "small"
    elif acres < 1000: return "medium"
    else:              return "large"

df["size_class"] = df["size_acres"].apply(assign_size_class)
df["source"]     = "calfire"
df["id"]         = [f"CAL-{i:06d}" for i in range(len(df))]

df.to_csv(OUT_PATH, index=False)
print(f"Saved {len(df):,} cleaned CAL FIRE records to {OUT_PATH}")
print(df["size_class"].value_counts())

