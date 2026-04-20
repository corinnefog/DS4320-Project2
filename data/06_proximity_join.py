"""
06_proximity_join.py
Computes distance (meters) from each fire ignition point to:
  1. The nearest road    — from US Census TIGER/Line road shapefile
  2. The nearest structure — from Microsoft US Building Footprints

Both datasets are downloaded automatically if not present.
Uses a spatial index (STRtree) for efficient nearest-neighbor lookup.

Outputs /data/wildfires_proximity.csv
"""

import os
import zipfile
import requests
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from shapely.strtree import STRtree

# ── Config ────────────────────────────────────────────────────────────────────
DATA_DIR   = "data"
IN_PATH    = os.path.join(DATA_DIR, "wildfires_topo.csv")
OUT_PATH   = os.path.join(DATA_DIR, "wildfires_proximity.csv")
GEO_DIR    = os.path.join(DATA_DIR, "geo")

os.makedirs(GEO_DIR, exist_ok=True)

# California FIPS code = 06
# TIGER primary roads (S1100) for California
TIGER_URL  = "https://www2.census.gov/geo/tiger/TIGER2023/PRIMARYROADS/tl_2023_06_prisecroads.zip"
TIGER_ZIP  = os.path.join(GEO_DIR, "ca_roads.zip")
TIGER_DIR  = os.path.join(GEO_DIR, "ca_roads")

# Microsoft Building Footprints (California GeoJSON — large file ~500MB)
# Hosted on Azure blob storage by Microsoft
BLDG_URL   = "https://minedbuildings.blob.core.windows.net/global-buildings/2023-04-25/California.zip"
BLDG_ZIP   = os.path.join(GEO_DIR, "ca_buildings.zip")
BLDG_DIR   = os.path.join(GEO_DIR, "ca_buildings")

# UTM Zone 10N (EPSG:26910) — meters, appropriate for California
PROJ_CRS   = "EPSG:26910"

# ── Load fire points ──────────────────────────────────────────────────────────
df = pd.read_csv(IN_PATH)
print(f"Loaded {len(df):,} fire records.")

fire_gdf = gpd.GeoDataFrame(
    df,
    geometry=[Point(lon, lat) for lat, lon in zip(df["latitude"], df["longitude"])],
    crs="EPSG:4326"
).to_crs(PROJ_CRS)

# ── Download and load roads ───────────────────────────────────────────────────
def download_and_extract(url, zip_path, extract_dir):
    if not os.path.exists(extract_dir):
        print(f"Downloading {os.path.basename(zip_path)}...")
        r = requests.get(url, stream=True, timeout=120)
        r.raise_for_status()
        with open(zip_path, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extractall(extract_dir)
        print("Done.")
    else:
        print(f"{extract_dir} already exists, skipping download.")

download_and_extract(TIGER_URL, TIGER_ZIP, TIGER_DIR)

shp_files = [f for f in os.listdir(TIGER_DIR) if f.endswith(".shp")]
roads_gdf = gpd.read_file(os.path.join(TIGER_DIR, shp_files[0])).to_crs(PROJ_CRS)
print(f"Loaded {len(roads_gdf):,} road segments.")

# ── Nearest road distance ─────────────────────────────────────────────────────
print("Building road spatial index...")
road_geoms  = list(roads_gdf.geometry)
road_tree   = STRtree(road_geoms)

print("Computing distance to nearest road...")
dist_road = []
for pt in fire_gdf.geometry:
    nearest_idx  = road_tree.nearest(pt)
    nearest_geom = road_geoms[nearest_idx]
    dist_road.append(round(pt.distance(nearest_geom), 1))

df["dist_road_m"] = dist_road
print(f"Road distances computed. Mean: {np.mean(dist_road):,.0f} m")

# ── Download and load building footprints ─────────────────────────────────────
# Note: the Microsoft building footprints file is large (~500MB).
# If bandwidth is a concern, use the county-level files instead:
# https://github.com/microsoft/USBuildingFootprints
try:
    download_and_extract(BLDG_URL, BLDG_ZIP, BLDG_DIR)
    geojson_files = [f for f in os.listdir(BLDG_DIR) if f.endswith(".geojson") or f.endswith(".json")]

    if geojson_files:
        bldg_gdf = gpd.read_file(os.path.join(BLDG_DIR, geojson_files[0])).to_crs(PROJ_CRS)
        # Use centroids for distance calculation
        bldg_pts = list(bldg_gdf.geometry.centroid)
        print(f"Loaded {len(bldg_pts):,} building footprints.")

        print("Building structure spatial index...")
        bldg_tree = STRtree(bldg_pts)

        print("Computing distance to nearest structure...")
        dist_bldg = []
        for pt in fire_gdf.geometry:
            nearest_idx  = bldg_tree.nearest(pt)
            nearest_geom = bldg_pts[nearest_idx]
            dist_bldg.append(round(pt.distance(nearest_geom), 1))

        df["dist_structure_m"] = dist_bldg
        print(f"Structure distances computed. Mean: {np.mean(dist_bldg):,.0f} m")
    else:
        print("No GeoJSON files found in building footprint archive.")
        df["dist_structure_m"] = np.nan

except Exception as e:
    print(f"Building footprint download failed: {e}")
    print("Setting dist_structure_m to NaN — download manually from")
    print("https://github.com/microsoft/USBuildingFootprints")
    df["dist_structure_m"] = np.nan

# ── Export ────────────────────────────────────────────────────────────────────
df.to_csv(OUT_PATH, index=False)
print(f"\nSaved proximity-enriched dataset to {OUT_PATH}")
print(df[["dist_road_m", "dist_structure_m"]].describe().round(1))
