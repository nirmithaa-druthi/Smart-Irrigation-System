"""
Create a multi-crop ML training dataset for the
AI-Powered Smart Irrigation System.

This script:
1. Loads the existing PostgreSQL sensor and weather data.
2. Loads the 22-crop agricultural reference dataset.
3. Creates crop-specific reference profiles.
4. Combines the existing sensor time-series conditions with
   each supported crop profile to create simulated crop scenarios.
5. Generates a transparent rule-based irrigation target.
6. Saves the final dataset as ml/ml_ready_dataset_multicrop.csv.

IMPORTANT:
The water quantity target is derived/simulated, not measured
irrigation data. It should therefore be treated as a
synthetic training target.
"""

import os
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg2
from dotenv import load_dotenv


# ============================================================
# 1. PATHS AND CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

AGRICULTURAL_DATASET = Path(
    r"C:\Users\nirmi\Downloads\archive\Crop_recommendationV2.csv"
)

OUTPUT_FILE = PROJECT_ROOT / "ml" / "ml_ready_dataset_multicrop.csv"

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# 2. DATABASE CONNECTION
# ============================================================

def get_database_connection():
    """
    Connect to the existing smart_irrigation PostgreSQL database.
    """

    database_url = os.getenv("DATABASE_URL")

    if database_url:
        return psycopg2.connect(database_url)

    db_name = os.getenv("DB_NAME", "smart_irrigation")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")

    if not db_password:
        raise ValueError(
            "Database password not found. "
            "Check your .env file."
        )

    return psycopg2.connect(
        dbname=db_name,
        user=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
    )


# ============================================================
# 3. LOAD SENSOR DATA
# ============================================================

def load_sensor_data(connection):
    query = """
        SELECT
            field_id,
            sensor_id,
            timestamp,
            soil_moisture
        FROM sensor_data
        WHERE field_id = 'FIELD001'
        ORDER BY timestamp
    """

    df = pd.read_sql_query(query, connection)

    if df.empty:
        raise ValueError(
            "No sensor data found for FIELD001."
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ============================================================
# 4. LOAD WEATHER DATA
# ============================================================

def load_weather_data(connection):
    query = """
        SELECT
            field_id,
            location,
            timestamp,
            temperature,
            humidity,
            rainfall,
            rain_probability
        FROM weather_data
        WHERE field_id = 'FIELD001'
        ORDER BY timestamp
    """

    df = pd.read_sql_query(query, connection)

    if df.empty:
        raise ValueError(
            "No weather data found for FIELD001."
        )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


# ============================================================
# 5. LOAD CURRENT CROP CONFIGURATION
# ============================================================

def load_current_crop(connection):
    query = """
        SELECT
            field_id,
            crop_type,
            growth_stage
        FROM crop
        WHERE field_id = 'FIELD001'
        LIMIT 1
    """

    df = pd.read_sql_query(query, connection)

    if df.empty:
        print(
            "WARNING: No crop configuration found for FIELD001."
        )
        return None

    return df.iloc[0].to_dict()


# ============================================================
# 6. LOAD AGRICULTURAL DATASET
# ============================================================

def load_agricultural_dataset():
    if not AGRICULTURAL_DATASET.exists():
        raise FileNotFoundError(
            f"Agricultural dataset not found:\n"
            f"{AGRICULTURAL_DATASET}"
        )

    df = pd.read_csv(AGRICULTURAL_DATASET)

    required_columns = [
        "label",
        "soil_moisture",
        "temperature",
        "humidity",
        "rainfall",
        "irrigation_frequency",
        "crop_density",
        "pest_pressure",
        "fertilizer_usage",
        "frost_risk",
        "water_usage_efficiency",
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            "Agricultural dataset is missing columns: "
            + ", ".join(missing_columns)
        )

    return df


# ============================================================
# 7. CREATE CROP PROFILES
# ============================================================

def create_crop_profiles(agri_df):
    """
    Create one reference profile for every supported crop.
    """

    numeric_columns = [
        "soil_moisture",
        "temperature",
        "humidity",
        "rainfall",
        "irrigation_frequency",
        "crop_density",
        "pest_pressure",
        "fertilizer_usage",
        "frost_risk",
        "water_usage_efficiency",
    ]

    profiles = (
        agri_df
        .groupby("label")[numeric_columns]
        .mean()
        .reset_index()
    )

    profiles = profiles.rename(
        columns={
            "label": "crop_type",
            "soil_moisture": "crop_soil_moisture_mean",
            "temperature": "crop_temperature_mean",
            "humidity": "crop_humidity_mean",
            "rainfall": "crop_rainfall_mean",
            "irrigation_frequency": "crop_irrigation_frequency_mean",
            "crop_density": "crop_density_mean",
            "pest_pressure": "crop_pest_pressure_mean",
            "fertilizer_usage": "crop_fertilizer_usage_mean",
            "frost_risk": "crop_frost_risk_mean",
            "water_usage_efficiency": "crop_water_efficiency_mean",
        }
    )

    profiles["crop_type"] = (
        profiles["crop_type"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    return profiles


# ============================================================
# 8. PREPARE SENSOR FEATURES
# ============================================================

def prepare_sensor_features(sensor_df):
    df = sensor_df.copy()

    df = df.sort_values("timestamp").reset_index(drop=True)

    df["soil_moisture_change"] = (
        df["soil_moisture"]
        .diff()
        .fillna(0)
    )

    df["soil_moisture_rolling_mean"] = (
        df["soil_moisture"]
        .rolling(window=6, min_periods=1)
        .mean()
    )

    df["soil_moisture_stress"] = (
        22 - df["soil_moisture"]
    ).clip(lower=0)

    df["hour"] = df["timestamp"].dt.hour

    df["day_of_week"] = (
        df["timestamp"].dt.dayofweek
    )

    df["day_of_month"] = (
        df["timestamp"].dt.day
    )

    return df


# ============================================================
# 9. PREPARE WEATHER FEATURES
# ============================================================

def prepare_weather_features(weather_df):
    df = weather_df.copy()

    df = df.sort_values("timestamp").reset_index(drop=True)

    # Weather history is sparse compared with sensor history.
    # Interpolate numeric weather values across the sensor period.
    df = df.set_index("timestamp")

    return df


# ============================================================
# 10. GENERATE WEATHER VALUES FOR SENSOR TIMESTAMPS
# ============================================================

def align_weather_with_sensor(sensor_df, weather_df):
    """
    Align weather observations with sensor timestamps.

    Actual weather observations are used where available.
    Between observations, interpolation is used.

    If only a small number of weather observations exist,
    this remains an approximation and should not be treated
    as historical measured weather for every sensor reading.
    """

    sensor = sensor_df.copy()
    weather = weather_df.copy()

    weather = weather[
        [
            "timestamp",
            "temperature",
            "humidity",
            "rainfall",
            "rain_probability",
        ]
    ].sort_values("timestamp")

    combined = pd.merge_asof(
        sensor.sort_values("timestamp"),
        weather.sort_values("timestamp"),
        on="timestamp",
        direction="nearest",
    )

    # Fill any remaining weather gaps using available
    # weather-column averages.
    weather_columns = [
        "temperature",
        "humidity",
        "rainfall",
        "rain_probability",
    ]

    for column in weather_columns:
        if combined[column].isna().any():
            combined[column] = combined[column].fillna(
                weather[column].mean()
            )

    return combined


# ============================================================
# 11. CROP-SPECIFIC GROWTH STAGE
# ============================================================

def assign_growth_stage(crop_type, agri_df):
    """
    Use the most common growth_stage value for each crop
    from the agricultural reference dataset.

    We do NOT invent semantic names for stages 1, 2 and 3.
    """

    crop_rows = agri_df[
        agri_df["label"]
        .astype(str)
        .str.strip()
        .str.lower()
        == crop_type
    ]

    if crop_rows.empty:
        return 1

    mode = crop_rows["growth_stage"].mode()

    if mode.empty:
        return 1

    return int(mode.iloc[0])


# ============================================================
# 12. GROWTH-STAGE MULTIPLIER
# ============================================================

def calculate_growth_stage_multiplier(stage):
    """
    Numeric multiplier for irrigation demand.

    Since the agricultural dataset provides stages as
    1, 2 and 3 without documented semantic names,
    we use neutral increasing demand factors.
    """

    stage_mapping = {
        1: 0.90,
        2: 1.00,
        3: 1.10,
    }

    return stage_mapping.get(int(stage), 1.00)


# ============================================================
# 13. GENERATE IRRIGATION TARGET
# ============================================================

def calculate_water_quantity(row):
    """
    Generate a transparent synthetic irrigation target.

    This is NOT measured irrigation data.
    """

    soil = float(row["soil_moisture"])
    temperature = float(row["temperature"])
    humidity = float(row["humidity"])
    rainfall = float(row["rainfall"])
    rain_probability = float(row["rain_probability"])

    crop_efficiency = float(
        row["crop_water_efficiency_mean"]
    )

    growth_multiplier = float(
        row["growth_stage_multiplier"]
    )

    # --------------------------------------------------------
    # Base irrigation requirement from soil moisture
    # --------------------------------------------------------

    if soil >= 22:
        base_water = 0.0

    elif soil < 12:
        base_water = 30.0

    elif soil < 15:
        base_water = 25.0

    elif soil < 18:
        base_water = 20.0

    else:
        base_water = 12.0

    # --------------------------------------------------------
    # Temperature effect
    # --------------------------------------------------------

    if temperature >= 30:
        base_water *= 1.15

    elif temperature < 20:
        base_water *= 0.90

    # --------------------------------------------------------
    # Humidity effect
    # --------------------------------------------------------

    if humidity >= 75:
        base_water *= 0.90

    elif humidity < 50:
        base_water *= 1.10

    # --------------------------------------------------------
    # Rainfall effect
    # --------------------------------------------------------

    if rainfall > 0:
        base_water *= 0.50

    # --------------------------------------------------------
    # Rain probability effect
    # --------------------------------------------------------

    if rain_probability >= 50:
        base_water *= 0.75

    # --------------------------------------------------------
    # Crop water-efficiency adjustment
    #
    # Higher efficiency means less irrigation required.
    # --------------------------------------------------------

    overall_efficiency = 3.0

    crop_factor = (
        overall_efficiency / max(crop_efficiency, 0.1)
    )

    crop_factor = float(
        np.clip(crop_factor, 0.70, 1.30)
    )

    base_water *= crop_factor

    # --------------------------------------------------------
    # Growth stage effect
    # --------------------------------------------------------

    base_water *= growth_multiplier

    # --------------------------------------------------------
    # Final safety rules
    # --------------------------------------------------------

    if soil >= 22:
        return 0.0

    if rainfall > 5:
        return 0.0

    if rain_probability >= 80:
        return 0.0

    return round(max(base_water, 0.0), 2)


# ============================================================
# 14. CREATE MULTI-CROP DATASET
# ============================================================

def create_multicrop_dataset(
    sensor_df,
    weather_df,
    crop_profiles,
    agri_df,
):
    """
    Combine the continuous sensor conditions with all
    supported crop profiles.

    Each sensor observation becomes one simulated scenario
    for each supported crop.
    """

    sensor_features = prepare_sensor_features(sensor_df)

    combined_sensor_weather = align_weather_with_sensor(
        sensor_features,
        weather_df,
    )

    all_crop_datasets = []

    for _, crop_profile in crop_profiles.iterrows():

        crop_type = crop_profile["crop_type"]

        growth_stage = assign_growth_stage(
            crop_type,
            agri_df,
        )

        growth_multiplier = (
            calculate_growth_stage_multiplier(
                growth_stage
            )
        )

        crop_df = combined_sensor_weather.copy()

        crop_df["crop_type"] = crop_type

        crop_df["growth_stage"] = growth_stage

        crop_df["growth_stage_multiplier"] = (
            growth_multiplier
        )

        # ----------------------------------------------------
        # Add crop-specific reference features
        # ----------------------------------------------------

        for column in crop_profiles.columns:

            if column == "crop_type":
                continue

            crop_df[column] = crop_profile[column]

        # ----------------------------------------------------
        # Crop water factor
        # ----------------------------------------------------

        crop_df["crop_water_factor"] = (
            3.0
            / crop_df["crop_water_efficiency_mean"]
        )

        crop_df["crop_water_factor"] = (
            crop_df["crop_water_factor"]
            .clip(0.70, 1.30)
        )

        # ----------------------------------------------------
        # Synthetic water target
        # ----------------------------------------------------

        crop_df["water_quantity_liters"] = (
            crop_df.apply(
                calculate_water_quantity,
                axis=1,
            )
        )

        crop_df["irrigation_required"] = (
            crop_df["water_quantity_liters"] > 0
        )

        # ----------------------------------------------------
        # Historical water usage feature
        #
        # Within each crop scenario, previous water usage
        # is based on the previous timestamp.
        # ----------------------------------------------------

        crop_df["previous_water_usage_liters"] = (
            crop_df["water_quantity_liters"]
            .shift(1)
            .fillna(0)
        )

        all_crop_datasets.append(crop_df)

    final_df = pd.concat(
        all_crop_datasets,
        ignore_index=True,
    )

    return final_df


# ============================================================
# 15. DATA QUALITY CHECKS
# ============================================================

def validate_dataset(df):

    print("\n" + "=" * 60)
    print("DATA QUALITY CHECKS")
    print("=" * 60)

    print(
        f"Total records: {len(df)}"
    )

    print(
        f"Total columns: {len(df.columns)}"
    )

    print(
        f"Missing values: {df.isna().sum().sum()}"
    )

    print(
        f"Duplicate rows: {df.duplicated().sum()}"
    )

    invalid_soil = (
        (df["soil_moisture"] < 0)
        | (df["soil_moisture"] > 100)
    ).sum()

    print(
        f"Invalid soil moisture values: {invalid_soil}"
    )

    invalid_water = (
        df["water_quantity_liters"] < 0
    ).sum()

    print(
        f"Invalid water quantity values: {invalid_water}"
    )

    print("\nCrop distribution:")

    print(
        df["crop_type"]
        .value_counts()
        .sort_index()
    )

    print("\nIrrigation distribution:")

    print(
        df["irrigation_required"]
        .value_counts()
        .sort_index()
    )

    print("\nWater quantity statistics:")

    print(
        df["water_quantity_liters"]
        .describe()
    )


# ============================================================
# 16. SAVE DATASET
# ============================================================

def save_dataset(df):

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

    print(
        f"\nMulti-crop dataset saved to:\n"
        f"{OUTPUT_FILE}"
    )


# ============================================================
# 17. MAIN PROGRAM
# ============================================================

def main():

    print("=" * 60)
    print("MULTI-CROP DATASET GENERATION")
    print("AI-Powered Smart Irrigation System")
    print("=" * 60)

    # --------------------------------------------------------
    # Load database
    # --------------------------------------------------------

    print("\nConnecting to PostgreSQL...")

    connection = get_database_connection()

    try:

        # ----------------------------------------------------
        # Sensor data
        # ----------------------------------------------------

        print("Loading sensor data...")

        sensor_df = load_sensor_data(
            connection
        )

        print(
            f"Sensor records: {len(sensor_df)}"
        )

        print(
            f"Sensor period: "
            f"{sensor_df['timestamp'].min()} "
            f"to "
            f"{sensor_df['timestamp'].max()}"
        )

        # ----------------------------------------------------
        # Weather data
        # ----------------------------------------------------

        print("\nLoading weather data...")

        weather_df = load_weather_data(
            connection
        )

        print(
            f"Weather records: {len(weather_df)}"
        )

        # ----------------------------------------------------
        # Current DB crop
        # ----------------------------------------------------

        print("\nLoading current crop configuration...")

        current_crop = load_current_crop(
            connection
        )

        if current_crop:

            print(
                "Current database crop:"
                f" {current_crop['crop_type']}"
            )

            print(
                "Current database growth stage:"
                f" {current_crop['growth_stage']}"
            )

        # ----------------------------------------------------
        # Agricultural dataset
        # ----------------------------------------------------

        print(
            "\nLoading agricultural crop dataset..."
        )

        agri_df = load_agricultural_dataset()

        print(
            f"Agricultural records: "
            f"{len(agri_df)}"
        )

        crop_count = (
            agri_df["label"]
            .astype(str)
            .str.strip()
            .str.lower()
            .nunique()
        )

        print(
            f"Supported crops: {crop_count}"
        )

        # ----------------------------------------------------
        # Crop profiles
        # ----------------------------------------------------

        print(
            "\nCreating crop reference profiles..."
        )

        crop_profiles = create_crop_profiles(
            agri_df
        )

        print(
            f"Crop profiles created: "
            f"{len(crop_profiles)}"
        )

        print("\nSupported crops:")

        for crop in sorted(
            crop_profiles["crop_type"].tolist()
        ):
            print(f"  - {crop}")

        # ----------------------------------------------------
        # Create dataset
        # ----------------------------------------------------

        print(
            "\nGenerating multi-crop scenarios..."
        )

        final_df = create_multicrop_dataset(
            sensor_df=sensor_df,
            weather_df=weather_df,
            crop_profiles=crop_profiles,
            agri_df=agri_df,
        )

        # ----------------------------------------------------
        # Sort
        # ----------------------------------------------------

        final_df = final_df.sort_values(
            ["crop_type", "timestamp"]
        ).reset_index(drop=True)

        # ----------------------------------------------------
        # Validate
        # ----------------------------------------------------

        validate_dataset(final_df)

        # ----------------------------------------------------
        # Save
        # ----------------------------------------------------

        save_dataset(final_df)

        # ----------------------------------------------------
        # Final information
        # ----------------------------------------------------

        print("\n" + "=" * 60)
        print("MULTI-CROP DATASET GENERATION COMPLETE")
        print("=" * 60)

        print(
            f"Records generated: {len(final_df)}"
        )

        print(
            f"Crops represented: "
            f"{final_df['crop_type'].nunique()}"
        )

        print(
            f"Output file:\n{OUTPUT_FILE}"
        )

        print(
            "\nIMPORTANT:"
        )

        print(
            "The water_quantity_liters target is "
            "rule-generated/simulated. It is not "
            "measured irrigation data."
        )

    finally:

        connection.close()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()