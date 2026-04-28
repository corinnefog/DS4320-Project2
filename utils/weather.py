import pandas as pd
import os

DATA_DIR = "data"

checkpoint = pd.read_csv(os.path.join(DATA_DIR, "weather_checkpoint.csv"))
checkpoint = checkpoint.rename(columns={
    "tmmx": "temp_max_c",
    "vs":   "wind_speed_ms",
    "rmin": "relative_humidity",
    "vpd":  "vpd_kpa",
    "pr":   "precip_mm",
})
checkpoint["id"] = checkpoint["id"].astype(str)
print(f"Checkpoint has {len(checkpoint):,} records with weather data.")

merged = pd.read_csv(os.path.join(DATA_DIR, "wildfires_merged.csv"), low_memory=False)
merged["id"] = merged["id"].astype(str)

result = merged.merge(checkpoint, on="id", how="inner")
print(f"Final dataset: {len(result):,} records with weather.")
print(result["size_class"].value_counts())

result.to_csv(os.path.join(DATA_DIR, "wildfires_weather.csv"), index=False)
print("Saved to data/wildfires_weather.csv")

os.remove(os.path.join(DATA_DIR, "weather_checkpoint.csv"))
print("Checkpoint deleted.")
