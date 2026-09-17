import mlflow
import mlflow.sklearn

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATASET
# ============================================================

df = pd.read_csv("ml/ml_ready_dataset.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)

print("Dataset loaded:", len(df), "records")


# ============================================================
# 2. DEFINE FEATURES AND TARGET
# ============================================================

features = [
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
    "growth_stage_multiplier",
    "previous_water_usage_liters"
]

target = "water_quantity_liters"

X = df[features]
y = df[target]


# ============================================================
# 3. CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
# ============================================================

train_end = int(len(df) * 0.70)
validation_end = int(len(df) * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_validation = X.iloc[train_end:validation_end]
y_validation = y.iloc[train_end:validation_end]

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]


# ============================================================
# 4. BEST RANDOM FOREST PARAMETERS
# ============================================================

n_estimators = 200
max_depth = None
min_samples_split = 2
random_state = 42


# ============================================================
# 5. SET UP MLFLOW
# ============================================================

mlflow.set_experiment("Smart Irrigation - Model Development")


# ============================================================
# 6. START MLFLOW RUN
# ============================================================

with mlflow.start_run(run_name="Random_Forest_Tuned"):

    # Create model
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        min_samples_split=min_samples_split,
        random_state=random_state,
        n_jobs=-1
    )

    # Train
    model.fit(X_train, y_train)

    print("Random Forest training completed.")


    # ========================================================
    # 7. VALIDATION PREDICTION
    # ========================================================

    validation_prediction = model.predict(X_validation)

    validation_mae = mean_absolute_error(
        y_validation,
        validation_prediction
    )

    validation_rmse = np.sqrt(
        mean_squared_error(
            y_validation,
            validation_prediction
        )
    )

    validation_r2 = r2_score(
        y_validation,
        validation_prediction
    )


    # ========================================================
    # 8. TEST PREDICTION
    # ========================================================

    test_prediction = model.predict(X_test)

    test_mae = mean_absolute_error(
        y_test,
        test_prediction
    )

    test_rmse = np.sqrt(
        mean_squared_error(
            y_test,
            test_prediction
        )
    )

    test_r2 = r2_score(
        y_test,
        test_prediction
    )


    # ========================================================
    # 9. LOG PARAMETERS
    # ========================================================

    mlflow.log_param(
        "model_type",
        "Random Forest Regressor"
    )

    mlflow.log_param(
        "n_estimators",
        n_estimators
    )

    mlflow.log_param(
        "max_depth",
        "None"
    )

    mlflow.log_param(
        "min_samples_split",
        min_samples_split
    )

    mlflow.log_param(
        "random_state",
        random_state
    )

    mlflow.log_param(
        "features_count",
        len(features)
    )


    # ========================================================
    # 10. LOG VALIDATION METRICS
    # ========================================================

    mlflow.log_metric(
        "validation_mae",
        validation_mae
    )

    mlflow.log_metric(
        "validation_rmse",
        validation_rmse
    )

    mlflow.log_metric(
        "validation_r2",
        validation_r2
    )


    # ========================================================
    # 11. LOG TEST METRICS
    # ========================================================

    mlflow.log_metric(
        "test_mae",
        test_mae
    )

    mlflow.log_metric(
        "test_rmse",
        test_rmse
    )

    mlflow.log_metric(
        "test_r2",
        test_r2
    )


    # ========================================================
    # 12. SAVE MODEL IN MLFLOW
    # ========================================================

    mlflow.sklearn.log_model(
        model,
        name="random_forest_model"
    )


    # ========================================================
    # 13. DISPLAY RESULTS
    # ========================================================

    print("\n========== MLFLOW RESULTS ==========")

    print("\nValidation:")
    print("MAE :", round(validation_mae, 4))
    print("RMSE:", round(validation_rmse, 4))
    print("R²  :", round(validation_r2, 4))

    print("\nTest:")
    print("MAE :", round(test_mae, 4))
    print("RMSE:", round(test_rmse, 4))
    print("R²  :", round(test_r2, 4))

    print("\nMLflow tracking completed successfully.")