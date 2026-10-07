import os
import sys
import tempfile
import mimetypes
from pathlib import Path
from html import escape

import requests
import streamlit as st
from PIL import Image

# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# TEAMMATE ELA MODULE
# ============================================================

from image_processing.ela import perform_ela


# ============================================================
# CONFIGURATION
# ============================================================

BACKEND_URL = "http://127.0.0.1:8000/predict"

st.set_page_config(
    page_title="True Vision | Image Authenticity",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# IMPORTANT:
# We use st.html(), NOT st.markdown(), for custom HTML.
# ============================================================

st.html(
    """
    <style>

    /* =====================================================
       GLOBAL
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at top left,
                rgba(59, 130, 246, 0.10),
                transparent 35%
            ),
            radial-gradient(
                circle at top right,
                rgba(168, 85, 247, 0.10),
                transparent 35%
            ),
            #f8fafc;
    }

    .main .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }


    /* =====================================================
       HEADER
       ===================================================== */

    .tv-header {
        text-align: center;
        padding: 2rem 1rem 1.5rem 1rem;
    }

    .tv-logo {
        display: inline-block;
        background: linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        );
        color: white;
        padding: 0.45rem 0.9rem;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 1rem;
        box-shadow: 0 8px 25px rgba(37, 99, 235, 0.25);
    }

    .tv-title {
        font-size: 3.5rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -2px;
        margin: 0;
        color: #0f172a;
    }

    .tv-title-gradient {
        background: linear-gradient(
            90deg,
            #2563eb,
            #7c3aed,
            #db2777
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }

    .tv-subtitle {
        max-width: 720px;
        margin: 1rem auto 0 auto;
        color: #64748b;
        font-size: 1.05rem;
        line-height: 1.7;
    }


    /* =====================================================
       INTRO CARD
       ===================================================== */

    .intro-card {
        background: rgba(255,255,255,0.92);
        border: 1px solid #e2e8f0;
        border-radius: 22px;
        padding: 1.5rem;
        margin: 1rem 0 1.5rem 0;
        box-shadow: 0 12px 35px rgba(15,23,42,0.06);
    }

    .intro-title {
        color: #0f172a;
        font-size: 1.25rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
    }

    .intro-text {
        color: #64748b;
        line-height: 1.65;
        font-size: 0.95rem;
    }


    /* =====================================================
       UPLOAD CARD
       ===================================================== */

    .upload-card {
        background: white;
        border: 2px dashed #93c5fd;
        border-radius: 22px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 10px 30px rgba(37,99,235,0.07);
    }

    .upload-title {
        font-size: 1.2rem;
        font-weight: 800;
        color: #0f172a;
        margin-bottom: 0.3rem;
    }

    .upload-subtitle {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }


    /* =====================================================
       METRIC CARDS
       ===================================================== */

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 18px;
        padding: 1.2rem;
        text-align: center;
        min-height: 105px;
        box-shadow: 0 8px 25px rgba(15,23,42,0.045);
    }

    .metric-icon {
        font-size: 1.4rem;
        margin-bottom: 0.3rem;
    }

    .metric-value {
        color: #0f172a;
        font-size: 1.05rem;
        font-weight: 800;
        word-break: break-word;
    }

    .metric-label {
        color: #64748b;
        font-size: 0.78rem;
        margin-top: 0.3rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }


    /* =====================================================
       SECTION HEADERS
       ===================================================== */

    .section-heading {
        font-size: 1.45rem;
        font-weight: 850;
        color: #0f172a;
        margin: 1.5rem 0 0.8rem 0;
    }

    .section-description {
        color: #64748b;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }


    /* =====================================================
       IMAGE LABEL
       ===================================================== */

    .image-label {
        background: #0f172a;
        color: white;
        display: inline-block;
        padding: 0.35rem 0.8rem;
        border-radius: 8px;
        font-size: 0.78rem;
        font-weight: 700;
        margin-bottom: 0.6rem;
    }


    /* =====================================================
       ANALYZE BUTTON
       ===================================================== */

    div.stButton > button {
        width: 100%;
        border: none;
        border-radius: 14px;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        font-weight: 800;
        color: white;
        background: linear-gradient(
            135deg,
            #2563eb,
            #7c3aed
        );
        box-shadow: 0 10px 25px rgba(79,70,229,0.25);
        transition: all 0.2s ease;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 30px rgba(79,70,229,0.32);
    }


    /* =====================================================
       RESULT CARD
       ===================================================== */

    .result-card {
        border-radius: 24px;
        padding: 2rem;
        margin-top: 1.5rem;
        text-align: center;
        border: 2px solid;
    }

    .result-real {
        background: linear-gradient(
            135deg,
            #ecfdf5,
            #f0fdf4
        );
        border-color: #86efac;
    }

    .result-tampered {
        background: linear-gradient(
            135deg,
            #fff1f2,
            #fef2f2
        );
        border-color: #fca5a5;
    }

    .result-icon {
        font-size: 3rem;
        margin-bottom: 0.5rem;
    }

    .result-title {
        font-size: 2.1rem;
        font-weight: 900;
        margin-bottom: 0.5rem;
    }

    .real-title {
        color: #15803d;
    }

    .tampered-title {
        color: #dc2626;
    }

    .result-confidence {
        color: #475569;
        font-size: 1rem;
        margin-top: 0.5rem;
    }

    .result-confidence strong {
        color: #0f172a;
        font-size: 1.25rem;
    }


    /* =====================================================
       PIPELINE
       ===================================================== */

    .pipeline-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 20px;
        padding: 1.4rem;
        margin-top: 1.5rem;
        box-shadow: 0 8px 25px rgba(15,23,42,0.04);
    }

    .pipeline-title {
        color: #0f172a;
        font-size: 1rem;
        font-weight: 800;
        margin-bottom: 1rem;
    }

    .pipeline {
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        flex-wrap: wrap;
    }

    .pipeline-step {
        background: #eff6ff;
        color: #1d4ed8;
        border: 1px solid #bfdbfe;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .pipeline-arrow {
        color: #94a3b8;
        font-weight: 900;
    }


    /* =====================================================
       INFO BOX
       ===================================================== */

    .info-box {
        background: linear-gradient(
            135deg,
            #eff6ff,
            #f5f3ff
        );
        border: 1px solid #c7d2fe;
        border-radius: 18px;
        padding: 1.2rem;
        color: #334155;
        line-height: 1.65;
        margin-top: 1.5rem;
    }

    .info-box-title {
        color: #3730a3;
        font-weight: 800;
        margin-bottom: 0.4rem;
    }


    /* =====================================================
       FOOTER
       ===================================================== */

    .footer {
        text-align: center;
        color: #94a3b8;
        font-size: 0.8rem;
        margin-top: 3rem;
        padding-top: 1.5rem;
        border-top: 1px solid #e2e8f0;
    }


    /* =====================================================
       FILE UPLOADER
       ===================================================== */

    [data-testid="stFileUploader"] {
        background: transparent;
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "uploaded_path" not in st.session_state:
    st.session_state.uploaded_path = None

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None

if "ela_path" not in st.session_state:
    st.session_state.ela_path = None

if "heatmap_path" not in st.session_state:
    st.session_state.heatmap_path = None

if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None

if "uploaded_filename" not in st.session_state:
    st.session_state.uploaded_filename = None


# ============================================================
# HEADER
# ============================================================

st.html(
    """
    <div class="tv-header">

        <div class="tv-logo">
            TRUE VISION • AI FORENSICS
        </div>

        <h1 class="tv-title">
            See Beyond the <span class="tv-title-gradient">Pixels.</span>
        </h1>

        <p class="tv-subtitle">
            An intelligent image authenticity system that combines
            Error Level Analysis with Machine Learning to detect
            possible image manipulation.
        </p>

    </div>
    """
)


# ============================================================
# INTRODUCTION
# ============================================================

st.html(
    """
    <div class="intro-card">

        <div class="intro-title">
            🔍 Detect Image Manipulation
        </div>

        <div class="intro-text">
            Upload an image and True Vision will examine its
            compression-error patterns using ELA and then send
            the extracted features to our trained Random Forest
            classifier through the FastAPI backend.
        </div>

    </div>
    """
)


# ============================================================
# UPLOAD AREA
# ============================================================

st.html(
    """
    <div class="upload-card">

        <div class="upload-title">
            📤 Upload an Image
        </div>

        <div class="upload-subtitle">
            Supported formats: JPG, JPEG, PNG, WEBP
        </div>

    </div>
    """
)

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

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        image = Image.open(uploaded_file).convert("RGB")

        st.session_state.uploaded_image = image
        st.session_state.uploaded_filename = uploaded_file.name

        # ----------------------------------------------------
        # Save temporary image
        # ----------------------------------------------------

        suffix = Path(uploaded_file.name).suffix.lower()

        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
            suffix = ".jpg"

        temp_input = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix,
        )

        temp_input.write(uploaded_file.getbuffer())
        temp_input.close()

        st.session_state.uploaded_path = temp_input.name

        # New upload = clear old prediction
        st.session_state.analysis_result = None

        # ----------------------------------------------------
        # File information
        # ----------------------------------------------------

        file_size_kb = len(uploaded_file.getbuffer()) / 1024

        safe_filename = escape(uploaded_file.name)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.html(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">📄</div>
                    <div class="metric-value">
                        {safe_filename}
                    </div>
                    <div class="metric-label">
                        File Name
                    </div>
                </div>
                """
            )

        with col2:
            st.html(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">🖼️</div>
                    <div class="metric-value">
                        {image.width} × {image.height}
                    </div>
                    <div class="metric-label">
                        Resolution
                    </div>
                </div>
                """
            )

        with col3:
            st.html(
                f"""
                <div class="metric-card">
                    <div class="metric-icon">💾</div>
                    <div class="metric-value">
                        {file_size_kb:.1f} KB
                    </div>
                    <div class="metric-label">
                        File Size
                    </div>
                </div>
                """
            )

        # ====================================================
        # ELA PROCESSING
        # ====================================================

        st.html(
            """
            <div class="section-heading">
                🧪 Image Forensic Analysis
            </div>

            <div class="section-description">
                Error Level Analysis highlights areas where
                compression behaviour may differ from the rest
                of the image.
            </div>
            """
        )

        temp_dir = tempfile.mkdtemp(
            prefix="true_vision_"
        )

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
                st.session_state.uploaded_path,
                ela_output_path,
                heatmap_path,
                quality=90,
            )

            st.session_state.ela_path = ela_output_path
            st.session_state.heatmap_path = heatmap_path

        except Exception as ela_error:

            st.session_state.ela_path = None
            st.session_state.heatmap_path = None

            st.warning(
                f"ELA visualization could not be generated: {ela_error}"
            )

        # ====================================================
        # ORIGINAL + ELA
        # ====================================================

        image_col, ela_col = st.columns(2)

        with image_col:

            st.html(
                """
                <div class="image-label">
                    ORIGINAL IMAGE
                </div>
                """
            )

            st.image(
                image,
                use_container_width=True,
            )

        with ela_col:

            st.html(
                """
                <div class="image-label">
                    ELA HEATMAP
                </div>
                """
            )

            if (
                st.session_state.heatmap_path
                and os.path.exists(
                    st.session_state.heatmap_path
                )
            ):

                st.image(
                    st.session_state.heatmap_path,
                    use_container_width=True,
                )

            else:

                st.info(
                    "ELA heatmap is unavailable for this image."
                )

        # ====================================================
        # ANALYZE BUTTON
        # ====================================================

        st.html(
            """
            <div style="height: 12px;"></div>
            """
        )

        analyze_button = st.button(
            "🔍  Analyze Image Authenticity",
            use_container_width=True,
        )

        if analyze_button:

            if not st.session_state.uploaded_path:

                st.error(
                    "Please upload an image first."
                )

            else:

                # =================================================
                # SEND IMAGE TO FASTAPI
                # =================================================

                try:

                    with st.spinner(
                        "Running ELA features and Random Forest analysis..."
                    ):

                        image_path = Path(
                            st.session_state.uploaded_path
                        )

                        content_type, _ = mimetypes.guess_type(
                            image_path.name
                        )

                        if content_type is None:
                            content_type = "application/octet-stream"

                        with open(
                            image_path,
                            "rb",
                        ) as image_file:

                            response = requests.post(
                                BACKEND_URL,
                                files={
                                    "file": (
                                        image_path.name,
                                        image_file,
                                        content_type,
                                    )
                                },
                                timeout=60,
                            )

                        response.raise_for_status()

                        api_result = response.json()

                    # =================================================
                    # SAVE RESULT
                    # =================================================

                    st.session_state.analysis_result = {
                        "result": api_result.get(
                            "prediction",
                            "UNKNOWN",
                        ),
                        "confidence": float(
                            api_result.get(
                                "confidence",
                                0,
                            )
                        ),
                        "model_name": api_result.get(
                            "model",
                            "Unknown",
                        ),
                    }

                except requests.exceptions.ConnectionError:

                    st.error(
                        "❌ Cannot connect to the FastAPI backend. "
                        "Please make sure the backend is running on "
                        "http://127.0.0.1:8000"
                    )

                except requests.exceptions.Timeout:

                    st.error(
                        "⏱️ The backend took too long to respond."
                    )

                except requests.exceptions.HTTPError as http_error:

                    st.error(
                        f"❌ Backend returned an error: {http_error}"
                    )

                except Exception as error:

                    st.error(
                        f"❌ Analysis failed: {error}"
                    )

        # ====================================================
        # DISPLAY RESULT
        # ====================================================

        if st.session_state.analysis_result is not None:

            result_data = st.session_state.analysis_result

            result = result_data["result"]
            confidence = result_data["confidence"]
            model_name = result_data["model_name"]

            is_real = result.upper() == "REAL"

            if is_real:

                result_class = "result-real"
                title_class = "real-title"
                icon = "✓"
                title = "IMAGE APPEARS AUTHENTIC"
                message = (
                    "The model found the image more consistent "
                    "with the real-image patterns learned during training."
                )

            else:

                result_class = "result-tampered"
                title_class = "tampered-title"
                icon = "⚠️"
                title = "POSSIBLE TAMPERING DETECTED"
                message = (
                    "The model found patterns that are more consistent "
                    "with manipulated images."
                )

            # =================================================
            # RESULT CARD
            # =================================================

            st.html(
                f"""
                <div class="result-card {result_class}">

                    <div class="result-icon">
                        {icon}
                    </div>

                    <div class="result-title {title_class}">
                        {title}
                    </div>

                    <div class="result-confidence">
                        {escape(message)}
                    </div>

                    <div class="result-confidence"
                         style="margin-top: 1rem;">

                        Confidence:
                        <strong>
                            {confidence:.2f}%
                        </strong>

                    </div>

                    <div class="result-confidence">

                        Model:
                        <strong>
                            {escape(str(model_name))}
                        </strong>

                    </div>

                </div>
                """
            )

            # =================================================
            # CONFIDENCE PROGRESS
            # =================================================

            st.html(
                """
                <div class="section-heading">
                    📊 Prediction Confidence
                </div>
                """
            )

            st.progress(
                min(
                    max(
                        confidence / 100.0,
                        0.0,
                    ),
                    1.0,
                )
            )

            # =================================================
            # PIPELINE
            # =================================================

            st.html(
                """
                <div class="pipeline-card">

                    <div class="pipeline-title">
                        ⚙️ Detection Pipeline
                    </div>

                    <div class="pipeline">

                        <div class="pipeline-step">
                            📤 Image Upload
                        </div>

                        <div class="pipeline-arrow">
                            →
                        </div>

                        <div class="pipeline-step">
                            🧪 ELA Features
                        </div>

                        <div class="pipeline-arrow">
                            →
                        </div>

                        <div class="pipeline-step">
                            🌲 Random Forest
                        </div>

                        <div class="pipeline-arrow">
                            →
                        </div>

                        <div class="pipeline-step">
                            🎯 Prediction
                        </div>

                    </div>

                </div>
                """
            )

            # =================================================
            # IMPORTANT DISCLAIMER
            # =================================================

            st.html(
                """
                <div class="info-box">

                    <div class="info-box-title">
                        ℹ️ Important
                    </div>

                    This result is a machine-learning prediction,
                    not a forensic guarantee. Image compression,
                    resizing, screenshots, and other processing
                    can affect ELA-based analysis.

                </div>
                """
            )

    except Exception as error:

        st.error(
            f"Unable to process the uploaded image: {error}"
        )


# ============================================================
# HOW IT WORKS
# ============================================================

st.html(
    """
    <div class="pipeline-card">

        <div class="pipeline-title">
            💡 How True Vision Works
        </div>

        <div style="
            color:#64748b;
            line-height:1.7;
            font-size:0.9rem;
        ">

            <b style="color:#2563eb;">1. Upload</b>
            — Select an image you want to inspect.

            <br><br>

            <b style="color:#7c3aed;">2. ELA</b>
            — The system recompresses the image and measures
            differences in compression error levels.

            <br><br>

            <b style="color:#db2777;">3. Feature Extraction</b>
            — Statistical properties of the ELA image are extracted.

            <br><br>

            <b style="color:#059669;">4. Machine Learning</b>
            — The extracted features are passed to the trained
            Random Forest classifier.

            <br><br>

            <b style="color:#dc2626;">5. Result</b>
            — True Vision reports whether the image is predicted
            as REAL or TAMPERED together with the model confidence.

        </div>

    </div>
    """
)


# ============================================================
# FOOTER
# ============================================================

st.html(
    """
    <div class="footer">

        <b>True Vision</b>
        &nbsp;•&nbsp;
        Image Tampering Detection
        &nbsp;•&nbsp;
        ELA + Machine Learning

        <br><br>

        Built for Hackathon Problem Statement 7

    </div>
    """
)