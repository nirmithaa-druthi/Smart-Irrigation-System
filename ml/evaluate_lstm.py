import numpy as np
import joblib

from tensorflow.keras.models import load_model
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


print("\n========== LSTM MODEL EVALUATION ==========\n")


# ============================================================
# LOAD TEST DATA
# ============================================================

X_test = np.load(
    "ml/lstm_data/X_test.npy"
)

y_test = np.load(
    "ml/lstm_data/y_test.npy"
)


# ============================================================
# LOAD SCALER
# ============================================================

y_scaler = joblib.load(
    "ml/lstm_data/y_scaler.joblib"
)


# ============================================================
# LOAD TRAINED LSTM MODEL
# ============================================================

model = load_model(
    "ml/models/lstm_irrigation_model.keras"
)


print("Test data loaded successfully.")
print(f"Test samples: {len(X_test)}")


# ============================================================
# GENERATE PREDICTIONS
# ============================================================

y_pred_scaled = model.predict(
    X_test,
    verbose=0
)


# ============================================================
# CONVERT BACK TO LITERS
# ============================================================

y_test_liters = y_scaler.inverse_transform(
    y_test
)

y_pred_liters = y_scaler.inverse_transform(
    y_pred_scaled
)


# ============================================================
# CALCULATE METRICS
# ============================================================

mae = mean_absolute_error(
    y_test_liters,
    y_pred_liters
)

rmse = np.sqrt(
    mean_squared_error(
        y_test_liters,
        y_pred_liters
    )
)

r2 = r2_score(
    y_test_liters,
    y_pred_liters
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print("\n========== LSTM TEST RESULTS ==========\n")

print(
    f"MAE  : {mae:.4f} liters"
)

print(
    f"RMSE : {rmse:.4f} liters"
)

print(
    f"R²   : {r2:.4f}"
)


# ============================================================
# SAMPLE PREDICTIONS
# ============================================================

print("\n========== SAMPLE PREDICTIONS ==========\n")

for i in range(
    min(10, len(y_test_liters))
):

    actual = float(
        y_test_liters[i][0]
    )

    predicted = float(
        y_pred_liters[i][0]
    )

    print(
        f"Actual: {actual:.2f} L"
        f"  |  Predicted: {predicted:.2f} L"
    )


print(
    "\nLSTM evaluation completed successfully."
)