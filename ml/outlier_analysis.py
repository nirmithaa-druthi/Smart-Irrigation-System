import pandas as pd
import numpy as np
import os

# ============================================================
# OUTLIER DETECTION AND HANDLING
# Smart Irrigation System - Milestone 2
# ============================================================

DATASET_PATH = "ml/ml_ready_dataset_multicrop.csv"

REPORT_DIR = "ml/eda_results"
os.makedirs(REPORT_DIR, exist_ok=True)

print("=" * 70)
print("OUTLIER DETECTION AND HANDLING")
print("=" * 70)

# ------------------------------------------------------------
# 1. Load dataset
# ------------------------------------------------------------

if not os.path.exists(DATASET_PATH):
    raise FileNotFoundError(
        f"Dataset not found: {DATASET_PATH}"
    )

df = pd.read_csv(DATASET_PATH)

print(f"\nDataset shape: {df.shape}")
print(f"Total records: {len(df)}")

# ------------------------------------------------------------
# 2. Numerical columns to inspect
# ------------------------------------------------------------

numeric_columns = [
    "soil_moisture",
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",
    "hour",
    "day_of_week",
    "day_of_month",
    "temperature",
    "humidity",
    "rainfall",
    "rain_probability",
    "growth_stage_multiplier",
    "crop_soil_moisture_mean",
    "crop_temperature_mean",
    "crop_humidity_mean",
    "crop_rainfall_mean",
    "crop_irrigation_frequency_mean",
    "crop_density_mean",
    "crop_pest_pressure_mean",
    "crop_fertilizer_usage_mean",
    "crop_frost_risk_mean",
    "crop_water_efficiency_mean",
    "crop_water_factor",
    "water_quantity_liters",
    "previous_water_usage_liters"
]

# Keep only columns actually present
numeric_columns = [
    col for col in numeric_columns
    if col in df.columns
]

# ------------------------------------------------------------
# 3. IQR-based outlier detection
# ------------------------------------------------------------

outlier_results = []

print("\n" + "=" * 70)
print("OUTLIER DETECTION USING IQR METHOD")
print("=" * 70)

for column in numeric_columns:

    series = pd.to_numeric(
        df[column],
        errors="coerce"
    ).dropna()

    if len(series) == 0:
        continue

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    outlier_mask = (
        (series < lower_bound) |
        (series > upper_bound)
    )

    outlier_count = int(outlier_mask.sum())

    outlier_percentage = (
        outlier_count / len(series) * 100
    )

    outlier_results.append({
        "column": column,
        "Q1": q1,
        "Q3": q3,
        "IQR": iqr,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "outlier_count": outlier_count,
        "outlier_percentage": outlier_percentage
    })

    print(
        f"{column:40s} "
        f"Outliers: {outlier_count:6d} "
        f"({outlier_percentage:.2f}%)"
    )

outlier_report = pd.DataFrame(outlier_results)

# Save detailed report
outlier_report.to_csv(
    f"{REPORT_DIR}/outlier_detection_report.csv",
    index=False
)

print(
    "\nOutlier detection report saved successfully."
)

# ------------------------------------------------------------
# 4. Determine columns requiring treatment
# ------------------------------------------------------------

columns_with_outliers = outlier_report[
    outlier_report["outlier_count"] > 0
]["column"].tolist()

print("\n" + "=" * 70)
print("OUTLIER SUMMARY")
print("=" * 70)

print(
    f"\nNumerical columns analyzed: "
    f"{len(numeric_columns)}"
)

print(
    f"Columns containing IQR outliers: "
    f"{len(columns_with_outliers)}"
)

if columns_with_outliers:
    print("\nColumns with detected IQR outliers:")

    for column in columns_with_outliers:
        row = outlier_report[
            outlier_report["column"] == column
        ].iloc[0]

        print(
            f"- {column}: "
            f"{int(row['outlier_count'])} "
            f"({row['outlier_percentage']:.2f}%)"
        )
else:
    print("\nNo IQR outliers detected.")

# ------------------------------------------------------------
# 5. Safe outlier handling
# ------------------------------------------------------------
#
# Agricultural boundary values such as high rainfall,
# temperature, soil moisture, etc. may be legitimate.
# Therefore, we do NOT blindly delete rows.
#
# For this milestone, we apply IQR clipping only to
# continuous derived variables where extreme values can
# distort downstream analysis.
#
# Original dataset remains unchanged.
# ------------------------------------------------------------

continuous_columns_for_clipping = [
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",
    "crop_soil_moisture_mean",
    "crop_temperature_mean",
    "crop_humidity_mean",
    "crop_rainfall_mean",
    "crop_irrigation_frequency_mean",
    "crop_density_mean",
    "crop_pest_pressure_mean",
    "crop_fertilizer_usage_mean",
    "crop_frost_risk_mean",
    "crop_water_efficiency_mean",
    "crop_water_factor",
    "previous_water_usage_liters"
]

continuous_columns_for_clipping = [
    col for col in continuous_columns_for_clipping
    if col in df.columns
]

df_clean = df.copy()

clipping_results = []

for column in continuous_columns_for_clipping:

    series = pd.to_numeric(
        df_clean[column],
        errors="coerce"
    )

    if series.dropna().empty:
        continue

    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    before_values = series.copy()

    df_clean[column] = series.clip(
        lower=lower_bound,
        upper=upper_bound
    )

    changed_count = int(
        (before_values != df_clean[column])
        .fillna(False)
        .sum()
    )

    clipping_results.append({
        "column": column,
        "lower_bound": lower_bound,
        "upper_bound": upper_bound,
        "values_clipped": changed_count
    })

clipping_report = pd.DataFrame(clipping_results)

clipping_report.to_csv(
    f"{REPORT_DIR}/outlier_handling_report.csv",
    index=False
)

# ------------------------------------------------------------
# 6. Save cleaned dataset
# ------------------------------------------------------------

cleaned_dataset_path = (
    "ml/ml_ready_dataset_multicrop_cleaned.csv"
)

df_clean.to_csv(
    cleaned_dataset_path,
    index=False
)

print(
    "\nOutlier handling report saved successfully."
)

print(
    f"Cleaned dataset saved to: "
    f"{cleaned_dataset_path}"
)

# ------------------------------------------------------------
# 7. Final verification
# ------------------------------------------------------------

print("\n" + "=" * 70)
print("OUTLIER ANALYSIS COMPLETED")
print("=" * 70)

print(
    f"\nOriginal records: {len(df)}"
)

print(
    f"Cleaned records: {len(df_clean)}"
)

print(
    f"Rows removed: {len(df) - len(df_clean)}"
)

total_clipped = int(
    clipping_report["values_clipped"].sum()
) if not clipping_report.empty else 0

print(
    f"Total values clipped: {total_clipped}"
)

print(
    "\nImportant: No rows were deleted."
)

print(
    "Legitimate agricultural boundary values were "
    "preserved while extreme derived continuous values "
    "were handled using IQR clipping."
)

print(
    "\nOutlier detection and handling completed successfully."
)