from pathlib import Path
from io import BytesIO
import sys

import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import joblib


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = Path(__file__).resolve().parent.parent / "model.pkl"

ELA_QUALITY = 90


# ============================================================
# ELA FEATURE EXTRACTION
# Must match train.py exactly
# ============================================================

def extract_ela_features(image_path):

    original = Image.open(image_path).convert("RGB")

    # JPEG compression in memory
    buffer = BytesIO()
    original.save(buffer, format="JPEG", quality=ELA_QUALITY)
    buffer.seek(0)

    compressed = Image.open(buffer).convert("RGB")

    # Pixel difference
    difference = ImageChops.difference(original, compressed)

    # Maximum difference
    extrema = difference.getextrema()
    max_difference = max(max(channel) for channel in extrema)

    if max_difference == 0:
        max_difference = 1

    # Same enhancement as train.py and teammate's ela.py
    scale = 255.0 / max_difference
    ela_image = ImageEnhance.Brightness(difference).enhance(scale)

    # Grayscale
    gray_image = ela_image.convert("L")

    pixels = np.array(gray_image, dtype=np.float32)

    # EXACTLY the same 14 features used during training
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

    return np.array(features).reshape(1, -1)


# ============================================================
# PREDICTION
# ============================================================

def predict_image(image_path):

    if not MODEL_PATH.exists():
        print("ERROR: model.pkl not found.")
        print(f"Expected location: {MODEL_PATH}")
        return

    if not Path(image_path).exists():
        print("ERROR: Image not found.")
        print(f"Path: {image_path}")
        return

    # Load model
    package = joblib.load(MODEL_PATH)

    model = package["model"]
    scaler = package["scaler"]
    model_name = package["model_name"]

    # Extract ELA features
    features = extract_ela_features(image_path)

    # Logistic Regression requires scaling.
    # Random Forest does not.
    if scaler is not None:
        features = scaler.transform(features)

    # Prediction
    prediction = model.predict(features)[0]

    # Probability
    probabilities = model.predict_proba(features)[0]
    confidence = probabilities[prediction] * 100

    if prediction == 0:
        result = "REAL"
    else:
        result = "TAMPERED"

    print()
    print("=" * 45)
    print("       IMAGE TAMPERING DETECTION")
    print("=" * 45)
    print(f"Model      : {model_name}")
    print(f"Image      : {image_path}")
    print(f"Prediction : {result}")
    print(f"Confidence : {confidence:.2f}%")
    print("=" * 45)


# ============================================================
# COMMAND LINE
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage:")
        print(
            'python ML_Model\\prediction.py "path\\to\\image.jpg"'
        )

    else:

        predict_image(sys.argv[1])