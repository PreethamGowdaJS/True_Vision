from pathlib import Path
from io import BytesIO

import numpy as np
import joblib

from PIL import Image, ImageChops, ImageEnhance

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent / "model.pkl"


# ============================================================
# LOAD MODEL
# ============================================================

package = joblib.load(MODEL_PATH)

model = package["model"]
scaler = package["scaler"]
model_name = package["model_name"]


# ============================================================
# FASTAPI
# ============================================================

app = FastAPI(
    title="Image Tampering Detection API",
    description="Detects whether an image is REAL or TAMPERED using ELA and Machine Learning.",
    version="1.0"
)


# Allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ELA FEATURE EXTRACTION
# Same implementation used during training
# ============================================================

def extract_ela_features(image_bytes):

    original = Image.open(BytesIO(image_bytes)).convert("RGB")

    # JPEG compression
    buffer = BytesIO()
    original.save(buffer, format="JPEG", quality=90)
    buffer.seek(0)

    compressed = Image.open(buffer).convert("RGB")

    # Pixel difference
    difference = ImageChops.difference(original, compressed)

    # Maximum difference
    extrema = difference.getextrema()
    max_difference = max(max(channel) for channel in extrema)

    if max_difference == 0:
        max_difference = 1

    # ELA enhancement
    scale = 255.0 / max_difference
    ela_image = ImageEnhance.Brightness(difference).enhance(scale)

    # Convert to grayscale
    gray_image = ela_image.convert("L")

    pixels = np.array(gray_image, dtype=np.float32)

    # Same 14 features used during training
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
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Image Tampering Detection API",
        "status": "running",
        "model": model_name
    }


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    image_bytes = await file.read()

    # Extract features
    features = extract_ela_features(image_bytes)

    # Scale only if required
    if scaler is not None:
        features = scaler.transform(features)

    # Prediction
    prediction = model.predict(features)[0]

    # Confidence
    probabilities = model.predict_proba(features)[0]
    confidence = float(probabilities[prediction] * 100)

    if prediction == 0:
        result = "REAL"
    else:
        result = "TAMPERED"

    return {
        "filename": file.filename,
        "prediction": result,
        "confidence": round(confidence, 2),
        "model": model_name
    }