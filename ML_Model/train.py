from pathlib import Path
from io import BytesIO

import numpy as np
from PIL import Image, ImageChops, ImageEnhance
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report,
)
import joblib
import matplotlib.pyplot as plt


# ============================================================
# PATHS
# ============================================================

DATASET_PATH = Path(
    r"C:\Users\bhanu\Downloads\CASIA2.0_revised_corrected\casia"
)

REAL_PATH = DATASET_PATH / "Au"
TAMPERED_PATH = DATASET_PATH / "Tp"

RANDOM_STATE = 42
SAMPLES_PER_CLASS = 1000
ELA_QUALITY = 90


# ============================================================
# ELA FEATURE EXTRACTION
# Same ELA principle as teammate's ela.py
# ============================================================

def extract_ela_features(image_path):
    original = Image.open(image_path).convert("RGB")

    # JPEG compression in memory
    buffer = BytesIO()
    original.save(buffer, format="JPEG", quality=ELA_QUALITY)
    buffer.seek(0)

    compressed = Image.open(buffer).convert("RGB")

    # Calculate pixel differences
    difference = ImageChops.difference(original, compressed)

    # Find maximum difference
    extrema = difference.getextrema()
    max_difference = max(max(channel) for channel in extrema)

    if max_difference == 0:
        max_difference = 1

    # Same enhancement used by teammate's ELA
    scale = 255.0 / max_difference
    ela_image = ImageEnhance.Brightness(difference).enhance(scale)

    # Convert to grayscale
    gray_image = ela_image.convert("L")

    pixels = np.array(gray_image, dtype=np.float32)

    # 14 numerical ELA features
    features = [
        pixels.mean(),
        pixels.std(),
        pixels.min(),
        pixels.max(),
        np.median(pixels),
        np.percentile(pixels, 25),
        np.percentile(pixels, 75),
        np.percentile(pixels, 90),
        np.percentile(pixels, 95),
        np.mean(pixels > 20),
        np.mean(pixels > 50),
        np.mean(pixels > 100),
        np.mean(pixels > 150),
        np.mean(pixels > 200),
    ]

    return features


# ============================================================
# GET IMAGE FILES
# ============================================================

def get_image_files(folder):
    extensions = {".jpg", ".jpeg", ".png", ".tif", ".tiff"}

    return [
        path
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in extensions
    ]


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 50)
    print("IMAGE TAMPERING DETECTION - MODEL TRAINING")
    print("=" * 50)

    real_images = get_image_files(REAL_PATH)
    tampered_images = get_image_files(TAMPERED_PATH)

    print(f"\nReal images available: {len(real_images)}")
    print(f"Tampered images available: {len(tampered_images)}")

    # Reproducible random selection
    rng = np.random.default_rng(RANDOM_STATE)

    real_selected = rng.choice(
        real_images,
        size=SAMPLES_PER_CLASS,
        replace=False
    )

    tampered_selected = rng.choice(
        tampered_images,
        size=SAMPLES_PER_CLASS,
        replace=False
    )

    print("\nImages selected:")
    print(f"Real: {len(real_selected)}")
    print(f"Tampered: {len(tampered_selected)}")

    # ========================================================
    # FEATURE EXTRACTION
    # ========================================================

    X = []
    y = []

    print("\nExtracting ELA features...")

    for i, image_path in enumerate(real_selected):
        try:
            features = extract_ela_features(image_path)
            X.append(features)
            y.append(0)  # REAL
        except Exception as e:
            print(f"Skipping real image {image_path.name}: {e}")

    for i, image_path in enumerate(tampered_selected):
        try:
            features = extract_ela_features(image_path)
            X.append(features)
            y.append(1)  # TAMPERED
        except Exception as e:
            print(f"Skipping tampered image {image_path.name}: {e}")

    X = np.array(X)
    y = np.array(y)

    print("\nFeature extraction completed.")
    print(f"Feature matrix shape: {X.shape}")
    print(f"Labels shape: {y.shape}")

    # ========================================================
    # TRAIN / TEST SPLIT
    # ========================================================

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=y
    )

    print(f"\nTraining samples: {len(X_train)}")
    print(f"Testing samples: {len(X_test)}")

    # ========================================================
    # LOGISTIC REGRESSION
    # ========================================================

    scaler = StandardScaler()

    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    logistic_model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE
    )

    logistic_model.fit(X_train_scaled, y_train)

    logistic_pred = logistic_model.predict(X_test_scaled)

    logistic_accuracy = accuracy_score(y_test, logistic_pred)
    logistic_precision = precision_score(y_test, logistic_pred)
    logistic_recall = recall_score(y_test, logistic_pred)
    logistic_f1 = f1_score(y_test, logistic_pred)

    print("\nLOGISTIC REGRESSION")
    print(f"Accuracy : {logistic_accuracy:.4f}")
    print(f"Precision: {logistic_precision:.4f}")
    print(f"Recall   : {logistic_recall:.4f}")
    print(f"F1 Score : {logistic_f1:.4f}")

    # ========================================================
    # RANDOM FOREST
    # ========================================================

    random_forest = RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )

    random_forest.fit(X_train, y_train)

    rf_pred = random_forest.predict(X_test)

    rf_accuracy = accuracy_score(y_test, rf_pred)
    rf_precision = precision_score(y_test, rf_pred)
    rf_recall = recall_score(y_test, rf_pred)
    rf_f1 = f1_score(y_test, rf_pred)

    print("\nRANDOM FOREST")
    print(f"Accuracy : {rf_accuracy:.4f}")
    print(f"Precision: {rf_precision:.4f}")
    print(f"Recall   : {rf_recall:.4f}")
    print(f"F1 Score : {rf_f1:.4f}")

    # ========================================================
    # MODEL COMPARISON
    # ========================================================

    print("\nMODEL COMPARISON")
    print(f"Logistic Regression Accuracy: {logistic_accuracy:.4f}")
    print(f"Random Forest Accuracy      : {rf_accuracy:.4f}")

    if logistic_accuracy >= rf_accuracy:
        best_model = logistic_model
        best_model_name = "Logistic Regression"
        best_prediction = logistic_pred
        best_scaler = scaler
    else:
        best_model = random_forest
        best_model_name = "Random Forest"
        best_prediction = rf_pred
        best_scaler = None

    print(f"\nBest model: {best_model_name}")

    # ========================================================
    # CONFUSION MATRIX
    # ========================================================

    cm = confusion_matrix(y_test, best_prediction)

    print("\nConfusion Matrix:")
    print(cm)

    print("\nClassification Report:")
    print(
        classification_report(
            y_test,
            best_prediction,
            target_names=["REAL", "TAMPERED"]
        )
    )

    # ========================================================
    # SAVE MODEL
    # ========================================================

    model_package = {
        "model": best_model,
        "scaler": best_scaler,
        "model_name": best_model_name,
    }

    joblib.dump(model_package, "model.pkl")

    # ========================================================
    # SAVE CONFUSION MATRIX
    # ========================================================

    plt.figure(figsize=(6, 5))
    plt.imshow(cm, interpolation="nearest")
    plt.title(f"Confusion Matrix - {best_model_name}")
    plt.colorbar()

    plt.xticks([0, 1], ["REAL", "TAMPERED"])
    plt.yticks([0, 1], ["REAL", "TAMPERED"])

    plt.xlabel("Predicted")
    plt.ylabel("Actual")

    for i in range(2):
        for j in range(2):
            plt.text(j, i, cm[i, j], ha="center", va="center")

    plt.tight_layout()
    plt.savefig("confusion_matrix.png")
    plt.close()

    print("\nModel saved as model.pkl")
    print("Confusion matrix saved as confusion_matrix.png")

    print("\n" + "=" * 50)
    print("TRAINING COMPLETE")
    print("=" * 50)


if __name__ == "__main__":
    main()