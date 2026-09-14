"""
Multi-Crop Irrigation Prediction Engine
AI-Powered Smart Irrigation System

Uses the final multi-crop Random Forest model and the
22-crop agricultural reference dataset.

Input:
    Soil moisture
    Temperature
    Humidity
    Rainfall
    Rain probability
    Crop type
    Growth stage
    Time information
    Previous water usage

Output:
    Irrigation decision
    Predicted water quantity

IMPORTANT:
The trained target is synthetic/rule-generated.
"""

from pathlib import Path
import json

import joblib
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "final_multicrop_model.joblib"
)

FEATURES_PATH = (
    PROJECT_ROOT
    / "ml"
    / "models"
    / "final_multicrop_features.json"
)

CROP_DATASET_PATH = Path(
    r"C:\Users\nirmi\Downloads\archive\Crop_recommendationV2.csv"
)


# ============================================================
# LOAD MODEL
# ============================================================

if not MODEL_PATH.exists():
    raise FileNotFoundError(
        f"Final model not found:\n{MODEL_PATH}"
    )

model = joblib.load(
    MODEL_PATH
)


# ============================================================
# LOAD FEATURE LIST
# ============================================================

if not FEATURES_PATH.exists():
    raise FileNotFoundError(
        f"Feature list not found:\n{FEATURES_PATH}"
    )

with open(
    FEATURES_PATH,
    "r",
    encoding="utf-8",
) as file:

    FEATURES = json.load(file)


# ============================================================
# LOAD CROP DATA
# ============================================================

if not CROP_DATASET_PATH.exists():
    raise FileNotFoundError(
        f"Crop dataset not found:\n"
        f"{CROP_DATASET_PATH}"
    )

crop_dataset = pd.read_csv(
    CROP_DATASET_PATH
)

crop_dataset["crop_type"] = (
    crop_dataset["label"]
    .astype(str)
    .str.strip()
    .str.lower()
)


# ============================================================
# CREATE CROP PROFILES
# ============================================================

CROP_NUMERIC_COLUMNS = [
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

crop_profiles = (
    crop_dataset
    .groupby("crop_type")[CROP_NUMERIC_COLUMNS]
    .mean()
    .reset_index()
)

crop_profiles = crop_profiles.rename(
    columns={
        "soil_moisture":
            "crop_soil_moisture_mean",

        "temperature":
            "crop_temperature_mean",

        "humidity":
            "crop_humidity_mean",

        "rainfall":
            "crop_rainfall_mean",

        "irrigation_frequency":
            "crop_irrigation_frequency_mean",

        "crop_density":
            "crop_density_mean",

        "pest_pressure":
            "crop_pest_pressure_mean",

        "fertilizer_usage":
            "crop_fertilizer_usage_mean",

        "frost_risk":
            "crop_frost_risk_mean",

        "water_usage_efficiency":
            "crop_water_efficiency_mean",
    }
)


# ============================================================
# SUPPORTED CROPS
# ============================================================

SUPPORTED_CROPS = sorted(
    crop_profiles[
        "crop_type"
    ].tolist()
)


# ============================================================
# GROWTH STAGE MULTIPLIER
# ============================================================

def get_growth_stage_multiplier(
    growth_stage
):
    """
    The agricultural dataset contains growth_stage
    values 1, 2 and 3 without documented semantic names.

    Therefore this function accepts those numeric stages
    directly and does not invent names for them.
    """

    stage = int(
        growth_stage
    )

    mapping = {
        1: 0.90,
        2: 1.00,
        3: 1.10,
    }

    if stage not in mapping:

        raise ValueError(
            "growth_stage must be 1, 2 or 3."
        )

    return mapping[stage]


# ============================================================
# GET CROP PROFILE
# ============================================================

def get_crop_profile(
    crop_type
):

    crop_type = (
        str(crop_type)
        .strip()
        .lower()
    )

    if crop_type not in SUPPORTED_CROPS:

        raise ValueError(
            f"Unsupported crop: {crop_type}. "
            f"Supported crops are: "
            f"{', '.join(SUPPORTED_CROPS)}"
        )

    profile = crop_profiles[
        crop_profiles["crop_type"]
        == crop_type
    ]

    if profile.empty:

        raise ValueError(
            f"No profile found for crop: "
            f"{crop_type}"
        )

    return profile.iloc[0]


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_irrigation(
    soil_moisture,
    temperature,
    humidity,
    rainfall,
    rain_probability,
    crop_type,
    growth_stage,
    hour=6,
    day_of_week=0,
    day_of_month=1,
    previous_water_usage_liters=0.0,
):
    """
    Generate an irrigation prediction.

    Parameters
    ----------
    soil_moisture : float
        Current soil moisture percentage.

    temperature : float
        Temperature in Celsius.

    humidity : float
        Relative humidity percentage.

    rainfall : float
        Rainfall amount.

    rain_probability : float
        Probability of rain in percentage.

    crop_type : str
        One of the 22 supported crops.

    growth_stage : int
        1, 2 or 3.

    hour : int
        Hour of the prediction.

    day_of_week : int
        Monday = 0, Sunday = 6.

    day_of_month : int
        Day of month.

    previous_water_usage_liters : float
        Previous irrigation quantity.
    """

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if not 0 <= float(
        soil_moisture
    ) <= 100:

        raise ValueError(
            "soil_moisture must be between 0 and 100."
        )

    if not 0 <= float(
        humidity
    ) <= 100:

        raise ValueError(
            "humidity must be between 0 and 100."
        )

    if not 0 <= float(
        rain_probability
    ) <= 100:

        raise ValueError(
            "rain_probability must be between 0 and 100."
        )

    if not 0 <= int(hour) <= 23:

        raise ValueError(
            "hour must be between 0 and 23."
        )

    if not 0 <= int(day_of_week) <= 6:

        raise ValueError(
            "day_of_week must be between 0 and 6."
        )

    if not 1 <= int(day_of_month) <= 31:

        raise ValueError(
            "day_of_month must be between 1 and 31."
        )

    if float(
        previous_water_usage_liters
    ) < 0:

        raise ValueError(
            "previous_water_usage_liters "
            "cannot be negative."
        )

    # --------------------------------------------------------
    # Crop profile
    # --------------------------------------------------------

    crop_type = (
        str(crop_type)
        .strip()
        .lower()
    )

    profile = get_crop_profile(
        crop_type
    )

    # --------------------------------------------------------
    # Growth stage
    # --------------------------------------------------------

    growth_multiplier = (
        get_growth_stage_multiplier(
            growth_stage
        )
    )

    # --------------------------------------------------------
    # Crop water factor
    # --------------------------------------------------------

    crop_water_efficiency = float(
        profile[
            "crop_water_efficiency_mean"
        ]
    )

    crop_water_factor = (
        3.0
        / max(
            crop_water_efficiency,
            0.1,
        )
    )

    crop_water_factor = float(
        np.clip(
            crop_water_factor,
            0.70,
            1.30,
        )
    )

    # --------------------------------------------------------
    # Build feature dictionary
    # --------------------------------------------------------

    feature_values = {

        "soil_moisture":
            float(soil_moisture),

        # No previous sensor reading is available
        # at direct API inference time.
        "soil_moisture_change":
            0.0,

        # Use current soil moisture as the safest
        # single-observation rolling estimate.
        "soil_moisture_rolling_mean":
            float(soil_moisture),

        "soil_moisture_stress":
            max(
                22.0
                - float(soil_moisture),
                0.0,
            ),

        "temperature":
            float(temperature),

        "humidity":
            float(humidity),

        "rainfall":
            float(rainfall),

        "rain_probability":
            float(rain_probability),

        "hour":
            int(hour),

        "day_of_week":
            int(day_of_week),

        "day_of_month":
            int(day_of_month),

        "growth_stage_multiplier":
            float(growth_multiplier),

        "crop_soil_moisture_mean":
            float(
                profile[
                    "crop_soil_moisture_mean"
                ]
            ),

        "crop_temperature_mean":
            float(
                profile[
                    "crop_temperature_mean"
                ]
            ),

        "crop_humidity_mean":
            float(
                profile[
                    "crop_humidity_mean"
                ]
            ),

        "crop_rainfall_mean":
            float(
                profile[
                    "crop_rainfall_mean"
                ]
            ),

        "crop_irrigation_frequency_mean":
            float(
                profile[
                    "crop_irrigation_frequency_mean"
                ]
            ),

        "crop_density_mean":
            float(
                profile[
                    "crop_density_mean"
                ]
            ),

        "crop_pest_pressure_mean":
            float(
                profile[
                    "crop_pest_pressure_mean"
                ]
            ),

        "crop_fertilizer_usage_mean":
            float(
                profile[
                    "crop_fertilizer_usage_mean"
                ]
            ),

        "crop_frost_risk_mean":
            float(
                profile[
                    "crop_frost_risk_mean"
                ]
            ),

        "crop_water_efficiency_mean":
            crop_water_efficiency,

        "crop_water_factor":
            crop_water_factor,

        "previous_water_usage_liters":
            float(
                previous_water_usage_liters
            ),
    }

    # --------------------------------------------------------
    # Arrange features exactly as model expects
    # --------------------------------------------------------

    input_data = pd.DataFrame(
        [
            [
                feature_values[feature]
                for feature in FEATURES
            ]
        ],
        columns=FEATURES,
    )

    # --------------------------------------------------------
    # Model prediction
    # --------------------------------------------------------

    prediction = model.predict(
        input_data
    )[0]

    predicted_water = float(
        max(
            float(prediction),
            0.0,
        )
    )

    # --------------------------------------------------------
    # Safety rules
    # --------------------------------------------------------

    safety_reason = None

    if float(
        soil_moisture
    ) >= 22:

        predicted_water = 0.0

        safety_reason = (
            "Soil moisture is sufficient."
        )

    elif float(
        rainfall
    ) > 5:

        predicted_water = 0.0

        safety_reason = (
            "Recent rainfall is high."
        )

    elif float(
        rain_probability
    ) >= 80:

        predicted_water = 0.0

        safety_reason = (
            "High probability of rainfall."
        )

    # --------------------------------------------------------
    # Final irrigation decision
    # --------------------------------------------------------

    predicted_water = round(
        predicted_water,
        2,
    )

    irrigation_required = bool(
        predicted_water > 0
    )

    # --------------------------------------------------------
    # Reason
    # --------------------------------------------------------

    if safety_reason:

        reason = safety_reason

    elif irrigation_required:

        reason = (
            "Irrigation recommended based "
            "on soil moisture, weather, "
            "crop profile and growth stage."
        )

    else:

        reason = (
            "Current conditions do not "
            "require irrigation."
        )

    return {
        "irrigation_required":
            irrigation_required,

        "predicted_water_quantity_liters":
            predicted_water,

        "crop_type":
            crop_type,

        "growth_stage":
            int(growth_stage),

        "reason":
            reason,
    }


# ============================================================
# DISPLAY SUPPORTED CROPS
# ============================================================

def get_supported_crops():

    return SUPPORTED_CROPS


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("MULTI-CROP IRRIGATION PREDICTION ENGINE")
    print("=" * 60)

    print(
        f"\nSupported crops: "
        f"{len(SUPPORTED_CROPS)}"
    )

    print(
        ", ".join(
            SUPPORTED_CROPS
        )
    )

    print(
        "\nRunning sample prediction..."
    )

    result = predict_irrigation(
        soil_moisture=15.0,
        temperature=29.0,
        humidity=60.0,
        rainfall=0.0,
        rain_probability=20.0,
        crop_type="rice",
        growth_stage=2,
        hour=6,
        day_of_week=0,
        day_of_month=1,
        previous_water_usage_liters=10.0,
    )

    print("\nPrediction:")

    print(
        json.dumps(
            result,
            indent=4,
        )
    )

    print(
        "\nPrediction engine test completed."
    )