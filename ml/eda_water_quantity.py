import pandas as pd
import matplotlib.pyplot as plt
import os


# ============================================================
# LOAD MULTI-CROP ML-READY DATASET
# ============================================================

DATA_PATH = "ml/ml_ready_dataset_multicrop.csv"

df = pd.read_csv(DATA_PATH)


# ============================================================
# CREATE GRAPHS / RESULTS FOLDERS
# ============================================================

os.makedirs("ml/graphs", exist_ok=True)
os.makedirs("ml/eda_results", exist_ok=True)


# ============================================================
# BASIC VALIDATION
# ============================================================

required_columns = [
    "crop_type",
    "water_quantity_liters"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


df["water_quantity_liters"] = pd.to_numeric(
    df["water_quantity_liters"],
    errors="coerce"
)

df = df.dropna(
    subset=["crop_type", "water_quantity_liters"]
)


# ============================================================
# WATER QUANTITY DISTRIBUTION
# ============================================================

plt.figure(figsize=(10, 6))

plt.hist(
    df["water_quantity_liters"],
    bins=20
)

plt.xlabel("Water Quantity (liters)")
plt.ylabel("Number of Records")
plt.title("Water Quantity Distribution")

plt.tight_layout()

plt.savefig(
    "ml/graphs/water_quantity_distribution.png",
    dpi=300
)

plt.close()

print(
    "\nWater quantity distribution graph "
    "saved successfully."
)


# ============================================================
# OVERALL WATER QUANTITY STATISTICS
# ============================================================

overall_stats = df[
    "water_quantity_liters"
].describe()

print("\nOverall water quantity statistics:")
print(overall_stats)


# ============================================================
# CROP-WISE WATER REQUIREMENTS
# ============================================================

crop_stats = (
    df.groupby("crop_type")[
        "water_quantity_liters"
    ]
    .agg(
        [
            "count",
            "mean",
            "median",
            "min",
            "max",
            "std"
        ]
    )
    .sort_values(
        "mean",
        ascending=False
    )
)

print("\n" + "=" * 70)
print("CROP-WISE WATER REQUIREMENTS")
print("=" * 70)

print(crop_stats)


# ============================================================
# SAVE CROP-WISE RESULTS
# ============================================================

crop_stats.to_csv(
    "ml/eda_results/crop_wise_water_requirements.csv"
)

print(
    "\nCrop-wise water requirements results "
    "saved successfully."
)


# ============================================================
# CROP-WISE MEAN WATER REQUIREMENT GRAPH
# ============================================================

plt.figure(
    figsize=(14, 8)
)

plt.bar(
    crop_stats.index,
    crop_stats["mean"]
)

plt.xlabel("Crop Type")
plt.ylabel("Average Water Quantity (liters)")
plt.title(
    "Crop-Wise Average Water Requirements"
)

plt.xticks(
    rotation=60,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "ml/graphs/crop_wise_water_requirements.png",
    dpi=300
)

plt.close()

print(
    "Crop-wise water requirement graph "
    "saved successfully."
)


# ============================================================
# CROP-WISE MIN / MAX WATER RANGE
# ============================================================

plt.figure(
    figsize=(14, 8)
)

plt.bar(
    crop_stats.index,
    crop_stats["max"] - crop_stats["min"]
)

plt.xlabel("Crop Type")
plt.ylabel(
    "Water Quantity Range (liters)"
)

plt.title(
    "Crop-Wise Water Requirement Range"
)

plt.xticks(
    rotation=60,
    ha="right"
)

plt.tight_layout()

plt.savefig(
    "ml/graphs/crop_wise_water_range.png",
    dpi=300
)

plt.close()

print(
    "Crop-wise water range graph "
    "saved successfully."
)


# ============================================================
# SUMMARY
# ============================================================

highest_crop = crop_stats["mean"].idxmax()
lowest_crop = crop_stats["mean"].idxmin()

highest_value = crop_stats.loc[
    highest_crop,
    "mean"
]

lowest_value = crop_stats.loc[
    lowest_crop,
    "mean"
]


summary = pd.DataFrame(
    {
        "metric": [
            "total_records",
            "number_of_crops",
            "highest_average_water_crop",
            "highest_average_water_quantity_liters",
            "lowest_average_water_crop",
            "lowest_average_water_quantity_liters"
        ],

        "value": [
            len(df),
            df["crop_type"].nunique(),
            highest_crop,
            highest_value,
            lowest_crop,
            lowest_value
        ]
    }
)

summary.to_csv(
    "ml/eda_results/water_quantity_eda_summary.csv",
    index=False
)


print("\n" + "=" * 70)
print("WATER QUANTITY EDA COMPLETED")
print("=" * 70)

print(
    f"\nTotal records analyzed: {len(df)}"
)

print(
    f"Crops analyzed: {df['crop_type'].nunique()}"
)

print(
    f"Highest average water requirement: "
    f"{highest_crop} ({highest_value:.2f} L)"
)

print(
    f"Lowest average water requirement: "
    f"{lowest_crop} ({lowest_value:.2f} L)"
)

print(
    "\nAll crop-wise EDA results and graphs "
    "have been saved."
)