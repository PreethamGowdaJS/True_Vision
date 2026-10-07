# Testing Documentation

## 1. Testing Objective

The objective of testing is to verify that the image authenticity detection system:

- Accepts valid image files.
- Processes uploaded images correctly.
- Generates Error Level Analysis (ELA) results.
- Produces machine-learning predictions.
- Displays prediction results and confidence values.
- Handles invalid inputs without crashing.
- Handles large images successfully.
- Provides a working FastAPI backend.
- Supports the complete workflow from image upload to final prediction.

Testing was performed on the integrated project modules.

---

## 2. Testing Areas

### 2.1 Image Input Testing

The image upload functionality was tested using:

- Valid JPG images.
- A large 4000 × 4000 pixel JPG image.
- An invalid JPG file containing non-image data.
- An unsupported file type.
- No-image input.

Results showed that valid images could be uploaded successfully and invalid image data was rejected with an appropriate error message.

---

### 2.2 Image Processing Testing

The image processing functionality was tested to verify that:

- Images are loaded correctly.
- ELA processing works successfully.
- ELA heatmaps are generated.
- Large images can be processed.
- Invalid image files are handled safely.

The tests confirmed that ELA processing worked successfully for valid images, including the large 4000 × 4000 pixel test image.

---

### 2.3 Prediction Testing

The machine-learning prediction system was tested using:

- The project sample image `test.jpg`.
- A generated 4000 × 4000 pixel image.

Observed results included:

- `test.jpg` → TAMPERED, 90.00% confidence.
- Generated large image → AUTHENTIC, 71.00% confidence.

The prediction functionality was successfully executed through both the Streamlit interface and FastAPI backend.

The classification correctness of `test.jpg` was not independently verified because its ground-truth label was not available.

---

### 2.4 Error Handling Testing

The system was tested with invalid inputs.

An invalid file named `invalid.jpg` was created with non-image contents. When uploaded, the application displayed:

> Unable to process the uploaded image: cannot identify image file

The application did not crash.

The file uploader also prevented unsupported file types from being selected.

The Analyze Image option was not displayed when no image was uploaded.

---

### 2.5 Integration Testing

The complete workflow was tested:

**Image Upload → ELA Processing → Model Prediction → Result Display**

The complete workflow executed successfully.

The Streamlit interface successfully displayed:

- Uploaded image information.
- ELA heatmap.
- Prediction result.
- Confidence value.
- Model name.
- Explanation of the ELA process.

A result-formatting issue that initially displayed raw HTML tags was identified and fixed. The result display was then retested successfully.

---

### 2.6 FastAPI Backend Testing

The FastAPI backend was also tested.

#### Server Startup

The backend successfully started using Uvicorn on:

`http://127.0.0.1:8000`

#### Health Endpoint

The `GET /` endpoint returned:

```json
{
    "message": "Image Tampering Detection API",
    "status": "running",
    "model": "Random Forest"
}