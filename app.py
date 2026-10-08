import os
import sys
import shutil
import hashlib
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
    page_title="True Vision | AI Image Forensics",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def stretch(fn, *args, **kwargs):
    """Full-width widgets across old and new Streamlit versions."""
    try:
        return fn(*args, width="stretch", **kwargs)
    except Exception:
        return fn(*args, use_container_width=True, **kwargs)


def keyed(key):
    """Container with a CSS hook (st-key-<key>); plain container on old Streamlit."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


# ============================================================
# SMALL INLINE ICONS (stroke icons, no external assets)
# ============================================================

ICONS = {
    "upload": "M12 16V4 M7 9l5-5 5 5 M4 20h16",
    "file": "M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z M14 3v5h5",
    "frame": "M4 4h6 M4 4v6 M20 4h-6 M20 4v6 M4 20h6 M4 20v-6 M20 20h-6 M20 20v-6",
    "list": "M4 6h16 M4 12h16 M4 18h10",
    "image": "M4 5h16v14H4z M4 16l5-5 4 4 3-3 4 4",
    "pulse": "M3 12h4l3-8 4 16 3-8h4",
    "shield": "M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z M8.5 12l2.5 2.5 4.5-5",
    "warn": "M12 3l10 18H2z M12 10v5 M12 18h.01",
    "chip": "M9 9h6v6H9z M4 9h2 M4 15h2 M18 9h2 M18 15h2 M9 4v2 M15 4v2 M9 18v2 M15 18v2",
    "check": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M8 12l3 3 5-6",
    "target": "M12 3a9 9 0 1 0 0 18 9 9 0 0 0 0-18z M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8z",
    "cube": "M12 3l8 4.5v9L12 21l-8-4.5v-9z M12 12l8-4.5 M12 12v9 M12 12L4 7.5",
    "arrow": "M5 12h14 M13 6l6 6-6 6",
    "flow": "M5 6a2 2 0 1 0 0 .01 M19 6a2 2 0 1 0 0 .01 M12 19a2 2 0 1 0 0 .01 M6.5 7.5L11 17 M17.5 7.5L13 17",
}


def ico(name, size=16):
    return (
        f'<svg class="ico" width="{size}" height="{size}" viewBox="0 0 24 24" '
        'fill="none" stroke="currentColor" stroke-width="1.7" '
        'stroke-linecap="round" stroke-linejoin="round">'
        f'<path d="{ICONS[name]}"/></svg>'
    )


# ============================================================
# DESIGN SYSTEM  (custom HTML/CSS goes through st.html)
#
# NOTE: this block must never contain a "<" character.
# Streamlit's sanitizer removes any <style> element whose text
# looks like markup, which silently drops the whole stylesheet.
# ============================================================

st.html(
    r"""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap');

    @property --p {
        syntax: '\3C number>';
        inherits: false;
        initial-value: 0;
    }

    :root {
        --bg: #050b18;
        --bg-2: #08142b;
        --sheet: #f1f5fb;
        --card: #ffffff;
        --ink: #0b1630;
        --text: #1b2742;
        --muted: #5b6784;
        --faint: #8792ab;
        --line: #e2e8f2;
        --line-2: #cdd7e8;
        --blue: #2b6bff;
        --blue-2: #1b4fe0;
        --blue-soft: #eaf1ff;
        --sky: #7fb0ff;
        --real: #0f9d6b;
        --real-soft: #e5f7ef;
        --fake: #d9452b;
        --fake-soft: #fdeae6;
        --amber: #b7791f;
        --amber-soft: #fdf4e1;
        --amber-line: #f1deb0;
        --sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
        --mono: 'JetBrains Mono', ui-monospace, 'SF Mono', Menlo, Consolas, monospace;
        --shadow: 0 1px 2px rgba(11,22,48,0.04), 0 8px 24px -8px rgba(11,22,48,0.08);
        --ease: cubic-bezier(0.2, 0.7, 0.2, 1);
    }

    html, section.main, [data-testid="stMain"] {
        scroll-behavior: smooth;
    }

    .stApp,
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(900px 420px at 80% -4%, rgba(43,107,255,0.28), transparent 65%),
            radial-gradient(700px 360px at 0% 30%, rgba(43,107,255,0.10), transparent 70%),
            var(--bg);
        color: var(--text);
        color-scheme: light;
        font-family: var(--sans);
        -webkit-font-smoothing: antialiased;
    }

    [data-testid="stHeader"],
    [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    footer {
        display: none !important;
    }

    .block-container,
    [data-testid="stMainBlockContainer"] {
        max-width: 1400px;
        padding: 0 1.5rem 0 1.5rem;
    }

    .ico { flex: none; }


    /* ===== NAV ===== */

    .nav {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 1rem 0.25rem;
        border-bottom: 1px solid rgba(255,255,255,0.08);
    }

    .brand { display: flex; align-items: center; gap: 0.75rem; }

    .brand-mark {
        position: relative;
        width: 36px;
        height: 36px;
        border-radius: 50%;
        border: 3px solid var(--blue);
        box-shadow: 0 0 18px rgba(43,107,255,0.55), inset 0 0 10px rgba(43,107,255,0.4);
    }

    .brand-mark::after {
        content: "";
        position: absolute;
        inset: 8px;
        border-radius: 50%;
        background: radial-gradient(circle, #ffffff 0 22%, var(--blue) 24% 100%);
    }

    .brand-name {
        font-size: 1.2rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: #ffffff;
        line-height: 1.05;
    }

    .brand-sub {
        margin-top: 0.15rem;
        font-size: 0.7rem;
        letter-spacing: 0.08em;
        color: #9fb3d6;
    }

    .nav-right { display: flex; align-items: center; gap: 0.4rem; }

    .nav-right a.lnk {
        color: #dce6fa;
        font-size: 0.9rem;
        font-weight: 500;
        text-decoration: none;
        padding: 0.5rem 0.9rem;
        border-radius: 8px;
        transition: color 0.2s ease, background 0.2s ease;
    }

    .nav-right a.lnk:hover { color: #ffffff; background: rgba(255,255,255,0.07); }

    .nav-cta {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin-left: 0.6rem;
        padding: 0.6rem 1.05rem;
        border: 1px solid var(--blue);
        border-radius: 8px;
        background: rgba(43,107,255,0.14);
        color: #ffffff;
        font-size: 0.88rem;
        font-weight: 600;
        text-decoration: none;
        transition: background 0.2s ease, transform 0.2s var(--ease);
    }

    .nav-cta:hover { background: var(--blue); transform: translateY(-1px); }


    /* ===== HERO ===== */

    .hero {
        position: relative;
        display: grid;
        grid-template-columns: 0.82fr 1.18fr;
        gap: 2rem;
        align-items: center;
        padding: 3.2rem 0.25rem 3.6rem 0.25rem;
    }

    .hero::before {
        content: "";
        position: absolute;
        inset: 0 -1.5rem;
        background-image:
            linear-gradient(rgba(80,140,255,0.07) 1px, transparent 1px),
            linear-gradient(90deg, rgba(80,140,255,0.07) 1px, transparent 1px);
        background-size: 44px 44px;
        -webkit-mask-image: radial-gradient(ellipse at 70% 45%, #000 0%, transparent 70%);
        mask-image: radial-gradient(ellipse at 70% 45%, #000 0%, transparent 70%);
        pointer-events: none;
    }

    .hero-copy, .hero-visual { position: relative; z-index: 1; min-width: 0; }

    .hero-eyebrow {
        font-family: var(--mono);
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.14em;
        color: var(--sky);
    }

    .hero h1 {
        margin: 0.9rem 0 0 0;
        padding: 0;
        font-family: var(--sans);
        font-size: 4rem;
        line-height: 1.02;
        font-weight: 700;
        letter-spacing: -0.04em;
        color: #ffffff;
    }

    .hero h1 span {
        background: linear-gradient(90deg, #ffffff, #8fb6ff);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: transparent;
    }

    .hero p {
        max-width: 440px;
        margin: 1.2rem 0 0 0;
        font-size: 1.05rem;
        line-height: 1.6;
        color: #d3def2;
    }

    .hero-actions { display: flex; align-items: center; gap: 1.4rem; margin-top: 1.8rem; flex-wrap: wrap; }

    .btn-blue {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0.85rem 1.4rem;
        border-radius: 8px;
        background: linear-gradient(180deg, #3b78ff, #1f58f0);
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 600;
        text-decoration: none;
        box-shadow: 0 10px 28px -10px rgba(43,107,255,0.8);
        transition: transform 0.2s var(--ease), box-shadow 0.2s ease;
    }

    .btn-blue:hover { transform: translateY(-2px); box-shadow: 0 16px 34px -10px rgba(43,107,255,0.9); color: #ffffff; }

    .btn-text {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        color: var(--sky);
        font-size: 0.95rem;
        font-weight: 500;
        text-decoration: none;
        transition: color 0.2s ease;
    }

    .btn-text:hover { color: #ffffff; }

    .nav-cta:focus-visible, .btn-blue:focus-visible, .btn-text:focus-visible, .nav-right a.lnk:focus-visible {
        outline: 2px solid var(--sky);
        outline-offset: 3px;
    }

    /* hero pipeline: image -> ELA -> AI -> verdict */

    .pipe { display: flex; align-items: center; gap: 0.5rem; }

    .vt {
        position: relative;
        flex: 1 1 0;
        min-width: 0;
        aspect-ratio: 1 / 1.18;
        border-radius: 12px;
        border: 1px solid rgba(90,150,255,0.4);
        background: linear-gradient(180deg, rgba(16,36,76,0.75), rgba(8,20,44,0.75));
        box-shadow: 0 0 24px -6px rgba(43,107,255,0.45), inset 0 0 20px rgba(43,107,255,0.08);
        transform: perspective(900px) rotateY(7deg);
        transition: transform 0.4s var(--ease), border-color 0.3s ease;
        overflow: hidden;
    }

    .vt:hover { transform: perspective(900px) rotateY(0deg) translateY(-4px); border-color: rgba(143,182,255,0.8); }

    .vt-cap {
        position: absolute;
        left: 0; right: 0; top: 0;
        padding: 0.55rem 0.4rem;
        text-align: center;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        color: #ffffff;
        z-index: 3;
    }

    .vt-body { position: absolute; left: 8%; right: 8%; top: 22%; bottom: 8%; border-radius: 6px; overflow: hidden; }

    .vt-photo { background: linear-gradient(180deg, #2b4a85 0%, #d1804f 62%, #f6c27f 78%, #231d1c 78%); }

    .vt-ela { background: #0a0a12; }

    .sil {
        position: absolute;
        inset: 8% 0 0 0;
        clip-path: polygon(10% 100%, 10% 72%, 18% 72%, 18% 62%, 26% 62%, 26% 52%, 34% 52%, 34% 42%, 42% 42%, 42% 32%, 46% 32%, 46% 20%, 50% 8%, 54% 20%, 54% 32%, 58% 32%, 58% 42%, 66% 42%, 66% 52%, 74% 52%, 74% 62%, 82% 62%, 82% 72%, 90% 72%, 90% 100%);
    }

    .vt-photo .sil { background: linear-gradient(180deg, #8a6f5e, #2a2220); }

    .vt-ela .sil {
        background:
            radial-gradient(circle at 50% 30%, #ffb347 0 10%, transparent 28%),
            radial-gradient(circle at 30% 70%, #ff4d2e 0 12%, transparent 34%),
            radial-gradient(circle at 70% 75%, #e02a1a 0 12%, transparent 34%),
            #5b0f0a;
    }

    .vt-ela::after {
        content: "";
        position: absolute;
        left: 0; right: 0; top: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, var(--sky), transparent);
        box-shadow: 0 0 12px var(--sky);
        animation: scan 3.8s ease-in-out infinite;
    }

    .vt-net { display: flex; align-items: center; justify-content: center; }

    .vt-net svg { width: 100%; height: 100%; }

    .vt-verdict { display: flex; flex-direction: column; justify-content: center; gap: 0.35rem; padding: 0 0.4rem; align-items: center; }

    .vt-verdict .row { display: flex; align-items: center; gap: 0.35rem; font-size: 0.78rem; font-weight: 700; letter-spacing: 0.02em; }

    .vt-verdict .real { color: #34d399; }
    .vt-verdict .fake { color: #ff6b4d; }
    .vt-verdict .or { font-size: 0.6rem; color: #8fa3c8; }

    .vt.v { border-color: rgba(52,211,153,0.5); box-shadow: 0 0 26px -6px rgba(52,211,153,0.4); }

    .arrow {
        position: relative;
        flex: 0 0 26px;
        height: 2px;
        background: linear-gradient(90deg, rgba(43,107,255,0.2), var(--blue));
        box-shadow: 0 0 8px rgba(43,107,255,0.6);
    }

    .arrow::after {
        content: "";
        position: absolute;
        right: -1px;
        top: -4px;
        width: 8px;
        height: 8px;
        border-top: 2px solid var(--blue);
        border-right: 2px solid var(--blue);
        transform: rotate(45deg);
    }

    .arrow::before {
        content: "";
        position: absolute;
        top: -2px;
        left: 0;
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #ffffff;
        box-shadow: 0 0 8px var(--sky);
        animation: travel 2.6s linear infinite;
    }


    /* ===== SHEET (light workspace) ===== */

    .st-key-sheet {
        background: var(--sheet);
        border-radius: 26px 26px 0 0;
        padding: 1.5rem;
        gap: 1.25rem;
        scroll-margin-top: 1rem;
    }

    .st-key-card_left,
    .st-key-card_mid,
    .st-key-card_right {
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        padding: 1.15rem 1.15rem 1.25rem 1.15rem;
        box-shadow: var(--shadow);
        gap: 0.9rem;
    }

    .anchor { position: relative; top: -1.5rem; height: 0; }

    .card-head {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-size: 0.82rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        color: var(--ink);
    }

    .card-head .ico { color: var(--blue); }

    .ph {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 0.6rem;
        margin-bottom: 0.6rem;
        font-size: 0.78rem;
    }

    .ph-l { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; letter-spacing: 0.03em; color: var(--ink); text-transform: uppercase; }
    .ph-l .ico { color: var(--blue); }
    .ph-r { font-size: 0.74rem; color: var(--faint); font-weight: 400; text-align: right; }


    /* ===== UPLOADER ===== */

    [data-testid="stFileUploaderDropzone"],
    [data-testid="stFileUploader"] section {
        display: flex !important;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.35rem;
        min-height: 190px;
        padding: 1.6rem 0.8rem;
        background: #f7faff;
        border: 1.5px dashed #86a8f5;
        border-radius: 10px;
        transition: border-color 0.2s ease, background 0.2s ease, box-shadow 0.25s ease;
    }

    [data-testid="stFileUploaderDropzone"]:hover,
    [data-testid="stFileUploaderDropzone"]:focus-within,
    [data-testid="stFileUploader"] section:hover {
        border-color: var(--blue);
        background: #f0f6ff;
        box-shadow: 0 0 0 4px rgba(43,107,255,0.10);
    }

    [data-testid="stFileUploaderDropzone"]::before,
    [data-testid="stFileUploader"] section::before {
        content: "";
        order: 0;
        width: 44px;
        height: 44px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44' viewBox='0 0 24 24' fill='none' stroke='%232b6bff' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M12 16V4'/%3E%3Cpath d='m7 9 5-5 5 5'/%3E%3Cpath d='M4 15v5h16v-5'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
        background-position: center;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] {
        order: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        text-align: center;
    }

    [data-testid="stFileUploaderDropzoneInstructions"] > * { display: none !important; }

    [data-testid="stFileUploaderDropzoneInstructions"]::before {
        content: "Drop an image to analyze";
        font-size: 1rem;
        font-weight: 600;
        color: var(--ink);
    }

    [data-testid="stFileUploaderDropzone"] button,
    [data-testid="stFileUploader"] section button {
        order: 2;
        font-size: 0;
        padding: 0.1rem 0.3rem;
        border: none;
        background: transparent;
        box-shadow: none;
        min-height: 0;
    }

    [data-testid="stFileUploaderDropzone"] button::after,
    [data-testid="stFileUploader"] section button::after {
        content: "or click to browse";
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--blue);
    }

    [data-testid="stFileUploaderDropzone"] button:hover::after,
    [data-testid="stFileUploader"] section button:hover::after { text-decoration: underline; }

    [data-testid="stFileUploaderDropzone"]::after,
    [data-testid="stFileUploader"] section::after {
        content: "JPG, JPEG, PNG, WEBP\A Maximum clarity. Maximum insight.";
        order: 3;
        margin-top: 0.7rem;
        white-space: pre-line;
        text-align: center;
        font-size: 0.74rem;
        line-height: 1.7;
        color: var(--faint);
    }

    [data-testid="stFileUploaderFile"] {
        padding: 0.3rem 0.5rem;
        border: 1px solid var(--line);
        border-radius: 10px;
        background: #ffffff;
        color: var(--ink);
    }

    [data-testid="stFileUploaderFile"] * { color: var(--ink); }


    /* ===== IMAGE INFORMATION ===== */

    .info { display: flex; flex-direction: column; }

    .info-row {
        display: grid;
        grid-template-columns: 1.4rem 1fr auto;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 0;
        border-bottom: 1px solid var(--line);
        font-size: 0.82rem;
        animation: rise 0.5s var(--ease) both;
    }

    .info-row:last-child { border-bottom: none; }
    .info-row .ico { color: var(--faint); }
    .info-k { color: var(--muted); }
    .info-v { color: var(--ink); font-weight: 500; text-align: right; max-width: 11rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }


    /* ===== IMAGES + ANALYZE ===== */

    [data-testid="stImage"] {
        overflow: hidden;
        border: 1px solid var(--line);
        border-radius: 8px;
        background: #0b1220;
    }

    [data-testid="stImage"] img {
        display: block;
        transition: transform 0.7s var(--ease);
    }

    [data-testid="stImage"]:hover img { transform: scale(1.03); }

    .empty-viewport {
        display: flex;
        align-items: center;
        justify-content: center;
        min-height: 300px;
        padding: 1rem;
        border: 1px dashed var(--line-2);
        border-radius: 10px;
        text-align: center;
        font-size: 0.88rem;
        line-height: 1.6;
        color: var(--faint);
    }

    div.stButton { display: flex; justify-content: center; margin-top: 0.4rem; }

    div.stButton > button {
        min-width: min(100%, 360px);
        padding: 0.85rem 1.6rem;
        border: none;
        border-radius: 10px;
        background: linear-gradient(180deg, #3b78ff, #1f58f0);
        box-shadow: 0 12px 28px -12px rgba(43,107,255,0.8);
        transition: transform 0.2s var(--ease), box-shadow 0.2s ease, filter 0.2s ease;
    }

    div.stButton > button p {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        color: #ffffff;
        font-size: 0.98rem;
        font-weight: 600;
    }

    div.stButton > button p::before {
        content: "";
        width: 17px;
        height: 17px;
        background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='17' height='17' viewBox='0 0 24 24' fill='%23ffffff'%3E%3Cpath d='M12 2l1.8 5.7L19.5 9.5l-5.7 1.8L12 17l-1.8-5.7L4.5 9.5l5.7-1.8z'/%3E%3Cpath d='M19 15l.8 2.2 2.2.8-2.2.8L19 21l-.8-2.2-2.2-.8 2.2-.8z'/%3E%3C/svg%3E");
        background-repeat: no-repeat;
    }

    div.stButton > button p::after { content: "→"; transition: transform 0.2s var(--ease); }

    div.stButton > button:hover { transform: translateY(-2px); filter: brightness(1.08); box-shadow: 0 18px 34px -12px rgba(43,107,255,0.9); }
    div.stButton > button:hover p::after { transform: translateX(4px); }
    div.stButton > button:active { transform: translateY(0); }
    div.stButton > button:focus-visible { outline: 3px solid rgba(43,107,255,0.4); outline-offset: 3px; }

    [data-testid="stSpinner"] {
        padding: 0.8rem 1rem;
        border: 1px solid var(--line);
        border-left: 3px solid var(--blue);
        border-radius: 10px;
        background: #ffffff;
        font-family: var(--mono);
        font-size: 0.74rem;
        letter-spacing: 0.06em;
        text-transform: uppercase;
    }

    [data-testid="stSpinner"] * { color: var(--ink); }

    [data-testid="stAlert"] { border-radius: 12px; }


    /* ===== RESULT CARD ===== */

    .res-empty {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 0.7rem;
        min-height: 300px;
        padding: 1rem;
        text-align: center;
        font-size: 0.86rem;
        line-height: 1.6;
        color: var(--faint);
    }

    .res-empty .ico { color: var(--line-2); }

    .res { --rc: var(--real); --rc-soft: var(--real-soft); animation: rise 0.6s var(--ease) both; }
    .res.is-fake { --rc: var(--fake); --rc-soft: var(--fake-soft); }

    .res-hero {
        display: flex;
        align-items: center;
        gap: 0.8rem;
        padding: 0.95rem 0.9rem;
        border-radius: 10px;
        background: var(--rc-soft);
        border: 1px solid color-mix(in srgb, var(--rc) 22%, transparent);
    }

    .res-hero .ico { color: var(--rc); }

    .res-title { font-size: 1.02rem; font-weight: 800; letter-spacing: 0.01em; color: var(--rc); text-transform: uppercase; line-height: 1.15; }
    .res-msg { margin-top: 0.2rem; font-size: 0.76rem; line-height: 1.45; color: var(--muted); }

    .ring {
        --size: 160px;
        display: grid;
        place-items: center;
        width: var(--size);
        height: var(--size);
        margin: 1.2rem auto 1rem auto;
        border-radius: 50%;
        background: conic-gradient(var(--rc) calc(var(--p) * 1%), #e6ebf3 0);
        animation: ringfill 1.4s var(--ease) both;
    }

    .ring-inner {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        width: 82%;
        height: 82%;
        border-radius: 50%;
        background: #ffffff;
        box-shadow: inset 0 0 0 1px var(--line);
    }

    .ring-value { font-size: 1.9rem; font-weight: 700; letter-spacing: -0.03em; color: var(--ink); line-height: 1; font-variant-numeric: tabular-nums; }
    .ring-label { margin-top: 0.4rem; font-size: 0.64rem; font-weight: 500; letter-spacing: 0.06em; color: var(--muted); text-transform: uppercase; }

    .res-row {
        display: grid;
        grid-template-columns: 1.4rem 1fr auto;
        align-items: center;
        gap: 0.5rem;
        padding: 0.55rem 0;
        border-top: 1px solid var(--line);
        font-size: 0.82rem;
    }

    .res-row .ico { color: var(--faint); }
    .res-row .k { color: var(--muted); }
    .res-row .v { font-weight: 600; color: var(--ink); text-align: right; max-width: 9rem; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .res-row .v.c { color: var(--rc); }

    .res-note { margin-top: 0.7rem; font-size: 0.72rem; line-height: 1.5; color: var(--faint); }


    /* ===== INSIGHTS ===== */

    .band {
        padding: 1.15rem 1.4rem 1.3rem 1.4rem;
        background: var(--card);
        border: 1px solid var(--line);
        border-radius: 14px;
        box-shadow: var(--shadow);
    }

    .insights { display: flex; align-items: flex-start; gap: 1rem; margin-top: 1rem; }

    .ins { flex: 1 1 0; min-width: 0; display: flex; align-items: flex-start; gap: 0.9rem; }

    .ins-n {
        flex: none;
        display: grid;
        place-items: center;
        width: 46px;
        height: 46px;
        border-radius: 50%;
        background: var(--blue-soft);
        font-family: var(--mono);
        font-size: 0.82rem;
        font-weight: 600;
        color: var(--blue);
    }

    .ins-t { font-size: 0.9rem; font-weight: 700; color: var(--ink); }
    .ins-d { margin-top: 0.3rem; font-size: 0.8rem; line-height: 1.55; color: var(--muted); }

    .ins-chip {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.2rem 0.55rem;
        border-radius: 6px;
        background: var(--blue-soft);
        font-family: var(--mono);
        font-size: 0.7rem;
        color: var(--blue-2);
    }

    .conn { flex: 0 0 56px; align-self: center; position: relative; height: 1px; background: var(--line-2); }

    .conn::after {
        content: "";
        position: absolute;
        right: 0; top: -3px;
        width: 6px; height: 6px;
        border-top: 1px solid var(--line-2);
        border-right: 1px solid var(--line-2);
        transform: rotate(45deg);
    }


    /* ===== METHOD + LIMITS ===== */

    .duo { display: grid; grid-template-columns: 1.9fr 1fr; gap: 1.25rem; scroll-margin-top: 1rem; }

    .steps { display: flex; align-items: flex-start; gap: 0.6rem; margin-top: 1rem; }

    .stp { flex: 1 1 0; min-width: 0; display: flex; align-items: flex-start; gap: 0.7rem; }

    .stp-i {
        flex: none;
        display: grid;
        place-items: center;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: var(--blue-soft);
        color: var(--blue);
        transition: background 0.2s ease, color 0.2s ease;
    }

    .stp:hover .stp-i { background: var(--blue); color: #ffffff; }
    .stp.last .stp-i { background: var(--real-soft); color: var(--real); }

    .stp-n { font-family: var(--mono); font-size: 0.7rem; color: var(--faint); }
    .stp-t { margin-top: 0.1rem; font-size: 0.84rem; font-weight: 700; color: var(--ink); }
    .stp-d { margin-top: 0.25rem; font-size: 0.74rem; line-height: 1.5; color: var(--muted); }

    .stp-arrow { flex: none; align-self: center; color: var(--line-2); font-size: 0.9rem; }

    .limits {
        padding: 1.15rem 1.4rem;
        background: var(--amber-soft);
        border: 1px solid var(--amber-line);
        border-radius: 14px;
    }

    .limits .card-head { color: var(--ink); }
    .limits .card-head .ico { color: #d99a1c; }
    .limits p { margin: 0.8rem 0 0 0; font-size: 0.82rem; line-height: 1.65; color: #5d5440; }


    /* ===== FOOTER ===== */

    .footer {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        flex-wrap: wrap;
        padding: 0.4rem 0.25rem 0.2rem 0.25rem;
        border-top: 1px solid var(--line);
        padding-top: 1.1rem;
    }

    .footer-l { display: flex; align-items: center; gap: 1.2rem; flex-wrap: wrap; }
    .footer-brand { display: flex; align-items: center; gap: 0.5rem; font-weight: 700; color: var(--ink); font-size: 0.95rem; }
    .footer-brand i { width: 22px; height: 22px; border-radius: 50%; border: 2.5px solid var(--blue); }
    .footer-tag { font-size: 0.8rem; color: var(--muted); }
    .footer-r { display: flex; gap: 1.4rem; }
    .footer-r a { font-size: 0.8rem; color: var(--muted); text-decoration: none; transition: color 0.2s ease; }
    .footer-r a:hover { color: var(--blue); }


    /* ===== MOTION ===== */

    @keyframes rise { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
    @keyframes ringfill { from { --p: 0; } }
    @keyframes scan { 0% { top: 0; opacity: 0; } 10% { opacity: 1; } 90% { opacity: 1; } 100% { top: calc(100% - 2px); opacity: 0; } }
    @keyframes travel { 0% { left: 0; opacity: 0; } 15% { opacity: 1; } 85% { opacity: 1; } 100% { left: calc(100% - 5px); opacity: 0; } }

    @media (prefers-reduced-motion: reduce) {
        * { animation: none !important; transition: none !important; }
    }


    /* ===== RESPONSIVE ===== */

    @media (max-width: 1100px) {
        .hero { grid-template-columns: 1fr; padding: 2.4rem 0.25rem 2.8rem 0.25rem; }
        .hero h1 { font-size: 3.2rem; }
        .duo { grid-template-columns: 1fr; }
    }

    @media (max-width: 860px) {
        .insights, .steps { flex-direction: column; gap: 1.1rem; }
        .conn, .stp-arrow { display: none; }
        .nav-right a.lnk { display: none; }
    }

    @media (max-width: 640px) {
        .block-container, [data-testid="stMainBlockContainer"] { padding: 0 0.75rem; }
        .st-key-sheet { padding: 0.9rem; border-radius: 20px 20px 0 0; }
        .brand-sub { display: none; }
        .hero h1 { font-size: 2.6rem; }
        .pipe { flex-wrap: wrap; gap: 0.7rem; }
        .vt { flex: 0 0 calc(50% - 0.4rem); }
        .arrow { display: none; }
        .footer { flex-direction: column; align-items: flex-start; }
    }

    </style>
    """
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULT_STATE = {
    "uploaded_path": None,
    "uploaded_image": None,
    "ela_path": None,
    "heatmap_path": None,
    "analysis_result": None,
    "uploaded_filename": None,
    "file_signature": None,
    "file_size_bytes": 0,
    "file_format": "",
    "work_dir": None,
    "ela_error": None,
    "process_error": None,
}

for _key, _default in DEFAULT_STATE.items():
    if _key not in st.session_state:
        st.session_state[_key] = _default


def reset_workspace():
    """Clear everything tied to the previous upload and free its temp files."""

    old_dir = st.session_state.get("work_dir")

    if old_dir and os.path.isdir(old_dir):
        shutil.rmtree(old_dir, ignore_errors=True)

    for key, default in DEFAULT_STATE.items():
        st.session_state[key] = default


def format_size(num_bytes):
    if num_bytes >= 1024 * 1024:
        return f"{num_bytes / (1024 * 1024):.1f} MB"
    return f"{num_bytes / 1024:.1f} KB"


# ============================================================
# NAVIGATION
# ============================================================

st.html(
    f"""
    <div class="nav">

        <div class="brand">
            <div class="brand-mark"></div>
            <div>
                <div class="brand-name">TRUE VISION</div>
                <div class="brand-sub">AI IMAGE FORENSICS</div>
            </div>
        </div>

        <div class="nav-right">
            <a class="lnk" href="#analyze">Analyze</a>
            <a class="lnk" href="#how-it-works">How it works</a>
            <a class="lnk" href="#about">About</a>
            <a class="nav-cta" href="#analyze">Analyze Image {ico("arrow", 15)}</a>
        </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

st.html(
    f"""
    <div class="hero">

        <div class="hero-copy">

            <div class="hero-eyebrow">AI-POWERED IMAGE FORENSICS</div>

            <h1>See beyond<br><span>the pixels.</span></h1>

            <p>
                Detect potential image manipulation using
                Error Level Analysis and machine learning.
            </p>

            <div class="hero-actions">
                <a class="btn-blue" href="#analyze">Analyze an image
                    <svg class="ico" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14 M13 6l6 6-6 6"/></svg>
                </a>
                <a class="btn-text" href="#how-it-works">How it works
                    <svg class="ico" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 5v14 M6 13l6 6 6-6"/></svg>
                </a>
            </div>

        </div>

        <div class="hero-visual">

            <div class="pipe">

                <div class="vt">
                    <div class="vt-cap">IMAGE</div>
                    <div class="vt-body vt-photo"><div class="sil"></div></div>
                </div>

                <div class="arrow"></div>

                <div class="vt">
                    <div class="vt-cap">ELA ANALYSIS</div>
                    <div class="vt-body vt-ela"><div class="sil"></div></div>
                </div>

                <div class="arrow"></div>

                <div class="vt">
                    <div class="vt-cap">AI CLASSIFICATION</div>
                    <div class="vt-body vt-net">
                        <svg viewBox="0 0 100 100" fill="none" stroke="#5b9bff" stroke-width="0.8">
                            <line x1="20" y1="30" x2="45" y2="20"/><line x1="45" y1="20" x2="75" y2="35"/>
                            <line x1="20" y1="30" x2="35" y2="60"/><line x1="35" y1="60" x2="65" y2="65"/>
                            <line x1="75" y1="35" x2="65" y2="65"/><line x1="45" y1="20" x2="35" y2="60"/>
                            <line x1="45" y1="20" x2="65" y2="65"/><line x1="35" y1="60" x2="50" y2="85"/>
                            <line x1="65" y1="65" x2="50" y2="85"/><line x1="20" y1="30" x2="12" y2="60"/>
                            <line x1="12" y1="60" x2="35" y2="60"/><line x1="75" y1="35" x2="88" y2="55"/>
                            <g fill="#8fb6ff" stroke="none">
                                <circle cx="20" cy="30" r="3"/><circle cx="45" cy="20" r="3.4"/><circle cx="75" cy="35" r="3"/>
                                <circle cx="35" cy="60" r="3.6"/><circle cx="65" cy="65" r="3.2"/><circle cx="50" cy="85" r="2.8"/>
                                <circle cx="12" cy="60" r="2.4"/><circle cx="88" cy="55" r="2.4"/>
                            </g>
                        </svg>
                    </div>
                </div>

                <div class="arrow"></div>

                <div class="vt v">
                    <div class="vt-cap">VERDICT</div>
                    <div class="vt-body vt-verdict">
                        <div class="row real">{ico("shield", 20)} REAL</div>
                        <div class="or">or</div>
                        <div class="row fake">{ico("warn", 20)} TAMPERED</div>
                    </div>
                </div>

            </div>

        </div>

    </div>
    """
)


# ============================================================
# LIGHT SHEET: WORKSPACE, INSIGHTS, METHOD, LIMITS, FOOTER
# ============================================================

with keyed("sheet"):

    st.html('<div class="anchor" id="analyze"></div>')

    col_left, col_mid, col_right = st.columns([1, 2.35, 1.05], gap="medium")

    # ========================================================
    # LEFT: UPLOAD + IMAGE INFORMATION
    # ========================================================

    with col_left:

        with keyed("card_left"):

            st.html(f'<div class="card-head">{ico("upload")} Upload image</div>')

            uploaded_file = st.file_uploader(
                "Choose an image",
                type=["jpg", "jpeg", "png", "webp"],
                label_visibility="collapsed",
            )

            # ----------------------------------------------------
            # Prepare the upload (only when the file changes)
            # ----------------------------------------------------

            if uploaded_file is None:

                # Uploader was cleared: drop stale state and temp files.
                if st.session_state.file_signature is not None:
                    reset_workspace()

            else:

                file_bytes = uploaded_file.getvalue()

                signature = "{}:{}:{}".format(
                    uploaded_file.name,
                    len(file_bytes),
                    hashlib.md5(file_bytes).hexdigest(),
                )

                if st.session_state.file_signature != signature:

                    # New image: clear previous prediction, regenerate everything.
                    reset_workspace()

                    st.session_state.file_signature = signature
                    st.session_state.uploaded_filename = uploaded_file.name
                    st.session_state.file_size_bytes = len(file_bytes)

                    try:

                        suffix = Path(uploaded_file.name).suffix.lower()

                        if suffix not in [".jpg", ".jpeg", ".png", ".webp"]:
                            suffix = ".jpg"

                        st.session_state.file_format = suffix.lstrip(".").upper()

                        work_dir = tempfile.mkdtemp(prefix="true_vision_")
                        st.session_state.work_dir = work_dir

                        input_path = os.path.join(work_dir, "input" + suffix)

                        with open(input_path, "wb") as handle:
                            handle.write(file_bytes)

                        st.session_state.uploaded_path = input_path

                        st.session_state.uploaded_image = (
                            Image.open(input_path).convert("RGB")
                        )

                        # ----- ELA (existing module, unchanged parameters) -----

                        ela_output_path = os.path.join(work_dir, "ela_output.jpg")
                        heatmap_path = os.path.join(work_dir, "ela_heatmap.jpg")

                        try:

                            perform_ela(
                                input_path,
                                ela_output_path,
                                heatmap_path,
                                quality=90,
                            )

                            st.session_state.ela_path = ela_output_path
                            st.session_state.heatmap_path = heatmap_path

                        except Exception as ela_exc:

                            st.session_state.ela_path = None
                            st.session_state.heatmap_path = None
                            st.session_state.ela_error = str(ela_exc)

                    except Exception as process_exc:

                        st.session_state.uploaded_image = None
                        st.session_state.process_error = str(process_exc)

            workspace_ready = (
                uploaded_file is not None
                and st.session_state.uploaded_image is not None
                and not st.session_state.process_error
            )

            if uploaded_file is not None and st.session_state.process_error:

                st.error(
                    "Unable to process the uploaded image. "
                    "Please try a different file. "
                    f"({st.session_state.process_error})"
                )

            # ----------------------------------------------------
            # Image information
            # ----------------------------------------------------

            if workspace_ready:

                image = st.session_state.uploaded_image

                safe_filename = escape(st.session_state.uploaded_filename or "")
                file_format = escape(st.session_state.file_format)
                size_label = format_size(st.session_state.file_size_bytes)

                st.html(
                    f"""
                    <div class="card-head">{ico("list")} Image information</div>

                    <div class="info">

                        <div class="info-row">
                            {ico("file", 15)}
                            <span class="info-k">File name</span>
                            <span class="info-v" title="{safe_filename}">{safe_filename}</span>
                        </div>

                        <div class="info-row">
                            {ico("frame", 15)}
                            <span class="info-k">Resolution</span>
                            <span class="info-v">{image.width} × {image.height}</span>
                        </div>

                        <div class="info-row">
                            {ico("file", 15)}
                            <span class="info-k">File size</span>
                            <span class="info-v">{size_label}</span>
                        </div>

                        <div class="info-row">
                            {ico("image", 15)}
                            <span class="info-k">Format</span>
                            <span class="info-v">{file_format}</span>
                        </div>

                    </div>
                    """
                )

    # ========================================================
    # MIDDLE: ORIGINAL + ELA + ANALYZE
    # ========================================================

    with col_mid:

        with keyed("card_mid"):

            if not workspace_ready:

                st.html(
                    f"""
                    <div class="ph">
                        <span class="ph-l">{ico("image")} Original and ELA analysis</span>
                    </div>
                    <div class="empty-viewport">
                        Upload an image to see it here next to its
                        Error Level Analysis heatmap.
                    </div>
                    """
                )

            else:

                image = st.session_state.uploaded_image

                if st.session_state.ela_error:

                    st.warning(
                        "The ELA visualization could not be generated for this image. "
                        f"({st.session_state.ela_error})"
                    )

                image_col, ela_col = st.columns(2, gap="medium")

                with image_col:

                    st.html(
                        f"""
                        <div class="ph">
                            <span class="ph-l">{ico("image")} Original image</span>
                            <span class="ph-r">{image.width} × {image.height}</span>
                        </div>
                        """
                    )

                    stretch(st.image, image)

                with ela_col:

                    st.html(
                        f"""
                        <div class="ph">
                            <span class="ph-l">{ico("pulse")} ELA analysis</span>
                            <span class="ph-r">Recompression · Q90</span>
                        </div>
                        """
                    )

                    if (
                        st.session_state.heatmap_path
                        and os.path.exists(st.session_state.heatmap_path)
                    ):

                        stretch(st.image, st.session_state.heatmap_path)

                    else:

                        st.info("ELA heatmap is unavailable for this image.")

                # ------------------------------------------------
                # Analyze button + backend call
                # ------------------------------------------------

                analyze_button = st.button("Analyze image authenticity")

                if analyze_button:

                    if not st.session_state.uploaded_path:

                        st.error("Please upload an image first.")

                    else:

                        try:

                            with st.spinner(
                                "Analyzing image · ELA features → classifier → verdict"
                            ):

                                image_path = Path(st.session_state.uploaded_path)

                                content_type, _ = mimetypes.guess_type(image_path.name)

                                if content_type is None:
                                    content_type = "application/octet-stream"

                                with open(image_path, "rb") as image_file:

                                    response = requests.post(
                                        BACKEND_URL,
                                        files={
                                            "file": (
                                                st.session_state.uploaded_filename
                                                or image_path.name,
                                                image_file,
                                                content_type,
                                            )
                                        },
                                        timeout=60,
                                    )

                                response.raise_for_status()

                                api_result = response.json()

                            st.session_state.analysis_result = {
                                "result": api_result.get("prediction", "UNKNOWN"),
                                "confidence": float(api_result.get("confidence", 0)),
                                "model_name": api_result.get("model", "Unknown"),
                            }

                        except requests.exceptions.ConnectionError:

                            st.error(
                                "Cannot connect to the analysis backend. "
                                "Please make sure the FastAPI server is running on "
                                "http://127.0.0.1:8000"
                            )

                        except requests.exceptions.Timeout:

                            st.error("The backend took too long to respond. Please try again.")

                        except requests.exceptions.HTTPError as http_error:

                            st.error(f"The backend returned an error: {http_error}")

                        except Exception as error:

                            st.error(f"Analysis failed: {error}")

    # ========================================================
    # RIGHT: RESULT
    # ========================================================

    result_view = None   # filled when a valid prediction exists

    with col_right:

        with keyed("card_right"):

            st.html(f'<div class="card-head">{ico("check")} Result</div>')

            data = st.session_state.analysis_result if workspace_ready else None

            if data is None:

                st.html(
                    f"""
                    <div class="res-empty">
                        {ico("shield", 40)}
                        <div>
                            No result yet.<br>
                            Upload an image and run the analysis
                            to see the verdict.
                        </div>
                    </div>
                    """
                )

            else:

                result = str(data["result"])
                confidence = data["confidence"]
                model_name = data["model_name"]

                verdict_key = result.strip().upper()

                if verdict_key == "REAL":

                    state_class = "is-real"
                    title = "Authentic image"
                    message = (
                        "More consistent with the real-image patterns "
                        "learned during training."
                    )
                    glyph = ico("shield", 32)

                elif verdict_key in ("TAMPERED", "FAKE"):

                    state_class = "is-fake"
                    title = "Possible manipulation"
                    message = (
                        "More consistent with the patterns of "
                        "manipulated images."
                    )
                    glyph = ico("warn", 32)

                else:

                    state_class = None

                if state_class is None:

                    st.warning(
                        "The backend returned an unrecognized prediction. "
                        "Please try analyzing the image again."
                    )

                else:

                    ring_value = min(max(confidence, 0.0), 100.0)

                    safe_verdict = escape(verdict_key)
                    safe_model = escape(str(model_name))

                    result_view = {
                        "verdict": safe_verdict,
                        "model": safe_model,
                        "confidence": confidence,
                    }

                    st.html(
                        f"""
                        <div class="res {state_class}">

                            <div class="res-hero">
                                {glyph}
                                <div>
                                    <div class="res-title">{title}</div>
                                    <div class="res-msg">{escape(message)}</div>
                                </div>
                            </div>

                            <div class="ring" style="--p: {ring_value:.2f};">
                                <div class="ring-inner">
                                    <div class="ring-value">{ring_value:.2f}%</div>
                                    <div class="ring-label">Confidence</div>
                                </div>
                            </div>

                            <div class="res-row">
                                {ico("target", 15)}
                                <span class="k">Prediction</span>
                                <span class="v c">{safe_verdict}</span>
                            </div>

                            <div class="res-row">
                                {ico("pulse", 15)}
                                <span class="k">Confidence</span>
                                <span class="v">{confidence:.2f}%</span>
                            </div>

                            <div class="res-row">
                                {ico("cube", 15)}
                                <span class="k">Model</span>
                                <span class="v" title="{safe_model}">{safe_model}</span>
                            </div>

                            <div class="res-note">
                                A machine-learning prediction, not a forensic guarantee.
                            </div>

                        </div>
                        """
                    )

    # ========================================================
    # FORENSIC INSIGHTS
    # ========================================================

    if result_view is not None:
        model_chip = f'<span class="ins-chip">{result_view["model"]}</span>'
        verdict_chip = (
            f'<span class="ins-chip">{result_view["verdict"]} · '
            f'{result_view["confidence"]:.2f}%</span>'
        )
    else:
        model_chip = ""
        verdict_chip = ""

    st.html(
        f"""
        <div class="band">

            <div class="card-head">{ico("flow")} Forensic insights</div>

            <div class="insights">

                <div class="ins">
                    <div class="ins-n">01</div>
                    <div>
                        <div class="ins-t">ELA feature extraction</div>
                        <div class="ins-d">
                            Compression-error patterns are measured and
                            summarized as statistical features.
                        </div>
                    </div>
                </div>

                <div class="conn"></div>

                <div class="ins">
                    <div class="ins-n">02</div>
                    <div>
                        <div class="ins-t">Machine-learning classification</div>
                        <div class="ins-d">
                            The extracted features are evaluated by the
                            trained classifier.
                        </div>
                        {model_chip}
                    </div>
                </div>

                <div class="conn"></div>

                <div class="ins">
                    <div class="ins-n">03</div>
                    <div>
                        <div class="ins-t">Verdict</div>
                        <div class="ins-d">
                            The classifier's output for the image,
                            with its confidence score.
                        </div>
                        {verdict_chip}
                    </div>
                </div>

            </div>

        </div>
        """
    )

    # ========================================================
    # HOW IT WORKS + LIMITATIONS
    # ========================================================

    st.html(
        f"""
        <div class="duo" id="how-it-works">

            <div class="band">

                <div class="card-head">{ico("cube")} How True Vision works</div>

                <div class="steps">

                    <div class="stp">
                        <div class="stp-i">{ico("upload", 20)}</div>
                        <div>
                            <div class="stp-n">01</div>
                            <div class="stp-t">Upload</div>
                            <div class="stp-d">Select a JPG, JPEG, PNG or WEBP image.</div>
                        </div>
                    </div>

                    <div class="stp-arrow">→</div>

                    <div class="stp">
                        <div class="stp-i">{ico("pulse", 20)}</div>
                        <div>
                            <div class="stp-n">02</div>
                            <div class="stp-t">ELA</div>
                            <div class="stp-d">Recompress the image and measure compression differences.</div>
                        </div>
                    </div>

                    <div class="stp-arrow">→</div>

                    <div class="stp">
                        <div class="stp-i">{ico("file", 20)}</div>
                        <div>
                            <div class="stp-n">03</div>
                            <div class="stp-t">Feature extraction</div>
                            <div class="stp-d">Extract statistical features from the ELA output.</div>
                        </div>
                    </div>

                    <div class="stp-arrow">→</div>

                    <div class="stp">
                        <div class="stp-i">{ico("chip", 20)}</div>
                        <div>
                            <div class="stp-n">04</div>
                            <div class="stp-t">Machine learning</div>
                            <div class="stp-d">A trained Random Forest classifies the features.</div>
                        </div>
                    </div>

                    <div class="stp-arrow">→</div>

                    <div class="stp last">
                        <div class="stp-i">{ico("check", 20)}</div>
                        <div>
                            <div class="stp-n">05</div>
                            <div class="stp-t">Verdict</div>
                            <div class="stp-d">REAL or TAMPERED, with a confidence score.</div>
                        </div>
                    </div>

                </div>

            </div>

            <div class="limits" id="about">

                <div class="card-head">{ico("warn")} Important limitations</div>

                <p>
                    ELA is an analytical indicator, not absolute proof of
                    manipulation. Compression, resizing, screenshots and other
                    image processing can affect results.
                </p>

            </div>

        </div>
        """
    )

    # ========================================================
    # FOOTER
    # ========================================================

    st.html(
        """
        <div class="footer">

            <div class="footer-l">
                <div class="footer-brand"><i></i>TRUE VISION</div>
                <div class="footer-tag">See beyond the pixels.</div>
            </div>

            <div class="footer-r">
                <a href="#analyze">Analyze</a>
                <a href="#how-it-works">How it works</a>
                <a href="#about">About</a>
            </div>

        </div>
        """
    )