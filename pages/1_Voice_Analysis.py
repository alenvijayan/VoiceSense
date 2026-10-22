import io
import os
import tempfile
from datetime import datetime
import soundfile as sf

import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

from utils.feature_extraction import extract_features
from utils.prediction import predict_voice
from utils.biomarker_interpretation import (
    load_biomarker_reference,
    interpret_biomarker,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Voice Analysis | VoiceSense",
    page_icon="🎙️",
    layout="wide",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES (shared with home via same font + design language)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 16px; }
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 1180px;
    padding-top: 0;
    padding-bottom: 4rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F766E 0%, #134E4A 100%) !important;
}
section[data-testid="stSidebar"] * { color: #E0FDFA !important; }
section[data-testid="stSidebar"] .stDivider { border-color: rgba(255,255,255,0.15) !important; }
section[data-testid="stSidebar"] .stCaption { color: rgba(204,251,241,0.6) !important; }

/* ── Page header strip ── */
.vs-page-header {
    background: linear-gradient(135deg, #0D9488 0%, #0F766E 50%, #115E59 100%);
    border-radius: 20px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 12px 40px rgba(13,148,136,0.2);
    position: relative;
    overflow: hidden;
}
.vs-page-header::after {
    content: "🎧";
    position: absolute;
    right: 2rem;
    font-size: 5rem;
    opacity: 0.12;
}
.vs-page-header-left h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: white;
    margin: 0 0 0.5rem 0;
}
.vs-page-header-left p {
    color: rgba(255,255,255,0.8);
    font-size: 1.05rem;
    line-height: 1.6;
    margin: 0;
}

/* ── Section heading ── */
.vs-section-heading {
    font-family: 'Outfit', sans-serif;
    font-size: 1.25rem;
    font-weight: 700;
    color: #0F766E;
    letter-spacing: 0.03em;
    text-transform: uppercase;
    margin: 2.5rem 0 1.1rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.vs-section-heading .step-badge {
    background: linear-gradient(135deg, #0D9488, #0F766E);
    color: white;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 4px 12px;
    border-radius: 50px;
    letter-spacing: 0.05em;
}

/* ── Panel / card wrapper ── */
.vs-panel {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.5rem 1.5rem;
    box-shadow: 0 2px 12px rgba(15,118,110,0.05);
}

/* ── Metric cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #F0FDFA, #ECFDF5);
    border: 1px solid #CCFBF1;
    padding: 1.1rem 1rem;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(13,148,136,0.07);
}
div[data-testid="stMetricLabel"] { color: #475569; font-size: 0.95rem; font-weight: 600; }
div[data-testid="stMetricValue"] { color: #0F172A; font-family: 'Outfit', sans-serif; font-weight: 700; font-size: 1.6rem; }

/* ── Result banner ── */
.vs-result-healthy {
    background: linear-gradient(135deg, #ECFDF5, #D1FAE5);
    border: 2px solid #34D399;
    border-radius: 18px;
    padding: 1.6rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.vs-result-parkinson {
    background: linear-gradient(135deg, #FFF7ED, #FFEDD5);
    border: 2px solid #FB923C;
    border-radius: 18px;
    padding: 1.6rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.2rem;
}
.vs-result-icon { font-size: 2.5rem; }
.vs-result-title { font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 800; margin: 0 0 4px 0; }
.vs-result-sub { font-size: 0.88rem; color: #64748B; margin: 0; }
.result-healthy .vs-result-title { color: #065F46; }
.result-parkinson .vs-result-title { color: #9A3412; }

/* ── Probability bar ── */
.vs-prob-bar-wrap {
    margin-bottom: 1.4rem;
}
.vs-prob-label {
    display: flex;
    justify-content: space-between;
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
}
.vs-prob-bar-bg {
    background: #E2E8F0;
    border-radius: 50px;
    height: 14px;
    overflow: hidden;
}
.vs-prob-bar-fill-healthy {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #10B981, #34D399);
    transition: width 0.6s ease;
}
.vs-prob-bar-fill-parkinson {
    height: 100%;
    border-radius: 50px;
    background: linear-gradient(90deg, #F97316, #FB923C);
    transition: width 0.6s ease;
}

/* ── Biomarker card ── */
.vs-bio-card {
    background: white;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.2rem 1rem;
    text-align: center;
    box-shadow: 0 2px 10px rgba(0,0,0,0.04);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative;
    overflow: hidden;
}
.vs-bio-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.08);
}
.vs-bio-card-label {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: #94A3B8;
    margin-bottom: 10px;
}
.vs-bio-card-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.1rem;
    font-weight: 800;
    color: #0F172A;
    line-height: 1;
    margin-bottom: 6px;
}
.vs-bio-card-unit {
    font-size: 0.85rem;
    color: #94A3B8;
    margin-bottom: 12px;
}
.vs-bio-card-status {
    font-size: 0.85rem;
    font-weight: 700;
    padding: 5px 13px;
    border-radius: 50px;
    display: inline-block;
}
.status-healthy { background: #ECFDF5; color: #065F46; }
.status-warning { background: #FFFBEB; color: #92400E; }
.status-unknown { background: #F1F5F9; color: #64748B; }
.vs-bio-card-ref {
    font-size: 0.82rem;
    color: #94A3B8;
    margin-top: 10px;
}
.vs-bio-top-bar {
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 4px;
}

/* ── Info pill ── */
.vs-info-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 50px;
    padding: 6px 14px;
    font-size: 0.83rem;
    color: #1D4ED8;
    font-weight: 500;
    margin-bottom: 1rem;
}

/* ── Guidelines list ── */
.vs-guideline {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    margin-bottom: 0.7rem;
    font-size: 0.9rem;
    color: #374151;
}
.vs-guideline-num {
    background: linear-gradient(135deg, #0D9488, #0F766E);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}

/* ── Disclaimer ── */
.vs-disclaimer {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 12px;
    padding: 1rem 1.2rem;
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin: 1.5rem 0;
}
.vs-disclaimer p { color: #78350F; font-size: 0.88rem; line-height: 1.6; margin: 0; }
.vs-disclaimer strong { color: #92400E; }

/* ── Primary button ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0D9488, #0F766E) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 16px rgba(13,148,136,0.3) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 26px rgba(13,148,136,0.4) !important;
}

/* ── Dataframe ── */
.stDataFrame { border-radius: 12px !important; overflow: hidden; }

/* ── Divider ── */
hr { border-color: #E2E8F0; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 0.5rem 0 0.2rem 0;">
        <div style="font-family:'Outfit',sans-serif;font-size:1.35rem;font-weight:800;color:#CCFBF1;letter-spacing:-0.01em;">
            🎙️ VoiceSense
        </div>
        <div style="font-size:0.78rem;color:rgba(204,251,241,0.6);margin-top:2px;font-weight:500;letter-spacing:0.04em;text-transform:uppercase;">
            Voice ML Screening
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.markdown("**🎧 Voice Analysis**")

    st.divider()

    st.markdown("""
    <div style="font-size:0.75rem;color:rgba(204,251,241,0.45);text-align:center;">
        MCA Mini Project · 2024
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# PAGE HEADER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-page-header">
    <div class="vs-page-header-left">
        <h1>🎧 Voice Analysis</h1>
        <p>Record or upload a voice sample · Extract acoustic features · Get ML screening result</p>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 01 — PARTICIPANT DETAILS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">01</span> Participant Details
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        participant_id = st.text_input(
            "Participant ID",
            placeholder="e.g. VS-001",
        )

    with col2:
        age = st.number_input(
            "Age (optional)",
            min_value=1,
            max_value=120,
            value=None,
            placeholder="Enter age",
        )

    with col3:
        gender = st.selectbox(
            "Gender (optional)",
            ["Prefer not to say", "Female", "Male", "Other"],
        )

    st.caption(
        "💡 Use an anonymised participant ID rather than a full name where possible."
    )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 02 — RECORDING INSTRUCTIONS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">02</span> Prepare Your Recording
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    left, right = st.columns([3, 2])

    with left:
        st.markdown("""<div style="font-family:'Outfit',sans-serif;font-size:1.05rem;font-weight:700;color:#0F172A;margin-bottom:1rem;">Recording guidelines</div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">
  <div style="background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;padding:12px 14px;">
    <div style="font-size:0.95rem;font-weight:600;color:#0F172A;">Quiet room</div>
    <div style="font-size:0.87rem;color:#64748B;margin-top:3px;">Minimal background noise</div>
  </div>
  <div style="background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;padding:12px 14px;">
    <div style="font-size:0.95rem;font-weight:600;color:#0F172A;">15–20 cm away</div>
    <div style="font-size:0.87rem;color:#64748B;margin-top:3px;">Keep mic at arm's length</div>
  </div>
  <div style="background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;padding:12px 14px;">
    <div style="font-size:0.95rem;font-weight:600;color:#0F172A;">Say "ah" clearly</div>
    <div style="font-size:0.87rem;color:#64748B;margin-top:3px;">Sustained vowel, 3–5 seconds</div>
  </div>
  <div style="background:#F0FDFA;border:1px solid #CCFBF1;border-radius:12px;padding:12px 14px;">
    <div style="font-size:0.95rem;font-weight:600;color:#0F172A;">Listen back</div>
    <div style="font-size:0.87rem;color:#64748B;margin-top:3px;">Check before submitting</div>
  </div>
</div>""", unsafe_allow_html=True)

    with right:
        st.markdown("##### 🔊 Sample audio")

        sample_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "sample_voice.wav",
        )

        if os.path.exists(sample_path):
            st.audio(sample_path, format="audio/wav")
            with open(sample_path, "rb") as sample_file:
                st.download_button(
                    "⬇ Download sample WAV",
                    data=sample_file.read(),
                    file_name="sample_voice.wav",
                    mime="audio/wav",
                    key="download_sample",
                )
        else:
            st.warning(
                "Sample audio not yet added. Place a WAV file at "
                "`assets/sample_voice.wav`.",
                icon="⚠️",
            )


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 03 — AUDIO INPUT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">03</span> Choose Audio Input
</div>
""", unsafe_allow_html=True)

with st.container(border=True):
    input_method = st.radio(
        "Select an input method",
        ["🎙️  Live Recording", "📁  Upload WAV File"],
        horizontal=True,
        key="input_method",
    )

    audio_file = None

    if "Live Recording" in input_method:
        st.markdown("##### Record using your microphone")
        st.caption(
            "Allow microphone access when prompted. Record a short, clear "
            "sample and listen back before submitting."
        )
        audio_file = st.audio_input(
            "Record your voice",
            key="voice_recorder",
        )
    else:
        st.markdown("##### Upload an existing recording")
        audio_file = st.file_uploader(
            "Choose a WAV audio file",
            type=["wav"],
            help="Upload a clear WAV recording.",
            key="voice_upload",
        )

    if audio_file is not None:
        st.success(f"✅ Audio ready: {audio_file.name}", icon="✅")
        st.audio(audio_file.getvalue(), format="audio/wav")


# ─────────────────────────────────────────────────────────────────────────────
# PDF REPORT GENERATOR
# ─────────────────────────────────────────────────────────────────────────────
def create_pdf_report(participant_id, age, gender, result, features, prediction_result, duration):
    """Create a downloadable preliminary screening report."""
    buffer = io.BytesIO()

    document = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40,
    )

    styles = getSampleStyleSheet()
    teal = colors.HexColor("#0D9488")
    dark = colors.HexColor("#0F172A")
    light_teal = colors.HexColor("#F0FDFA")
    border_color = colors.HexColor("#CCFBF1")
    grey_text = colors.HexColor("#64748B")

    title_style = ParagraphStyle(
        "VSTitleStyle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=dark,
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "VSSubTitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=11,
        textColor=grey_text,
        spaceAfter=2,
    )
    heading2_style = ParagraphStyle(
        "VSHeading2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=teal,
        spaceBefore=14,
        spaceAfter=6,
    )

    story = []

    story.append(Paragraph("VoiceSense", title_style))
    story.append(Paragraph("Voice-Based ML Screening Assessment", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=teal, spaceAfter=10))
    story.append(
        Paragraph(
            f"Generated: {datetime.now().strftime('%d %B %Y, %H:%M')}",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 14))

    details = [
        ["Participant ID", participant_id or "Not provided"],
        ["Age", str(age) if age is not None else "Not provided"],
        ["Gender", gender],
        ["Audio duration", f"{duration:.2f} seconds"],
        ["Features extracted", str(len(features))],
        ["Model", "Random Forest"],
    ]

    table = Table(details, colWidths=[150, 330])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), light_teal),
        ("TEXTCOLOR", (0, 0), (-1, -1), dark),
        ("GRID", (0, 0), (-1, -1), 0.4, border_color),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (1, 0), (1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Model Output", heading2_style))
    output_data = [
        ["Metric", "Value"],
        ["Predicted class", result],
        ["Maximum class probability", f"{prediction_result['confidence']:.2f}%"],
        ["Healthy class probability", f"{prediction_result['healthy_probability']:.2f}%"],
        ["Parkinsons class probability", f"{prediction_result['parkinson_probability']:.2f}%"],
    ]
    output_table = Table(output_data, colWidths=[200, 280])
    output_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, border_color),
        ("PADDING", (0, 0), (-1, -1), 7),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_teal]),
    ]))
    story.append(output_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Key Acoustic Measurements", heading2_style))
    key_features = ["Pitch", "Jitter", "Shimmer", "HNR", "RMS", "ZCR"]
    feature_rows = [["Feature", "Measured value"]]
    for feature_name in key_features:
        feature_rows.append([feature_name, f"{features[feature_name]:.6f}"])

    feature_table = Table(feature_rows, colWidths=[200, 280], repeatRows=1)
    feature_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.4, border_color),
        ("PADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_teal]),
    ]))
    story.append(feature_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("All 37 Extracted Features", heading2_style))
    all_rows = [["Feature", "Value"]]
    for name, value in features.items():
        all_rows.append([name, f"{value:.6f}"])

    all_table = Table(all_rows, colWidths=[200, 280], repeatRows=1)
    all_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), teal),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.3, border_color),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
    ]))
    story.append(all_table)
    story.append(Spacer(1, 18))

    story.append(Paragraph("Important Limitations", heading2_style))
    story.append(
        Paragraph(
            "This report contains output from an experimental machine-learning "
            "model. The predicted class and class probabilities are not a "
            "medical diagnosis, and the probability values are not calibrated "
            "estimates of the likelihood that a person has Parkinson's disease. "
            "Voice characteristics can be affected by many factors. This tool "
            "must not replace assessment by a qualified healthcare professional.",
            styles["Normal"],
        )
    )

    document.build(story)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 04 — ANALYSE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">04</span> Run Analysis
</div>
""", unsafe_allow_html=True)

analyse_col, _ = st.columns([1, 2])
with analyse_col:
    analyse_clicked = st.button(
        "🔬  Analyse Voice",
        type="primary",
        use_container_width=True,
    )

if analyse_clicked:
    if audio_file is None:
        st.warning()
        st.stop()

    if not participant_id.strip():
        st.warning("⚠️ Please enter a Participant ID before running the analysis.", icon="⚠️")
        st.stop()

    temp_path = None

    try:
        audio_bytes = audio_file.getvalue()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
            temp_audio.write(audio_bytes)
            temp_path = temp_audio.name

        waveform, sample_rate = librosa.load(temp_path, sr=None, mono=True)
        duration = len(waveform) / sample_rate

        if duration < 1.0:
            st.error(
                "The recording is too short — please provide at least 1 second of audio.",
                icon="🚫",
            )
            st.stop()

        if not np.isfinite(waveform).all():
            st.error("The audio contains invalid samples.", icon="🚫")
            st.stop()

        if np.max(np.abs(waveform)) < 1e-5:
            st.error("The recording appears silent. Please record again.", icon="🚫")
            st.stop()

        with st.spinner("🔬 Extracting 37 acoustic features and running classifier..."):
            features = extract_features(temp_path)
            prediction_result = predict_voice(features)

        result = prediction_result["label"]

        st.session_state["voice_analysis"] = {
            "participant_id": participant_id.strip(),
            "age": age,
            "gender": gender,
            "features": features,
            "prediction_result": prediction_result,
            "duration": duration,
            "sample_rate": sample_rate,
            "waveform": waveform,
        }

    except Exception as error:
        st.error(f"Analysis failed: {error}", icon="❌")

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS
# ─────────────────────────────────────────────────────────────────────────────
analysis = st.session_state.get("voice_analysis")

if analysis:
    features = analysis["features"]
    prediction_result = analysis["prediction_result"]
    result = prediction_result["label"]

    st.markdown("---")

    # ── 05 Screening Results ──────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">05</span> Screening Results
</div>
""", unsafe_allow_html=True)

    st.caption("These are model outputs for the supplied recording, not a clinical diagnosis.")

    # Result banner
    is_healthy = "healthy" in result.lower()
    banner_class = "vs-result-healthy" if is_healthy else "vs-result-parkinson"
    icon = "✅" if is_healthy else "⚠️"
    color_class = "result-healthy" if is_healthy else "result-parkinson"

    st.markdown(f"""
<div class="{banner_class} {color_class}" style="margin-bottom:1.2rem;">
    <div class="vs-result-icon">{icon}</div>
    <div>
        <p class="vs-result-title">{result}</p>
        <p class="vs-result-sub">Confidence: {prediction_result['confidence']:.1f}% &nbsp;|&nbsp; Audio duration: {analysis['duration']:.2f}s</p>
    </div>
</div>
""", unsafe_allow_html=True)

    # Metrics row
    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted class", result)
    col2.metric("Maximum class probability", f"{prediction_result['confidence']:.2f}%")
    col3.metric("Audio duration", f"{analysis['duration']:.2f} s")

    # Probability bars
    st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
    pb1, pb2 = st.columns(2)

    h_prob = prediction_result["healthy_probability"]
    p_prob = prediction_result["parkinson_probability"]

    with pb1:
        st.markdown(f"""
<div class="vs-prob-bar-wrap">
    <div class="vs-prob-label">
        <span>🟢 Healthy probability</span>
        <span>{h_prob:.1f}%</span>
    </div>
    <div class="vs-prob-bar-bg">
        <div class="vs-prob-bar-fill-healthy" style="width:{h_prob}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

    with pb2:
        st.markdown(f"""
<div class="vs-prob-bar-wrap">
    <div class="vs-prob-label">
        <span>🟠 Parkinson's probability</span>
        <span>{p_prob:.1f}%</span>
    </div>
    <div class="vs-prob-bar-bg">
        <div class="vs-prob-bar-fill-parkinson" style="width:{p_prob}%;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

    st.info(
        "Random Forest class probabilities are model outputs and should not be interpreted "
        "as a clinical probability of Parkinson's disease.",
        icon="ℹ️",
    )

    # ── 06 Audio Quality ──────────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">06</span> Audio Quality
</div>
""", unsafe_allow_html=True)

    quality_col1, quality_col2, quality_col3 = st.columns(3)
    quality_col1.metric("Sample rate", f"{analysis['sample_rate']} Hz")
    quality_col2.metric("RMS energy", f"{features['RMS']:.5f}")
    quality_col3.metric("Zero crossing rate", f"{features['ZCR']:.5f}")

    st.caption(
        "These are basic signal measurements, not a validated overall recording-quality score."
    )

    # ── 07 Voice Measurements ─────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">07</span> Voice Measurements
</div>
""", unsafe_allow_html=True)

    st.caption(
        "Acoustic measurements compared with the healthy-training reference range. "
        "These are exploratory comparisons, not clinical thresholds."
    )

    reference = load_biomarker_reference()

    biomarker_info = [
        ("Pitch", "Pitch", "Hz"),
        ("Jitter", "Jitter", "Relative"),
        ("Shimmer", "Shimmer", "Relative"),
        ("HNR", "HNR", "dB"),
    ]

    cards = st.columns(4)
    for col, (name, key, unit) in zip(cards, biomarker_info):
        value = float(features[key])
        info = interpret_biomarker(key, value, reference)
        status = info["status"]

        if status == "Within healthy-dataset reference range":
            bar_color = "linear-gradient(90deg,#10B981,#34D399)"
            status_cls = "status-healthy"
            short_status = "✓ Within range"
        elif status in (
            "Below healthy-dataset reference range",
            "Above healthy-dataset reference range",
        ):
            bar_color = "linear-gradient(90deg,#F97316,#FB923C)"
            status_cls = "status-warning"
            short_status = (
                "↓ Below reference"
                if status.startswith("Below")
                else "↑ Above reference"
            )
        else:
            bar_color = "linear-gradient(90deg,#94A3B8,#CBD5E1)"
            status_cls = "status-unknown"
            short_status = "— No reference"

        ref_text = (
            f"Ref: {info['p05']:.4f} – {info['p95']:.4f}"
            if info["p05"] is not None
            else "Reference not available"
        )

        with col:
            st.markdown(f"""
<div class="vs-bio-card">
    <div class="vs-bio-top-bar" style="background:{bar_color};"></div>
    <div class="vs-bio-card-label">{name}</div>
    <div class="vs-bio-card-value">{value:.4f}</div>
    <div class="vs-bio-card-unit">{unit}</div>
    <div class="vs-bio-card-status {status_cls}">{short_status}</div>
    <div class="vs-bio-card-ref">{ref_text}</div>
</div>
""", unsafe_allow_html=True)

    with st.expander("📖 Understand these measurements"):
        st.markdown("""
| Measure | Description |
|---|---|
| **Pitch** | Average fundamental frequency of voiced frames (Hz). |
| **Jitter** | Variation in consecutive voice-period durations. |
| **Shimmer** | Variation in the amplitude of consecutive periods. |
| **HNR** | Harmonic-to-noise ratio — signal clarity. |

**Reading the colours:** Green = within the healthy-dataset reference range; 
Amber = outside it. These are exploratory comparisons and are **not clinical thresholds**.
        """)

    # ── 08 Waveform ───────────────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">08</span> Waveform
</div>
""", unsafe_allow_html=True)

    waveform = analysis["waveform"]
    sample_rate = analysis["sample_rate"]
    time_axis = np.arange(len(waveform)) / sample_rate

    fig, ax = plt.subplots(figsize=(12, 3), facecolor="#F0FDFA")
    ax.set_facecolor("#F0FDFA")
    ax.plot(time_axis, waveform, linewidth=0.7, color="#0D9488", alpha=0.9)
    ax.fill_between(time_axis, waveform, alpha=0.12, color="#0D9488")
    ax.set_xlabel("Time (seconds)", color="#475569", fontsize=9)
    ax.set_ylabel("Amplitude", color="#475569", fontsize=9)
    ax.set_title("Audio Waveform", color="#0F172A", fontsize=11, fontweight="bold", pad=12)
    ax.tick_params(colors="#94A3B8", labelsize=8)
    ax.spines[:].set_color("#E2E8F0")
    ax.grid(alpha=0.25, color="#CBD5E1", linestyle="--")
    fig.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    # ── 09 Spectrogram ────────────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">09</span> Spectrogram
</div>
""", unsafe_allow_html=True)

    fig2, ax2 = plt.subplots(figsize=(12, 4), facecolor="#F0FDFA")
    ax2.set_facecolor("#F0FDFA")

    D = librosa.amplitude_to_db(
        np.abs(
            librosa.stft(
                librosa.resample(waveform, orig_sr=sample_rate, target_sr=8000),
                n_fft=1024,
            )
        ),
        ref=np.max,
    )

    img = librosa.display.specshow(D, sr=8000, x_axis="time", y_axis="hz", ax=ax2, cmap="YlOrRd")
    ax2.set_title("Magnitude Spectrogram", color="#0F172A", fontsize=11, fontweight="bold", pad=12)
    ax2.tick_params(colors="#94A3B8", labelsize=8)
    ax2.spines[:].set_color("#E2E8F0")
    ax2.set_xlabel("Time (s)", color="#475569", fontsize=9)
    ax2.set_ylabel("Frequency (Hz)", color="#475569", fontsize=9)
    fig2.colorbar(img, ax=ax2, format="%+2.0f dB")
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    # ── 10 Extracted Features ─────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">10</span> All Extracted Features
</div>
""", unsafe_allow_html=True)

    feature_table = [
        {"Feature": name, "Value": f"{value:.6f}"}
        for name, value in features.items()
    ]

    st.dataframe(
        feature_table,
        use_container_width=True,
        hide_index=True,
    )

    # ── 11 Download Report ────────────────────────────────────────────────────
    st.markdown("""
<div class="vs-section-heading">
    <span class="step-badge">11</span> Download Screening Report
</div>
""", unsafe_allow_html=True)

    st.markdown("""
<div class="vs-disclaimer">
    <span>⚠️</span>
    <p>
        <strong>Important —</strong> This PDF report contains output from an experimental 
        ML model. It is <strong>not a medical diagnosis</strong> and must not replace 
        assessment by a qualified healthcare professional.
    </p>
</div>
""", unsafe_allow_html=True)

    pdf_bytes = create_pdf_report(
        participant_id=analysis["participant_id"],
        age=analysis["age"],
        gender=analysis["gender"],
        result=result,
        features=features,
        prediction_result=prediction_result,
        duration=analysis["duration"],
    )

    dl_col, _ = st.columns([1, 2])
    with dl_col:
        st.download_button(
            "📄  Download Screening Report (PDF)",
            data=pdf_bytes,
            file_name=f"VoiceSense_{analysis['participant_id']}_report.pdf",
            mime="application/pdf",
            type="primary",
            use_container_width=True,
        )
