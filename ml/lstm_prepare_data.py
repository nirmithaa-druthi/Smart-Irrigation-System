import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sklearn.preprocessing import MinMaxScaler


load_dotenv()


# ============================================================
# LOAD ML-READY DATASET
# ============================================================

dataset_path = "ml/ml_ready_dataset.csv"

df = pd.read_csv(dataset_path)

print("\n========== LSTM DATA PREPARATION ==========\n")

print(f"Total records loaded: {len(df)}")

print("\nDataset columns:")
print(list(df.columns))


# ============================================================
# BASIC CLEANING
# ============================================================

df["timestamp"] = pd.to_datetime(df["timestamp"])

df = df.sort_values("timestamp").reset_index(drop=True)

df = df.dropna(
    subset=[
        "soil_moisture",
        "temperature",
        "humidity",
        "rainfall",
        "rain_probability",
        "water_quantity_liters"
    ]
)

print(f"\nRecords after cleaning: {len(df)}")


# ============================================================
# USE CONTINUOUS SENSOR PERIOD
# ============================================================

continuous_df = df[
    (df["timestamp"] >= "2026-08-01") &
    (df["timestamp"] < "2026-08-17")
].copy()

continuous_df = continuous_df.sort_values(
    "timestamp"
).reset_index(drop=True)


print(
    f"\nContinuous time-series records: "
    f"{len(continuous_df)}"
)

print(
    f"Time range: "
    f"{continuous_df['timestamp'].min()} "
    f"to "
    f"{continuous_df['timestamp'].max()}"
)


# ============================================================
# SELECT LSTM FEATURES
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


print("\n========== LSTM FEATURES ==========")

print("\nInput features:")

for feature in features:
    print(f"- {feature}")

print(f"\nTarget: {target}")


# ============================================================
# PREPARE FEATURES AND TARGET
# ============================================================

X_values = continuous_df[
    features
].values.astype(np.float32)

y_values = continuous_df[
    [target]
].values.astype(np.float32)


# ============================================================
# NORMALIZATION
# ============================================================

X_scaler = MinMaxScaler()

y_scaler = MinMaxScaler()

X_scaled = X_scaler.fit_transform(
    X_values
)

y_scaled = y_scaler.fit_transform(
    y_values
)


# ============================================================
# CREATE TIME-SERIES SEQUENCES
# ============================================================

sequence_length = 12

X = []

y = []

for i in range(
    sequence_length,
    len(X_scaled)
):

    X.append(
        X_scaled[
            i - sequence_length:i
        ]
    )

    y.append(
        y_scaled[i]
    )


X = np.array(
    X,
    dtype=np.float32
)

y = np.array(
    y,
    dtype=np.float32
)


# ============================================================
# CHRONOLOGICAL TRAIN / VALIDATION / TEST SPLIT
# ============================================================

total_samples = len(X)

train_end = int(
    total_samples * 0.70
)

validation_end = int(
    total_samples * 0.85
)


X_train = X[
    :train_end
]

y_train = y[
    :train_end
]


X_validation = X[
    train_end:validation_end
]

y_validation = y[
    train_end:validation_end
]


X_test = X[
    validation_end:
]

y_test = y[
    validation_end:
]


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n========== LSTM SEQUENCES ==========")

print(
    f"Sequence length: "
    f"{sequence_length} readings"
)

print(
    "Sequence duration: 2 hours"
)

print(
    f"\nTotal sequences: "
    f"{total_samples}"
)

print(
    f"Training sequences: "
    f"{len(X_train)}"
)

print(
    f"Validation sequences: "
    f"{len(X_validation)}"
)

print(
    f"Testing sequences: "
    f"{len(X_test)}"
)


print(
    f"\nX training shape: "
    f"{X_train.shape}"
)

print(
    f"y training shape: "
    f"{y_train.shape}"
)

print(
    f"\nX validation shape: "
    f"{X_validation.shape}"
)

print(
    f"y validation shape: "
    f"{y_validation.shape}"
)

print(
    f"\nX testing shape: "
    f"{X_test.shape}"
)

print(
    f"y testing shape: "
    f"{y_test.shape}"
)


# ============================================================
# SAVE LSTM DATA
# ============================================================

os.makedirs(
    "ml/lstm_data",
    exist_ok=True
)


np.save(
    "ml/lstm_data/X_train.npy",
    X_train
)

np.save(
    "ml/lstm_data/y_train.npy",
    y_train
)

np.save(
    "ml/lstm_data/X_validation.npy",
    X_validation
)

np.save(
    "ml/lstm_data/y_validation.npy",
    y_validation
)

np.save(
    "ml/lstm_data/X_test.npy",
    X_test
)

np.save(
    "ml/lstm_data/y_test.npy",
    y_test
)


# ============================================================
# SAVE SCALERS
# ============================================================

import joblib


joblib.dump(
    X_scaler,
    "ml/lstm_data/X_scaler.joblib"
)

joblib.dump(
    y_scaler,
    "ml/lstm_data/y_scaler.joblib"
)


print(
    "\nLSTM training data and scalers "
    "saved successfully."
)