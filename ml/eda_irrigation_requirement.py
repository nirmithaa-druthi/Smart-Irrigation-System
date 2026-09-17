import pandas as pd
import matplotlib.pyplot as plt
import os

# Load the current multi-crop ML-ready dataset
dataset_path = "ml/ml_ready_dataset_multicrop.csv"

if not os.path.exists(dataset_path):
    raise FileNotFoundError(
        f"Dataset not found: {dataset_path}"
    )

df = pd.read_csv(dataset_path)

# Create output folders
os.makedirs("ml/graphs", exist_ok=True)
os.makedirs("ml/eda_results", exist_ok=True)

# Validate required columns
required_columns = [
    "crop_type",
    "irrigation_required",
    "water_quantity_liters",
    "previous_water_usage_liters"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Convert required numeric columns
df["water_quantity_liters"] = pd.to_numeric(
    df["water_quantity_liters"],
    errors="coerce"
)

df["previous_water_usage_liters"] = pd.to_numeric(
    df["previous_water_usage_liters"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "crop_type",
        "irrigation_required",
        "water_quantity_liters"
    ]
)

# ---------------------------------------------------------
# 1. Overall irrigation requirement distribution
# ---------------------------------------------------------

irrigation_counts = (
    df["irrigation_required"]
    .map({False: "No irrigation required",
          True: "Irrigation required"})
    .value_counts()
)

plt.figure(figsize=(8, 6))
irrigation_counts.plot(kind="bar")
plt.title("Irrigation Requirement Distribution")
plt.xlabel("Irrigation Requirement")
plt.ylabel("Number of Records")
plt.xticks(rotation=0)
plt.tight_layout()

plt.savefig(
    "ml/graphs/irrigation_requirement_distribution.png",
    dpi=300
)

plt.close()

print("Irrigation requirement distribution graph saved successfully.")

print("\nCounts:")
print(
    f"No irrigation required: "
    f"{irrigation_counts.get('No irrigation required', 0)}"
)
print(
    f"Irrigation required: "
    f"{irrigation_counts.get('Irrigation required', 0)}"
)

# ---------------------------------------------------------
# 2. Crop-wise irrigation requirement
# ---------------------------------------------------------

crop_irrigation = (
    df.groupby("crop_type")["irrigation_required"]
    .agg(
        total_records="count",
        irrigation_required="sum"
    )
)

crop_irrigation["no_irrigation_required"] = (
    crop_irrigation["total_records"]
    - crop_irrigation["irrigation_required"]
)

crop_irrigation["irrigation_percentage"] = (
    crop_irrigation["irrigation_required"]
    / crop_irrigation["total_records"]
    * 100
)

crop_irrigation = crop_irrigation.sort_values(
    "irrigation_percentage",
    ascending=False
)

crop_irrigation.to_csv(
    "ml/eda_results/crop_wise_irrigation_requirement.csv"
)

# ---------------------------------------------------------
# 3. Historical water usage analysis
# ---------------------------------------------------------

historical_usage = (
    df.groupby("crop_type")["previous_water_usage_liters"]
    .agg(
        count="count",
        mean="mean",
        median="median",
        min="min",
        max="max",
        std="std"
    )
    .sort_values("mean", ascending=False)
)

historical_usage.to_csv(
    "ml/eda_results/historical_irrigation_water_usage.csv"
)

# ---------------------------------------------------------
# 4. Crop-wise irrigation requirement graph
# ---------------------------------------------------------

plt.figure(figsize=(12, 8))

crop_irrigation["irrigation_percentage"].sort_values().plot(
    kind="barh"
)

plt.title("Crop-wise Irrigation Requirement")
plt.xlabel("Irrigation Required (%)")
plt.ylabel("Crop")

plt.tight_layout()

plt.savefig(
    "ml/graphs/crop_wise_irrigation_requirement.png",
    dpi=300
)

plt.close()

print(
    "\nCrop-wise irrigation requirement graph "
    "saved successfully."
)

# ---------------------------------------------------------
# 5. Historical irrigation usage graph
# ---------------------------------------------------------

plt.figure(figsize=(12, 8))

historical_usage["mean"].sort_values().plot(
    kind="barh"
)

plt.title("Historical Irrigation Water Usage by Crop")
plt.xlabel("Average Previous Water Usage (Liters)")
plt.ylabel("Crop")

plt.tight_layout()

plt.savefig(
    "ml/graphs/historical_irrigation_water_usage.png",
    dpi=300
)

plt.close()

print(
    "Historical irrigation water usage graph "
    "saved successfully."
)

# ---------------------------------------------------------
# 6. Summary
# ---------------------------------------------------------

summary = pd.DataFrame({
    "metric": [
        "Total records analyzed",
        "Total crops analyzed",
        "Irrigation required records",
        "No irrigation required records",
        "Average historical water usage (L)",
        "Maximum historical water usage (L)"
    ],
    "value": [
        len(df),
        df["crop_type"].nunique(),
        int(df["irrigation_required"].sum()),
        int((~df["irrigation_required"]).sum()),
        df["previous_water_usage_liters"].mean(),
        df["previous_water_usage_liters"].max()
    ]
})

summary.to_csv(
    "ml/eda_results/irrigation_eda_summary.csv",
    index=False
)

print("\n" + "=" * 70)
print("HISTORICAL IRRIGATION PATTERN EDA COMPLETED")
print("=" * 70)

print(f"\nTotal records analyzed: {len(df)}")
print(f"Crops analyzed: {df['crop_type'].nunique()}")

print(
    f"Irrigation required records: "
    f"{int(df['irrigation_required'].sum())}"
)

print(
    f"No irrigation required records: "
    f"{int((~df['irrigation_required']).sum())}"
)

print(
    f"Average historical water usage: "
    f"{df['previous_water_usage_liters'].mean():.2f} L"
)

print(
    f"Maximum historical water usage: "
    f"{df['previous_water_usage_liters'].max():.2f} L"
)

print(
    "\nAll historical irrigation EDA results "
    "and graphs have been saved."
)