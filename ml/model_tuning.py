"""
Multi-Crop Model Hyperparameter Tuning
AI-Powered Smart Irrigation System

Compares several Random Forest and Gradient Boosting
configurations using the validation set.

The final model is selected using the lowest validation MAE.

IMPORTANT:
The water_quantity_liters target is synthetic/rule-generated.
"""

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
)
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)


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

FINAL_MODEL_PATH = (
    MODEL_DIR
    / "final_multicrop_model.joblib"
)

FINAL_FEATURES_PATH = (
    MODEL_DIR
    / "final_multicrop_features.json"
)

FINAL_METADATA_PATH = (
    MODEL_DIR
    / "final_multicrop_metadata.json"
)


# ============================================================
# FEATURES
# ============================================================

FEATURES = [
    "soil_moisture",
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",

    "temperature",
    "humidity",
    "rainfall",
    "rain_probability",

    "hour",
    "day_of_week",
    "day_of_month",

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

    "previous_water_usage_liters",
]

TARGET = "water_quantity_liters"


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
# LOAD DATASET
# ============================================================

def load_dataset():

    print("=" * 60)
    print("MULTI-CROP MODEL HYPERPARAMETER TUNING")
    print("=" * 60)

    print("\nLoading dataset...")

    if not DATASET_PATH.exists():

        raise FileNotFoundError(
            f"Dataset not found:\n{DATASET_PATH}"
        )

    df = pd.read_csv(
        DATASET_PATH
    )

    print(
        f"Dataset records: {len(df)}"
    )

    print(
        f"Crops: {df['crop_type'].nunique()}"
    )

    print(
        f"Missing values: "
        f"{df.isna().sum().sum()}"
    )

    return df


# ============================================================
# VALIDATE DATA
# ============================================================

def validate_dataset(df):

    required_columns = (
        FEATURES
        + [TARGET, "timestamp", "crop_type"]
    )

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing columns:\n"
            + "\n".join(missing_columns)
        )

    df = df.dropna(
        subset=FEATURES + [TARGET]
    ).copy()

    return df


# ============================================================
# CHRONOLOGICAL SPLIT
# ============================================================

def chronological_split(df):

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
# RANDOM FOREST CONFIGURATIONS
# ============================================================

RANDOM_FOREST_CONFIGS = [

    {
        "n_estimators": 100,
        "max_depth": 5,
        "min_samples_split": 2,
    },

    {
        "n_estimators": 150,
        "max_depth": 10,
        "min_samples_split": 2,
    },

    {
        "n_estimators": 200,
        "max_depth": 15,
        "min_samples_split": 2,
    },

    {
        "n_estimators": 200,
        "max_depth": None,
        "min_samples_split": 2,
    },

]


# ============================================================
# GRADIENT BOOSTING CONFIGURATIONS
# ============================================================

GRADIENT_BOOSTING_CONFIGS = [

    {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 3,
    },

    {
        "n_estimators": 150,
        "learning_rate": 0.1,
        "max_depth": 3,
    },

    {
        "n_estimators": 150,
        "learning_rate": 0.05,
        "max_depth": 3,
    },

    {
        "n_estimators": 200,
        "learning_rate": 0.1,
        "max_depth": 2,
    },

]


# ============================================================
# TUNE RANDOM FOREST
# ============================================================

def tune_random_forest(
    X_train,
    y_train,
    X_validation,
    y_validation,
):

    print("\n" + "=" * 60)
    print("RANDOM FOREST TUNING")
    print("=" * 60)

    results = []

    best_model = None
    best_metrics = None
    best_config = None

    for index, config in enumerate(
        RANDOM_FOREST_CONFIGS,
        start=1,
    ):

        print(
            f"\nConfiguration {index}: "
            f"{config}"
        )

        model = RandomForestRegressor(
            n_estimators=config[
                "n_estimators"
            ],
            max_depth=config[
                "max_depth"
            ],
            min_samples_split=config[
                "min_samples_split"
            ],
            random_state=42,
            n_jobs=-1,
        )

        model.fit(
            X_train,
            y_train,
        )

        metrics = calculate_metrics(
            model,
            X_validation,
            y_validation,
        )

        print(
            f"Validation MAE: "
            f"{metrics['MAE']:.4f}"
        )

        print(
            f"Validation RMSE: "
            f"{metrics['RMSE']:.4f}"
        )

        print(
            f"Validation R²: "
            f"{metrics['R2']:.4f}"
        )

        results.append({
            "model": "Random Forest",
            "config": config,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "R2": metrics["R2"],
        })

        if (
            best_metrics is None
            or metrics["MAE"]
            < best_metrics["MAE"]
        ):

            best_model = model
            best_metrics = metrics
            best_config = config

    print(
        "\nBest Random Forest configuration:"
    )

    print(best_config)

    print(
        f"Best validation MAE: "
        f"{best_metrics['MAE']:.4f}"
    )

    return (
        best_model,
        best_config,
        best_metrics,
        results,
    )


# ============================================================
# TUNE GRADIENT BOOSTING
# ============================================================

def tune_gradient_boosting(
    X_train,
    y_train,
    X_validation,
    y_validation,
):

    print("\n" + "=" * 60)
    print("GRADIENT BOOSTING TUNING")
    print("=" * 60)

    results = []

    best_model = None
    best_metrics = None
    best_config = None

    for index, config in enumerate(
        GRADIENT_BOOSTING_CONFIGS,
        start=1,
    ):

        print(
            f"\nConfiguration {index}: "
            f"{config}"
        )

        model = GradientBoostingRegressor(
            n_estimators=config[
                "n_estimators"
            ],
            learning_rate=config[
                "learning_rate"
            ],
            max_depth=config[
                "max_depth"
            ],
            random_state=42,
        )

        model.fit(
            X_train,
            y_train,
        )

        metrics = calculate_metrics(
            model,
            X_validation,
            y_validation,
        )

        print(
            f"Validation MAE: "
            f"{metrics['MAE']:.4f}"
        )

        print(
            f"Validation RMSE: "
            f"{metrics['RMSE']:.4f}"
        )

        print(
            f"Validation R²: "
            f"{metrics['R2']:.4f}"
        )

        results.append({
            "model": "Gradient Boosting",
            "config": config,
            "MAE": metrics["MAE"],
            "RMSE": metrics["RMSE"],
            "R2": metrics["R2"],
        })

        if (
            best_metrics is None
            or metrics["MAE"]
            < best_metrics["MAE"]
        ):

            best_model = model
            best_metrics = metrics
            best_config = config

    print(
        "\nBest Gradient Boosting configuration:"
    )

    print(best_config)

    print(
        f"Best validation MAE: "
        f"{best_metrics['MAE']:.4f}"
    )

    return (
        best_model,
        best_config,
        best_metrics,
        results,
    )


# ============================================================
# MAIN
# ============================================================

def main():

    df = load_dataset()

    df = validate_dataset(df)

    (
        train_df,
        validation_df,
        test_df,
    ) = chronological_split(df)

    print("\nDataset split:")

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
    # Feature matrices
    # --------------------------------------------------------

    X_train = train_df[FEATURES]
    y_train = train_df[TARGET]

    X_validation = validation_df[FEATURES]
    y_validation = validation_df[TARGET]

    X_test = test_df[FEATURES]
    y_test = test_df[TARGET]

    # --------------------------------------------------------
    # Tune Random Forest
    # --------------------------------------------------------

    (
        best_rf_model,
        best_rf_config,
        best_rf_validation,
        rf_results,
    ) = tune_random_forest(
        X_train,
        y_train,
        X_validation,
        y_validation,
    )

    # --------------------------------------------------------
    # Tune Gradient Boosting
    # --------------------------------------------------------

    (
        best_gb_model,
        best_gb_config,
        best_gb_validation,
        gb_results,
    ) = tune_gradient_boosting(
        X_train,
        y_train,
        X_validation,
        y_validation,
    )

    # --------------------------------------------------------
    # Select final model
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL MODEL SELECTION")
    print("=" * 60)

    if (
        best_rf_validation["MAE"]
        <= best_gb_validation["MAE"]
    ):

        final_model = best_rf_model
        final_model_name = "Random Forest"
        final_config = best_rf_config
        final_validation_metrics = (
            best_rf_validation
        )

    else:

        final_model = best_gb_model
        final_model_name = "Gradient Boosting"
        final_config = best_gb_config
        final_validation_metrics = (
            best_gb_validation
        )

    print(
        f"\nSelected model: "
        f"{final_model_name}"
    )

    print(
        f"Configuration: "
        f"{final_config}"
    )

    print(
        f"Validation MAE: "
        f"{final_validation_metrics['MAE']:.4f}"
    )

    # --------------------------------------------------------
    # Final test evaluation
    # --------------------------------------------------------

    final_test_metrics = calculate_metrics(
        final_model,
        X_test,
        y_test,
    )

    print("\nFinal test metrics:")

    print(
        f"MAE  : "
        f"{final_test_metrics['MAE']:.4f}"
    )

    print(
        f"RMSE : "
        f"{final_test_metrics['RMSE']:.4f}"
    )

    print(
        f"R²   : "
        f"{final_test_metrics['R2']:.4f}"
    )

    # --------------------------------------------------------
    # Save final model
    # --------------------------------------------------------

    MODEL_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    joblib.dump(
        final_model,
        FINAL_MODEL_PATH,
    )

    print(
        f"\nFinal model saved to:\n"
        f"{FINAL_MODEL_PATH}"
    )

    # --------------------------------------------------------
    # Save final feature list
    # --------------------------------------------------------

    with open(
        FINAL_FEATURES_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            FEATURES,
            file,
            indent=4,
        )

    print(
        f"Final feature list saved to:\n"
        f"{FINAL_FEATURES_PATH}"
    )

    # --------------------------------------------------------
    # Save tuning results
    # --------------------------------------------------------

    tuning_results = (
        rf_results
        + gb_results
    )

    tuning_results_path = (
        MODEL_DIR
        / "multicrop_tuning_results.json"
    )

    with open(
        tuning_results_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            tuning_results,
            file,
            indent=4,
        )

    print(
        f"Tuning results saved to:\n"
        f"{tuning_results_path}"
    )

    # --------------------------------------------------------
    # Save metadata
    # --------------------------------------------------------

    metadata = {

        "model_name": (
            f"{final_model_name} Multi-Crop"
        ),

        "model_version": "2.0",

        "model_type": type(
            final_model
        ).__name__,

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

        "selected_model": final_model_name,

        "selected_hyperparameters": (
            final_config
        ),

        "validation_metrics": (
            final_validation_metrics
        ),

        "test_metrics": (
            final_test_metrics
        ),

        "random_forest_best_validation": (
            best_rf_validation
        ),

        "gradient_boosting_best_validation": (
            best_gb_validation
        ),

        "status": "Selected final multi-crop model",

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
        FINAL_METADATA_PATH,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
        )

    print(
        f"Final metadata saved to:\n"
        f"{FINAL_METADATA_PATH}"
    )

    # --------------------------------------------------------
    # Final comparison
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("MODEL COMPARISON")
    print("=" * 60)

    print(
        "\nBest Random Forest:"
    )

    print(
        f"Validation MAE = "
        f"{best_rf_validation['MAE']:.4f}"
    )

    print(
        "\nBest Gradient Boosting:"
    )

    print(
        f"Validation MAE = "
        f"{best_gb_validation['MAE']:.4f}"
    )

    print(
        f"\n🏆 Selected: "
        f"{final_model_name}"
    )

    print(
        "\nNOTE: Performance must be "
        "interpreted in the context of "
        "the synthetic/rule-generated "
        "target."
    )


if __name__ == "__main__":
    main()