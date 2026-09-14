import pandas as pd
import matplotlib.pyplot as plt
import os


# Load ML-ready dataset
df = pd.read_csv("ml/ml_ready_dataset.csv")


# Convert timestamp
df["timestamp"] = pd.to_datetime(df["timestamp"])


# Create graphs folder
os.makedirs("ml/graphs", exist_ok=True)


# ============================================================
# RAINFALL OVER TIME
# ============================================================

weather = (
    df[
        [
            "timestamp",
            "rainfall"
        ]
    ]
    .drop_duplicates()
    .sort_values("timestamp")
)


plt.figure(figsize=(12, 6))

plt.bar(
    weather["timestamp"].dt.strftime("%Y-%m-%d %H:%M"),
    weather["rainfall"]
)

plt.xlabel("Weather Observation")
plt.ylabel("Rainfall (mm)")
plt.title("Rainfall Pattern Over Time")

plt.xticks(
    rotation=45,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "ml/graphs/rainfall_pattern.png",
    dpi=300
)

plt.show()


print(
    "\nRainfall pattern graph "
    "saved successfully."
)