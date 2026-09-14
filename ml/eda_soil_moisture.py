import pandas as pd
import matplotlib.pyplot as plt
import os


# Load ML-ready dataset
df = pd.read_csv("ml/ml_ready_dataset.csv")


# Create graphs folder
os.makedirs("ml/graphs", exist_ok=True)


# ============================================================
# SOIL MOISTURE DISTRIBUTION
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["soil_moisture"],
    bins=30
)

plt.xlabel("Soil Moisture (%)")
plt.ylabel("Number of Readings")
plt.title("Soil Moisture Distribution")

plt.tight_layout()

plt.savefig(
    "ml/graphs/soil_moisture_distribution.png",
    dpi=300
)

plt.show()


print(
    "\nSoil moisture distribution graph "
    "saved successfully."
)