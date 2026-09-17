"""
Multi-Crop Gradient Boosting Model
AI-Powered Smart Irrigation System

Uses:
    ml/ml_ready_dataset_multicrop.csv

The water_quantity_liters target is synthetic/rule-generated.
"""

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATASET_PATH = (
    PROJECT_ROOT
    / "ml"
    / "ml_ready_dataset_multicrop.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "ml"
    / "models"
)

MODEL_PATH = (
    MODEL_DIR
    / "gradient_boosting_multicrop_model.joblib"
)

METADATA_PATH = (
    MODEL_DIR
    / "gradient_boosting_multicrop_metadata.json"
)

FEATURES_PATH = (
    MODEL_DIR
    / "gradient_boosting_multicrop_features.json"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    # Sensor features
    "soil_moisture",
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",

    # Weather features
    "temperature",
    "humidity",
    "rainfall",
    "rain_probability",

    # Time features
    "hour",
    "day_of_week",
    "day_of_month",

    # Crop growth
    "growth_stage_multiplier",

    # Crop reference features
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

    # Crop water adjustment
    "crop_water_factor",

    # Historical water usage
    "previous_water_usage_liters",
]

TARGET = "water_quantity_liters"


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("=" * 60)
    print("MULTI-CROP GRADIENT BOOSTING MODEL")
    print("=" * 60)

    print("\nLoading dataset...")

    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(DATASET_PATH)

    print(
        f"Dataset records: {len(df)}"
    )

    print(
        f"Dataset columns: {len(df.columns)}"
    )

    print(
        f"Crops: {df['crop_type'].nunique()}"
    )

    print(
        f"Missing values: {df.isna().sum().sum()}"
    )

    return df


# ============================================================
# VALIDATE FEATURES
# ============================================================

def validate_features(df):

    missing_features = [
        feature
        for feature in FEATURES
        if feature not in df.columns
    ]

    if missing_features:

        raise ValueError(
            "Missing required features:\n"
            + "\n".join(missing_features)
        )

    if TARGET not in df.columns:

        raise ValueError(
            f"Target column '{TARGET}' not found."
        )


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

def chronological_split(df):

    """
    Keep observations in chronological order.

    70% training
    15% validation
    15% testing
    """

    df = df.sort_values(
        "timestamp"
    ).reset_index(drop=True)

    total = len(df)

    train_end = int(
        total * 0.70
    )

    validation_end = int(
        total * 0.85
    )

    train_df = df.iloc[
        :train_end
    ].copy()

    validation_df = df.iloc[
        train_end:validation_end
    ].copy()

    test_df = df.iloc[
        validation_end:
    ].copy()

    return (
        train_df,
        validation_df,
        test_df,
    )


# ============================================================
# METRICS
# ============================================================

def calculate_metrics(
    model,
    X,
    y,
):

    predictions = model.predict(X)

    mae = mean_absolute_error(
        y,
        predictions,
    )

    rmse = mean_squared_error(
        y,
        predictions,
    ) ** 0.5

    r2 = r2_score(
        y,
        predictions,
    )

    return {
        "MAE": float(mae),
        "RMSE": float(rmse),
        "R2": float(r2),
    }


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_dataset()

    validate_features(df)

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    df = df.dropna(
        subset=FEATURES + [TARGET]
    ).copy()

    print(
        f"\nRecords after validation: "
        f"{len(df)}"
    )

    # --------------------------------------------------------
    # Chronological split
    # --------------------------------------------------------

    (
        train_df,
        validation_df,
        test_df,
    ) = chronological_split(df)

    print("\nChronological split:")

    print(
        f"Training:   {len(train_df)}"
    )

    print(
        f"Validation: {len(validation_df)}"
    )

    print(
        f"Test:       {len(test_df)}"
    )

    # --------------------------------------------------------
    # Prepare X and y
    # --------------------------------------------------------

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_validation = validation_df[FEATURES]
    y_validation = validation_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    # --------------------------------------------------------
    # Train Gradient Boosting
    # --------------------------------------------------------

    print(
        "\nTraining Gradient Boosting..."
    )

    model = GradientBoostingRegressor(
        n_estimators=150,
        learning_rate=0.1,
        max_depth=3,
        random_state=42,
    )

    model.fit(
        X_train,
        y_train,
    )

    print(
        "Gradient Boosting training completed."
    )

    # --------------------------------------------------------
    # Validation metrics
    # --------------------------------------------------------

    validation_metrics = calculate_metrics(
        model,
        X_validation,
        y_validation,
    )

    print("\nValidation metrics:")

    print(
        f"MAE  : {validation_metrics['MAE']:.4f}"
    )

    print(
        f"RMSE : {validation_metrics['RMSE']:.4f}"
    )

    print(
        f"R²   : {validation_metrics['R2']:.4f}"
    )

    # --------------------------------------------------------
    # Test metrics
    # --------------------------------------------------------

    test_metrics = calculate_metrics(
        model,
        X_test,
        y_test,
    )

    print("\nTest metrics:")

    print(
        f"MAE  : {test_metrics['MAE']:.4f}"
    )

    print(
        f"RMSE : {test_metrics['RMSE']:.4f}"
    )

    print(
        f"R²   : {test_metrics['R2']:.4f}"
    )

    # --------------------------------------------------------
    # Feature importance
    # --------------------------------------------------------

    importance_df = pd.DataFrame({
        "feature": FEATURES,
        "importance": model.feature_importances_,
    })

    importance_df = importance_df.sort_values(
        "importance",
        ascending=False,
    )

    print("\nTop feature importances:")

    print(
        importance_df.head(15).to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # Crop coverage
    # --------------------------------------------------------

    print("\nCrop coverage:")

    crop_counts = (
        df["crop_type"]
        .value_counts()
        .sort_index()
    )

    print(
        crop_counts.to_string()
    )

    # --------------------------------------------------------
    # Save model
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        model,
        MODEL_PATH,
    )

    print(
        f"\nModel saved to:\n{MODEL_PATH}"
    )

    # --------------------------------------------------------
    # Save feature list
    # --------------------------------------------------------

    with open(
        FEATURES_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            FEATURES,
            file,
            indent=4,
        )

    print(
        f"Feature list saved to:\n"
        f"{FEATURES_PATH}"
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = {
        "model_name": "Gradient Boosting Multi-Crop",
        "model_version": "2.0",
        "model_type": "GradientBoostingRegressor",

        "dataset": (
            "ml_ready_dataset_multicrop.csv"
        ),

        "target": TARGET,

        "crop_count": int(
            df["crop_type"].nunique()
        ),

        "crop_types": sorted(
            df["crop_type"]
            .unique()
            .tolist()
        ),

        "feature_count": len(FEATURES),

        "training_records": len(
            train_df
        ),

        "validation_records": len(
            validation_df
        ),

        "test_records": len(
            test_df
        ),

        "hyperparameters": {
            "n_estimators": 150,
            "learning_rate": 0.1,
            "max_depth": 3,
            "random_state": 42,
        },

        "validation_metrics": validation_metrics,

        "test_metrics": test_metrics,

        "status": "Multi-crop model trained",

        "target_note": (
            "water_quantity_liters is a "
            "rule-generated/synthetic target "
            "derived from sensor, weather, "
            "crop reference and growth-stage "
            "conditions. It is not measured "
            "irrigation data."
        ),
    }

    with open(
        METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    print(
        f"Metadata saved to:\n"
        f"{METADATA_PATH}"
    )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print(
        "MULTI-CROP GRADIENT BOOSTING "
        "TRAINING COMPLETE"
    )
    print("=" * 60)

    print(
        f"\nCrops trained: "
        f"{df['crop_type'].nunique()}"
    )

    print(
        f"Features used: "
        f"{len(FEATURES)}"
    )

    print(
        f"Training records: "
        f"{len(train_df)}"
    )

    print(
        f"Validation records: "
        f"{len(validation_df)}"
    )

    print(
        f"Test records: "
        f"{len(test_df)}"
    )

    print(
        "\nNOTE: Model performance must be "
        "interpreted in the context of the "
        "synthetic/rule-generated target."
    )


if __name__ == "__main__":
    main()