from pathlib import Path
from io import BytesIO
import sys

import numpy as np
from PIL import Image, ImageChops, ImageEnhance
import joblib


# ============================================================
# MODEL PATH
# ============================================================

# Project structure:
#
# True_Vision/
# ├── ML_Model/
# │   └── prediction.py
# └── model/
#     └── model.pkl
#
# Therefore, go up one level from ML_Model,
# then enter the model folder.

MODEL_PATH = (
    Path(__file__).resolve().parent.parent/ "model.pkl"
)

ELA_QUALITY = 90


# ============================================================
# ELA FEATURE EXTRACTION
# Must match train.py exactly
# ============================================================

def extract_ela_features(image_path):

    # Load original image
    original = Image.open(image_path).convert("RGB")

    # --------------------------------------------------------
    # JPEG compression in memory
    # --------------------------------------------------------

    buffer = BytesIO()

    original.save(
        buffer,
        format="JPEG",
        quality=ELA_QUALITY
    )

    buffer.seek(0)

    compressed = Image.open(buffer).convert("RGB")

    # --------------------------------------------------------
    # Calculate pixel difference
    # --------------------------------------------------------

    difference = ImageChops.difference(
        original,
        compressed
    )

    # --------------------------------------------------------
    # Find maximum difference
    # --------------------------------------------------------

    extrema = difference.getextrema()

    max_difference = max(
        max(channel)
        for channel in extrema
    )

    if max_difference == 0:
        max_difference = 1

    # --------------------------------------------------------
    # Enhance ELA difference
    # --------------------------------------------------------

    scale = 255.0 / max_difference

    ela_image = ImageEnhance.Brightness(
        difference
    ).enhance(scale)

    # --------------------------------------------------------
    # Convert ELA image to grayscale
    # --------------------------------------------------------

    gray_image = ela_image.convert("L")

    pixels = np.array(
        gray_image,
        dtype=np.float32
    )

    # --------------------------------------------------------
    # EXACTLY THE SAME 14 FEATURES USED DURING TRAINING
    # --------------------------------------------------------

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

    image_path = Path(image_path)

    # --------------------------------------------------------
    # Check whether model exists
    # --------------------------------------------------------

    if not MODEL_PATH.exists():

        raise FileNotFoundError(
            f"model.pkl not found.\n"
            f"Expected location: {MODEL_PATH}"
        )

    # --------------------------------------------------------
    # Check whether image exists
    # --------------------------------------------------------

    if not image_path.exists():

        raise FileNotFoundError(
            f"Image not found.\n"
            f"Expected location: {image_path}"
        )

    # --------------------------------------------------------
    # Load trained model package
    # --------------------------------------------------------

    package = joblib.load(MODEL_PATH)

    model = package["model"]
    scaler = package["scaler"]
    model_name = package["model_name"]

    # --------------------------------------------------------
    # Extract ELA features
    # --------------------------------------------------------

    features = extract_ela_features(
        image_path
    )

    # --------------------------------------------------------
    # Apply scaler if available
    #
    # Logistic Regression requires scaling.
    # Random Forest does not.
    # --------------------------------------------------------

    if scaler is not None:

        features = scaler.transform(
            features
        )

    # --------------------------------------------------------
    # Make prediction
    # --------------------------------------------------------

    prediction = model.predict(
        features
    )[0]

    # --------------------------------------------------------
    # Get prediction probabilities
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        features
    )[0]

    confidence = (
        probabilities[prediction] * 100
    )

    # --------------------------------------------------------
    # Convert prediction to readable label
    # --------------------------------------------------------

    if prediction == 0:

        result = "REAL"

    else:

        result = "TAMPERED"

    # --------------------------------------------------------
    # Display result in terminal
    # --------------------------------------------------------

    print()

    print("=" * 45)
    print("       IMAGE TAMPERING DETECTION")
    print("=" * 45)

    print(f"Model      : {model_name}")
    print(f"Image      : {image_path}")
    print(f"Prediction : {result}")
    print(f"Confidence : {confidence:.2f}%")

    print("=" * 45)

    # --------------------------------------------------------
    # Return result for Streamlit/frontend
    # --------------------------------------------------------

    return {
        "result": result,
        "confidence": float(confidence),
        "model_name": model_name
    }


# ============================================================
# COMMAND LINE USAGE
# ============================================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print("Usage:")

        print(
            'python ML_Model\\prediction.py '
            '"path\\to\\image.jpg"'
        )

    else:

        predict_image(
            sys.argv[1]
        )