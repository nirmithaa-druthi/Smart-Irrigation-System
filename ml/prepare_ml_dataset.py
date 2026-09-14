import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

CROP_DATASET_PATH = (
    r"C:\Users\nirmi\Downloads\archive\Crop_recommendationV2.csv"
)


# ============================================================
# 2. CONNECT TO POSTGRESQL
# ============================================================

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

print("Connected to PostgreSQL successfully.\n")


# ============================================================
# 3. LOAD SENSOR DATA
# ============================================================

sensor_query = """
SELECT
    sensor_id,
    field_id,
    timestamp,
    soil_moisture
FROM sensor_data
WHERE field_id = 'FIELD001'
ORDER BY timestamp;
"""

sensor_df = pd.read_sql(sensor_query, conn)

print("========== SENSOR DATA ==========")
print("Total sensor records:", len(sensor_df))
print(sensor_df.head())
print()


# ============================================================
# 4. LOAD WEATHER DATA
# ============================================================

weather_query = """
SELECT
    field_id,
    timestamp,
    temperature,
    humidity,
    rainfall,
    rain_probability
FROM weather_data
WHERE field_id = 'FIELD001'
ORDER BY timestamp;
"""

weather_df = pd.read_sql(weather_query, conn)

print("========== WEATHER DATA ==========")
print("Total weather records:", len(weather_df))
print(weather_df.head())
print()


# ============================================================
# 5. LOAD CURRENT FIELD/CROP CONFIGURATION
# ============================================================

crop_query = """
SELECT
    field_id,
    crop_type,
    growth_stage
FROM crop
WHERE field_id = 'FIELD001'
ORDER BY field_id;
"""

crop_df = pd.read_sql(crop_query, conn)

print("========== DATABASE CROP DATA ==========")
print(crop_df)
print()


# ============================================================
# 6. LOAD AGRICULTURAL MULTI-CROP DATASET
# ============================================================

print("========== AGRICULTURAL CROP DATASET ==========")

if not os.path.exists(CROP_DATASET_PATH):
    raise FileNotFoundError(
        f"Crop dataset not found at: {CROP_DATASET_PATH}"
    )

agri_df = pd.read_csv(CROP_DATASET_PATH)

print("Total agricultural records:", len(agri_df))
print("Total crops:", agri_df["label"].nunique())
print("Crops:")
print(sorted(agri_df["label"].unique()))
print()


# ============================================================
# 7. AGRICULTURAL DATA QUALITY CHECKS
# ============================================================

print("========== AGRICULTURAL DATA QUALITY ==========")

print("Missing values:")
print(agri_df.isnull().sum().sum())

print("Duplicate records:", agri_df.duplicated().sum())

print(
    "Invalid soil moisture values:",
    (
        (agri_df["soil_moisture"] < 0)
        | (agri_df["soil_moisture"] > 100)
    ).sum()
)

print()


# ============================================================
# 8. CREATE CROP-SPECIFIC REFERENCE FEATURES
# ============================================================

print("========== CROP-SPECIFIC FEATURES ==========")

crop_reference = (
    agri_df.groupby("label")
    .agg(
        crop_soil_moisture_mean=("soil_moisture", "mean"),
        crop_temperature_mean=("temperature", "mean"),
        crop_humidity_mean=("humidity", "mean"),
        crop_rainfall_mean=("rainfall", "mean"),
        crop_irrigation_frequency_mean=("irrigation_frequency", "mean"),
        crop_water_efficiency_mean=("water_usage_efficiency", "mean"),
        crop_density_mean=("crop_density", "mean"),
        crop_pest_pressure_mean=("pest_pressure", "mean"),
        crop_fertilizer_usage_mean=("fertilizer_usage", "mean"),
        crop_frost_risk_mean=("frost_risk", "mean")
    )
    .reset_index()
)

print("Crop reference records:", len(crop_reference))
print(crop_reference.round(2).to_string(index=False))
print()


# ============================================================
# 9. CURRENT FIELD CROP
# ============================================================

current_crop = crop_df.iloc[0]["crop_type"].strip().lower()

print("Current database crop:", current_crop)

if current_crop not in set(agri_df["label"].str.lower()):
    print(
        "Warning: current database crop is not present "
        "in the agricultural dataset."
    )

print()


# ============================================================
# 10. DATA QUALITY CHECKS
# ============================================================

print("========== SENSOR / WEATHER / CROP QUALITY ==========")

print("\nMissing values - Sensor:")
print(sensor_df.isnull().sum())

print("\nMissing values - Weather:")
print(weather_df.isnull().sum())

print("\nMissing values - Crop:")
print(crop_df.isnull().sum())

print("\nDuplicate sensor records:", sensor_df.duplicated().sum())
print("Duplicate weather records:", weather_df.duplicated().sum())

print("\nInvalid sensor soil moisture:")
print(
    (
        (sensor_df["soil_moisture"] < 0)
        | (sensor_df["soil_moisture"] > 100)
    ).sum()
)

print("\nInvalid weather values:")

print(
    "Temperature:",
    (
        (weather_df["temperature"] < -50)
        | (weather_df["temperature"] > 60)
    ).sum()
)

print(
    "Humidity:",
    (
        (weather_df["humidity"] < 0)
        | (weather_df["humidity"] > 100)
    ).sum()
)

print(
    "Rainfall:",
    (weather_df["rainfall"] < 0).sum()
)

print(
    "Rain probability:",
    (
        (weather_df["rain_probability"] < 0)
        | (weather_df["rain_probability"] > 100)
    ).sum()
)

print()


# ============================================================
# 11. SENSOR STATISTICS
# ============================================================

print("========== SENSOR STATISTICS ==========")

print(sensor_df["soil_moisture"].describe())

Q1 = sensor_df["soil_moisture"].quantile(0.25)
Q3 = sensor_df["soil_moisture"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = sensor_df[
    (sensor_df["soil_moisture"] < lower_bound)
    | (sensor_df["soil_moisture"] > upper_bound)
]

print("\nNumber of soil moisture outliers:", len(outliers))

print("\nSensor date range:")
print("From:", sensor_df["timestamp"].min())
print("To  :", sensor_df["timestamp"].max())

print("\nWeather date range:")
print("From:", weather_df["timestamp"].min())
print("To  :", weather_df["timestamp"].max())

print()


# ============================================================
# 12. WEATHER EDA
# ============================================================

print("========== WEATHER EDA ==========")

print(
    "Average temperature:",
    weather_df["temperature"].mean()
)

print(
    "Average humidity:",
    weather_df["humidity"].mean()
)

print(
    "Total rainfall:",
    weather_df["rainfall"].sum()
)

print(
    "Average rain probability:",
    weather_df["rain_probability"].mean()
)

print(
    "Maximum rainfall:",
    weather_df["rainfall"].max()
)

print()


# ============================================================
# 13. PREPARE SENSOR + FIELD CROP DATA
# ============================================================

sensor_df["timestamp"] = pd.to_datetime(
    sensor_df["timestamp"]
)

weather_df["timestamp"] = pd.to_datetime(
    weather_df["timestamp"]
)

crop_info = crop_df[
    ["field_id", "crop_type", "growth_stage"]
].drop_duplicates()

sensor_crop_df = sensor_df.merge(
    crop_info,
    on="field_id",
    how="left"
)

print("========== SENSOR + CURRENT CROP ==========")
print("Total records:", len(sensor_crop_df))
print(
    "Missing crop information:",
    sensor_crop_df["crop_type"].isnull().sum()
)
print()


# ============================================================
# 14. ADD CROP-SPECIFIC REFERENCE FEATURES
# ============================================================

sensor_crop_df["crop_key"] = (
    sensor_crop_df["crop_type"]
    .str.strip()
    .str.lower()
)

sensor_crop_df = sensor_crop_df.merge(
    crop_reference,
    left_on="crop_key",
    right_on="label",
    how="left"
)

sensor_crop_df.drop(
    columns=["crop_key", "label"],
    inplace=True
)

print("Crop-specific reference features added.")

print(
    "\nMissing crop reference values:"
)

print(
    sensor_crop_df[
        [
            "crop_soil_moisture_mean",
            "crop_temperature_mean",
            "crop_humidity_mean",
            "crop_rainfall_mean",
            "crop_irrigation_frequency_mean",
            "crop_water_efficiency_mean"
        ]
    ].isnull().sum()
)

print()


# ============================================================
# 15. HISTORICAL WEATHER FEATURES
# ============================================================

# Actual weather_data contains only a small number of
# observations. Therefore, available weather observations
# are used as the basis for derived historical weather
# features.
#
# These historical values are simulated/derived and are
# not claimed to be actual historical measurements.

weather_means = {
    "temperature": weather_df["temperature"].mean(),
    "humidity": weather_df["humidity"].mean(),
    "rainfall": weather_df["rainfall"].mean(),
    "rain_probability": weather_df["rain_probability"].mean()
}

print("========== HISTORICAL WEATHER ==========")
print("Available weather records:", len(weather_df))
print("Using available weather observations to derive")
print("historical weather features.")
print("These values are simulated/derived,")
print("not actual historical measurements.")
print()


# ============================================================
# 16. CREATE ML DATAFRAME
# ============================================================

ml_df = sensor_crop_df.copy()

ml_df["temperature"] = weather_means["temperature"]
ml_df["humidity"] = weather_means["humidity"]
ml_df["rainfall"] = weather_means["rainfall"]
ml_df["rain_probability"] = weather_means["rain_probability"]


# ============================================================
# 17. TIME FEATURES
# ============================================================

ml_df["hour"] = ml_df["timestamp"].dt.hour
ml_df["day_of_week"] = ml_df["timestamp"].dt.dayofweek
ml_df["day_of_month"] = ml_df["timestamp"].dt.day


# ============================================================
# 18. WEATHER VARIATION
# ============================================================

ml_df["temperature"] = (
    ml_df["temperature"]
    + ((ml_df["hour"] - 12).abs() * -0.08)
)

ml_df["humidity"] = (
    ml_df["humidity"]
    + ((18 - ml_df["hour"]).abs() * 0.25)
)

ml_df["humidity"] = ml_df["humidity"].clip(0, 100)
ml_df["temperature"] = ml_df["temperature"].clip(-50, 60)


# ============================================================
# 19. SOIL MOISTURE FEATURES
# ============================================================

ml_df = ml_df.sort_values(
    "timestamp"
).reset_index(drop=True)

ml_df["soil_moisture_change"] = (
    ml_df["soil_moisture"].diff()
)

ml_df["soil_moisture_rolling_mean"] = (
    ml_df["soil_moisture"]
    .rolling(window=5, min_periods=1)
    .mean()
)

ml_df["soil_moisture_stress"] = (
    25 - ml_df["soil_moisture"]
).clip(lower=0)


# ============================================================
# 20. WEATHER FEATURES
# ============================================================

ml_df["rain_expected"] = (
    ml_df["rain_probability"] >= 50
).astype(int)


# ============================================================
# 21. CROP / GROWTH-STAGE FEATURES
# ============================================================

growth_stage_multiplier = {
    "Seedling": 0.8,
    "Vegetative": 1.1,
    "Flowering": 1.2,
    "Fruiting": 1.15,
    "Maturity": 0.9
}

ml_df["growth_stage_multiplier"] = (
    ml_df["growth_stage"]
    .map(growth_stage_multiplier)
    .fillna(1.0)
)


# ============================================================
# 22. CROP-SPECIFIC WATER FACTOR
# ============================================================

# Water usage efficiency is used as a crop-specific
# reference factor.
#
# Higher efficiency means less additional water is required.
#
# The factor is normalized around the overall dataset mean.

overall_efficiency = (
    agri_df["water_usage_efficiency"].mean()
)

ml_df["crop_water_factor"] = (
    overall_efficiency
    / ml_df["crop_water_efficiency_mean"]
)

ml_df["crop_water_factor"] = (
    ml_df["crop_water_factor"]
    .clip(0.70, 1.30)
)


# ============================================================
# 23. GENERATE WATER-QUANTITY TARGET
# ============================================================

def calculate_water_quantity(row):

    soil = row["soil_moisture"]

    # No irrigation when soil moisture is sufficient
    if soil >= 22:
        return 0.0

    # Base quantity according to soil moisture
    if soil < 12:
        water = 30
    elif soil < 15:
        water = 25
    elif soil < 18:
        water = 20
    elif soil < 22:
        water = 12
    else:
        water = 0

    # Crop growth stage
    water *= row["growth_stage_multiplier"]

    # Crop-specific water efficiency
    water *= row["crop_water_factor"]

    # Temperature effect
    if row["temperature"] >= 30:
        water *= 1.15
    elif row["temperature"] < 20:
        water *= 0.90

    # Humidity effect
    if row["humidity"] >= 75:
        water *= 0.90
    elif row["humidity"] < 50:
        water *= 1.10

    # Rainfall effect
    if row["rainfall"] > 0:
        water *= 0.50

    # Rain probability effect
    if row["rain_probability"] >= 50:
        water *= 0.75

    return round(
        max(water, 0),
        2
    )


ml_df["water_quantity_liters"] = (
    ml_df.apply(
        calculate_water_quantity,
        axis=1
    )
)


# ============================================================
# 24. IRRIGATION REQUIRED
# ============================================================

ml_df["irrigation_required"] = (
    ml_df["water_quantity_liters"] > 0
).astype(int)


# ============================================================
# 25. HISTORICAL IRRIGATION FEATURE
# ============================================================

ml_df["previous_water_usage_liters"] = (
    ml_df["water_quantity_liters"]
    .shift(1)
    .fillna(0)
)


# ============================================================
# 26. DISPLAY TARGET STATISTICS
# ============================================================

print("========== HISTORICAL WATER USAGE ==========")

print(
    ml_df["water_quantity_liters"].describe()
)

print("\nIrrigation requirement distribution:")

print(
    ml_df["irrigation_required"]
    .value_counts()
    .sort_index()
)

print(
    "\nCurrent crop distribution:"
)

print(
    ml_df["crop_type"].value_counts()
)

print()


# ============================================================
# 27. HANDLE MISSING VALUES
# ============================================================

ml_df["soil_moisture_change"] = (
    ml_df["soil_moisture_change"]
    .fillna(0)
)

ml_df["soil_moisture_rolling_mean"] = (
    ml_df["soil_moisture_rolling_mean"]
    .fillna(ml_df["soil_moisture"])
)

ml_df = ml_df.dropna(
    subset=[
        "soil_moisture",
        "temperature",
        "humidity",
        "rainfall",
        "rain_probability",
        "crop_type",
        "growth_stage",
        "crop_water_factor",
        "water_quantity_liters"
    ]
)


# ============================================================
# 28. SELECT FINAL ML FEATURES
# ============================================================

final_columns = [
    "timestamp",
    "field_id",

    "soil_moisture",
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",

    "temperature",
    "humidity",
    "rainfall",
    "rain_probability",
    "rain_expected",

    "hour",
    "day_of_week",
    "day_of_month",

    "crop_type",
    "growth_stage",
    "growth_stage_multiplier",

    "crop_soil_moisture_mean",
    "crop_temperature_mean",
    "crop_humidity_mean",
    "crop_rainfall_mean",
    "crop_irrigation_frequency_mean",
    "crop_water_efficiency_mean",
    "crop_density_mean",
    "crop_pest_pressure_mean",
    "crop_fertilizer_usage_mean",
    "crop_frost_risk_mean",
    "crop_water_factor",

    "previous_water_usage_liters",

    "water_quantity_liters",
    "irrigation_required"
]

ml_ready_df = ml_df[
    final_columns
].copy()


# ============================================================
# 29. FINAL DATASET CHECK
# ============================================================

print("========== FINAL ML DATASET ==========")

print(
    "Final records:",
    len(ml_ready_df)
)

print(
    "Final columns:",
    len(ml_ready_df.columns)
)

print("\nFinal features:")

print(
    ml_ready_df.columns.tolist()
)

print("\nFinal missing values:")

print(
    ml_ready_df.isnull().sum()
)

print("\nFinal crop distribution:")

print(
    ml_ready_df["crop_type"].value_counts()
)

print("\nFinal target statistics:")

print(
    ml_ready_df["water_quantity_liters"].describe()
)

print("\nFinal irrigation distribution:")

print(
    ml_ready_df["irrigation_required"]
    .value_counts()
    .sort_index()
)


# ============================================================
# 30. SAVE ML-READY DATASET
# ============================================================

output_path = "ml/ml_ready_dataset.csv"

ml_ready_df.to_csv(
    output_path,
    index=False
)

print("\nML-ready dataset saved to:")
print(output_path)


# ============================================================
# 31. CLOSE DATABASE CONNECTION
# ============================================================

conn.close()

print("\nDatabase connection closed.")
print("Multi-crop ML dataset preparation completed successfully.")