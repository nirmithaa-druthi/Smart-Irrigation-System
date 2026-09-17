"""
Multi-Crop Baseline Model
AI-Powered Smart Irrigation System

This baseline predicts the mean water quantity from the
training data for every validation/test observation.

It provides a simple reference point for comparing:
- Baseline
- Random Forest
- Gradient Boosting

The water_quantity_liters target is synthetic/rule-generated.
"""

from pathlib import Path
import json

import joblib
import pandas as pd

from sklearn.dummy import DummyRegressor
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
    / "baseline_multicrop_model.joblib"
)

METADATA_PATH = (
    MODEL_DIR
    / "baseline_multicrop_metadata.json"
)


# ============================================================
# TARGET
# ============================================================

TARGET = "water_quantity_liters"


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset():

    print("=" * 60)
    print("MULTI-CROP BASELINE MODEL")
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

    if TARGET not in df.columns:

        raise ValueError(
            f"Target column '{TARGET}' not found."
        )

    # --------------------------------------------------------
    # Remove missing target values
    # --------------------------------------------------------

    df = df.dropna(
        subset=[TARGET]
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
    # Prepare target
    #
    # DummyRegressor needs an input matrix, but the baseline
    # deliberately ignores all features.
    # --------------------------------------------------------

    X_train = train_df[
        ["soil_moisture"]
    ]

    y_train = train_df[TARGET]

    X_validation = validation_df[
        ["soil_moisture"]
    ]

    y_validation = validation_df[TARGET]

    X_test = test_df[
        ["soil_moisture"]
    ]

    y_test = test_df[TARGET]

    # --------------------------------------------------------
    # Train baseline
    # --------------------------------------------------------

    print(
        "\nTraining mean baseline..."
    )

    model = DummyRegressor(
        strategy="mean"
    )

    model.fit(
        X_train,
        y_train,
    )

    print(
        "Baseline training completed."
    )

    # --------------------------------------------------------
    # Training mean
    # --------------------------------------------------------

    training_mean = float(
        y_train.mean()
    )

    print(
        f"\nTraining mean water quantity: "
        f"{training_mean:.4f} L"
    )

    # --------------------------------------------------------
    # Validation
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
    # Test
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
    # Save metadata
    # --------------------------------------------------------

    metadata = {
        "model_name": "Mean Baseline Multi-Crop",
        "model_version": "2.0",
        "model_type": "DummyRegressor",

        "dataset": (
            "ml_ready_dataset_multicrop.csv"
        ),

        "target": TARGET,

        "strategy": "mean",

        "crop_count": int(
            df["crop_type"].nunique()
        ),

        "crop_types": sorted(
            df["crop_type"]
            .unique()
            .tolist()
        ),

        "training_records": len(
            train_df
        ),

        "validation_records": len(
            validation_df
        ),

        "test_records": len(
            test_df
        ),

        "training_mean_water_quantity_liters": (
            training_mean
        ),

        "validation_metrics": validation_metrics,

        "test_metrics": test_metrics,

        "status": "Baseline model trained",

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
        "MULTI-CROP BASELINE TRAINING COMPLETE"
    )
    print("=" * 60)

    print(
        f"\nCrops: "
        f"{df['crop_type'].nunique()}"
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
        "\nNOTE: The baseline intentionally "
        "ignores crop and sensor features. "
        "It is only used as a reference "
        "for evaluating the ML models."
    )

    print(
        "\nNOTE: Model performance must be "
        "interpreted in the context of the "
        "synthetic/rule-generated target."
    )


if __name__ == "__main__":
    main()