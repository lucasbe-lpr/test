import streamlit as st
import streamlit.components.v1 as components
import subprocess
import tempfile
import base64 as _b64
import os
import math
import io
import zipfile
from PIL import Image

LOGO_FILE       = "luluflix.png"
DEFAULT_WM_FILE = "lpr.png"
FAVICON_FILE    = "favicon.png"

try:
    _fav_img = Image.open(FAVICON_FILE)
except Exception:
    _fav_img = "▶"

st.set_page_config(
    page_title="Luluflix",
    page_icon=_fav_img,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- NOUVEAU DESIGN UI/UX ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

:root {
  --blue:      #0068B1;
  --blue-hover:#005591;
  --blue-soft: #eef7ff;
  --white:      #ffffff;
  --bg-app:    #F8FAFC;
  --ink:        #0F172A;
  --sub:        #475569;
  --muted:      #94A3B8;
  --border:     #E2E8F0;
  --card-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
}

/* Reset Streamlit */
.stApp { background-color: var(--bg-app); }
.block-container { padding: 1rem 3rem !important; }
[data-testid="stHeader"], [data-testid="stToolbar"] { display: none !important; }

/* Global Font */
* { font-family: 'Inter', sans-serif !important; }

/* --- Site Header --- */
.site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1.5rem 0;
    margin-bottom: 1rem;
}
.site-header img { height: 42px; filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1)); }
.site-header-right { 
    background: var(--blue-soft);
    padding: 0.5rem 1rem;
    border-radius: 99px;
    color: var(--blue);
    font-size: 0.8rem;
    font-weight: 500;
}

/* --- Tabs Styling --- */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 1.5rem;
    border-bottom: 2px solid var(--border);
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
    height: 45px;
    background-color: transparent !important;
    border: none !important;
    color: var(--muted) !important;
    font-weight: 500 !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
    color: var(--blue) !important;
    border-bottom: 2px solid var(--blue) !important;
}

/* --- Content Cards --- */
.col-card {
    background: var(--white);
    padding: 2rem;
    border-radius: 16px;
    border: 1px solid var(--border);
    box-shadow: var(--card-shadow);
    margin-top: 1rem;
}

/* --- Inputs & Buttons --- */
div.stButton > button {
    width: 100% !important;
    background: var(--blue) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}
div.stButton > button:hover {
    background: var(--blue-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,104,177,0.3);
}

/* Download Button Specific */
div.stDownloadButton > button {
    background: #10B981 !important; /* Vert moderne */
}
div.stDownloadButton > button:hover {
    background: #059669 !important;
    box-shadow: 0 4px 12px rgba(16,185,129,0.3);
}

/* File Uploader Customization */
[data-testid="stFileUploader"] section {
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    background: var(--bg-app) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: var(--blue) !important;
}

/* Titles */
.section-label {
    color: var(--ink);
    font-size: 0.9rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Preview Wrap */
.preview-wrap {
    background: #1E293B; /* Dark background for preview contrast */
    padding: 10px;
    border-radius: 12px;
    box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1);
}
.preview-header {
    color: #94A3B8;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-bottom: 8px;
    text-align: center;
}

/* Status Messages */
.status-box {
    padding: 1rem;
    border-radius: 8px;
    font-size: 0.85rem;
    margin: 1rem 0;
}
.status-idle { background: var(--blue-soft); color: var(--blue); border: 1px solid #d0e8ff; }

</style>
""", unsafe_allow_html=True)

# --- Header ---
import base64 as _b64h
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">🚀 Support : lulu@support.com</span>
</div>
""", unsafe_allow_html=True)

# (Garder toutes tes fonctions de calcul intactes ici...)
# ... compute_xy, composite_logo, get_video_info, etc. ...

# --- Logic Streamlit ---
tab_v, tab_p, tab_s = st.tabs([
    "🎥 Watermark Vidéo", "📸 Watermark Photo", "🖼️ Capture d'écran"
])

with tab_v:
    # On encapsule dans des colonnes Streamlit mais on applique notre style "Card" via Markdown
    col_ctrl, col_prev = st.columns([4, 6], gap="large")

    with col_ctrl:
        st.markdown('<div class="col-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">📁 Source de la vidéo</p>', unsafe_allow_html=True)
        video_file = st.file_uploader(
            "Upload", type=["mp4", "mov", "avi"], key="vu", label_visibility="collapsed"
        )
        
        if video_file:
            # Code logique existant...
            st.markdown('<p class="section-label" style="margin-top:1.5rem">⚙️ Configuration</p>', unsafe_allow_html=True)
            # Tes widgets Streamlit (selectbox, etc.)
            
        else:
            st.markdown('<div class="status-box status-idle">En attente d\'un fichier vidéo pour commencer le traitement.</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_prev:
        st.markdown('<div class="col-card">', unsafe_allow_html=True)
        st.markdown('<p class="section-label">👁️ Aperçu du rendu</p>', unsafe_allow_html=True)
        
        if video_file:
            st.markdown('<div class="preview-wrap"><div class="preview-header">Live Preview</div>', unsafe_allow_html=True)
            # Affichage de l'image
            # st.image(...) 
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:300px; display:flex; align-items:center; justify-content:center; border:2px dashed #E2E8F0; border-radius:12px; color:#94A3B8;">
                L'aperçu s'affichera ici après l'upload
            </div>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# (Répéter la structure div class="col-card" pour les autres onglets)
