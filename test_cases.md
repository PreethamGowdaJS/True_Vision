# Test Case Record

## Test Cases

| Test ID | Test Description | Input | Expected Result | Actual Result | Status |
|---------|------------------|-------|-----------------|---------------|--------|
| TC-01 | Upload a valid image | `image_processing/Samples/test.jpg` | Image should be accepted and displayed | Image was uploaded and displayed successfully | Pass |
| TC-02 | Test an authentic image | Generated 4000 × 4000 pixel JPG image | System should classify the authentic image appropriately | Model returned AUTHENTIC with 71.00% confidence using Random Forest | Pass |
| TC-03 | Test a manipulated image | `image_processing/Samples/test.jpg` | System should provide a prediction | Model returned TAMPERED with 90.00% confidence | Pass* |
| TC-04 | Upload an unsupported file | Non-image file | Unsupported file should not be accepted | File picker only allows JPG, JPEG, PNG, and WEBP files | Pass |
| TC-05 | Submit without an image | No input | Analyze option should not be available without an image | Analyze button is not displayed until an image is uploaded | Pass |
| TC-06 | Test supported image format | JPG image | Image should be processed correctly | JPG image was processed successfully | Pass |
| TC-07 | Test a large image | 4000 × 4000 pixel JPG image | System should handle the image without crashing | Large image was uploaded, processed, analyzed, and a prediction was displayed successfully | Pass |
| TC-08 | Check final prediction | `test.jpg` | Prediction should be displayed | TAMPERED, 90.00% confidence, Random Forest displayed successfully | Pass |
| TC-09 | Check complete workflow | Valid image | Input should successfully pass through the complete system | Upload → ELA → analysis → prediction → result display completed successfully | Pass |
| TC-10 | Check error handling | Invalid JPG file | Appropriate error should be displayed | Application displayed: "Unable to process the uploaded image: cannot identify image file" | Pass |
---

## Additional API Tests

| Test ID | Test Description | Input | Expected Result | Actual Result | Status |
|---------|------------------|-------|-----------------|---------------|--------|
| API-01 | FastAPI server startup | Backend application | Server should start successfully | Uvicorn started successfully on `127.0.0.1:8000` | Pass |
| API-02 | API health endpoint | `GET /` | API should return running status and model information | Returned `status: running` and `model: Random Forest` | Pass |
| API-03 | Prediction endpoint | `POST /predict` with `test.jpg` | API should return prediction and confidence | Returned TAMPERED with 90.0% confidence and Random Forest model | Pass |

---

## Status Definitions

### Pass
The system performed the tested operation successfully.

### Fail
The system did not produce the expected result.

### Pending
The test has not been performed yet.

### Pass*
The system successfully produced a prediction, but the ground-truth label of the test image has not been independently verified. Therefore, prediction correctness is not being claimed.

---

## Notes

- Testing was performed using the current integrated project modules.
- `test.jpg` was successfully processed by both the Streamlit interface and FastAPI backend.
- The machine-learning model returned `TAMPERED` with 90.00% confidence using the Random Forest model.
- The prediction output was successfully displayed in the Streamlit interface.
- ELA processing and heatmap generation were successfully verified.
- The result formatting issue that displayed raw HTML tags was fixed and retested successfully.
- Prediction correctness cannot be confirmed for `test.jpg` without a verified ground-truth label.
- Additional negative, authentic-image, unsupported-file, and large-image tests remain pending.