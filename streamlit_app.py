
import streamlit as st

st.set_page_config(
    page_title="VoiceSense | Parkinson Voice Screening",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL STYLES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@400;600;700;800&display=swap" rel="stylesheet">

<style>
/* ── Root font ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
}

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    max-width: 1180px;
    padding-top: 0rem;
    padding-bottom: 4rem;
    padding-left: 2.5rem;
    padding-right: 2.5rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0F766E 0%, #134E4A 100%) !important;
}
section[data-testid="stSidebar"] * { color: #E0FDFA !important; }
section[data-testid="stSidebar"] a:hover { color: #CCFBF1 !important; }
section[data-testid="stSidebar"] .stDivider { border-color: rgba(255,255,255,0.15) !important; }
section[data-testid="stSidebar"] .stCaption { color: rgba(204,251,241,0.65) !important; }

/* ── Hero banner ── */
.vs-hero {
    background: linear-gradient(135deg, #0D9488 0%, #0F766E 40%, #115E59 100%);
    border-radius: 24px;
    padding: 3.5rem 3rem 3rem 3rem;
    margin-bottom: 2.5rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 20px 60px rgba(13,148,136,0.25);
}
.vs-hero::before {
    content: "";
    position: absolute;
    top: -60px; right: -60px;
    width: 320px; height: 320px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.vs-hero::after {
    content: "";
    position: absolute;
    bottom: -80px; left: 40%;
    width: 240px; height: 240px;
    background: rgba(255,255,255,0.04);
    border-radius: 50%;
}
.vs-hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
    color: #CCFBF1;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 6px 14px;
    border-radius: 50px;
    margin-bottom: 1.4rem;
}
.vs-hero h1 {
    font-family: 'Outfit', sans-serif;
    font-size: 3.4rem;
    font-weight: 800;
    color: #FFFFFF;
    line-height: 1.15;
    margin: 0 0 1.2rem 0;
}
.vs-hero h1 span {
    background: linear-gradient(90deg, #A7F3D0, #5EEAD4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.vs-hero p {
    color: rgba(255,255,255,0.85);
    font-size: 1.15rem;
    line-height: 1.8;
    max-width: 620px;
    margin: 0;
}

/* ── Section title ── */
.vs-section-title {
    font-family: 'Outfit', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #134E4A;
    margin: 3rem 0 1.4rem 0;
    display: flex;
    align-items: center;
    gap: 10px;
}
.vs-section-title::after {
    content: "";
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #CCFBF1, transparent);
}

/* ── Step cards ── */
.vs-step-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 18px;
    padding: 1.6rem 1.4rem;
    height: 100%;
    transition: transform 0.22s ease, box-shadow 0.22s ease;
    box-shadow: 0 2px 16px rgba(15,118,110,0.06);
    position: relative;
    overflow: hidden;
}
.vs-step-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(15,118,110,0.14);
}
.vs-step-card::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, #0D9488, #0F766E);
}
.vs-step-number {
    font-family: 'Outfit', sans-serif;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #0D9488;
    margin-bottom: 0.7rem;
}
.vs-step-card h3 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #0F172A;
    margin: 0 0 0.7rem 0;
}
.vs-step-card p {
    color: #64748B;
    font-size: 1rem;
    line-height: 1.7;
    margin: 0;
}

/* ── Feature cards ── */
.vs-feature-card {
    background: rgba(240,249,255,0.7);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(13,148,136,0.15);
    border-radius: 18px;
    padding: 1.6rem 1.5rem;
    height: 100%;
    transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
}
.vs-feature-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 36px rgba(13,148,136,0.12);
    border-color: rgba(13,148,136,0.35);
}
.vs-feature-icon {
    font-size: 1.8rem;
    margin-bottom: 0.8rem;
}
.vs-feature-card h3 {
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #0F766E;
    margin: 0 0 0.6rem 0;
}
.vs-feature-card p {
    color: #475569;
    font-size: 0.95rem;
    line-height: 1.7;
    margin: 0;
}

/* ── Stats strip ── */
.vs-stat-strip {
    background: linear-gradient(135deg, #F0FDFA, #ECFDF5);
    border: 1px solid #CCFBF1;
    border-radius: 18px;
    padding: 1.4rem 2rem;
    display: flex;
    justify-content: space-around;
    align-items: center;
    margin: 1.5rem 0;
    flex-wrap: wrap;
    gap: 1rem;
}
.vs-stat {
    text-align: center;
}
.vs-stat-value {
    font-family: 'Outfit', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #0D9488;
    line-height: 1;
}
.vs-stat-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #64748B;
    margin-top: 5px;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* ── Disclaimer ── */
.vs-disclaimer {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-left: 4px solid #F59E0B;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    display: flex;
    gap: 10px;
    align-items: flex-start;
    margin-top: 2rem;
}
.vs-disclaimer-icon { font-size: 1.2rem; flex-shrink: 0; margin-top: 2px; }
.vs-disclaimer p { color: #78350F; font-size: 0.9rem; line-height: 1.6; margin: 0; }
.vs-disclaimer strong { color: #92400E; }

/* ── Footer ── */
.vs-footer {
    text-align: center;
    margin-top: 3.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #E2E8F0;
    color: #94A3B8;
    font-size: 0.82rem;
}
.vs-footer strong { color: #0D9488; }

/* ── Primary button override ── */
div[data-testid="stButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0D9488, #0F766E) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.65rem 2rem !important;
    box-shadow: 0 4px 20px rgba(13,148,136,0.3) !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(13,148,136,0.4) !important;
}
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

    st.markdown("**Navigation**")
    st.markdown("🏠 &nbsp; **Home**")
    st.page_link("pages/1_Voice_Analysis.py", label="Voice Analysis", icon="🎧")

    st.divider()

    st.markdown("""
    <div style="font-size:0.75rem;color:rgba(204,251,241,0.45);text-align:center;">
        MCA Mini Project · 2024
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-hero">
    <div class="vs-hero-badge">🔬 &nbsp;Parkinson's Voice Screening Tool</div>
    <h1>Understand the Voice.<br><span>Detect the Signal.</span></h1>
    <p>
        VoiceSense uses machine learning to analyse acoustic features of voice 
        recordings and generate a preliminary screening result — helping researchers
        and clinicians gain rapid acoustic insights.
    </p>
</div>
""", unsafe_allow_html=True)

col_btn, col_spacer = st.columns([1, 3])
with col_btn:
    if st.button("Start Voice Analysis →", type="primary", use_container_width=True):
        st.switch_page("pages/1_Voice_Analysis.py")


# ─────────────────────────────────────────────────────────────────────────────
# STATS STRIP
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-stat-strip">
    <div class="vs-stat">
        <div class="vs-stat-value">37</div>
        <div class="vs-stat-label">Acoustic Features</div>
    </div>
    <div class="vs-stat">
        <div class="vs-stat-value">RF</div>
        <div class="vs-stat-label">Random Forest Model</div>
    </div>
    <div class="vs-stat">
        <div class="vs-stat-value">WAV</div>
        <div class="vs-stat-label">Audio Format</div>
    </div>
    <div class="vs-stat">
        <div class="vs-stat-value">PDF</div>
        <div class="vs-stat-label">Screening Report</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HOW IT WORKS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="vs-section-title">How it works</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="vs-step-card">
        <div class="vs-step-number">Step 01</div>
        <h3>🎤 Record</h3>
        <p>
            Record a voice sample directly in your browser using the built-in 
            microphone recorder, or upload an existing WAV audio file.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="vs-step-card">
        <div class="vs-step-number">Step 02</div>
        <h3>🧬 Analyse</h3>
        <p>
            Extract 37 acoustic features — MFCCs, pitch, jitter, shimmer, HNR 
            and spectral measures — then classify with our Random Forest model.
        </p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="vs-step-card">
        <div class="vs-step-number">Step 03</div>
        <h3>📋 Review</h3>
        <p>
            Explore the prediction result, probability scores, acoustic 
            measurements, waveform visualisations and download a PDF report.
        </p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FEATURES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="vs-section-title">Inside VoiceSense</div>', unsafe_allow_html=True)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown("""
    <div class="vs-feature-card">
        <div class="vs-feature-icon">🎚️</div>
        <h3>Acoustic Analysis</h3>
        <p>MFCCs, Chroma, pitch, jitter, shimmer, HNR and spectral features extracted per recording.</p>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown("""
    <div class="vs-feature-card">
        <div class="vs-feature-icon">🤖</div>
        <h3>ML Classification</h3>
        <p>Trained Random Forest classifier with class probability scores for Healthy vs Parkinson's.</p>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown("""
    <div class="vs-feature-card">
        <div class="vs-feature-icon">📊</div>
        <h3>Visualisations</h3>
        <p>Waveform plot, magnitude spectrogram and biomarker reference comparison cards.</p>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown("""
    <div class="vs-feature-card">
        <div class="vs-feature-icon">📄</div>
        <h3>Screening Report</h3>
        <p>Downloadable PDF containing model output, participant details and all extracted features.</p>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# DISCLAIMER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-disclaimer">
    <div class="vs-disclaimer-icon">⚠️</div>
    <p>
        <strong>Important notice —</strong>
        VoiceSense is an experimental machine-learning research project.
        Its output is <strong>not a medical diagnosis</strong> and must never be 
        used as a substitute for evaluation by a qualified healthcare professional. 
        Probability values are model outputs, not calibrated clinical estimates.
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="vs-footer">
    <strong>VoiceSense</strong> &nbsp;·&nbsp; MCA Mini Project &nbsp;·&nbsp; 
    Built with Streamlit &amp; scikit-learn
</div>
""", unsafe_allow_html=True)
