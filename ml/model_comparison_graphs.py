import matplotlib.pyplot as plt
import os


# Create graphs folder
os.makedirs("ml/graphs", exist_ok=True)


# ============================================================
# FINAL MODEL RESULTS
# ============================================================

models = [
    "Baseline",
    "Random Forest",
    "Gradient Boosting",
    "LSTM"
]


mae = [
    5.4215,
    0.0058,
    0.0001,
    5.5072
]


rmse = [
    6.2350,
    0.0486,
    0.0002,
    6.2789
]


r2 = [
    -0.0077,
    0.9999,
    1.0000,
    -0.0238
]


# ============================================================
# MAE COMPARISON
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    models,
    mae
)

plt.xlabel("Model")
plt.ylabel("MAE (liters)")
plt.title("Model Comparison - Mean Absolute Error")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    "ml/graphs/model_comparison_mae.png",
    dpi=300
)

plt.close()


# ============================================================
# RMSE COMPARISON
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    models,
    rmse
)

plt.xlabel("Model")
plt.ylabel("RMSE (liters)")
plt.title("Model Comparison - Root Mean Squared Error")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    "ml/graphs/model_comparison_rmse.png",
    dpi=300
)

plt.close()


# ============================================================
# R2 COMPARISON
# ============================================================

plt.figure(figsize=(10, 6))

plt.bar(
    models,
    r2
)

plt.xlabel("Model")
plt.ylabel("R² Score")
plt.title("Model Comparison - R² Score")

plt.xticks(rotation=15)

plt.tight_layout()

plt.savefig(
    "ml/graphs/model_comparison_r2.png",
    dpi=300
)

plt.close()


# ============================================================
# COMPLETION MESSAGE
# ============================================================

print("\n========== MODEL COMPARISON GRAPHS ==========\n")

print("MAE graph saved:")
print("ml/graphs/model_comparison_mae.png")

print("\nRMSE graph saved:")
print("ml/graphs/model_comparison_rmse.png")

print("\nR² graph saved:")
print("ml/graphs/model_comparison_r2.png")

print("\nAll model comparison graphs saved successfully.")