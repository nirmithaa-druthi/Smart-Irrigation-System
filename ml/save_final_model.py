import os
import joblib
import pandas as pd

from sklearn.ensemble import RandomForestRegressor


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATASET_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "ml_ready_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "random_forest_model.joblib"
)


# ============================================================
# FEATURES AND TARGET
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


# ============================================================
# LOAD DATASET
# ============================================================

df = pd.read_csv(DATASET_PATH)

print(f"Dataset loaded: {len(df)} records")


X = df[features]
y = df[target]


# ============================================================
# TRAIN FINAL RANDOM FOREST
# ============================================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=None,
    min_samples_split=2,
    random_state=42,
    n_jobs=-1
)

model.fit(X, y)

print("Final Random Forest model trained.")


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)

joblib.dump(
    {
        "model": model,
        "features": features,
        "target": target
    },
    MODEL_PATH
)

print()
print("========== MODEL SAVED ==========")
print(f"Model path: {MODEL_PATH}")
print("Features saved successfully.")
print("Final Random Forest model saved successfully.")