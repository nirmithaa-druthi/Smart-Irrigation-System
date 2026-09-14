import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# 1. LOAD DATA
# ============================================================

df = pd.read_csv("ml/ml_ready_dataset.csv")

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)


# ============================================================
# 2. FEATURES AND TARGET
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
# 3. CHRONOLOGICAL SPLIT
# ============================================================

train_end = int(len(df) * 0.70)
validation_end = int(len(df) * 0.85)

X_train = X.iloc[:train_end]
y_train = y.iloc[:train_end]

X_validation = X.iloc[train_end:validation_end]
y_validation = y.iloc[train_end:validation_end]

X_test = X.iloc[validation_end:]
y_test = y.iloc[validation_end:]


print("========== DATA SPLIT ==========")
print("Training:", len(X_train))
print("Validation:", len(X_validation))
print("Testing:", len(X_test))


# ============================================================
# 4. RANDOM FOREST
# ============================================================

rf_model = RandomForestRegressor(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

rf_validation_pred = rf_model.predict(X_validation)

rf_mae = mean_absolute_error(
    y_validation,
    rf_validation_pred
)

rf_rmse = np.sqrt(
    mean_squared_error(
        y_validation,
        rf_validation_pred
    )
)

rf_r2 = r2_score(
    y_validation,
    rf_validation_pred
)


# ============================================================
# 5. GRADIENT BOOSTING
# ============================================================

gb_model = GradientBoostingRegressor(
    n_estimators=100,
    learning_rate=0.1,
    max_depth=3,
    random_state=42
)

gb_model.fit(X_train, y_train)

gb_validation_pred = gb_model.predict(X_validation)

gb_mae = mean_absolute_error(
    y_validation,
    gb_validation_pred
)

gb_rmse = np.sqrt(
    mean_squared_error(
        y_validation,
        gb_validation_pred
    )
)

gb_r2 = r2_score(
    y_validation,
    gb_validation_pred
)


# ============================================================
# 6. VALIDATION RESULTS
# ============================================================

print("\n========== VALIDATION RESULTS ==========")

print("\nRandom Forest:")
print("MAE :", round(rf_mae, 4))
print("RMSE:", round(rf_rmse, 4))
print("R²  :", round(rf_r2, 4))

print("\nGradient Boosting:")
print("MAE :", round(gb_mae, 4))
print("RMSE:", round(gb_rmse, 4))
print("R²  :", round(gb_r2, 4))


# ============================================================
# 7. TEST RESULTS
# ============================================================

rf_test_pred = rf_model.predict(X_test)
gb_test_pred = gb_model.predict(X_test)

rf_test_mae = mean_absolute_error(y_test, rf_test_pred)
rf_test_rmse = np.sqrt(
    mean_squared_error(y_test, rf_test_pred)
)
rf_test_r2 = r2_score(y_test, rf_test_pred)

gb_test_mae = mean_absolute_error(y_test, gb_test_pred)
gb_test_rmse = np.sqrt(
    mean_squared_error(y_test, gb_test_pred)
)
gb_test_r2 = r2_score(y_test, gb_test_pred)


print("\n========== TEST RESULTS ==========")

print("\nRandom Forest:")
print("MAE :", round(rf_test_mae, 4))
print("RMSE:", round(rf_test_rmse, 4))
print("R²  :", round(rf_test_r2, 4))

print("\nGradient Boosting:")
print("MAE :", round(gb_test_mae, 4))
print("RMSE:", round(gb_test_rmse, 4))
print("R²  :", round(gb_test_r2, 4))


# ============================================================
# 8. MODEL SELECTION
# ============================================================

if gb_test_mae < rf_test_mae:
    best_model = "Gradient Boosting"
else:
    best_model = "Random Forest"


print("\n========== MODEL SELECTION ==========")
print("Best model based on test MAE:", best_model)

print("\nValidation and testing completed successfully.")