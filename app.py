import os
import sys
import tempfile
from pathlib import Path
import textwrap

import streamlit as st
from PIL import Image, ImageOps


# ============================================================
# PROJECT PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

# Make sure Python can find the teammate modules
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from image_processing.ela import perform_ela
from ML_Model.prediction import predict_image


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="True Vision | Image Authenticity",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f8fafc;
    }

    .main {
        padding-top: 1rem;
    }

    /* ---------- HEADER ---------- */

    .brand {
        font-size: 2.4rem;
        font-weight: 800;
        letter-spacing: 2px;
        color: #0f172a;
        margin-bottom: 0;
    }

    .brand-accent {
        color: #2563eb;
    }

    .subtitle {
        color: #64748b;
        font-size: 1rem;
        margin-top: 0.2rem;
        margin-bottom: 2rem;
    }

    /* ---------- CARDS ---------- */

    .info-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .card-title {
        color: #0f172a;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.8rem;
    }

    .card-description {
        color: #64748b;
        font-size: 0.92rem;
        line-height: 1.6;
    }

    /* ---------- UPLOAD ---------- */

    [data-testid="stFileUploader"] {
        background: white;
        border: 2px dashed #bfdbfe;
        border-radius: 14px;
        padding: 1rem;
    }

    [data-testid="stFileUploader"] section {
        border: none;
    }

    /* ---------- BUTTON ---------- */

    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background: #2563eb;
        color: white;
        font-weight: 700;
        padding: 0.75rem 1rem;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background: #1d4ed8;
        color: white;
    }

    /* ---------- IMAGE LABEL ---------- */

    .image-label {
        font-size: 0.9rem;
        font-weight: 700;
        color: #334155;
        margin-bottom: 0.5rem;
    }

    /* ---------- RESULT ---------- */

    .result-card {
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        margin-top: 1.5rem;
        margin-bottom: 1.5rem;
    }

    .result-tampered {
        background: #fef2f2;
        border: 1px solid #fecaca;
    }

    .result-authentic {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
    }

    .result-title {
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .result-confidence {
        font-size: 1.1rem;
        color: #475569;
    }

    /* ---------- METRICS ---------- */

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
    }

    .metric-value {
        font-size: 1.25rem;
        font-weight: 700;
        color: #0f172a;
    }

    .metric-label {
        font-size: 0.8rem;
        color: #64748b;
        margin-top: 0.25rem;
    }

    /* ---------- INFO BOX ---------- */

    .info-box {
        background: #eff6ff;
        border: 1px solid #bfdbfe;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        color: #1e3a8a;
        line-height: 1.6;
        margin-top: 1rem;
    }

    /* ---------- FOOTER ---------- */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding: 1rem;
        border-top: 1px solid #e2e8f0;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

if "uploaded_image" not in st.session_state:
    st.session_state["uploaded_image"] = None

if "uploaded_path" not in st.session_state:
    st.session_state["uploaded_path"] = None

if "ela_path" not in st.session_state:
    st.session_state["ela_path"] = None

if "heatmap_path" not in st.session_state:
    st.session_state["heatmap_path"] = None

if "analysis_result" not in st.session_state:
    st.session_state["analysis_result"] = None


# ============================================================
# HEADER
# ============================================================


# ============================================================
# INTRODUCTION
# ============================================================

st.markdown(
    """
    <div class="info-card">
        <div class="card-title">🔍 Detect Image Manipulation</div>
        <div class="card-description">
            Upload an image and True Vision will analyze it using
            Error Level Analysis (ELA) and a machine-learning model
            to identify possible image manipulation.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FILE UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Choose an image",
    type=["jpg", "jpeg", "png", "webp"],
    label_visibility="collapsed",
)


# ============================================================
# PROCESS UPLOADED IMAGE
# ============================================================

if uploaded_file is not None:

    try:

        # --------------------------------------------------------
        # Load image for displaying in Streamlit
        # --------------------------------------------------------

        image = Image.open(uploaded_file).convert("RGB")

        st.session_state["uploaded_image"] = image

        # --------------------------------------------------------
        # Save uploaded image to a temporary file
        # --------------------------------------------------------

        suffix = Path(uploaded_file.name).suffix.lower()

        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            suffix = ".jpg"

        temp_input = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        )

        temp_input.write(uploaded_file.getbuffer())
        temp_input.close()

        st.session_state["uploaded_path"] = temp_input.name

        # --------------------------------------------------------
        # Display file information
        # --------------------------------------------------------

        file_size_kb = len(uploaded_file.getbuffer()) / 1024

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{uploaded_file.name}</div>
                    <div class="metric-label">File Name</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col2:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {image.width} × {image.height}
                    </div>
                    <div class="metric-label">Resolution</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col3:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">
                        {file_size_kb:.1f} KB
                    </div>
                    <div class="metric-label">File Size</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # --------------------------------------------------------
        # Generate REAL ELA
        # --------------------------------------------------------

        temp_dir = tempfile.mkdtemp(prefix="true_vision_")

        ela_output_path = os.path.join(
            temp_dir,
            "ela_output.jpg",
        )

        heatmap_path = os.path.join(
            temp_dir,
            "ela_heatmap.jpg",
        )

        try:

            perform_ela(
                st.session_state["uploaded_path"],
                ela_output_path,
                heatmap_path,
                quality=90,
            )

            st.session_state["ela_path"] = ela_output_path
            st.session_state["heatmap_path"] = heatmap_path

        except Exception as ela_error:

            st.error(
                f"ELA processing failed: {ela_error}"
            )

            st.session_state["ela_path"] = None
            st.session_state["heatmap_path"] = None

        # --------------------------------------------------------
        # Original + ELA Heatmap
        # --------------------------------------------------------

        st.markdown(
            '<div class="image-label">Image Analysis</div>',
            unsafe_allow_html=True,
        )

        image_col, ela_col = st.columns(2)

        with image_col:

            st.markdown(
                '<div class="image-label">Original Image</div>',
                unsafe_allow_html=True,
            )

            st.image(
                image,
                use_container_width=True,
            )

        with ela_col:

            st.markdown(
                '<div class="image-label">ELA Heatmap</div>',
                unsafe_allow_html=True,
            )

            if (
                st.session_state["heatmap_path"]
                and os.path.exists(
                    st.session_state["heatmap_path"]
                )
            ):

                st.image(
                    st.session_state["heatmap_path"],
                    use_container_width=True,
                )

            else:

                st.warning(
                    "ELA heatmap could not be generated."
                )

        # --------------------------------------------------------
        # Analysis Button
        # --------------------------------------------------------

        st.markdown("<br>", unsafe_allow_html=True)

        analyze_button = st.button(
            "🔍  Analyze Image",
            use_container_width=True,
        )

        if analyze_button:

            if not st.session_state["uploaded_path"]:

                st.error(
                    "Please upload an image first."
                )

            else:

                try:

                    with st.spinner(
                        "Analyzing image authenticity..."
                    ):

                        # ------------------------------------------------
                        # REAL ML PREDICTION
                        # ------------------------------------------------

                        result = predict_image(
                            st.session_state["uploaded_path"]
                        )

                        st.session_state[
                            "analysis_result"
                        ] = result

                    st.success(
                        "Analysis completed successfully."
                    )

                except Exception as analysis_error:

                    st.session_state[
                        "analysis_result"
                    ] = None

                    st.error(
                        f"Analysis failed: {analysis_error}"
                    )


    except Exception as upload_error:

        st.error(
            f"Unable to process the uploaded image: "
            f"{upload_error}"
        )


# ============================================================
# RESULT SECTION
# ============================================================

result = st.session_state.get("analysis_result")

if result is not None:

    # Get values FIRST
    prediction = result.get("result", "UNKNOWN")
    confidence = float(result.get("confidence", 0))
    model_name = result.get("model_name", "Machine Learning Model")

    st.markdown("<br>", unsafe_allow_html=True)

    if prediction == "TAMPERED":

        st.markdown(
    textwrap.dedent(
        f"""
        <div class="result-card result-tampered">
            <div class="result-title">
                ⚠ TAMPERED
            </div>
            <div class="result-confidence">
                The model detected possible image manipulation.
            </div>
            <br>
            <div class="result-confidence">
                Confidence:
                <strong>{confidence:.2f}%</strong>
            </div>
            <div class="result-confidence">
                Model:
                <strong>{model_name}</strong>
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)
    elif prediction == "REAL":

        st.markdown(
    textwrap.dedent(
        f"""
        <div class="result-card result-authentic">
            <div class="result-title">
                ✓ AUTHENTIC
            </div>
            <div class="result-confidence">
                No significant manipulation was detected
                by the trained model.
            </div>
            <br>
            <div class="result-confidence">
                Confidence:
                <strong>{confidence:.2f}%</strong>
            </div>
            <div class="result-confidence">
                Model:
                <strong>{model_name}</strong>
            </div>
        </div>
        """
    ),
    unsafe_allow_html=True,
)
    else:

        st.warning(
            f"Model returned an unexpected result: {prediction}"
        )

    # Confidence
    st.markdown(
        "<div class='image-label'>Model Confidence</div>",
        unsafe_allow_html=True,
    )

    st.progress(
        min(max(confidence / 100, 0.0), 1.0)
    )

    # Explanation
    st.markdown(
        """
        <div class="info-box">
            <strong>How does this work?</strong><br>
            Error Level Analysis compares an image with a
            JPEG-compressed version to identify regions with
            unusual compression differences. These ELA
            characteristics are then analyzed by the trained
            machine-learning model to classify the image as
            potentially authentic or tampered.
        </div>
        """,
        unsafe_allow_html=True,
    )