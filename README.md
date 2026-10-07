# True_Vision – Image Tampering Detection

## Project Overview

True_Vision is an image tampering detection system designed to identify whether a digital image is potentially authentic or manipulated.

The system combines **Error Level Analysis (ELA)** with a trained **machine-learning model** to analyze uploaded images and produce a prediction.

The project includes:

- A Streamlit user interface.
- An ELA image-processing module.
- A machine-learning prediction module.
- A FastAPI backend.
- Testing and documentation.

---

## Problem Statement

Digital images can be easily modified using image-editing software.

Identifying whether an image has been manipulated manually can be difficult and time-consuming. True_Vision aims to assist users by analyzing image characteristics and providing a machine-learning-based prediction.

---

## Objectives

- Accept digital images for analysis.
- Generate Error Level Analysis results.
- Extract ELA-based image features.
- Classify images as `REAL` or `TAMPERED`.
- Display prediction confidence.
- Provide an understandable result to the user.
- Provide a backend API for image prediction.
- Test the system under different input conditions.

---

## System Workflow

The main workflow is:

**Image Upload → ELA Processing → Feature Extraction → Machine-Learning Prediction → Result Display**

### 1. Image Upload

The user uploads an image through the Streamlit interface.

Supported formats:

- JPG
- JPEG
- PNG
- WEBP

### 2. Error Level Analysis

The system compares the original image with a JPEG-compressed version.

The resulting differences are used to generate an ELA representation and heatmap.

### 3. Feature Extraction

Statistical features are extracted from the ELA information.

These features are passed to the trained machine-learning model.

### 4. Prediction

The model classifies the image as:

- `REAL`
- `TAMPERED`

The system also returns a confidence value and model name.

### 5. Result

The Streamlit interface displays:

- Image information
- ELA heatmap
- Prediction
- Confidence
- Model name
- Explanation of the analysis

---

## Technologies Used

- Python
- Streamlit
- FastAPI
- Pillow
- NumPy
- scikit-learn
- Joblib
- Matplotlib
- Uvicorn

---

## Project Structure

```text
True_Vision/
│
├── app.py
├── model.pkl
├── confusion_matrix.png
├── ela_output.jpg
├── ela_heatmap.jpg
│
├── Backend/
│   └── main.py
│
├── frontend/
│   ├── .gitignore
│   └── requirements.txt
│
├── image_processing/
│   ├── ela.py
│   ├── preprocessing.py
│   ├── __init__.py
│   └── Samples/
│       └── test.jpg
│
└── ML_Model/
    ├── prediction.py
    └── train.py