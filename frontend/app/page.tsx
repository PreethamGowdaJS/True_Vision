"use client";

import { ChangeEvent, useEffect, useState } from "react";

type Prediction = {
  filename: string;
  prediction: "REAL" | "TAMPERED";
  confidence: number;
  model: string;
  ela_image: string | null;
  ela_error: string | null;
};

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/predict";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState("");
  const [result, setResult] = useState<Prediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    return () => {
      if (preview) {
        URL.revokeObjectURL(preview);
      }
    };
  }, [preview]);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const selected = event.target.files?.[0];

    if (!selected) {
      return;
    }

    if (!selected.type.startsWith("image/")) {
      setError("Please select a valid image file.");
      return;
    }

    setFile(selected);
    setResult(null);
    setError("");

    const objectUrl = URL.createObjectURL(selected);
    setPreview(objectUrl);
  }

  async function analyzeImage() {
    if (!file) {
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(API_URL, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Backend returned ${response.status}`);
      }

      const data: Prediction = await response.json();

      setResult(data);
    } catch (err) {
      console.error(err);

      setError(
        "Unable to connect to the analysis server. Make sure the FastAPI backend is running."
      );
    } finally {
      setLoading(false);
    }
  }

  function scrollToAnalyzer() {
    document
      .getElementById("analyzer")
      ?.scrollIntoView({
        behavior: "smooth",
      });
  }

  return (
    <main>
      {/* =====================================================
          NAVIGATION
      ====================================================== */}

      <nav className="nav">
        <div className="brand">
          <div className="brand-mark">
            <span />
          </div>

          <div>
            <div className="brand-name">TRUE VISION</div>

            <div className="brand-sub">
              AI IMAGE FORENSICS
            </div>
          </div>
        </div>

        <div className="nav-links">
          <a href="#analyzer">Analyze</a>

          <a href="#method">
            How it works
          </a>

          <a href="#limitations">
            Limitations
          </a>

          <button
            onClick={scrollToAnalyzer}
            className="nav-button"
          >
            Analyze Image →
          </button>
        </div>
      </nav>

      {/* =====================================================
          HERO
      ====================================================== */}

      <section className="hero">
        <div className="hero-grid" />

        <div className="hero-content">
          <div className="eyebrow">
            <span className="status-dot" />

            AI-POWERED IMAGE FORENSICS
          </div>

          <h1>
            See beyond
            <br />
            <span>the pixels.</span>
          </h1>

          <p>
            Detect potential image manipulation using
            Error Level Analysis and machine learning.
            Upload an image and let True Vision examine
            its digital fingerprints.
          </p>

          <div className="hero-actions">
            <button
              onClick={scrollToAnalyzer}
              className="primary-button"
            >
              <span>Analyze an image</span>
              <span>→</span>
            </button>

            <a
              href="#method"
              className="text-button"
            >
              Explore the method ↓
            </a>
          </div>

          <div className="hero-meta">
            <span>ELA</span>

            <span className="meta-line" />

            <span>RANDOM FOREST</span>

            <span className="meta-line" />

            <span>REAL / TAMPERED</span>
          </div>
        </div>

        {/* =====================================================
            HERO PIPELINE
        ====================================================== */}

        <div className="pipeline">
          <div className="pipeline-card">
            <div className="pipeline-label">
              01 · IMAGE
            </div>

            <div className="fake-photo">
              <div className="mountain mountain-one" />
              <div className="mountain mountain-two" />

              <div className="sun" />

              <div className="photo-ground" />
            </div>
          </div>

          <div className="pipeline-arrow">
            →
          </div>

          <div className="pipeline-card">
            <div className="pipeline-label">
              02 · ELA
            </div>

            <div className="fake-ela">
              <div className="ela-glow glow-one" />

              <div className="ela-glow glow-two" />

              <div className="ela-glow glow-three" />

              <div className="scan-line" />
            </div>
          </div>

          <div className="pipeline-arrow">
            →
          </div>

          <div className="pipeline-card">
            <div className="pipeline-label">
              03 · AI
            </div>

            <div className="neural">
              <div className="node n1" />
              <div className="node n2" />
              <div className="node n3" />
              <div className="node n4" />
              <div className="node n5" />

              <div className="connection c1" />
              <div className="connection c2" />
              <div className="connection c3" />
              <div className="connection c4" />
              <div className="connection c5" />
            </div>
          </div>

          <div className="pipeline-arrow">
            →
          </div>

          <div className="pipeline-card verdict-preview">
            <div className="pipeline-label">
              04 · VERDICT
            </div>

            <div className="verdict-symbol">
              <span>✓</span>
            </div>

            <div className="verdict-real">
              REAL
            </div>

            <div className="verdict-or">
              OR
            </div>

            <div className="verdict-fake">
              TAMPERED
            </div>
          </div>
        </div>
      </section>

      {/* =====================================================
          ANALYZER
      ====================================================== */}

      <section
        id="analyzer"
        className="workspace"
      >
        <div className="section-heading">
          <div>
            <div className="section-kicker">
              FORENSIC WORKSPACE
            </div>

            <h2>
              Analyze an image
            </h2>
          </div>

          <p>
            Upload an image and inspect the result
            through our forensic pipeline.
          </p>
        </div>

        <div className="analysis-grid">

          {/* =================================================
              UPLOAD
          ================================================== */}

          <section className="analysis-card upload-card">
            <div className="card-heading">
              <span className="card-number">
                01
              </span>

              <div>
                <span className="card-title">
                  Upload
                </span>

                <span className="card-subtitle">
                  SOURCE IMAGE
                </span>
              </div>
            </div>

            {!file ? (
              <label className="dropzone">
                <input
                  type="file"
                  accept=".jpg,.jpeg,.png,.webp"
                  onChange={handleFileChange}
                />

                <div className="upload-icon">
                  ↑
                </div>

                <strong>
                  Drop an image here
                </strong>

                <span>
                  or click to browse
                </span>

                <small>
                  JPG · JPEG · PNG · WEBP
                </small>
              </label>
            ) : (
              <div className="selected-file">
                <img
                  src={preview}
                  alt="Selected image"
                />

                <div className="file-info">
                  <strong>
                    {file.name}
                  </strong>

                  <span>
                    {(file.size / 1024).toFixed(1)}
                    {" "}
                    KB · {file.type}
                  </span>
                </div>

                <label className="change-file">
                  Change

                  <input
                    type="file"
                    accept=".jpg,.jpeg,.png,.webp"
                    onChange={handleFileChange}
                  />
                </label>
              </div>
            )}

            {file && (
              <button
                className="analyze-button"
                onClick={analyzeImage}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />

                    Analyzing image...
                  </>
                ) : (
                  <>
                    Analyze image

                    <span>
                      →
                    </span>
                  </>
                )}
              </button>
            )}

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}
          </section>

          {/* =================================================
              ORIGINAL IMAGE
          ================================================== */}

          <section className="analysis-card">
            <div className="card-heading">
              <span className="card-number">
                02
              </span>

              <div>
                <span className="card-title">
                  Original
                </span>

                <span className="card-subtitle">
                  SOURCE VIEW
                </span>
              </div>
            </div>

            <div className="image-viewer">
              {preview ? (
                <img
                  src={preview}
                  alt="Original uploaded image"
                />
              ) : (
                <div className="empty-viewer">
                  <div>
                    ◎
                  </div>

                  <span>
                    Image preview will appear here
                  </span>
                </div>
              )}
            </div>
          </section>

          {/* =================================================
              REAL ELA HEATMAP
          ================================================== */}

          <section className="analysis-card">
            <div className="card-heading">
              <span className="card-number">
                03
              </span>

              <div>
                <span className="card-title">
                  ELA analysis
                </span>

                <span className="card-subtitle">
                  ERROR LEVEL ANALYSIS
                </span>
              </div>
            </div>

            <div className="image-viewer ela-viewer">

              {/* =============================================
                  REAL ELA IMAGE FROM FASTAPI
              ============================================== */}

              {result?.ela_image ? (
                <img
                  src={result.ela_image}
                  alt="ELA heatmap generated by True Vision"
                />
              ) : result?.ela_error ? (

                /* ===========================================
                   ELA ERROR
                ============================================ */

                <div className="ela-placeholder">
                  <div className="ela-icon">
                    !
                  </div>

                  <strong>
                    ELA unavailable
                  </strong>

                  <span>
                    The image was analyzed, but the
                    ELA visualization could not be
                    generated.
                  </span>
                </div>

              ) : (

                /* ===========================================
                   WAITING STATE
                ============================================ */

                <div className="ela-placeholder">
                  <div className="ela-icon">
                    ◌
                  </div>

                  <strong>
                    Awaiting analysis
                  </strong>

                  <span>
                    Run the analysis to generate the
                    ELA forensic heatmap.
                  </span>

                  <div className="ela-bars">
                    <i />
                    <i />
                    <i />
                    <i />
                    <i />
                  </div>
                </div>
              )}

            </div>
          </section>

          {/* =================================================
              VERDICT
          ================================================== */}

          <section className="analysis-card result-card">
            <div className="card-heading">
              <span className="card-number">
                04
              </span>

              <div>
                <span className="card-title">
                  Verdict
                </span>

                <span className="card-subtitle">
                  MODEL CLASSIFICATION
                </span>
              </div>
            </div>

            {!result ? (
              <div className="result-empty">
                <div className="result-target">
                  ◎
                </div>

                <strong>
                  Awaiting analysis
                </strong>

                <span>
                  Upload an image and run the forensic
                  analysis to receive a classification.
                </span>
              </div>
            ) : (
              <ResultView
                result={result}
              />
            )}
          </section>
        </div>
      </section>

      {/* =====================================================
          FORENSIC INSIGHTS
      ====================================================== */}

      <section className="insights-section">
        <div className="section-kicker">
          FORENSIC INSIGHTS
        </div>

        <div className="insight-grid">

          <Insight
            number="01"
            title="Compression patterns"
            text="ELA examines differences introduced by JPEG recompression and can reveal areas with unusual error levels."
          />

          <Insight
            number="02"
            title="Statistical features"
            text="The analysis extracts numerical ELA statistics that describe the distribution of compression differences."
          />

          <Insight
            number="03"
            title="Machine learning"
            text="A Random Forest classifier evaluates the extracted features and produces the final classification."
          />

        </div>
      </section>

      {/* =====================================================
          HOW IT WORKS
      ====================================================== */}

      <section
        id="method"
        className="method-section"
      >
        <div className="method-main">
          <div className="section-kicker">
            HOW IT WORKS
          </div>

          <h2>
            From pixels to a forensic verdict.
          </h2>

          <p className="method-intro">
            True Vision combines image-level forensic
            analysis with machine learning to identify
            patterns associated with manipulated images.
          </p>

          <div className="steps">

            <Step
              number="01"
              title="Upload"
              text="The image enters the forensic analysis pipeline."
            />

            <Step
              number="02"
              title="ELA"
              text="Error Level Analysis highlights differences in JPEG compression levels."
            />

            <Step
              number="03"
              title="Features"
              text="Statistical properties are extracted from the ELA image."
            />

            <Step
              number="04"
              title="Classification"
              text="The Random Forest model predicts REAL or TAMPERED."
            />

          </div>
        </div>

        {/* =================================================
            LIMITATIONS
        ================================================== */}

        <div
          id="limitations"
          className="limitations"
        >
          <div className="warning-icon">
            !
          </div>

          <div>
            <div className="section-kicker">
              IMPORTANT
            </div>

            <h3>
              Know the limitations
            </h3>

            <p>
              ELA is sensitive to compression,
              resizing, screenshots and other
              processing operations. A legitimate
              image that has been resaved or transformed
              may produce forensic patterns that look
              unusual.
            </p>

            <p>
              True Vision should therefore be treated
              as an analytical aid, not as definitive
              proof of image manipulation.
            </p>
          </div>
        </div>
      </section>

      {/* =====================================================
          FOOTER
      ====================================================== */}

      <footer>
        <div className="footer-brand">
          <div className="footer-mark" />

          <strong>
            TRUE VISION
          </strong>
        </div>

        <span>
          AI-powered image forensics
        </span>

        <span>
          © 2026 True Vision
        </span>
      </footer>
    </main>
  );
}


/* ============================================================
   RESULT COMPONENT
============================================================ */

function ResultView({
  result,
}: {
  result: Prediction;
}) {
  const isReal =
    result.prediction === "REAL";

  return (
    <div
      className={`result-content ${
        isReal
          ? "is-real"
          : "is-tampered"
      }`}
    >

      {/* ================================================
          RESULT BADGE
      ================================================= */}

      <div className="result-badge">
        <span>
          {isReal ? "✓" : "!"}
        </span>

        {result.prediction}
      </div>


      {/* ================================================
          CONFIDENCE RING
      ================================================= */}

      <div
        className="confidence-ring"
        style={
          {
            "--confidence":
              `${result.confidence}%`,
          } as React.CSSProperties
        }
      >
        <div className="confidence-inner">
          <strong>
            {result.confidence}%
          </strong>

          <span>
            CONFIDENCE
          </span>
        </div>
      </div>


      {/* ================================================
          DETAILS
      ================================================= */}

      <div className="result-details">

        <div>
          <span>
            CLASSIFICATION
          </span>

          <strong>
            {result.prediction}
          </strong>
        </div>

        <div>
          <span>
            MODEL
          </span>

          <strong>
            {result.model}
          </strong>
        </div>

        <div>
          <span>
            FILE
          </span>

          <strong
            title={result.filename}
          >
            {result.filename}
          </strong>
        </div>

      </div>


      {/* ================================================
          DISCLAIMER
      ================================================= */}

      <p className="result-disclaimer">
        Classification is based on the trained model
        and should be interpreted as an analytical
        indication rather than definitive proof.
      </p>

    </div>
  );
}


/* ============================================================
   FORENSIC INSIGHT COMPONENT
============================================================ */

function Insight({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <article className="insight">

      <div className="insight-number">
        {number}
      </div>

      <div>
        <h3>
          {title}
        </h3>

        <p>
          {text}
        </p>
      </div>

    </article>
  );
}


/* ============================================================
   METHOD STEP COMPONENT
============================================================ */

function Step({
  number,
  title,
  text,
}: {
  number: string;
  title: string;
  text: string;
}) {
  return (
    <article className="step">

      <div className="step-number">
        {number}
      </div>

      <div>
        <h3>
          {title}
        </h3>

        <p>
          {text}
        </p>
      </div>

    </article>
  );
}