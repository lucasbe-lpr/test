import base64
import html as _html
import io
import json
import math
import os
import re
import shutil
import subprocess
import tempfile
import zipfile
from functools import lru_cache

import streamlit as st
import streamlit.components.v1 as components
from PIL import Image, ImageOps

# ============================================================
# CONSTANTES & FICHIERS
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def _asset(name: str) -> str:
    """Cherche d'abord à côté de app.py, puis dans le dossier courant."""
    p = os.path.join(BASE_DIR, name)
    return p if os.path.exists(p) else name


LOGO_FILE = _asset("luluflix.png")
DEFAULT_WM_FILE = _asset("lpr.png")
FAVICON_FILE = _asset("favicon.png")

RESAMPLE = getattr(getattr(Image, "Resampling", Image), "LANCZOS")

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

# ============================================================
# CSS
# ============================================================
APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --blue:        #0068B1;
  --blue-dark:   #005494;
  --blue-light:  #1a85d1;
  --blue-soft:   #e8f2fb;
  --blue-line:   #cfe3f5;
  --blue-grad:   linear-gradient(135deg, #1a85d1 0%, #0068B1 55%, #005494 100%);
  --white:       #ffffff;
  --page:        #f5f7fb;
  --bg:          #f7f9fc;
  --bg-soft:     #eef2f7;
  --ink:         #0f172a;
  --sub:         #475569;
  --muted:       #74829a;
  --border:      #e2e8f0;
  --border-mid:  #cbd5e1;
  --green:       #16a34a;
  --green-dark:  #15803d;
  --red:         #dc2626;
  --red-bg:      #fef2f2;
  --radius-sm:   10px;
  --radius-md:   12px;
  --radius-lg:   18px;
  --radius-pill: 999px;
  --shadow-sm:   0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06);
  --shadow-md:   0 6px 18px rgba(15,23,42,0.07), 0 2px 4px rgba(15,23,42,0.04);
  --ring:        0 0 0 3px rgba(0,104,177,0.18);
  --header-h:    72px;
  --gutter:      2.5rem;
}

*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }

html, body,
[data-testid="stApp"],
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background: var(--page) !important;
  color: var(--ink) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden !important;
}

/* fine barre d'accent en haut de page */
[data-testid="stApp"]::before {
  content: "";
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 3px;
  background: var(--blue-grad);
  z-index: 1000;
}

.block-container {
  background: transparent !important;
  padding: 0 var(--gutter) 3rem !important;
  max-width: 1400px !important;
  margin: 0 auto !important;
}

#MainMenu, footer, header,
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

::selection { background: var(--blue-soft); color: var(--blue-dark); }

/* ---------- En-tête ---------- */
.site-header {
  min-height: var(--header-h);
  padding: 0.6rem 0;
  margin-bottom: 1.1rem;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}
.site-header img { height: 36px; width: auto; max-width: 60%; display: block; flex-shrink: 0; object-fit: contain; }
.brand-fallback { font-size: 1.35rem; font-weight: 700; color: var(--blue); letter-spacing: -0.02em; }
.version-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.45rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--blue);
  background: var(--blue-soft);
  border: 1px solid var(--blue-line);
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-pill);
  white-space: nowrap;
  letter-spacing: 0.02em;
}
.version-pill::before {
  content: "";
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--green);
  box-shadow: 0 0 0 3px rgba(22,163,74,0.18);
}

/* ---------- Onglets (contrôle segmenté) ---------- */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: var(--bg-soft) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-pill) !important;
  padding: 4px !important;
  gap: 2px !important;
  margin-bottom: 0 !important;
  width: fit-content !important;
  max-width: 100% !important;
  overflow-x: auto !important;
  flex-wrap: nowrap !important;
  scrollbar-width: none !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-radius: var(--radius-pill) !important;
  margin: 0 !important;
  color: var(--sub) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.74rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em;
  padding: 0.55rem 1.15rem !important;
  height: auto !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  transition: color 0.15s ease, background 0.15s ease, box-shadow 0.15s ease !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--ink) !important; background: rgba(255,255,255,0.55) !important; }
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue) !important;
  background: var(--white) !important;
  box-shadow: var(--shadow-sm) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.4rem !important; }

/* ---------- Colonnes & cartes ---------- */
[data-testid="stHorizontalBlock"] {
  align-items: flex-start !important;
  row-gap: 1.4rem !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  min-height: 0 !important;
  padding-top: 0 !important;
}

[class*="st-key-card-"] {
  background: var(--white) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-sm) !important;
  padding: 1.4rem 1.5rem 1.5rem !important;
}

/* ---------- Libellés ---------- */
.section-label, .section-label-mt {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--sub);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin: 0 0 0.6rem;
}
.section-label::before, .section-label-mt::before {
  content: "";
  width: 6px; height: 6px;
  border-radius: 50%;
  background: var(--blue);
  flex-shrink: 0;
}
.section-label-mt { margin-top: 1.5rem; }

[data-testid="stWidgetLabel"] p { font-size: 0.8rem !important; font-weight: 500 !important; color: var(--sub) !important; }

/* ---------- Uploader ---------- */
[data-testid="stFileUploader"] { background: transparent !important; margin-bottom: 0.4rem !important; }
[data-testid="stFileUploader"] section {
  background: var(--bg) !important;
  border: 1.5px dashed var(--border-mid) !important;
  border-radius: var(--radius-md) !important;
  padding: 1.3rem 1rem !important;
  transition: border-color 0.2s, background 0.2s, box-shadow 0.2s !important;
}
[data-testid="stFileUploader"] section:hover,
[data-testid="stFileUploader"] section:focus-within {
  border-color: var(--blue) !important;
  background: var(--blue-soft) !important;
  box-shadow: var(--ring) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.8rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span {
  color: var(--sub) !important;
  font-weight: 600 !important;
}
[data-testid="stFileUploader"] button {
  background: var(--white) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--sub) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.78rem !important;
  font-weight: 500 !important;
  padding: 0.34rem 1rem !important;
  border-radius: var(--radius-pill) !important;
  box-shadow: var(--shadow-sm) !important;
}
[data-testid="stFileUploader"] button:hover {
  border-color: var(--blue) !important;
  color: var(--blue) !important;
}
[data-testid="stFileUploaderFileName"] {
  color: var(--ink) !important;
  font-weight: 500 !important;
  font-size: 0.82rem !important;
}
[data-testid="stFileUploaderDeleteBtn"] button {
  background: transparent !important;
  border: none !important;
  color: var(--muted) !important;
  box-shadow: none !important;
  border-radius: 6px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button:hover {
  color: var(--red) !important;
  background: var(--red-bg) !important;
}

/* ---------- Fiche technique vidéo ---------- */
.specs-row {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 1px;
  background: var(--border);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin: 1.1rem 0 0.2rem;
}
.spec-cell {
  background: var(--bg);
  padding: 0.7rem 0.85rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  min-width: 0;
}
.spec-k {
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.spec-v {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.2;
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ---------- Boutons ---------- */
div.stButton > button {
  width: 100% !important;
  background: var(--blue-grad) !important;
  border: none !important;
  color: var(--white) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.86rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  padding: 0 1.4rem !important;
  height: 44px !important;
  border-radius: var(--radius-pill) !important;
  transition: filter 0.15s, transform 0.1s, box-shadow 0.15s !important;
  box-shadow: 0 1px 2px rgba(0,104,177,0.2), 0 4px 12px rgba(0,104,177,0.18) !important;
  cursor: pointer !important;
}
div.stButton > button:hover {
  filter: brightness(1.07);
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 16px rgba(0,104,177,0.28) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }
div.stButton > button:focus-visible { outline: none !important; box-shadow: var(--ring), 0 4px 12px rgba(0,104,177,0.2) !important; }
div.stButton > button:disabled {
  background: var(--border) !important;
  color: var(--muted) !important;
  box-shadow: none !important;
  cursor: default !important;
  transform: none !important;
  filter: none !important;
}

div.stDownloadButton > button,
div[data-testid="stDownloadButton"] > button {
  width: 100% !important;
  background: linear-gradient(135deg, #22b45a 0%, #16a34a 55%, #15803d 100%) !important;
  border: none !important;
  color: #fff !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.86rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  padding: 0 1.2rem !important;
  height: 44px !important;
  border-radius: var(--radius-pill) !important;
  transition: filter 0.15s, transform 0.1s, box-shadow 0.15s !important;
  box-shadow: 0 1px 2px rgba(22,163,74,0.2), 0 4px 12px rgba(22,163,74,0.18) !important;
}
div.stDownloadButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  filter: brightness(1.06);
  transform: translateY(-1px) !important;
  box-shadow: 0 6px 16px rgba(22,163,74,0.28) !important;
}
div.stDownloadButton > button:active,
div[data-testid="stDownloadButton"] > button:active { transform: translateY(0) !important; }
div.stDownloadButton > button:focus-visible,
div[data-testid="stDownloadButton"] > button:focus-visible { outline: none !important; box-shadow: 0 0 0 3px rgba(22,163,74,0.25) !important; }
div[data-testid="stDownloadButton"] button p,
div.stDownloadButton button p {
  margin: 0 !important;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

div[data-testid="stProgress"] { display: none !important; }

/* ---------- Encodage ---------- */
.encoding-box {
  margin: 0.9rem 0 0.4rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--blue-line);
  background: var(--blue-soft);
  border-radius: var(--radius-md);
}
.encoding-wrap { display: flex; align-items: center; gap: 0.7rem; margin-bottom: 0.7rem; }
.encoding-ring {
  width: 16px; height: 16px;
  border: 2px solid var(--blue-line);
  border-top-color: var(--blue);
  border-radius: 50%;
  flex-shrink: 0;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.encoding-text { font-size: 0.82rem; color: var(--blue-dark); font-weight: 600; }
.encoding-pct {
  margin-left: auto;
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--blue);
  font-variant-numeric: tabular-nums;
}
.progress-track { height: 6px; background: rgba(0,104,177,0.14); border-radius: 99px; overflow: hidden; }
.progress-fill {
  height: 100%;
  border-radius: 99px;
  background: var(--blue-grad);
  transition: width 0.45s ease;
}
.progress-fill.indeterminate { width: 40%; animation: indeterminate 1.3s ease-in-out infinite; }
@keyframes indeterminate {
  0%   { transform: translateX(-100%); }
  100% { transform: translateX(260%); }
}

/* ---------- Messages ---------- */
.status {
  display: flex;
  align-items: flex-start;
  gap: 0.65rem;
  font-size: 0.82rem;
  line-height: 1.5;
  padding: 0.8rem 0.95rem;
  margin: 0.8rem 0 0.2rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--sub);
  word-break: break-word;
}
.status-ico {
  width: 18px; height: 18px;
  border-radius: 50%;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  font-weight: 700;
  margin-top: 1px;
  background: var(--border-mid);
  color: #fff;
}
.status-ok   { color: var(--green-dark); background: #f0fdf4; border-color: #bbf7d0; font-weight: 500; }
.status-ok .status-ico { background: var(--green); }
.status-err  { color: #991b1b; background: var(--red-bg); border-color: #fecaca; font-weight: 500; }
.status-err .status-ico { background: var(--red); }
.status-idle { color: var(--sub); }
.status-idle .status-ico { background: var(--blue); }
.status code { font-size: 0.74rem; background: rgba(15,23,42,0.06); padding: 0.05rem 0.35rem; border-radius: 5px; }
.status .err-detail { display: block; margin-top: 0.35rem; font-size: 0.72rem; font-weight: 400; opacity: 0.85; font-family: ui-monospace, SFMono-Regular, Menlo, monospace; max-height: 140px; overflow: auto; }

div[data-testid="stSpinner"] p {
  font-size: 0.8rem !important;
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ---------- Champs ---------- */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] [data-baseweb="base-input"] { align-items: center !important; }
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  align-self: center !important;
  width: 28px !important; height: 28px !important;
  min-width: 28px !important; min-height: 28px !important;
  padding: 0 !important; margin: 0 2px !important;
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: 7px !important;
  color: var(--sub) !important;
  box-shadow: none !important;
  cursor: pointer !important;
}
[data-testid="stNumberInputStepDown"]:hover,
[data-testid="stNumberInputStepUp"]:hover {
  background: var(--bg) !important;
  border-color: var(--border-mid) !important;
  color: var(--ink) !important;
  box-shadow: none !important;
}
[data-testid="stNumberInputStepDown"] svg,
[data-testid="stNumberInputStepUp"] svg { width: 12px !important; height: 12px !important; display: block !important; }

[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stNumberInput"] [data-baseweb="base-input"],
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="base-input"],
[data-testid="stTextArea"] [data-baseweb="textarea"],
[data-testid="stTextArea"] [data-baseweb="base-input"] {
  border-radius: var(--radius-sm) !important;
  background: var(--white) !important;
}
[data-testid="stNumberInput"] [data-baseweb="input"],
[data-testid="stTextInput"] [data-baseweb="input"],
[data-testid="stTextArea"] [data-baseweb="textarea"] {
  border-color: var(--border-mid) !important;
  transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within,
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within,
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
[data-testid="stTextArea"] [data-baseweb="textarea"]:focus-within {
  border-color: var(--blue) !important;
  box-shadow: var(--ring) !important;
}
[data-testid="stNumberInput"] input:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus { outline: none !important; box-shadow: none !important; }

[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea,
[data-testid="stNumberInput"] input {
  font-size: 0.86rem !important;
  font-family: 'Inter', sans-serif !important;
}

[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  background: var(--white) !important;
  border-color: var(--border-mid) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.86rem !important;
  min-height: 42px;
  transition: border-color 0.15s, box-shadow 0.15s;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--blue) !important; }
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within { border-color: var(--blue) !important; box-shadow: var(--ring) !important; }
[data-baseweb="popover"] ul { font-size: 0.86rem !important; }
[data-baseweb="popover"] > div { border-radius: var(--radius-md) !important; box-shadow: var(--shadow-md) !important; }

[data-testid="stRadio"] label { font-size: 0.85rem !important; }
[data-testid="stSlider"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }
[data-testid="stSlider"] > div { padding-bottom: 0 !important; }
[data-testid="stSliderThumbValue"], [data-testid="stSlider"] [data-testid="stTickBarMin"], [data-testid="stSlider"] [data-testid="stTickBarMax"] { font-size: 0.74rem !important; }
[data-testid="stColorPicker"] { margin-bottom: 0 !important; }

/* ---------- Liste de fichiers ---------- */
.photo-batch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.6rem;
  padding: 0.55rem 0.85rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 0.4rem;
  background: var(--bg);
  font-size: 0.8rem;
  color: var(--ink);
  min-width: 0;
}
.photo-batch-item.bad { background: var(--red-bg); border-color: #fecaca; color: #991b1b; }
.photo-batch-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 0;
}
.photo-batch-dim {
  font-size: 0.72rem;
  color: var(--muted);
  flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}

/* ---------- Aperçus ---------- */
[data-testid="stImage"] img {
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-md);
}
[data-testid="stImageCaption"], [data-testid="stCaptionContainer"] {
  font-size: 0.74rem !important;
  color: var(--muted) !important;
  overflow: hidden;
  text-overflow: ellipsis;
}
[data-testid="stCustomComponentV1"] iframe,
iframe[title*="components"] {
  border-radius: var(--radius-md);
  display: block;
  width: 100%;
}

.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.9rem;
  min-height: 300px;
  border: 1.5px dashed var(--border-mid);
  border-radius: var(--radius-lg);
  background: linear-gradient(180deg, var(--bg) 0%, var(--white) 100%);
  color: var(--muted);
  font-size: 0.84rem;
  text-align: center;
  padding: 1.5rem;
  font-weight: 500;
}
.ph-icon {
  width: 64px; height: 64px;
  border-radius: 50%;
  background: var(--blue-soft);
  color: var(--blue);
  display: flex;
  align-items: center;
  justify-content: center;
}
.ph-icon svg { width: 28px; height: 28px; }

.hint {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  margin: 0.9rem 0 0;
  padding: 0.7rem 0.9rem;
  background: var(--blue-soft);
  border: 1px solid var(--blue-line);
  border-radius: var(--radius-md);
  font-size: 0.78rem;
  color: var(--blue-dark);
  line-height: 1.55;
}
.hint code { background: rgba(0,104,177,0.1); padding: 0.05rem 0.35rem; border-radius: 5px; font-size: 0.74rem; }

/* champ relais (invisible) utilisé par l'aperçu du template */
div[data-testid="stTextInput"]:has(input[aria-label="canva_offset_bridge"]) {
  position: fixed !important; top: -9999px !important; left: -9999px !important;
  width: 1px !important; height: 1px !important; min-height: 0 !important;
  overflow: hidden !important; opacity: 0 !important; margin: 0 !important; padding: 0 !important;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important; transition-duration: 0.01ms !important; }
}

/* ---------- Responsive ---------- */
@media (max-width: 1100px) {
  :root { --gutter: 2rem; }
}

/* tablette : les deux colonnes principales s'empilent */
@media (min-width: 641px) and (max-width: 900px) {
  :root { --gutter: 1.5rem; }
  [data-testid="stHorizontalBlock"] { flex-wrap: wrap !important; }
  [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    flex: 1 1 100% !important;
    min-width: 100% !important;
    width: 100% !important;
  }
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] { flex-wrap: nowrap !important; }
  [data-testid="stColumn"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
    flex: 1 1 0 !important;
    min-width: 0 !important;
    width: auto !important;
  }
}

@media (max-width: 640px) {
  :root { --header-h: 60px; --gutter: max(0.85rem, env(safe-area-inset-left)); }
  .block-container { padding: 0 var(--gutter) calc(1.5rem + env(safe-area-inset-bottom)) !important; }

  .site-header { padding: 0.4rem 0; margin-bottom: 0.9rem; }
  .site-header img { height: 28px; }
  .version-pill { font-size: 0.64rem; padding: 0.25rem 0.6rem; }

  div[data-testid="stTabs"] [data-baseweb="tab"] { font-size: 0.7rem !important; padding: 0.55rem 0.9rem !important; }
  div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1rem !important; }

  [data-testid="stHorizontalBlock"] { row-gap: 1rem !important; }
  [class*="st-key-card-"] { padding: 1.05rem 1rem 1.15rem !important; border-radius: 16px !important; }

  .specs-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }

  /* évite le zoom automatique d'iOS au focus d'un champ */
  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea,
  [data-testid="stNumberInput"] input,
  [data-testid="stSelectbox"] input,
  [data-testid="stSelectbox"] [data-baseweb="select"] > div { font-size: 16px !important; }

  div.stButton > button,
  div.stDownloadButton > button,
  div[data-testid="stDownloadButton"] > button { height: 48px !important; font-size: 0.9rem !important; }

  [data-testid="stNumberInputStepDown"],
  [data-testid="stNumberInputStepUp"] { width: 32px !important; height: 32px !important; min-width: 32px !important; min-height: 32px !important; }

  .preview-placeholder { min-height: 210px; }
  .ph-icon { width: 52px; height: 52px; }
}

@media (max-width: 380px) {
  .specs-row { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .spec-v { font-size: 0.85rem; }
}
</style>
"""
st.markdown(APP_CSS, unsafe_allow_html=True)


# ============================================================
# HELPERS UI
# ============================================================
def md_html(html: str) -> None:
    """Injecte du HTML sans risque d'interprétation Markdown (pas de lignes vides / indentations)."""
    flat = " ".join(line.strip() for line in html.strip().splitlines() if line.strip())
    st.markdown(flat, unsafe_allow_html=True)


def esc(s) -> str:
    return _html.escape(str(s), quote=True)


def label(text: str, mt: bool = False) -> None:
    md_html(f'<p class="section-label{"-mt" if mt else ""}">{text}</p>')


def spacer(rem: float = 1.0) -> None:
    md_html(f'<div style="height:{rem}rem"></div>')


def show_status(kind: str, text: str, detail: str = "") -> None:
    icon = {"ok": "✓", "err": "!", "idle": "i"}.get(kind, "i")
    det = ""
    if detail:
        det = '<span class="err-detail">' + esc(detail[-700:]).replace("\n", "<br>") + "</span>"
    md_html(
        f'<div class="status status-{kind}"><span class="status-ico">{icon}</span>'
        f"<div>{text}{det}</div></div>"
    )


def card(parent, key: str):
    """Conteneur stylé en « carte » (nécessite une version récente de Streamlit pour `key`)."""
    try:
        return parent.container(key=key)
    except TypeError:
        return parent.container(border=True)


def placeholder(icon_svg: str, text: str) -> None:
    md_html(
        f'<div class="preview-placeholder"><div class="ph-icon">{icon_svg}</div><span>{text}</span></div>'
    )


def show_image(img, caption=None, stretch: bool = False) -> None:
    if not stretch:
        st.image(img, caption=caption)
        return
    try:
        st.image(img, caption=caption, width="stretch")
    except Exception:
        try:
            st.image(img, caption=caption, use_container_width=True)
        except Exception:
            st.image(img, caption=caption, use_column_width=True)


def progress_html(pct=None, text: str = "Encodage en cours…") -> str:
    if pct is None:
        fill = '<div class="progress-fill indeterminate"></div>'
        pct_txt = ""
    else:
        p = max(0, min(100, int(pct * 100)))
        fill = f'<div class="progress-fill" style="width:{p}%"></div>'
        pct_txt = f'<span class="encoding-pct">{p} %</span>'
    return (
        '<div class="encoding-box"><div class="encoding-wrap">'
        f'<div class="encoding-ring"></div><span class="encoding-text">{text}</span>{pct_txt}</div>'
        f'<div class="progress-track">{fill}</div></div>'
    )


ICON_VIDEO = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>'
ICON_IMAGE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>'
ICON_CAMERA = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"><path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/></svg>'

# ============================================================
# EN-TÊTE
# ============================================================
try:
    with open(LOGO_FILE, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()
    _logo_html = f'<img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />'
except Exception:
    _logo_html = '<span class="brand-fallback">Luluflix</span>'

md_html(
    f"""
<div class="site-header">
  {_logo_html}
  <span class="version-pill">version 2.1</span>
</div>
"""
)

if not os.path.exists(DEFAULT_WM_FILE):
    st.error(f"Le fichier de watermark « {os.path.basename(DEFAULT_WM_FILE)} » est introuvable.")
    st.stop()

WM_SIG = os.path.getmtime(DEFAULT_WM_FILE)

# ============================================================
# TRAITEMENT IMAGE / VIDÉO
# ============================================================
PREVIEW_MAX_W = 680
PREVIEW_MAX_H = 500


class MediaError(Exception):
    """Erreur lisible côté utilisateur (ffmpeg / ffprobe / média illisible)."""


def cap_image_for_preview(img: Image.Image) -> Image.Image:
    w, h = img.size
    if w > PREVIEW_MAX_W:
        ratio = PREVIEW_MAX_W / w
        w = PREVIEW_MAX_W
        h = int(h * ratio)
    if h > PREVIEW_MAX_H:
        ratio = PREVIEW_MAX_H / h
        h = PREVIEW_MAX_H
        w = int(w * ratio)
    if (w, h) == img.size:
        return img
    return img.resize((max(1, w), max(1, h)), RESAMPLE)


def get_default_logo() -> str:
    return DEFAULT_WM_FILE


def open_image(src) -> Image.Image:
    """Ouvre une image en respectant l'orientation EXIF (photos de téléphone)."""
    img = Image.open(src)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass
    return img


POSITIONS = [
    "Haut gauche",
    "Haut centre",
    "Haut droite",
    "Milieu gauche",
    "Centre",
    "Milieu droite",
    "Bas gauche",
    "Bas centre",
    "Bas droite",
    "Coordonnées personnalisées",
]
DEFAULT_POSITION = "Haut droite"


def compute_xy(
    position: str,
    W: int,
    H: int,
    logo_w: int,
    logo_h: int,
    custom_x: int = 0,
    custom_y: int = 0,
    margin_pct: float = 0.05,
) -> tuple:
    mx = int(W * margin_pct)
    my = int(H * margin_pct)
    if position == "Haut gauche":
        return mx, my
    if position == "Haut centre":
        return (W - logo_w) // 2, my
    if position == "Haut droite":
        return W - logo_w - mx, my
    if position == "Milieu gauche":
        return mx, (H - logo_h) // 2
    if position == "Centre":
        return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite":
        return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche":
        return mx, H - logo_h - my
    if position == "Bas centre":
        return (W - logo_w) // 2, H - logo_h - my
    if position == "Bas droite":
        return W - logo_w - mx, H - logo_h - my
    return custom_x, custom_y


@lru_cache(maxsize=16)
def load_scaled_logo(path: str, logo_w: int, mtime: float) -> Image.Image:
    logo = Image.open(path).convert("RGBA")
    ratio = logo_w / logo.width
    logo_h = max(1, int(logo.height * ratio))
    return logo.resize((logo_w, logo_h), RESAMPLE)


def composite_logo(
    base: Image.Image,
    logo_path: str,
    position: str = DEFAULT_POSITION,
    custom_x: int = 0,
    custom_y: int = 0,
    force_w: int = None,
    force_h: int = None,
) -> Image.Image:
    W = force_w if force_w else base.size[0]
    H = force_h if force_h else base.size[1]
    logo_w = max(1, int(math.sqrt(W**2 + H**2) * 0.1307))
    logo = load_scaled_logo(logo_path, logo_w, os.path.getmtime(logo_path))
    x, y = compute_xy(position, W, H, logo_w, logo.height, custom_x, custom_y)
    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer)


def _to_float(v, default: float = 0.0) -> float:
    try:
        f = float(v)
        return f if math.isfinite(f) else default
    except (TypeError, ValueError):
        return default


def get_video_info(path: str) -> dict:
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration,tags=rotate",
        "-show_entries", "stream_side_data=rotation",
        "-show_entries", "format=duration",
        "-of", "json", path,
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
    except FileNotFoundError:
        raise MediaError("ffprobe est introuvable : vérifiez que ffmpeg est bien installé (packages.txt).")
    except subprocess.TimeoutExpired:
        raise MediaError("Lecture des informations de la vidéo trop longue (timeout).")

    try:
        data = json.loads(result.stdout or "{}")
    except ValueError:
        data = {}
    streams = data.get("streams") or []
    if not streams:
        raise MediaError("Aucun flux vidéo lisible dans ce fichier.")
    stream = streams[0]

    w = int(_to_float(stream.get("width")))
    h = int(_to_float(stream.get("height")))
    if w <= 0 or h <= 0:
        raise MediaError("Impossible de lire les dimensions de la vidéo.")

    dur = _to_float((data.get("format") or {}).get("duration"))
    if dur <= 0:
        dur = _to_float(stream.get("duration"))

    fps_raw = stream.get("r_frame_rate", "25/1")
    try:
        num, den = fps_raw.split("/")
        fps = round(float(num) / float(den), 2)
    except Exception:
        fps = 25.0

    rotate = 0
    for sd in stream.get("side_data_list", []) or []:
        if "rotation" in sd:
            rotate = int(_to_float(sd["rotation"]))
            break
    if rotate == 0:
        rotate = int(_to_float((stream.get("tags") or {}).get("rotate", 0)))
    if abs(rotate) in (90, 270):
        w, h = h, w
    return {"width": w, "height": h, "duration": dur, "fps": fps, "rotate": rotate}


def fmt_time(secs: float) -> str:
    secs = max(0, int(secs))
    h, rem = divmod(secs, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def _ffmpeg_png(args: list) -> Image.Image:
    cmd = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", *args,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, timeout=180)
    except FileNotFoundError:
        raise MediaError("ffmpeg est introuvable : vérifiez qu'il est bien installé (packages.txt).")
    except subprocess.TimeoutExpired:
        raise MediaError("L'extraction de l'image a pris trop de temps (timeout).")
    if not result.stdout:
        raise MediaError("Impossible d'extraire une image à cet endroit de la vidéo.")
    try:
        return Image.open(io.BytesIO(result.stdout)).convert("RGB")
    except Exception:
        raise MediaError("L'image extraite de la vidéo est illisible.")


def extract_frame(video_path: str, timecode: float) -> Image.Image:
    return _ffmpeg_png(["-ss", str(timecode), "-i", video_path])


def make_thumbnail(
    video_path: str,
    logo_path: str,
    info: dict,
    position: str = DEFAULT_POSITION,
    custom_x: int = 0,
    custom_y: int = 0,
) -> Image.Image:
    frame = _ffmpeg_png(["-i", video_path]).convert("RGBA")
    return composite_logo(
        frame, logo_path,
        position=position,
        custom_x=custom_x,
        custom_y=custom_y,
        force_w=info["width"],
        force_h=info["height"],
    ).convert("RGB")


QUALITY_PRESETS = {
    "Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)": {"crf": "12", "preset": "slow"},
    "Sans perte (CRF 0)": {"crf": "0", "preset": "ultrafast"},
}


def _run_ffmpeg(cmd: list, total: float, progress_cb=None):
    """Lance ffmpeg ; stderr est écrit dans un fichier temporaire (évite tout blocage de pipe)."""
    with tempfile.TemporaryFile(mode="w+", encoding="utf-8", errors="replace") as err:
        try:
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=err, text=True)
        except FileNotFoundError:
            raise MediaError("ffmpeg est introuvable : vérifiez qu'il est bien installé (packages.txt).")
        for line in proc.stdout:
            line = line.strip()
            if line.startswith(("out_time_us=", "out_time_ms=")):
                try:
                    us = int(line.split("=", 1)[1])
                    if total > 0 and progress_cb:
                        progress_cb(max(0.0, min(us / 1_000_000 / total, 1.0)))
                except ValueError:
                    pass
        proc.wait()
        err.seek(0)
        return proc.returncode, err.read()


def render_video(
    video_path: str,
    logo_path: str,
    output_path: str,
    info: dict,
    position: str = DEFAULT_POSITION,
    custom_x: int = 0,
    custom_y: int = 0,
    quality_key: str = "Standard (CRF 18 — recommandé)",
    progress_cb=None,
):
    W, H = info["width"], info["height"]
    logo_w = max(1, int(math.sqrt(W**2 + H**2) * 0.1307))
    logo_scaled = load_scaled_logo(logo_path, logo_w, os.path.getmtime(logo_path))
    x, y = compute_xy(position, W, H, logo_w, logo_scaled.height, custom_x, custom_y)

    work_dir = tempfile.mkdtemp(prefix="luluflix_wm_")
    try:
        tmp_logo_path = os.path.join(work_dir, "wm_prescaled.png")
        logo_scaled.save(tmp_logo_path, format="PNG")

        filter_complex = f"[0:v][1:v]overlay={x}:{y}"
        if W % 2 or H % 2:
            # libx264 / yuv420p exigent des dimensions paires
            filter_complex += f",pad={W + (W % 2)}:{H + (H % 2)}"

        q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])

        def build(audio_args: list) -> list:
            return [
                "ffmpeg", "-hide_banner", "-loglevel", "error", "-nostats", "-y",
                "-i", video_path,
                "-i", tmp_logo_path,
                "-filter_complex", filter_complex,
                "-c:v", "libx264",
                "-crf", q["crf"],
                "-preset", q["preset"],
                "-pix_fmt", "yuv420p",
                *audio_args,
                "-movflags", "+faststart",
                "-progress", "pipe:1",
                output_path,
            ]

        total = info["duration"]
        rc, err = _run_ffmpeg(build(["-c:a", "copy"]), total, progress_cb)
        if rc != 0:
            # certains conteneurs (avi, webm…) n'acceptent pas la copie audio vers mp4
            if progress_cb:
                progress_cb(0.0)
            rc, err2 = _run_ffmpeg(build(["-c:a", "aac", "-b:a", "192k"]), total, progress_cb)
            if rc != 0:
                raise RuntimeError((err2 or err or "Erreur ffmpeg inconnue.").strip())
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def stage_upload(uploaded, slot: str):
    """Écrit l'upload sur disque UNE seule fois (pas à chaque rerun) et mémorise ses infos."""
    sig = (uploaded.name, uploaded.size, getattr(uploaded, "file_id", None))
    key = f"_stage_{slot}"
    cur = st.session_state.get(key)
    if cur and cur["sig"] == sig and os.path.exists(cur["path"]):
        return cur["path"], cur["info"]
    if cur:
        shutil.rmtree(cur["dir"], ignore_errors=True)
        st.session_state[key] = None
    d = tempfile.mkdtemp(prefix="luluflix_")
    path = os.path.join(d, "src" + os.path.splitext(uploaded.name)[1])
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    try:
        info = get_video_info(path)
    except MediaError:
        shutil.rmtree(d, ignore_errors=True)
        raise
    st.session_state[key] = {"sig": sig, "dir": d, "path": path, "info": info}
    return path, info


def specs_html(nfo: dict) -> str:
    cells = [
        ("Largeur", f'{nfo["width"]} px'),
        ("Hauteur", f'{nfo["height"]} px'),
        ("Durée", fmt_time(nfo["duration"])),
        ("FPS", f'{nfo["fps"]:g}'),
    ]
    inner = "".join(
        f'<div class="spec-cell"><span class="spec-k">{k}</span><span class="spec-v">{esc(v)}</span></div>'
        for k, v in cells
    )
    return f'<div class="specs-row">{inner}</div>'


@st.cache_data(show_spinner=False, max_entries=128)
def image_size(data: bytes):
    img = Image.open(io.BytesIO(data))
    w, h = img.size
    try:
        orient = img.getexif().get(0x0112, 1)
    except Exception:
        orient = 1
    if orient in (5, 6, 7, 8):
        w, h = h, w
    return w, h


@st.cache_data(show_spinner=False, max_entries=24, ttl=1800)
def process_photo(data: bytes, name: str, position: str, custom_x: int, custom_y: int, wm_sig: float):
    base = open_image(io.BytesIO(data))
    result = composite_logo(base, DEFAULT_WM_FILE, position=position, custom_x=custom_x, custom_y=custom_y)
    stem, ext = os.path.splitext(name)
    buf = io.BytesIO()
    if ext.lower() == ".png":
        result.save(buf, format="PNG")
        out_name, mime = stem + "_wm.png", "image/png"
    else:
        result.convert("RGB").save(buf, format="JPEG", quality=100, subsampling=0)
        out_name, mime = stem + "_wm.jpg", "image/jpeg"
    preview = cap_image_for_preview(result.convert("RGB"))
    return buf.getvalue(), out_name, mime, preview


@st.cache_data(show_spinner=False, max_entries=16)
def cached_frame(path: str, timecode: float, sig: tuple):
    frame = extract_frame(path, timecode)
    buf = io.BytesIO()
    frame.save(buf, format="PNG")
    return buf.getvalue(), cap_image_for_preview(frame)


@st.cache_data(show_spinner=False, max_entries=4)
def prepare_canvas_bg(data: bytes, ext: str):
    """Prépare l'arrière-plan du template : allège les très grosses photos pour l'aperçu."""
    mime = "image/png" if ext == "png" else ("image/webp" if ext == "webp" else "image/jpeg")
    if len(data) > 3_000_000:
        try:
            img = open_image(io.BytesIO(data))
            img.thumbnail((4000, 4000), RESAMPLE)
            has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
            buf = io.BytesIO()
            if has_alpha:
                img.convert("RGBA").save(buf, format="PNG")
                mime = "image/png"
            else:
                img.convert("RGB").save(buf, format="JPEG", quality=90)
                mime = "image/jpeg"
            return base64.b64encode(buf.getvalue()).decode(), mime
        except Exception:
            pass
    return base64.b64encode(data).decode(), mime


def watermark_options_ui(key_prefix: str) -> dict:
    label("Watermark", mt=True)
    position = st.selectbox(
        "Position",
        POSITIONS,
        index=POSITIONS.index(DEFAULT_POSITION),
        key=f"{key_prefix}_pos",
    )
    custom_x, custom_y = 0, 0
    if position == "Coordonnées personnalisées":
        col_x, col_y = st.columns(2)
        with col_x:
            custom_x = st.number_input(
                "X (px depuis gauche)", min_value=0, value=0, step=1,
                key=f"{key_prefix}_cx",
            )
        with col_y:
            custom_y = st.number_input(
                "Y (px depuis haut)", min_value=0, value=0, step=1,
                key=f"{key_prefix}_cy",
            )
    return {"position": position, "custom_x": int(custom_x), "custom_y": int(custom_y)}


# ============================================================
# TEMPLATE HTML/JS DE L'APERÇU « TEMPLATE »
# (chaîne brute + jetons __NOM__ : pas d'accolades à doubler)
# ============================================================
CANVAS_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  html,body{margin:0;padding:0;background:#f1f5f9;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;}
  body{padding:12px 0 14px;overflow:hidden;}
  #app{display:flex;flex-direction:column;align-items:center;gap:14px;}
  #canvasWrap{box-shadow:0 6px 28px rgba(15,23,42,0.22);border-radius:6px;overflow:hidden;line-height:0;}
  canvas{display:block;touch-action:none;}
  #dl{appearance:none;-webkit-appearance:none;border:0;cursor:pointer;height:42px;padding:0 26px;border-radius:999px;
      background:linear-gradient(135deg,#1a85d1 0%,#0068B1 55%,#005494 100%);color:#fff;font:600 14px/1 inherit;font-family:inherit;
      box-shadow:0 1px 2px rgba(0,104,177,.25),0 4px 12px rgba(0,104,177,.22);transition:filter .15s,transform .1s;}
  #dl:hover{filter:brightness(1.07);transform:translateY(-1px);}
  #dl:active{transform:translateY(0);}
</style>
</head>
<body>
<div id="app">
  <div id="canvasWrap"><canvas id="c"></canvas></div>
  <button id="dl" type="button">↓&nbsp; Télécharger le visuel</button>
</div>
<script>
const CANVAS_W = __CANVAS_W__;
const CANVAS_H = __CANVAS_H__;
const BG_B64   = __BG_B64__;
const BG_MIME  = __BG_MIME__;
const WM_B64   = __WM_B64__;
const WM_MIME  = __WM_MIME__;
const TITLE    = __TITLE__;
const SURTITRE = __SURTITRE__;
const Y_PCT    = __Y_PCT__ / 100;
const X_PCT    = 50 / 100;
const IMG_ZOOM = __IMG_ZOOM__ / 100;
const BLOCK_COLOR = __BLOCK_COLOR__;
const TEXT_COLOR  = __TEXT_COLOR__;
const SUR_BG      = __SUR_BG__;
const SUR_COLOR   = __SUR_COLOR__;
const WM_SIZE_PCT = 13 / 100;
const WM_OPAC     = 1.0;
const WM_POS      = __WM_POS__;
const WM_CX       = __WM_CX__;
const WM_CY       = __WM_CY__;
const MARGIN_R    = 0.04;
const INIT_OFF_X  = __INIT_OFF_X__;
const INIT_OFF_Y  = __INIT_OFF_Y__;
const MAX_H       = __MAX_H__;

const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');
canvas.width  = CANVAS_W;
canvas.height = CANVAS_H;

let UI_ZOOM = 1;
let bgImg = null, wmImg = null;
let overlay = null;
let bgOffX = INIT_OFF_X, bgOffY = INIT_OFF_Y;
let isDragging = false, dragSX = 0, dragSY = 0, dragBX = 0, dragBY = 0;

/* ---------- Mise à l'échelle responsive de l'aperçu ---------- */
function fitFrame() {
  try {
    const fe = window.frameElement;
    const app = document.getElementById('app');
    if (fe && app) fe.style.height = Math.ceil(app.getBoundingClientRect().height + 28) + 'px';
  } catch (e) {}
}
function layout() {
  const maxW = Math.max(160, Math.min(window.innerWidth - 24, 520));
  UI_ZOOM = Math.min(MAX_H / CANVAS_H, maxW / CANVAS_W);
  canvas.style.width  = Math.round(CANVAS_W * UI_ZOOM) + 'px';
  canvas.style.height = Math.round(CANVAS_H * UI_ZOOM) + 'px';
  fitFrame();
}
layout();
window.addEventListener('resize', layout);

/* ---------- Géométrie ---------- */
function clampOffset() {
  if (!bgImg || !bgImg.naturalWidth) return;
  const scaleX = CANVAS_W / bgImg.naturalWidth;
  const scaleY = CANVAS_H / bgImg.naturalHeight;
  const base   = Math.max(scaleX, scaleY) * IMG_ZOOM;
  const dw = bgImg.naturalWidth  * base;
  const dh = bgImg.naturalHeight * base;
  const maxOffX = dw / 2 - CANVAS_W / 2;
  const maxOffY = dh / 2 - CANVAS_H / 2;
  bgOffX = Math.max(-maxOffX, Math.min(maxOffX, bgOffX));
  bgOffY = Math.max(-maxOffY, Math.min(maxOffY, bgOffY));
}

function roundRect(c, x, y, w, h, r, fill) {
  c.beginPath();
  c.moveTo(x+r,y); c.lineTo(x+w-r,y); c.arcTo(x+w,y,x+w,y+r,r);
  c.lineTo(x+w,y+h-r); c.arcTo(x+w,y+h,x+w-r,y+h,r);
  c.lineTo(x+r,y+h); c.arcTo(x,y+h,x,y+h-r,r);
  c.lineTo(x,y+r); c.arcTo(x,y,x+r,y,r);
  c.closePath(); c.fillStyle=fill; c.fill();
}

function hexToRgb(hex) {
  return [parseInt(hex.slice(1,3),16), parseInt(hex.slice(3,5),16), parseInt(hex.slice(5,7),16)];
}

/* ---------- Calque texte + watermark (calculé une seule fois) ---------- */
function buildOverlay() {
  const ov = document.createElement('canvas');
  ov.width = CANVAS_W; ov.height = CANVAS_H;
  const oc = ov.getContext('2d');

  const fs     = Math.round(CANVAS_W * 0.056);
  const fsSur  = Math.round(CANVAS_W * 0.043);
  const pad    = Math.round(CANVAS_W * 0.017);
  const radius = Math.round(CANVAS_W * 0.019);
  const lh     = Math.round(fs * 1.25);
  const overlap= Math.round(CANVAS_W * 0.003);
  const cx     = X_PCT * CANVAS_W;
  const maxPx  = CANVAS_W * 0.96;

  const FONT_TITLE = `bold ${fs}px 'Inter','Roboto Condensed',sans-serif`;
  const FONT_SUR   = `bold ${fsSur}px 'Inter',sans-serif`;

  oc.font = FONT_TITLE;
  function wrapSegment(text, maxLen) {
    const words = text.split(' ');
    const segs = []; let cur = '';
    words.forEach(function(w) {
      const cand = cur ? cur + ' ' + w : w;
      /* règle d'origine (nb de caractères) + garde-fou : ne jamais dépasser du visuel */
      if ((cur + w).length < maxLen && oc.measureText(cand).width + pad*2 <= maxPx) { cur = cand; }
      else { if (cur) segs.push(cur); cur = w; }
    });
    if (cur) segs.push(cur);
    return segs.length ? segs : [''];
  }
  const lines = [];
  TITLE.split('\n').forEach(function(seg) {
    const wrapped = wrapSegment(seg, 34);
    for (let i = 0; i < wrapped.length; i++) lines.push(wrapped[i]);
  });

  oc.font = FONT_TITLE;
  const lineWidths = lines.map(l => oc.measureText(l).width + pad*2);

  oc.font = FONT_SUR;
  const hasSur = SURTITRE.trim().length > 0;
  const surW = oc.measureText(SURTITRE).width + pad*2;
  const surH = fsSur + Math.round(pad*0.8);

  const totalH   = lh * lines.length;
  const blockTop = CANVAS_H * Y_PCT - totalH/2;

  /* blocs arrondis, fusionnés par un flou + seuillage */
  const off = document.createElement('canvas');
  off.width = CANVAS_W; off.height = CANVAS_H;
  const octx = off.getContext('2d');
  lines.forEach((line,i) => {
    const lw = lineWidths[i];
    const lx = cx - lw/2;
    const ly = blockTop + i*lh - (i>0?overlap:0);
    roundRect(octx, lx, ly, lw, lh+overlap, radius, BLOCK_COLOR);
  });

  const off2 = document.createElement('canvas');
  off2.width = CANVAS_W; off2.height = CANVAS_H;
  const o2 = off2.getContext('2d');
  o2.filter = 'blur(10px)';
  o2.drawImage(off, 0, 0);
  o2.filter = 'none';
  const id = o2.getImageData(0, 0, CANVAS_W, CANVAS_H);
  const px = id.data;
  const [br, bg2, bb] = hexToRgb(BLOCK_COLOR);
  for (let i = 0; i < px.length; i += 4) {
    if (px[i+3] > 60) { px[i]=br; px[i+1]=bg2; px[i+2]=bb; px[i+3]=255; }
    else px[i+3] = 0;
  }
  o2.putImageData(id, 0, 0);
  oc.drawImage(off2, 0, 0);

  /* surtitre */
  if (hasSur) {
    const surX = cx - surW/2;
    const surY = blockTop - surH;
    roundRect(oc, surX, surY, surW, surH, radius, SUR_BG);
    oc.fillStyle = SUR_COLOR;
    oc.font = FONT_SUR;
    oc.textAlign = 'left'; oc.textBaseline = 'middle';
    oc.fillText(SURTITRE, surX + pad, surY + surH/2);
  }

  /* titre */
  oc.font = FONT_TITLE;
  oc.fillStyle = TEXT_COLOR;
  oc.textAlign = 'left'; oc.textBaseline = 'middle';
  lines.forEach((line,i) => {
    const lw = lineWidths[i];
    const lx = cx - lw/2;
    const ly = blockTop + i*lh - (i>0?overlap:0);
    oc.fillText(line, lx + pad, ly + lh/2);
  });

  /* watermark */
  if (wmImg && wmImg.naturalWidth) {
    const diag = Math.sqrt(CANVAS_W**2 + CANVAS_H**2);
    const wmW  = diag * WM_SIZE_PCT;
    const wmH  = (wmImg.naturalHeight / wmImg.naturalWidth) * wmW;
    const mx   = CANVAS_W * MARGIN_R, my = CANVAS_H * MARGIN_R;
    const posMap = {
      'Haut gauche':   [mx, my],
      'Haut centre':   [(CANVAS_W-wmW)/2, my],
      'Haut droite':   [CANVAS_W-wmW-mx, my],
      'Milieu gauche': [mx, (CANVAS_H-wmH)/2],
      'Centre':        [(CANVAS_W-wmW)/2, (CANVAS_H-wmH)/2],
      'Milieu droite': [CANVAS_W-wmW-mx, (CANVAS_H-wmH)/2],
      'Bas gauche':    [mx, CANVAS_H-wmH-my],
      'Bas centre':    [(CANVAS_W-wmW)/2, CANVAS_H-wmH-my],
      'Bas droite':    [CANVAS_W-wmW-mx, CANVAS_H-wmH-my],
      'Coordonnées personnalisées': [WM_CX, WM_CY],
    };
    const pos = posMap[WM_POS] || [CANVAS_W-wmW-mx, CANVAS_H-wmH-my];
    oc.globalAlpha = WM_OPAC;
    oc.drawImage(wmImg, pos[0], pos[1], wmW, wmH);
    oc.globalAlpha = 1.0;
  }
  return ov;
}

/* ---------- Rendu (léger : fond + calque) ---------- */
function render() {
  ctx.clearRect(0, 0, CANVAS_W, CANVAS_H);
  ctx.fillStyle = '#222'; ctx.fillRect(0, 0, CANVAS_W, CANVAS_H);
  if (bgImg && bgImg.naturalWidth) {
    const scaleX = CANVAS_W / bgImg.naturalWidth;
    const scaleY = CANVAS_H / bgImg.naturalHeight;
    const base   = Math.max(scaleX, scaleY) * IMG_ZOOM;
    const dw = bgImg.naturalWidth  * base;
    const dh = bgImg.naturalHeight * base;
    const dx = (CANVAS_W - dw) / 2 + bgOffX;
    const dy = (CANVAS_H - dh) / 2 + bgOffY;
    ctx.drawImage(bgImg, dx, dy, dw, dh);
  }
  if (overlay) ctx.drawImage(overlay, 0, 0);
}

/* ---------- Chargement des images ---------- */
let loaded = 0;
const toLoad = (BG_B64 ? 1 : 0) + (WM_B64 ? 1 : 0);
function ready() {
  clampOffset();
  overlay = buildOverlay();
  render();
  fitFrame();
}
function onLoad() { loaded++; if (loaded >= toLoad) ready(); }
if (!toLoad) ready();

if (BG_B64) {
  bgImg = new Image();
  bgImg.onload  = onLoad;
  bgImg.onerror = function() { bgImg = null; onLoad(); };
  bgImg.src = 'data:' + BG_MIME + ';base64,' + BG_B64;
}
if (WM_B64) {
  wmImg = new Image();
  wmImg.onload  = onLoad;
  wmImg.onerror = function() { wmImg = null; onLoad(); };
  wmImg.src = 'data:' + WM_MIME + ';base64,' + WM_B64;
}
if (bgImg) canvas.style.cursor = 'grab';

/* ---------- Glisser pour recadrer (souris + tactile) ---------- */
function startDrag(x, y) {
  if (!bgImg) return;
  isDragging = true; dragSX = x; dragSY = y; dragBX = bgOffX; dragBY = bgOffY;
  canvas.style.cursor = 'grabbing';
}
function moveDrag(x, y) {
  if (!isDragging) return;
  const s = 1 / UI_ZOOM;
  bgOffX = dragBX + (x - dragSX) * s;
  bgOffY = dragBY + (y - dragSY) * s;
  clampOffset();
  render();
}
function endDrag() {
  if (!isDragging) return;
  isDragging = false;
  canvas.style.cursor = bgImg ? 'grab' : 'default';
  syncOffsetToStreamlit();
}
canvas.addEventListener('mousedown', e => startDrag(e.clientX, e.clientY));
window.addEventListener('mousemove', e => moveDrag(e.clientX, e.clientY));
window.addEventListener('mouseup', endDrag);
canvas.addEventListener('touchstart', e => {
  if (e.touches.length !== 1) return;
  startDrag(e.touches[0].clientX, e.touches[0].clientY);
  e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  if (!isDragging || e.touches.length !== 1) return;
  moveDrag(e.touches[0].clientX, e.touches[0].clientY);
  e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchend', endDrag);
canvas.addEventListener('touchcancel', endDrag);

function syncOffsetToStreamlit() {
  try {
    const bridge = window.parent.document.querySelector('input[aria-label="canva_offset_bridge"]');
    if (!bridge) return;
    const newVal = Math.round(bgOffX) + ',' + Math.round(bgOffY);
    if (bridge.value === newVal) return;
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
    bridge.focus();
    nativeInputValueSetter.call(bridge, newVal);
    bridge.dispatchEvent(new Event('input', {bubbles: true}));
    bridge.blur();
  } catch (e) {}
}

/* ---------- Téléchargement ---------- */
document.getElementById('dl').addEventListener('click', function() {
  try {
    canvas.toBlob(function(blob) {
      if (!blob) return;
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'luluflix_visuel.png';
      document.body.appendChild(a); a.click(); a.remove();
      setTimeout(function() { URL.revokeObjectURL(url); }, 4000);
    }, 'image/png');
  } catch (e) {}
});
</script>
</body>
</html>"""


def _js(value) -> str:
    """Valeur Python -> littéral JS sûr (échappe aussi « < » pour ne jamais fermer la balise script)."""
    return json.dumps(value).replace("<", "\\u003c")


def build_canvas_html(params: dict) -> str:
    # une seule passe : le contenu injecté (titre saisi par l'utilisateur…) n'est jamais ré-interprété
    return re.sub(
        r"__([A-Z][A-Z0-9_]*)__",
        lambda m: str(params.get(m.group(1), m.group(0))),
        CANVAS_HTML_TEMPLATE,
    )


# ============================================================
# SESSION STATE
# ============================================================
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ============================================================
# ONGLETS — VID / IMG / CAPTURE / TEMPLATE
# ============================================================
tab_v, tab_p, tab_s, tab_canva = st.tabs(
    ["WATERMARK VID", "WATERMARK IMG", "CAPTURE D'ÉCRAN", "TEMPLATE"]
)

VIDEO_TYPES = ["mp4", "mov", "avi", "mkv", "webm"]

# ============================================================
# ONGLET VID
# ============================================================
with tab_v:
    col_ctrl, col_prev = st.columns([4, 6], gap="large")
    ctrl = card(col_ctrl, "card-ctrl-v")
    prev = card(col_prev, "card-prev-v")

    with ctrl:
        label("Source")
        video_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=VIDEO_TYPES,
            key="vu",
            label_visibility="collapsed",
        )

    vp, nfo = None, None
    if video_file:
        try:
            vp, nfo = stage_upload(video_file, "v")
        except MediaError as e:
            with ctrl:
                show_status("err", "Impossible de lire cette vidéo.", str(e))

    if nfo:
        lp = get_default_logo()
        vsig = (video_file.name, video_file.size)
        if st.session_state._last_video_name != vsig:
            st.session_state.thumbnail = None
            st.session_state.rendered_bytes = None
            st.session_state._last_video_name = vsig

        with ctrl:
            md_html(specs_html(nfo))

            wm_opts = watermark_options_ui("v")

            label("Qualité d'export", mt=True)
            quality_key = st.selectbox(
                "Qualité",
                list(QUALITY_PRESETS.keys()),
                key="v_quality",
                label_visibility="collapsed",
            )

            opts_sig = (wm_opts["position"], wm_opts["custom_x"], wm_opts["custom_y"])
            if st.session_state.get("_v_opts_sig") != opts_sig:
                st.session_state.thumbnail = None
                st.session_state.rendered_bytes = None
                st.session_state["_v_opts_sig"] = opts_sig

            # la qualité n'affecte pas l'aperçu, mais invalide le rendu déjà produit
            if st.session_state.get("_v_quality_sig") != quality_key:
                st.session_state.rendered_bytes = None
                st.session_state["_v_quality_sig"] = quality_key

            if st.session_state.thumbnail is None:
                try:
                    with st.spinner("Génération de l'aperçu…"):
                        st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, **wm_opts)
                except MediaError as e:
                    show_status("err", "Impossible de générer l'aperçu.", str(e))

            if st.session_state.thumbnail is not None:
                spacer(0.9)
                if not st.session_state.rendered_bytes:
                    if st.button("Générer le rendu", key="vbtn"):
                        out = os.path.join(os.path.dirname(vp), "video_ready_to_post.mp4")
                        ph = st.empty()
                        ph.markdown(progress_html(None), unsafe_allow_html=True)
                        last = {"p": -1}

                        def _on_progress(p, _ph=ph, _last=last):
                            step = int(p * 100)
                            if step != _last["p"]:
                                _last["p"] = step
                                _ph.markdown(progress_html(p), unsafe_allow_html=True)

                        ok = False
                        try:
                            render_video(vp, lp, out, nfo, quality_key=quality_key,
                                         progress_cb=_on_progress, **wm_opts)
                            with open(out, "rb") as f:
                                st.session_state.rendered_bytes = f.read()
                            ok = True
                        except Exception as e:
                            ph.empty()
                            show_status("err", "Le rendu a échoué.", str(e))
                        finally:
                            try:
                                os.remove(out)
                            except OSError:
                                pass
                        if ok:
                            ph.empty()
                            st.rerun()
                else:
                    size_mb = len(st.session_state.rendered_bytes) / 1_048_576
                    show_status("ok", f"Rendu terminé · {size_mb:.1f} Mo")
                    spacer(0.5)
                    st.download_button(
                        "↓  Télécharger la vidéo",
                        data=st.session_state.rendered_bytes,
                        file_name="video_ready_to_post.mp4",
                        mime="video/mp4",
                        key="vdl",
                    )

        with prev:
            label("Aperçu")
            if st.session_state.thumbnail is not None:
                st.image(cap_image_for_preview(st.session_state.thumbnail))
            else:
                placeholder(ICON_VIDEO, "L'aperçu apparaîtra ici")

    else:
        if not video_file:
            with ctrl:
                show_status("idle", "Déposez une vidéo pour commencer (mp4, mov, avi, mkv, webm).")
        with prev:
            label("Aperçu")
            placeholder(ICON_VIDEO, "L'aperçu apparaîtra ici")

# ============================================================
# ONGLET IMG
# ============================================================
with tab_p:
    col_ctrl_p, col_prev_p = st.columns([4, 6], gap="large")
    ctrl_p = card(col_ctrl_p, "card-ctrl-p")
    prev_p = card(col_prev_p, "card-prev-p")

    with ctrl_p:
        label("Source")
        photo_files = st.file_uploader(
            "Déposez vos images ici",
            type=["png", "jpg", "jpeg"],
            key="pu",
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

    valid = []  # (nom, octets)
    if photo_files:
        with ctrl_p:
            label("Fichiers importés", mt=True)
            for pf in photo_files:
                data_in = pf.getvalue()
                try:
                    W_tmp, H_tmp = image_size(data_in)
                except Exception:
                    md_html(
                        f'<div class="photo-batch-item bad"><span class="photo-batch-name">{esc(pf.name)}</span>'
                        '<span class="photo-batch-dim">illisible</span></div>'
                    )
                    continue
                valid.append((pf.name, data_in))
                md_html(
                    f'<div class="photo-batch-item"><span class="photo-batch-name">{esc(pf.name)}</span>'
                    f'<span class="photo-batch-dim">{W_tmp} × {H_tmp} px</span></div>'
                )

    if valid:
        with ctrl_p:
            wm_opts_p = watermark_options_ui("p")

        results = []
        try:
            with st.spinner("Application du watermark…"):
                for name, data_in in valid:
                    results.append(
                        process_photo(
                            data_in, name,
                            wm_opts_p["position"], wm_opts_p["custom_x"], wm_opts_p["custom_y"],
                            WM_SIG,
                        )
                    )
        except Exception as e:
            results = []
            with ctrl_p:
                show_status("err", "Le traitement des images a échoué.", str(e))

        with prev_p:
            label("Aperçu")
            if results:
                n_cols = 1 if len(results) == 1 else 2
                grid_cols = st.columns(n_cols)
                for idx, (_, _, _, preview_img) in enumerate(results):
                    with grid_cols[idx % n_cols]:
                        show_image(preview_img, caption=valid[idx][0], stretch=(n_cols > 1))
            else:
                placeholder(ICON_IMAGE, "L'aperçu apparaîtra ici")

        if results:
            with ctrl_p:
                if len(results) == 1:
                    data_out, fname, mime, _ = results[0]
                    spacer(0.9)
                    st.download_button(
                        "↓  Télécharger la photo",
                        data=data_out,
                        file_name=fname,
                        mime=mime,
                        key="pdl_single",
                    )
                else:
                    label("Téléchargement", mt=True)
                    for i in range(0, len(results), 2):
                        row = results[i: i + 2]
                        btn_cols = st.columns(len(row), gap="small")
                        for j, (data_out, fname, mime, _) in enumerate(row):
                            with btn_cols[j]:
                                st.download_button(
                                    f"↓  {valid[i + j][0]}",
                                    data=data_out,
                                    file_name=fname,
                                    mime=mime,
                                    key=f"pdl_{i + j}",
                                )

                    zip_buf = io.BytesIO()
                    used = set()
                    with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_STORED) as zf:
                        for data_out, fname, _, _ in results:
                            zname, n = fname, 1
                            while zname in used:  # deux fichiers de même nom ne s'écrasent pas
                                stem, ext = os.path.splitext(fname)
                                zname = f"{stem}_{n}{ext}"
                                n += 1
                            used.add(zname)
                            zf.writestr(zname, data_out)
                    spacer(0.6)
                    st.download_button(
                        "↓  Tout télécharger (.zip)",
                        data=zip_buf.getvalue(),
                        file_name="photos_watermark.zip",
                        mime="application/zip",
                        key="pdl_zip",
                    )
    else:
        if not photo_files:
            with ctrl_p:
                show_status("idle", "Déposez une ou plusieurs images (png, jpg, jpeg).")
        with prev_p:
            label("Aperçu")
            placeholder(ICON_IMAGE, "L'aperçu apparaîtra ici")

# ============================================================
# ONGLET CAPTURE D'ÉCRAN
# ============================================================
with tab_s:
    col_ctrl_s, col_prev_s = st.columns([4, 6], gap="large")
    ctrl_s = card(col_ctrl_s, "card-ctrl-s")
    prev_s = card(col_prev_s, "card-prev-s")

    with ctrl_s:
        label("Source")
        scr_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=VIDEO_TYPES,
            key="su",
            label_visibility="collapsed",
        )

    sp, nfo_s = None, None
    if scr_file:
        try:
            sp, nfo_s = stage_upload(scr_file, "s")
        except MediaError as e:
            with ctrl_s:
                show_status("err", "Impossible de lire cette vidéo.", str(e))

    if nfo_s:
        dur_s = nfo_s["duration"]
        ssig = (scr_file.name, scr_file.size)

        with ctrl_s:
            md_html(specs_html(nfo_s))

            label("Timecode (secondes)", mt=True)
            tc_max = max(float(dur_s) - 0.05, 0.1)
            timecode = st.number_input(
                "tc",
                min_value=0.0,
                max_value=float(tc_max),
                value=0.0,
                step=0.1,
                format="%.2f",
                key="cap_tc_ni",
                label_visibility="collapsed",
            )

        frame_png, frame_prev = None, None
        try:
            with st.spinner("Extraction de la frame…"):
                frame_png, frame_prev = cached_frame(sp, float(timecode), ssig)
        except MediaError as e:
            with ctrl_s:
                show_status("err", "Impossible d'extraire cette image.", str(e))

        if frame_png:
            with ctrl_s:
                spacer(0.9)
                cap_name = f"capture_{fmt_time(timecode).replace(':', '-')}-{int((timecode % 1) * 100):02d}.png"
                st.download_button(
                    "↓  Télécharger la capture",
                    data=frame_png,
                    file_name=cap_name,
                    mime="image/png",
                    key="sdl",
                )

        with prev_s:
            label("Aperçu")
            if frame_prev is not None:
                st.image(frame_prev)
            else:
                placeholder(ICON_CAMERA, "L'aperçu apparaîtra ici")

    else:
        if not scr_file:
            with ctrl_s:
                show_status("idle", "Déposez une vidéo pour en extraire une image.")
        with prev_s:
            label("Aperçu")
            placeholder(ICON_CAMERA, "L'aperçu apparaîtra ici")

# ============================================================
# ONGLET TEMPLATE (réseaux sociaux)
# ============================================================
with tab_canva:
    try:
        with open(DEFAULT_WM_FILE, "rb") as _wm_f:
            _wm_b64_canva = base64.b64encode(_wm_f.read()).decode()
    except Exception:
        _wm_b64_canva = ""
    _wm_mime_canva = "image/png"

    col_ctrl_cv, col_prev_cv = st.columns([4, 6], gap="large")
    ctrl_cv = card(col_ctrl_cv, "card-ctrl-cv")
    prev_cv = card(col_prev_cv, "card-prev-cv")

    for _k, _v in {"canva_y": 72, "canva_imgzoom": 100}.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    _fmt_map = {
        "1080×1350 — Portrait": (1080, 1350),
        "1080×1080 — Carré": (1080, 1080),
        "1080×1920 — Stories": (1080, 1920),
    }

    with ctrl_cv:
        label("Arrière-plan")
        canva_bg_file = st.file_uploader(
            "Déposez votre image ici",
            type=["png", "jpg", "jpeg", "webp"],
            key="canva_bg",
            label_visibility="collapsed",
        )

        _cr1, _cr2 = st.columns(2)
        with _cr1:
            label("Format", mt=True)
            canva_format = st.selectbox(
                "Format",
                list(_fmt_map.keys()),
                key="canva_format",
                label_visibility="collapsed",
            )
        with _cr2:
            label("Watermark", mt=True)
            wm_opts_cv = {
                "position": st.selectbox(
                    "Position watermark",
                    POSITIONS,
                    index=POSITIONS.index(DEFAULT_POSITION),
                    key="cv_pos",
                    label_visibility="collapsed",
                ),
                "custom_x": 0,
                "custom_y": 0,
            }
        if wm_opts_cv["position"] == "Coordonnées personnalisées":
            _wx, _wy = st.columns(2)
            with _wx:
                wm_opts_cv["custom_x"] = int(
                    st.number_input("X", min_value=0, value=0, step=1, key="cv_cx")
                )
            with _wy:
                wm_opts_cv["custom_y"] = int(
                    st.number_input("Y", min_value=0, value=0, step=1, key="cv_cy")
                )

        canva_w, canva_h = _fmt_map[canva_format]

        _canva_offset_sig = (canva_bg_file.name if canva_bg_file else None, canva_format)
        if st.session_state.get("_canva_offset_sig") != _canva_offset_sig:
            st.session_state["canva_offset"] = "0,0"
            st.session_state["_canva_offset_sig"] = _canva_offset_sig
        if "canva_offset" not in st.session_state:
            st.session_state["canva_offset"] = "0,0"

        # champ relais (invisible via CSS) : l'aperçu y écrit le recadrage de la photo
        canva_offset_raw = st.text_input(
            "canva_offset_bridge", key="canva_offset", label_visibility="collapsed"
        )
        try:
            _cox_s, _coy_s = canva_offset_raw.split(",")
            canva_off_x = float(_cox_s)
            canva_off_y = float(_coy_s)
        except Exception:
            canva_off_x, canva_off_y = 0.0, 0.0

        label("Surtitre", mt=True)
        canva_sur = st.text_input(
            "Surtitre",
            value="Modifier le surtitre",
            key="canva_sur",
            label_visibility="collapsed",
        )

        label("Titre principal", mt=True)
        canva_title = st.text_area(
            "Titre",
            value="Modifier le titre (il est possible de faire des retours à la ligne grâce à la touche Entrée)",
            key="canva_title",
            label_visibility="collapsed",
            height=96,
        )

        canva_block_color = "#0068B1"
        canva_text_color = "#ffffff"
        canva_sur_bg = "#ffffff"
        canva_sur_color = "#0068B1"

        label("Position du texte", mt=True)
        canva_y = st.slider(
            "Position Y",
            min_value=5,
            max_value=95,
            key="canva_y",
            label_visibility="collapsed",
        )

        if canva_bg_file:
            label("Zoom photo", mt=True)
            canva_img_zoom = st.slider(
                "Zoom photo",
                min_value=100,
                max_value=300,
                key="canva_imgzoom",
                label_visibility="collapsed",
            )
        else:
            canva_img_zoom = 100

    with prev_cv:
        label("Aperçu")

        if not canva_bg_file:
            placeholder(ICON_IMAGE, "Glissez une image pour voir l'aperçu")
        else:
            _ext = canva_bg_file.name.rsplit(".", 1)[-1].lower()
            _canva_bg_b64, _canva_bg_mime = prepare_canvas_bg(canva_bg_file.getvalue(), _ext)

            # hauteur maximale du visuel dans l'aperçu (la hauteur réelle de l'iframe
            # est ensuite ajustée côté navigateur selon la largeur disponible)
            _preview_h = min(620, int(560 * canva_h / canva_w))
            _html = build_canvas_html(
                {
                    "CANVAS_W": canva_w,
                    "CANVAS_H": canva_h,
                    "BG_B64": _js(_canva_bg_b64),
                    "BG_MIME": _js(_canva_bg_mime),
                    "WM_B64": _js(_wm_b64_canva),
                    "WM_MIME": _js(_wm_mime_canva),
                    "TITLE": _js(canva_title),
                    "SURTITRE": _js(canva_sur),
                    "Y_PCT": canva_y,
                    "IMG_ZOOM": canva_img_zoom,
                    "BLOCK_COLOR": _js(canva_block_color),
                    "TEXT_COLOR": _js(canva_text_color),
                    "SUR_BG": _js(canva_sur_bg),
                    "SUR_COLOR": _js(canva_sur_color),
                    "WM_POS": _js(wm_opts_cv["position"]),
                    "WM_CX": int(wm_opts_cv["custom_x"]),
                    "WM_CY": int(wm_opts_cv["custom_y"]),
                    "INIT_OFF_X": canva_off_x,
                    "INIT_OFF_Y": canva_off_y,
                    "MAX_H": _preview_h,
                }
            )
            components.html(_html, height=_preview_h + 90, scrolling=False)
            md_html(
                '<div class="hint"><span>Glissez (souris ou doigt) pour recadrer la photo. '
                "Téléchargez avec le bouton sous l'aperçu, ou par <b>clic droit</b> → "
                "<code>Enregistrer l'image sous…</code></span></div>"
            )
