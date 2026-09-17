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
# 5. LOAD CROP DATA
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

print("========== CROP DATA ==========")
print(crop_df)
print()


# ============================================================
# 6. DATA QUALITY CHECKS
# ============================================================

print("========== DATA QUALITY CHECKS ==========")

print("\nMissing values - Sensor:")
print(sensor_df.isnull().sum())

print("\nMissing values - Weather:")
print(weather_df.isnull().sum())

print("\nMissing values - Crop:")
print(crop_df.isnull().sum())

print("\nDuplicate sensor records:", sensor_df.duplicated().sum())
print("Duplicate weather records:", weather_df.duplicated().sum())

print("\nInvalid soil moisture values:")
print(((sensor_df["soil_moisture"] < 0) |
       (sensor_df["soil_moisture"] > 100)).sum())

print("\nInvalid weather values:")

print(
    "Temperature:",
    ((weather_df["temperature"] < -50) |
     (weather_df["temperature"] > 60)).sum()
)

print(
    "Humidity:",
    ((weather_df["humidity"] < 0) |
     (weather_df["humidity"] > 100)).sum()
)

print(
    "Rainfall:",
    (weather_df["rainfall"] < 0).sum()
)

print(
    "Rain probability:",
    ((weather_df["rain_probability"] < 0) |
     (weather_df["rain_probability"] > 100)).sum()
)


# ============================================================
# 7. SENSOR DATA STATISTICS
# ============================================================

print("\n========== SENSOR STATISTICS ==========")

print(sensor_df["soil_moisture"].describe())

Q1 = sensor_df["soil_moisture"].quantile(0.25)
Q3 = sensor_df["soil_moisture"].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

outliers = sensor_df[
    (sensor_df["soil_moisture"] < lower_bound) |
    (sensor_df["soil_moisture"] > upper_bound)
]

print("\nNumber of soil moisture outliers:", len(outliers))

print("\nSensor date range:")
print("From:", sensor_df["timestamp"].min())
print("To  :", sensor_df["timestamp"].max())

print("\nWeather date range:")
print("From:", weather_df["timestamp"].min())
print("To  :", weather_df["timestamp"].max())


# ============================================================
# 8. BASIC WEATHER EDA
# ============================================================

print("\n========== WEATHER EDA ==========")

print("Average temperature:",
      weather_df["temperature"].mean())

print("Average humidity:",
      weather_df["humidity"].mean())

print("Total rainfall:",
      weather_df["rainfall"].sum())

print("Average rain probability:",
      weather_df["rain_probability"].mean())

print("Maximum rainfall:",
      weather_df["rainfall"].max())


# ============================================================
# 9. COMBINE SENSOR + CROP DATA
# ============================================================

sensor_df["timestamp"] = pd.to_datetime(sensor_df["timestamp"])
weather_df["timestamp"] = pd.to_datetime(weather_df["timestamp"])

crop_info = crop_df[
    ["field_id", "crop_type", "growth_stage"]
].drop_duplicates()

sensor_crop_df = sensor_df.merge(
    crop_info,
    on="field_id",
    how="left"
)

print("\n========== SENSOR + CROP ==========")
print("Total records:", len(sensor_crop_df))
print("Missing crop information:")
print(sensor_crop_df["crop_type"].isnull().sum())


# ============================================================
# 10. CREATE HISTORICAL WEATHER FEATURES
# ============================================================
#
# Actual weather_data contains only a small number of records.
# Therefore, for historical ML preparation, we derive a
# simulated historical weather series from the available
# weather observations.
#
# These values are NOT claimed to be actual historical
# measurements.
# ============================================================

weather_means = {
    "temperature": weather_df["temperature"].mean(),
    "humidity": weather_df["humidity"].mean(),
    "rainfall": weather_df["rainfall"].mean(),
    "rain_probability": weather_df["rain_probability"].mean()
}

print("\n========== HISTORICAL WEATHER ==========")
print("Available weather records:", len(weather_df))
print("Using available weather observations to derive")
print("historical weather features for ML preparation.")
print("These historical values are simulated/derived,")
print("not actual historical measurements.")


# Create a copy
ml_df = sensor_crop_df.copy()

# Base historical weather values
ml_df["temperature"] = weather_means["temperature"]
ml_df["humidity"] = weather_means["humidity"]
ml_df["rainfall"] = weather_means["rainfall"]
ml_df["rain_probability"] = weather_means["rain_probability"]


# Add small deterministic time-based variation.
# This avoids making every historical row identical.

ml_df["hour"] = ml_df["timestamp"].dt.hour
ml_df["day_of_week"] = ml_df["timestamp"].dt.dayofweek
ml_df["day_of_month"] = ml_df["timestamp"].dt.day


# Temperature variation based on hour
ml_df["temperature"] = (
    ml_df["temperature"]
    + ((ml_df["hour"] - 12).abs() * -0.08)
)

# Humidity variation based on hour
ml_df["humidity"] = (
    ml_df["humidity"]
    + ((18 - ml_df["hour"]).abs() * 0.25)
)

# Keep values within valid ranges
ml_df["humidity"] = ml_df["humidity"].clip(0, 100)
ml_df["temperature"] = ml_df["temperature"].clip(-50, 60)


# ============================================================
# 11. FEATURE ENGINEERING - SOIL MOISTURE
# ============================================================

ml_df = ml_df.sort_values("timestamp").reset_index(drop=True)

ml_df["soil_moisture_change"] = (
    ml_df["soil_moisture"].diff()
)

ml_df["soil_moisture_rolling_mean"] = (
    ml_df["soil_moisture"]
    .rolling(window=5, min_periods=1)
    .mean()
)

# Soil moisture stress
ml_df["soil_moisture_stress"] = (
    25 - ml_df["soil_moisture"]
).clip(lower=0)


# ============================================================
# 12. WEATHER FEATURES
# ============================================================

ml_df["rain_expected"] = (
    ml_df["rain_probability"] >= 50
).astype(int)


# ============================================================
# 13. CROP / GROWTH-STAGE FEATURES
# ============================================================

# Vegetative stage gets higher water requirement.
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
# 14. GENERATE HISTORICAL WATER-USAGE TARGET
# ============================================================
#
# Target:
# water_quantity_liters
#
# Irrigation is required only when soil moisture is below
# the threshold.
#
# This creates both irrigation-required and
# irrigation-not-required cases.
# ============================================================

def calculate_water_quantity(row):

    soil = row["soil_moisture"]

    # No irrigation when soil is sufficiently moist
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

    # Crop growth stage effect
    water *= row["growth_stage_multiplier"]

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

    return round(max(water, 0), 2)


ml_df["water_quantity_liters"] = ml_df.apply(
    calculate_water_quantity,
    axis=1
)


# ============================================================
# 15. IRRIGATION REQUIRED
# ============================================================

ml_df["irrigation_required"] = (
    ml_df["water_quantity_liters"] > 0
).astype(int)


# ============================================================
# 16. HISTORICAL IRRIGATION FEATURE
# ============================================================
#
# Previous water usage is a historical feature.
# It does NOT use the current target.
# ============================================================

ml_df["previous_water_usage_liters"] = (
    ml_df["water_quantity_liters"]
    .shift(1)
    .fillna(0)
)


# ============================================================
# 17. DISPLAY TARGET STATISTICS
# ============================================================

print("\n========== HISTORICAL WATER USAGE ==========")

print(
    ml_df["water_quantity_liters"].describe()
)

print("\nIrrigation requirement distribution:")
print(
    ml_df["irrigation_required"].value_counts()
    .sort_index()
)

print("\nPrevious water usage sample:")
print(
    ml_df[
        [
            "timestamp",
            "water_quantity_liters",
            "previous_water_usage_liters"
        ]
    ].head(10)
)


# ============================================================
# 18. HANDLE MISSING VALUES
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
        "water_quantity_liters"
    ]
)


# ============================================================
# 19. SELECT FINAL ML FEATURES
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
    "previous_water_usage_liters",
    "water_quantity_liters",
    "irrigation_required"
]

ml_ready_df = ml_df[final_columns].copy()


# ============================================================
# 20. FINAL DATASET CHECK
# ============================================================

print("\n========== FINAL ML DATASET ==========")

print("Final records:", len(ml_ready_df))

print("\nFinal features:")
print(
    ml_ready_df.columns.tolist()
)

print("\nFinal missing values:")
print(
    ml_ready_df.isnull().sum()
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
# 21. SAVE ML-READY DATASET
# ============================================================

output_path = "ml/ml_ready_dataset.csv"

ml_ready_df.to_csv(
    output_path,
    index=False
)

print("\nML-ready dataset saved to:")
print(output_path)


# ============================================================
# 22. CLOSE DATABASE CONNECTION
# ============================================================

conn.close()

print("\nDatabase connection closed.")
print("ML dataset preparation completed successfully.")