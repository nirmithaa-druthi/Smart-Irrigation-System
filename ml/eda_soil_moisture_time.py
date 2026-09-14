import pandas as pd
import matplotlib.pyplot as plt
import os


# Load ML-ready dataset
df = pd.read_csv("ml/ml_ready_dataset.csv")


# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])


# Use continuous historical sensor period
df = df[
    (df["timestamp"] >= "2026-08-01") &
    (df["timestamp"] < "2026-08-17")
].copy()


# Sort by time
df = df.sort_values("timestamp")


# Create graphs folder
os.makedirs("ml/graphs", exist_ok=True)


# ============================================================
# SOIL MOISTURE OVER TIME
# ============================================================

plt.figure(figsize=(12, 6))

plt.plot(
    df["timestamp"],
    df["soil_moisture"]
)

plt.xlabel("Time")
plt.ylabel("Soil Moisture (%)")
plt.title("Soil Moisture Variation Over Time")

plt.xticks(rotation=45)

plt.tight_layout()

plt.savefig(
    "ml/graphs/soil_moisture_over_time.png",
    dpi=300
)

plt.show()


print(
    "\nSoil moisture over time graph "
    "saved successfully."
)