import os
import json
import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras.optimizers import Adam


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "ml_ready_dataset_multicrop.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "models"
)

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "lstm_irrigation_model.keras"
)

METRICS_PATH = os.path.join(
    MODEL_DIR,
    "lstm_model_metrics.json"
)

FEATURES_PATH = os.path.join(
    MODEL_DIR,
    "lstm_features.json"
)

SEQUENCE_LENGTH = 6


# ============================================================
# FEATURES FROM ACTUAL DATASET
# ============================================================

FEATURES = [
    "soil_moisture",
    "soil_moisture_change",
    "soil_moisture_rolling_mean",
    "soil_moisture_stress",
    "hour",
    "day_of_week",
    "day_of_month",
    "temperature",
    "humidity",
    "rainfall",
    "rain_probability",
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
    "previous_water_usage_liters"
]

TARGET = "water_quantity_liters"


# ============================================================
# LOAD DATASET
# ============================================================

print("=" * 70)
print("SMART IRRIGATION - LSTM MODEL TRAINING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_PATH)

print(f"\nDataset shape: {df.shape}")
print(f"Number of crops: {df['crop_type'].nunique()}")

print(
    "Crops:",
    ", ".join(sorted(df["crop_type"].unique()))
)


# ============================================================
# VERIFY COLUMNS
# ============================================================

required_columns = FEATURES + [
    TARGET,
    "crop_type",
    "timestamp"
]

missing_columns = [
    column
    for column in required_columns
    if column not in df.columns
]

if missing_columns:

    print("\nERROR: Missing columns:")

    for column in missing_columns:
        print(" -", column)

    print("\nAvailable columns:")

    for column in df.columns:
        print(" -", column)

    raise ValueError(
        "Dataset column mismatch."
    )

print("\nAll required columns are available.")


# ============================================================
# CHRONOLOGICAL SORT
# ============================================================

df["timestamp"] = pd.to_datetime(
    df["timestamp"],
    errors="coerce"
)

df = df.sort_values(
    ["crop_type", "timestamp"]
).reset_index(drop=True)

print(
    "Dataset sorted chronologically by crop and timestamp."
)


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for column in FEATURES:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df[TARGET] = pd.to_numeric(
    df[TARGET],
    errors="coerce"
)


# ============================================================
# DATA CLEANING
# ============================================================

rows_before = len(df)

df = df.dropna(
    subset=FEATURES + [TARGET]
).reset_index(drop=True)

rows_after = len(df)

print("\nData cleaning:")
print(f"Rows before cleaning: {rows_before}")
print(f"Rows after cleaning:  {rows_after}")
print(f"Rows removed:         {rows_before - rows_after}")


# ============================================================
# CREATE TIME-SERIES SEQUENCES
# ============================================================

print("\nCreating LSTM time-series sequences...")
print(f"Sequence length: {SEQUENCE_LENGTH}")

X_sequences = []
y_values = []
sequence_crops = []

for crop in sorted(df["crop_type"].unique()):

    crop_df = df[
        df["crop_type"] == crop
    ].copy()

    crop_df = crop_df.reset_index(drop=True)

    X_crop = crop_df[
        FEATURES
    ].values.astype(np.float32)

    y_crop = crop_df[
        TARGET
    ].values.astype(np.float32)

    if len(crop_df) <= SEQUENCE_LENGTH:
        continue

    for i in range(
        SEQUENCE_LENGTH,
        len(crop_df)
    ):

        X_sequences.append(
            X_crop[
                i - SEQUENCE_LENGTH:i
            ]
        )

        y_values.append(
            y_crop[i]
        )

        sequence_crops.append(
            crop
        )


X = np.array(
    X_sequences,
    dtype=np.float32
)

y = np.array(
    y_values,
    dtype=np.float32
)

sequence_crops = np.array(
    sequence_crops
)

print(
    f"\nSequence data shape: {X.shape}"
)

print(
    f"Target shape:        {y.shape}"
)

if len(X) == 0:

    raise ValueError(
        "No time-series sequences were created."
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

X_train = X[:train_end]
y_train = y[:train_end]

X_val = X[
    train_end:validation_end
]

y_val = y[
    train_end:validation_end
]

X_test = X[
    validation_end:
]

y_test = y[
    validation_end:
]

print("\nChronological split:")

print(
    f"Training:   {len(X_train)}"
)

print(
    f"Validation: {len(X_val)}"
)

print(
    f"Test:       {len(X_test)}"
)


# ============================================================
# SCALE FEATURES
# ============================================================

print("\nScaling features...")

scaler = StandardScaler()

n_train, sequence_length, n_features = X_train.shape

X_train_2d = X_train.reshape(
    -1,
    n_features
)

scaler.fit(
    X_train_2d
)


def scale_sequences(X_data):

    original_shape = X_data.shape

    X_2d = X_data.reshape(
        -1,
        original_shape[2]
    )

    X_scaled = scaler.transform(
        X_2d
    )

    return X_scaled.reshape(
        original_shape
    ).astype(np.float32)


X_train_scaled = scale_sequences(
    X_train
)

X_val_scaled = scale_sequences(
    X_val
)

X_test_scaled = scale_sequences(
    X_test
)


# ============================================================
# BUILD LSTM MODEL
# ============================================================

print("\nBuilding LSTM neural network...")

model = Sequential([

    Input(
        shape=(
            SEQUENCE_LENGTH,
            n_features
        )
    ),

    LSTM(
        64,
        return_sequences=True
    ),

    Dropout(
        0.20
    ),

    LSTM(
        32,
        return_sequences=False
    ),

    Dropout(
        0.20
    ),

    Dense(
        16,
        activation="relu"
    ),

    Dense(
        1,
        activation="linear"
    )
])


model.compile(

    optimizer=Adam(
        learning_rate=0.001
    ),

    loss="mse",

    metrics=[
        "mae"
    ]
)


print("\nModel architecture:")

model.summary()


# ============================================================
# TRAIN
# ============================================================

print("\n" + "=" * 70)
print("TRAINING LSTM")
print("=" * 70)

early_stopping = EarlyStopping(

    monitor="val_loss",

    patience=8,

    restore_best_weights=True
)


history = model.fit(

    X_train_scaled,

    y_train,

    validation_data=(
        X_val_scaled,
        y_val
    ),

    epochs=50,

    batch_size=64,

    callbacks=[
        early_stopping
    ],

    verbose=1
)


# ============================================================
# PREDICTIONS
# ============================================================

print("\nGenerating predictions...")

train_predictions = model.predict(
    X_train_scaled,
    verbose=0
).flatten()

validation_predictions = model.predict(
    X_val_scaled,
    verbose=0
).flatten()

test_predictions = model.predict(
    X_test_scaled,
    verbose=0
).flatten()


# ============================================================
# METRIC FUNCTION
# ============================================================

def calculate_metrics(
    actual,
    predicted
):

    mae = mean_absolute_error(
        actual,
        predicted
    )

    rmse = np.sqrt(
        mean_squared_error(
            actual,
            predicted
        )
    )

    r2 = r2_score(
        actual,
        predicted
    )

    return {

        "MAE": float(mae),

        "RMSE": float(rmse),

        "R2": float(r2)
    }


train_metrics = calculate_metrics(
    y_train,
    train_predictions
)

validation_metrics = calculate_metrics(
    y_val,
    validation_predictions
)

test_metrics = calculate_metrics(
    y_test,
    test_predictions
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n")

print("=" * 70)
print("LSTM RESULTS")
print("=" * 70)


print("\nTraining metrics:")

print(
    f"MAE:  {train_metrics['MAE']:.4f}"
)

print(
    f"RMSE: {train_metrics['RMSE']:.4f}"
)

print(
    f"R²:   {train_metrics['R2']:.4f}"
)


print("\nValidation metrics:")

print(
    f"MAE:  {validation_metrics['MAE']:.4f}"
)

print(
    f"RMSE: {validation_metrics['RMSE']:.4f}"
)

print(
    f"R²:   {validation_metrics['R2']:.4f}"
)


print("\nTest metrics:")

print(
    f"MAE:  {test_metrics['MAE']:.4f}"
)

print(
    f"RMSE: {test_metrics['RMSE']:.4f}"
)

print(
    f"R²:   {test_metrics['R2']:.4f}"
)


# ============================================================
# SAVE MODEL
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)

print("\nSaving LSTM model...")

model.save(
    MODEL_PATH
)


# ============================================================
# SAVE FEATURES
# ============================================================

with open(
    FEATURES_PATH,
    "w"
) as file:

    json.dump(

        {

            "model_name": "LSTM",

            "sequence_length":
                SEQUENCE_LENGTH,

            "feature_count":
                len(FEATURES),

            "features":
                FEATURES,

            "target":
                TARGET
        },

        file,

        indent=4
    )


# ============================================================
# SAVE METRICS
# ============================================================

metrics_data = {

    "model_name":
        "LSTM",

    "model_type":
        "Long Short-Term Memory Neural Network",

    "sequence_length":
        SEQUENCE_LENGTH,

    "feature_count":
        len(FEATURES),

    "features":
        FEATURES,

    "target":
        TARGET,

    "dataset_records":
        int(len(df)),

    "sequence_records":
        int(len(X)),

    "training_records":
        int(len(X_train)),

    "validation_records":
        int(len(X_val)),

    "test_records":
        int(len(X_test)),

    "epochs_requested":
        50,

    "epochs_completed":
        len(history.history["loss"]),

    "training_metrics":
        train_metrics,

    "validation_metrics":
        validation_metrics,

    "test_metrics":
        test_metrics,

    "status":
        "Completed",

    "note":
        (
            "The LSTM was trained using "
            "chronological time-series sequences. "
            "The water quantity target is "
            "rule-generated/simulated in the "
            "Milestone 2 dataset and does not "
            "represent measured real-world "
            "irrigation volume."
        )
}


with open(
    METRICS_PATH,
    "w"
) as file:

    json.dump(
        metrics_data,
        file,
        indent=4
    )


# ============================================================
# COMPLETE
# ============================================================

print("\n")

print("=" * 70)
print("LSTM TRAINING COMPLETED SUCCESSFULLY")
print("=" * 70)

print("\nSaved files:")

print(
    f"Model:   {MODEL_PATH}"
)

print(
    f"Metrics: {METRICS_PATH}"
)

print(
    f"Config:  {FEATURES_PATH}"
)

print(
    "\nMilestone 2 LSTM implementation is complete."
)