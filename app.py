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

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
  --blue: #0068B1;
  --blue-600: #005A9A;
  --blue-700: #004B80;
  --blue-soft: #EAF4FD;
  --blue-soft-2: #F4F9FE;
  --bg: #F7F9FC;
  --panel: rgba(255,255,255,.86);
  --white: #FFFFFF;
  --ink: #0F172A;
  --sub: #475569;
  --muted: #94A3B8;
  --border: rgba(148,163,184,.22);
  --border-strong: rgba(0,104,177,.18);
  --shadow-sm: 0 1px 2px rgba(15, 23, 42, .04);
  --shadow-md: 0 10px 30px rgba(15, 23, 42, .08);
  --shadow-blue: 0 12px 30px rgba(0,104,177,.14);
  --radius-sm: 10px;
  --radius-md: 14px;
  --radius-lg: 18px;
  --header-h: 72px;
  --footer-h: 52px;
  --panel-pad: 1.25rem;
}

*, *::before, *::after { box-sizing: border-box; }

html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background:
    radial-gradient(circle at top left, rgba(0,104,177,.08), transparent 32%),
    linear-gradient(180deg, #ffffff 0%, var(--bg) 100%) !important;
  color: var(--ink) !important;
  font-family: 'Inter', sans-serif !important;
  overflow-x: hidden !important;
}

.block-container {
  padding: 0 2.25rem 2rem !important;
  max-width: 100% !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* Header */
.site-header {
  height: var(--header-h);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  border-bottom: 1px solid var(--border);
  background: rgba(255,255,255,.72);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  margin-bottom: 0.2rem;
}
.site-header img { height: 40px; width: auto; display: block; }
.site-header-right {
  font-size: 0.8rem;
  color: var(--sub);
  background: var(--blue-soft-2);
  border: 1px solid var(--border);
  padding: 0.55rem 0.85rem;
  border-radius: 999px;
}

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 0.35rem !important;
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  padding-bottom: 0.5rem !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: 1px solid transparent !important;
  border-radius: 999px !important;
  color: var(--muted) !important;
  font-size: 0.88rem !important;
  font-weight: 600 !important;
  padding: 0.6rem 1rem !important;
  transition: all .15s ease !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue-700) !important;
  background: linear-gradient(180deg, #ffffff 0%, var(--blue-soft) 100%) !important;
  border-color: var(--border-strong) !important;
  box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover {
  color: var(--blue-600) !important;
  background: rgba(0,104,177,.04) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding: 0 !important; }

/* Layout */
[data-testid="column"] { padding-top: 0 !important; }
.col-controls {
  padding-top: var(--panel-pad);
  padding-right: 1.8rem;
  border-right: 1px solid var(--border);
}
.col-preview {
  padding-top: var(--panel-pad);
  padding-left: 1.8rem;
}

/* Typography */
.section-label,
.section-label-mt {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--muted);
  letter-spacing: 0.11em;
  text-transform: uppercase;
  margin-bottom: 0.65rem;
}
.section-label-mt { margin-top: 1.1rem; }

/* Cards / specs */
.specs-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  background: linear-gradient(180deg, #fff 0%, var(--blue-soft-2) 100%);
  box-shadow: var(--shadow-sm);
  margin-bottom: 1.15rem;
}
.spec-cell {
  padding: 0.85rem 0.95rem;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.spec-cell:last-child { border-right: none; }
.spec-k {
  font-size: 0.62rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.spec-v {
  font-size: 0.92rem;
  font-weight: 700;
  color: var(--ink);
}

/* File uploader */
[data-testid="stFileUploader"] {
  background: transparent !important;
  margin-bottom: 1.15rem !important;
}
[data-testid="stFileUploader"] section {
  background: linear-gradient(180deg, #fff 0%, var(--blue-soft-2) 100%) !important;
  border: 1px solid var(--border) !important;
  border-radius: 16px !important;
  padding: 1.15rem 1rem !important;
  box-shadow: var(--shadow-sm) !important;
  transition: all .18s ease !important;
}
[data-testid="stFileUploader"] section:hover,
[data-testid="stFileUploader"] section:focus-within {
  border-color: rgba(0,104,177,.38) !important;
  box-shadow: var(--shadow-blue) !important;
  transform: translateY(-1px);
}
[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.84rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
  color: var(--ink) !important;
  font-weight: 700 !important;
}
[data-testid="stFileUploader"] button {
  background: linear-gradient(180deg, #ffffff 0%, #f7fbff 100%) !important;
  border: 1px solid rgba(0,104,177,.18) !important;
  color: var(--blue-700) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.8rem !important;
  font-weight: 600 !important;
  padding: 0.38rem 1rem !important;
  border-radius: 999px !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stFileUploader"] button:hover {
  border-color: rgba(0,104,177,.35) !important;
  background: var(--blue-soft) !important;
}
[data-testid="stFileUploaderFileName"] {
  color: var(--ink) !important;
  font-weight: 600 !important;
  font-size: 0.84rem !important;
}
[data-testid="stFileUploaderDeleteBtn"] button {
  background: transparent !important;
  border: none !important;
  color: var(--muted) !important;
  box-shadow: none !important;
}
[data-testid="stFileUploaderDeleteBtn"] button:hover {
  color: #b91c1c !important;
  background: rgba(185,28,28,.08) !important;
}

/* Buttons */
div.stButton > button,
div[data-testid="stDownloadButton"] > button {
  width: 100% !important;
  height: 42px !important;
  border-radius: 999px !important;
  border: none !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.88rem !important;
  font-weight: 700 !important;
  letter-spacing: 0.01em !important;
  transition: transform .12s ease, box-shadow .12s ease, background .12s ease !important;
}

div.stButton > button {
  background: linear-gradient(180deg, var(--blue) 0%, var(--blue-600) 100%) !important;
  color: white !important;
  box-shadow: var(--shadow-blue) !important;
}
div.stButton > button:hover {
  transform: translateY(-1px) !important;
  background: linear-gradient(180deg, var(--blue-600) 0%, var(--blue-700) 100%) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }
div.stButton > button:disabled {
  background: #e2e8f0 !important;
  color: #94a3b8 !important;
  box-shadow: none !important;
}

div.stDownloadButton > button,
div[data-testid="stDownloadButton"] > button {
  background: linear-gradient(180deg, #16a34a 0%, #15803d 100%) !important;
  color: white !important;
  box-shadow: 0 10px 24px rgba(22,163,74,.18) !important;
}
div.stDownloadButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  transform: translateY(-1px) !important;
  background: linear-gradient(180deg, #15803d 0%, #166534 100%) !important;
}

/* Inputs */
[data-testid="stSelectbox"] [data-baseweb="select"] > div,
[data-testid="stNumberInput"] [data-baseweb="base-input"] {
  border-radius: 12px !important;
  border-color: var(--border) !important;
  box-shadow: none !important;
  transition: border-color .14s ease, box-shadow .14s ease !important;
  background: white !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover,
[data-testid="stNumberInput"] [data-baseweb="base-input"]:hover {
  border-color: rgba(0,104,177,.35) !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within,
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
  border-color: rgba(0,104,177,.55) !important;
  box-shadow: 0 0 0 4px rgba(0,104,177,.08) !important;
}
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
  border-radius: 8px !important;
  border: 1px solid var(--border) !important;
}
[data-testid="stNumberInputStepDown"]:hover,
[data-testid="stNumberInputStepUp"]:hover {
  border-color: rgba(0,104,177,.35) !important;
  background: var(--blue-soft) !important;
}

/* Preview */
.preview-wrap {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: #0b1220;
  box-shadow: var(--shadow-md);
}
.preview-bar {
  padding: 0.55rem 0.9rem;
  border-bottom: 1px solid rgba(255,255,255,.08);
  background: rgba(255,255,255,.04);
  font-size: 0.66rem;
  color: rgba(255,255,255,.72);
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}
.preview-wrap [data-testid="stImage"],
.preview-wrap [data-testid="stImage"] > div,
.preview-wrap [data-testid="stImage"] figure {
  margin: 0 !important;
  padding: 0 !important;
  line-height: 0 !important;
  width: 100% !important;
}
.preview-wrap [data-testid="stImage"] img {
  width: 100% !important;
  height: auto !important;
  display: block !important;
  object-fit: contain !important;
}

.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.75rem;
  min-height: 300px;
  border: 1px dashed rgba(0,104,177,.22);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(180deg, rgba(255,255,255,.95) 0%, rgba(244,249,254,.98) 100%);
  color: var(--muted);
  font-size: 0.86rem;
  text-align: center;
  box-shadow: var(--shadow-sm);
}
.preview-placeholder svg { opacity: 0.28; }

/* Status */
.status {
  font-size: 0.82rem;
  padding: 0.65rem 0;
  margin: 0.5rem 0;
  line-height: 1.5;
  color: var(--sub);
}
.status-idle { color: var(--muted); }
.status-ok { color: #166534; }
.status-err { color: #b91c1c; }

/* Footer */
.site-footer {
  height: var(--footer-h);
  margin-top: 1.5rem;
  padding-top: 0.9rem;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.74rem;
  color: var(--muted);
}
.footer-name { color: var(--sub); font-weight: 700; }

/* Misc */
div[data-testid="stSpinner"] p {
  font-size: 0.82rem !important;
  color: var(--sub) !important;
  font-family: 'Inter', sans-serif !important;
}

.encoding-wrap { display: flex; align-items: center; gap: 0.7rem; padding: 0.5rem 0; margin: 0.5rem 0; }
.encoding-ring {
  width: 16px; height: 16px; border: 2px solid rgba(0,104,177,.18);
  border-top-color: var(--blue); border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.fake-progress-wrap { margin: 0.6rem 0 0.4rem; }
.fake-progress-track { height: 4px; background: rgba(148,163,184,.24); border-radius: 99px; overflow: hidden; }
.fake-progress-bar {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--blue-soft), var(--blue), var(--blue-soft));
  background-size: 200% 100%;
  animation: indeterminate 1.4s ease-in-out infinite;
}
@keyframes indeterminate { 0% { background-position: 200% center; } 100% { background-position: -200% center; } }

.photo-batch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.55rem 0.75rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  margin-bottom: 0.45rem;
  background: rgba(255,255,255,.82);
  font-size: 0.82rem;
  color: var(--ink);
  box-shadow: var(--shadow-sm);
}
.photo-batch-name { font-weight: 600; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim { font-size: 0.7rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

@media (max-width: 1100px) {
  .block-container { padding: 0 1rem 1rem !important; }
  .specs-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .col-controls { border-right: none; padding-right: 0; }
  .col-preview { padding-left: 0; margin-top: 1rem; }
}
</style>
""", unsafe_allow_html=True)

import base64 as _b64h
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()

st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">Merci pour vos retours — l’interface a été pensée pour rester simple et rapide.</span>
</div>
""", unsafe_allow_html=True)
