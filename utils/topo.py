#One-time helper to recover and save topo data from API checkpoint after interruption
import pandas as pd
import os

DATA_DIR = "data"

checkpoint = pd.read_csv(os.path.join(DATA_DIR, "topo_checkpoint.csv"))
checkpoint["id"] = checkpoint["id"].astype(str)
print(f"Checkpoint has {len(checkpoint):,} records with topo data.")

weather = pd.read_csv(os.path.join(DATA_DIR, "wildfires_weather.csv"), low_memory=False)
weather["id"] = weather["id"].astype(str)

result = weather.merge(checkpoint, on="id", how="left")
print(f"Final dataset: {len(result):,} records.")
print(f"Elevation available: {result['elevation_m'].notna().sum():,}")

result.to_csv(os.path.join(DATA_DIR, "wildfires_topo.csv"), index=False)
print("Saved to data/wildfires_topo.csv")

os.remove(os.path.join(DATA_DIR, "topo_checkpoint.csv"))
print("Checkpoint deleted.")
