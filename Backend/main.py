from pathlib import Path
from io import BytesIO
import base64
import tempfile
import shutil

import numpy as np
import joblib

from PIL import Image, ImageChops, ImageEnhance

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# BACKEND PATH
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

# IMPORTANT:
# model.pkl must be inside the Backend folder
MODEL_PATH = BASE_DIR / "model.pkl"


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
# ELA PROCESSING
# ============================================================

def create_ela_image(image_bytes):
    """
    Create an ELA image using JPEG recompression at quality 90.
    """

    original = Image.open(
        BytesIO(image_bytes)
    ).convert("RGB")

    # --------------------------------------------------------
    # Recompress image at JPEG quality 90
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Calculate pixel difference
    # --------------------------------------------------------

    difference = ImageChops.difference(
        original,
        compressed,
    )

    extrema = difference.getextrema()

    max_difference = max(
        max(channel)
        for channel in extrema
    )

    if max_difference == 0:
        max_difference = 1

    # --------------------------------------------------------
    # Scale difference
    # --------------------------------------------------------

    scale = 255.0 / max_difference

    ela_image = ImageEnhance.Brightness(
        difference
    ).enhance(scale)

    return ela_image


# ============================================================
# ELA FEATURES FOR MACHINE LEARNING
# ============================================================

def extract_ela_features(image_bytes):
    """
    Extract the exact 14 numerical ELA features
    used during model training.
    """

    ela_image = create_ela_image(
        image_bytes
    )

    # Convert to grayscale
    gray_image = ela_image.convert("L")

    pixels = np.array(
        gray_image,
        dtype=np.float32,
    )

    # --------------------------------------------------------
    # EXACT 14 FEATURES USED DURING TRAINING
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

    return np.array(
        features
    ).reshape(1, -1)


# ============================================================
# GENERATE ELA HEATMAP
# ============================================================

def generate_ela_heatmap(image_bytes):
    """
    Generate ELA visualization and return it as
    a Base64 data URL for the Next.js frontend.
    """

    temp_dir = Path(
        tempfile.mkdtemp(
            prefix="true_vision_api_"
        )
    )

    try:

        # ----------------------------------------------------
        # Create ELA image
        # ----------------------------------------------------

        ela_image = create_ela_image(
            image_bytes
        )

        # ----------------------------------------------------
        # Save temporary JPEG
        # ----------------------------------------------------

        heatmap_path = (
            temp_dir / "ela_heatmap.jpg"
        )

        ela_image.save(
            heatmap_path,
            format="JPEG",
            quality=90,
        )

        # ----------------------------------------------------
        # Read generated image
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
@app.post("/api/predict")
async def predict(
    file: UploadFile = File(...)
):

    # --------------------------------------------------------
    # Read uploaded image
    # --------------------------------------------------------

    image_bytes = await file.read()

    # --------------------------------------------------------
    # Extract ELA features
    # --------------------------------------------------------

    features = extract_ela_features(
        image_bytes
    )

    # --------------------------------------------------------
    # Apply scaler if required
    # --------------------------------------------------------

    if scaler is not None:

        features = scaler.transform(
            features
        )

    # --------------------------------------------------------
    # Model prediction
    # --------------------------------------------------------

    prediction = model.predict(
        features
    )[0]

    # --------------------------------------------------------
    # Prediction probability
    # --------------------------------------------------------

    probabilities = model.predict_proba(
        features
    )[0]

    confidence = float(
        probabilities[prediction] * 100
    )

    # --------------------------------------------------------
    # Convert prediction to label
    # --------------------------------------------------------

    if prediction == 0:
        result = "REAL"
    else:
        result = "TAMPERED"

    # --------------------------------------------------------
    # Generate ELA visualization
    # --------------------------------------------------------

    try:

        ela_image = generate_ela_heatmap(
            image_bytes
        )

        ela_error = None

    except Exception as error:

        ela_image = None
        ela_error = str(error)

    # --------------------------------------------------------
    # Return result
    # --------------------------------------------------------

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
