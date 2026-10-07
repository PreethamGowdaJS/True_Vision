# Project Documentation

## 1. Project Overview

**True_Vision** is an image tampering detection system designed to identify whether a digital image is potentially authentic or manipulated.

The project combines **Error Level Analysis (ELA)** with a trained **machine-learning model**. The system provides a prediction along with a confidence value and the name of the model used.

The project provides two ways to interact with the detection system:

- A Streamlit-based user interface.
- A FastAPI backend API.

---

## 2. Problem Statement

Digital images can be easily edited or manipulated using modern image-editing software.

Detecting image manipulation manually can be difficult and time-consuming. True_Vision aims to assist users by analyzing images and identifying patterns that may indicate manipulation.

---

## 3. Objectives

The main objectives of the project are:

1. Accept digital images as input.
2. Process uploaded images using Error Level Analysis.
3. Extract relevant ELA-based features.
4. Use a trained machine-learning model to classify images.
5. Provide a prediction of `REAL` or `TAMPERED`.
6. Display the model confidence.
7. Provide an understandable result through a user interface.
8. Provide a backend API for image prediction.

---

## 4. Technologies Used

The project uses the following technologies:

- **Python** – Main programming language.
- **Streamlit** – User interface.
- **FastAPI** – Backend REST API.
- **Pillow (PIL)** – Image loading and processing.
- **NumPy** – Numerical and feature-processing operations.
- **scikit-learn** – Machine-learning models and evaluation.
- **Joblib** – Saving and loading the trained model.
- **Matplotlib** – ELA heatmap visualization.
- **Uvicorn** – FastAPI server.

---

## 5. System Workflow

The main workflow of the system is:

**Image Upload → ELA Processing → Feature Extraction → Machine-Learning Prediction → Result Display**

### Step 1 – Image Input

The user uploads an image through the Streamlit interface.

The supported upload formats are:

- JPG
- JPEG
- PNG
- WEBP

The application displays basic information such as the file name, resolution, and file size.

---

### Step 2 – Error Level Analysis

The uploaded image is processed using **Error Level Analysis (ELA)**.

The system creates a JPEG-compressed version of the image and compares it with the original image.

The difference between the images is used to generate an ELA representation and heatmap.

Areas with unusual compression differences can provide useful information for detecting possible image manipulation.

---

### Step 3 – Feature Extraction

ELA information is converted into numerical features for the machine-learning model.

The extracted features include statistical measurements such as:

- Mean
- Standard deviation
- Minimum
- Maximum
- Median
- Percentiles
- Fractions of pixels above selected difference thresholds

These features are used as input to the trained classification model.

---

### Step 4 – Machine-Learning Prediction

The trained model analyzes the extracted ELA features.

The prediction system returns:

- `REAL`
- `TAMPERED`

It also provides:

- Prediction confidence.
- Model name.

The current loaded model used during testing was **Random Forest**.

---

### Step 5 – Result Display

The Streamlit interface displays:

- Prediction result.
- Confidence percentage.
- Model name.
- ELA heatmap.
- Explanation of the analysis process.

---

## 6. Project Structure

The main project structure is:

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