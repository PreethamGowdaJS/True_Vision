from pathlib import Path
from io import BytesIO
import base64
import tempfile
import shutil
import sys

import numpy as np
import joblib

from PIL import Image, ImageChops, ImageEnhance

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PROJECT PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

# Allow this file to import modules from the project root
sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# IMPORT EXISTING ELA MODULE
# ============================================================

from image_processing.ela import perform_ela


# ============================================================
# MODEL PATH
# ============================================================

MODEL_PATH = PROJECT_ROOT / "model.pkl"


# ============================================================
# LOAD TRAINED MODEL
# ============================================================

package = joblib.load(MODEL_PATH)

model = package["model"]
scaler = package["scaler"]
model_name = package["model_name"]


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="Image Tampering Detection API",
    description=(
        "Detects whether an image is REAL or TAMPERED "
        "using Error Level Analysis and Machine Learning."
    ),
    version="1.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ELA FEATURES FOR MACHINE LEARNING
# ============================================================

def extract_ela_features(image_bytes):
    """
    Extract the same 14 numerical ELA features used
    during model training.
    """

    # Open uploaded image
    original = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    # Recompress at JPEG quality 90
    buffer = BytesIO()

    original.save(
        buffer,
        format="JPEG",
        quality=90,
    )

    buffer.seek(0)

    compressed = Image.open(
        buffer
    ).convert("RGB")

    # Calculate pixel difference
    difference = ImageChops.difference(
        original,
        compressed,
    )

    # Find maximum difference
    extrema = difference.getextrema()

    max_difference = max(
        max(channel)
        for channel in extrema
    )

    if max_difference == 0:
        max_difference = 1

    # Scale ELA difference
    scale = 255.0 / max_difference

    ela_image = ImageEnhance.Brightness(
        difference
    ).enhance(scale)

    # Convert to grayscale
    gray_image = ela_image.convert("L")

    pixels = np.array(
        gray_image,
        dtype=np.float32,
    )

    # ========================================================
    # 14 FEATURES
    # ========================================================

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

    return np.array(
        features
    ).reshape(1, -1)


# ============================================================
# GENERATE ELA HEATMAP
# ============================================================

def generate_ela_heatmap(image_bytes):
    """
    Generate the actual ELA heatmap using the existing
    image_processing/ela.py module.

    The resulting JPEG is converted to Base64 so that
    the Next.js frontend can display it directly.
    """

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="true_vision_api_"
        )
    )

    try:

        # ----------------------------------------------------
        # Temporary file paths
        # ----------------------------------------------------

        input_path = temp_dir / "input.jpg"

        ela_output_path = (
            temp_dir / "ela_output.jpg"
        )

        heatmap_path = (
            temp_dir / "ela_heatmap.jpg"
        )

        # ----------------------------------------------------
        # Save uploaded image
        # ----------------------------------------------------

        input_path.write_bytes(
            image_bytes
        )

        # ----------------------------------------------------
        # Run existing ELA implementation
        # ----------------------------------------------------

        perform_ela(
            str(input_path),
            str(ela_output_path),
            str(heatmap_path),
            quality=90,
        )

        # ----------------------------------------------------
        # Read generated heatmap
        # ----------------------------------------------------

        heatmap_bytes = heatmap_path.read_bytes()

        # ----------------------------------------------------
        # Convert to Base64
        # ----------------------------------------------------

        encoded = base64.b64encode(
            heatmap_bytes
        ).decode("utf-8")

        return (
            "data:image/jpeg;base64,"
            + encoded
        )

    finally:

        # ----------------------------------------------------
        # Remove temporary directory
        # ----------------------------------------------------

        shutil.rmtree(
            temp_dir,
            ignore_errors=True,
        )


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Image Tampering Detection API",
        "status": "running",
        "model": model_name,
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
async def predict(
    file: UploadFile = File(...)
):

    # ========================================================
    # READ UPLOADED IMAGE
    # ========================================================

    image_bytes = await file.read()

    # ========================================================
    # EXTRACT ELA FEATURES
    # ========================================================

    features = extract_ela_features(
        image_bytes
    )

    # ========================================================
    # APPLY SCALER
    # ========================================================

    if scaler is not None:

        features = scaler.transform(
            features
        )

    # ========================================================
    # MODEL PREDICTION
    # ========================================================

    prediction = model.predict(
        features
    )[0]

    # ========================================================
    # PREDICTION PROBABILITIES
    # ========================================================

    probabilities = model.predict_proba(
        features
    )[0]

    confidence = float(
        probabilities[prediction] * 100
    )

    # ========================================================
    # CONVERT LABEL TO RESULT
    # ========================================================

    if prediction == 0:

        result = "REAL"

    else:

        result = "TAMPERED"

    # ========================================================
    # GENERATE ELA HEATMAP
    # ========================================================

    try:

        ela_image = generate_ela_heatmap(
            image_bytes
        )

        ela_error = None

    except Exception as error:

        ela_image = None

        ela_error = str(error)

    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {
        "filename": file.filename,
        "prediction": result,
        "confidence": round(
            confidence,
            2,
        ),
        "model": model_name,
        "ela_image": ela_image,
        "ela_error": ela_error,
    }