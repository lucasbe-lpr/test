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


# FICHIERS STATIQUES — logo principal, watermark par défaut, favicon
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


# CSS GLOBAL — toute la DA est ici, ne pas toucher sans raison
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&family=Roboto+Condensed:wght@400;500;700&display=swap');

/* VARIABLES DE COULEUR ET DE TAILLE — modifier ici pour changer le thème */
:root {
  --blue:        #0068B1;
  --blue-dim:    #e8f2fb;
  --white:       #ffffff;
  --bg:          #fafafa;
  --ink:         #111111;
  --sub:         #555555;
  --muted:       #999999;
  --border:      #e4e4e4;
  --border-mid:  #d0d0d0;
  --green:       #166534;
  --red:         #991b1b;
  --red-bg:      #fff1f1;
  --header-h:    64px;
  --tabs-h:      48px;
  --footer-h:    52px;
  --panel-v-pad: 1.5rem;
}

*, *::before, *::after { box-sizing: border-box; }

/* BASE — fond blanc, typo Roboto sur tout le body Streamlit */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background: var(--white) !important;
  color: var(--ink) !important;
  font-family: 'Roboto', sans-serif !important;
  font-weight: 400 !important;
  overflow-x: hidden !important;
}

/* LAYOUT PRINCIPAL — pleine largeur, padding horizontal uniquement */
.block-container {
  background: var(--white) !important;
  padding: 0 2.5rem 2rem !important;
  max-width: 100% !important;
}

/* MASQUER les éléments natifs Streamlit non souhaités */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* HEADER SITE */
.site-header {
  height: var(--header-h);
  padding: 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.site-header img { height: 38px; width: auto; display: block; }
.site-header-right { font-size: 0.7rem; color: var(--muted); letter-spacing: 0.01em; }

/* ONGLETS — style minimaliste, soulignement bleu sur l'actif */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important; margin-bottom: 0 !important; padding: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 1.5px solid transparent !important;
  margin-bottom: -1px !important;
  color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 400 !important;
  padding: 0.6rem 1.6rem 0.6rem 0 !important;
  transition: color 0.12s !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--ink) !important;
  font-weight: 500 !important;
  border-bottom: 1.5px solid var(--blue) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--sub) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding: 0 !important; }

/* COLONNES — panneau gauche (contrôles) et panneau droit (aperçu) */
.col-controls {
  padding-top: var(--panel-v-pad);
  padding-right: 2rem;
  border-right: 1px solid var(--border);
  min-height: calc(100vh - var(--header-h) - var(--tabs-h) - var(--footer-h));
}
.col-preview {
  padding-top: var(--panel-v-pad);
  padding-left: 2rem;
}
[data-testid="column"] { padding-top: 0 !important; }

/* COLONNES STREAMLIT — aligner en haut, pas de hauteur forcée */
[data-testid="stHorizontalBlock"] { align-items: flex-start !important; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-height: 0 !important; }

/* FILE UPLOADER — zone de dépôt stylisée */
[data-testid="stFileUploader"] { background: transparent !important; margin-bottom: 1.4rem !important; }
[data-testid="stFileUploader"] section {
  background: var(--bg) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  padding: 1.2rem 1rem !important;
  transition: border-color 0.15s, background 0.15s !important;
}
[data-testid="stFileUploader"] section:hover,
[data-testid="stFileUploader"] section:focus-within {
  border-color: var(--blue) !important;
  background: var(--blue-dim) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.82rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span { color: var(--sub) !important; font-weight: 500 !important; }
[data-testid="stFileUploader"] button {
  background: var(--white) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--sub) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.78rem !important;
  padding: 0.28rem 0.9rem !important;
  border-radius: 999px !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
}
[data-testid="stFileUploader"] button:hover { border-color: var(--blue) !important; color: var(--blue) !important; }
[data-testid="stFileUploaderFileName"] { color: var(--ink) !important; font-weight: 500 !important; font-size: 0.82rem !important; }
[data-testid="stFileUploaderDeleteBtn"] button {
  background: transparent !important; border: none !important;
  color: var(--muted) !important; box-shadow: none !important; border-radius: 4px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button:hover { color: var(--red) !important; background: var(--red-bg) !important; }

/* LABELS DE SECTION — petites caps grises au-dessus de chaque bloc */
.section-label {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 0;
}
.section-label-mt {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 1.2rem;
}

/* SPECS ROW — bande d'infos techniques (dimensions, durée, fps) */
.specs-row {
  display: flex; border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden; margin-bottom: 1.2rem; background: var(--bg);
}
.spec-cell {
  flex: 1; padding: 0.6rem 0.9rem; border-right: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 0.15rem;
}
.spec-cell:last-child { border-right: none; }
.spec-k { font-size: 0.58rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); }
.spec-v { font-size: 0.88rem; font-weight: 500; color: var(--ink); line-height: 1.2; }

/* PREVIEW WRAP — cadre autour de l'aperçu vidéo/image */
.preview-wrap {
  border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; background: #f0f0f0;
  display: flex; flex-direction: column;
}
.preview-bar {
  padding: 0.35rem 0.85rem; border-bottom: 1px solid var(--border);
  background: var(--white); font-size: 0.62rem; color: var(--muted);
  font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;
  flex-shrink: 0;
}
.preview-wrap [data-testid="stImage"],
.preview-wrap [data-testid="stImage"] > div,
.preview-wrap [data-testid="stImage"] figure {
  margin: 0 !important; padding: 0 !important;
  line-height: 0 !important; width: 100% !important;
}
.preview-wrap [data-testid="stImage"] img {
  width: 100% !important; height: auto !important;
  display: block !important; object-fit: contain !important;
}

/* BOUTONS — bleu pour les actions, vert pour les téléchargements */
div.stButton > button {
  width: 100% !important; background: var(--blue) !important; border: none !important;
  color: var(--white) !important; font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  padding: 0 1.4rem !important; height: 38px !important; border-radius: 999px !important;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 2px rgba(0,104,177,0.15), 0 2px 6px rgba(0,104,177,0.1) !important;
  cursor: pointer !important;
}
div.stButton > button:hover { background: #005fa8 !important; transform: translateY(-1px) !important; }
div.stButton > button:active { transform: translateY(0) !important; }
div.stButton > button:disabled {
  background: var(--border) !important; color: var(--muted) !important;
  box-shadow: none !important; cursor: default !important; transform: none !important;
}

/* BOUTONS DE TELECHARGEMENT — vert uniforme pour tous */
div.stDownloadButton > button,
div[data-testid="stDownloadButton"] > button {
  width: 100% !important; background: #16a34a !important; border: none !important;
  color: #fff !important; font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  padding: 0 1.4rem !important; height: 38px !important; border-radius: 999px !important;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 2px rgba(22,163,74,0.18), 0 2px 6px rgba(22,163,74,0.1) !important;
}
div.stDownloadButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  background: #15803d !important; transform: translateY(-1px) !important;
}
div.stDownloadButton > button:active,
div[data-testid="stDownloadButton"] > button:active { transform: translateY(0) !important; }

div[data-testid="stProgress"] { display: none !important; }

/* SPINNER D'ENCODAGE — anneau rotatif + barre de progression animée */
.encoding-wrap { display: flex; align-items: center; gap: 0.7rem; padding: 0.5rem 0; margin: 0.5rem 0; }
.encoding-ring {
  width: 16px; height: 16px; border: 2px solid var(--border);
  border-top-color: var(--blue); border-radius: 50%; flex-shrink: 0;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.encoding-text { font-size: 0.8rem; color: var(--sub); }

.fake-progress-wrap { margin: 0.6rem 0 0.4rem; }
.fake-progress-track { height: 3px; background: var(--border); border-radius: 99px; overflow: hidden; }
.fake-progress-bar {
  height: 100%; border-radius: 99px;
  background: linear-gradient(90deg, var(--blue-dim), var(--blue), var(--blue-dim));
  background-size: 200% 100%; animation: indeterminate 1.4s ease-in-out infinite;
}
@keyframes indeterminate { 0% { background-position: 200% center; } 100% { background-position: -200% center; } }

/* MESSAGES DE STATUT — ok / erreur / idle */
.status { font-size: 0.78rem; padding: 0.5rem 0; margin: 0.5rem 0; color: var(--muted); line-height: 1.4; }
.status-ok   { color: var(--green); }
.status-err  { color: var(--red); }
.status-idle { color: var(--muted); }

/* FOOTER */
.site-footer {
  height: var(--footer-h);
  margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.7rem; color: var(--muted);
}
.footer-name { color: var(--sub); font-weight: 500; }

div[data-testid="stSpinner"] p {
  font-size: 0.78rem !important; color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
}

/* NUMBER INPUT — boutons +/- centrés et carrés */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] [data-baseweb="base-input"] { align-items: center !important; }
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
  display: flex !important; align-items: center !important;
  justify-content: center !important; align-self: center !important;
  width: 28px !important; height: 28px !important;
  min-width: 28px !important; min-height: 28px !important;
  padding: 0 !important; margin: 0 2px !important;
  background: transparent !important; border: 1px solid var(--border) !important;
  border-radius: 4px !important; color: var(--sub) !important;
  box-shadow: none !important; cursor: pointer !important;
}
[data-testid="stNumberInputStepDown"]:hover,
[data-testid="stNumberInputStepUp"]:hover {
  background: var(--bg) !important; border-color: var(--border-mid) !important;
  color: var(--ink) !important; box-shadow: none !important;
}
[data-testid="stNumberInputStepDown"] svg,
[data-testid="stNumberInputStepUp"] svg { width: 12px !important; height: 12px !important; display: block !important; }
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
  border-color: var(--border-mid) !important; box-shadow: none !important;
}
[data-testid="stNumberInput"] input:focus { outline: none !important; box-shadow: none !important; }

/* SELECT BOX */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: var(--border) !important; border-radius: 6px !important; font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--blue) !important; }

/* --- SECTION SUPPRIMÉE ICI : Styles personnalisés des Sliders --- */

/* LISTE DES FICHIERS IMPORTÉS (onglet photo) */
.photo-batch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.photo-batch-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim  { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

/* PLACEHOLDER APERÇU — affiché quand aucun fichier n'est uploadé */
.preview-placeholder {
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; gap: 0.6rem; min-height: 260px;
  border: 1px dashed var(--border); border-radius: 10px;
  background: var(--bg); color: var(--muted);
  font-size: 0.8rem; text-align: center;
  margin-top: 1.8rem;
}
.preview-placeholder svg { opacity: 0.25; }

/* TIMELINE CUTTER — outil de découpe vidéo */
.timeline-wrap {
  position: relative; height: 52px; background: var(--bg);
  border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
  margin: 0.6rem 0; cursor: pointer; user-select: none;
}
.timeline-track {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    90deg, transparent 0px, transparent 18px,
    var(--border) 18px, var(--border) 19px
  );
}
.timeline-selection {
  position: absolute; top: 0; bottom: 0;
  background: rgba(0, 104, 177, 0.15);
  border-left: 2px solid var(--blue); border-right: 2px solid var(--blue);
}
.timeline-handle {
  position: absolute; top: 0; bottom: 0; width: 6px;
  background: var(--blue); border-radius: 2px; cursor: ew-resize;
  display: flex; align-items: center; justify-content: center;
}
.timeline-handle::after {
  content: ''; display: block; width: 2px; height: 16px;
  background: rgba(255,255,255,0.7); border-radius: 1px;
}
.timeline-time-label {
  position: absolute; top: -1.4rem; font-size: 0.62rem;
  color: var(--blue); font-weight: 600; white-space: nowrap;
  transform: translateX(-50%);
}
.cut-info-row {
  display: flex; gap: 0.5rem; margin-top: 0.4rem;
}
.cut-info-cell {
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.4rem 0.7rem;
  font-size: 0.78rem; color: var(--ink);
}
.cut-info-cell span { display: block; font-size: 0.58rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }

/* FUSION — liste des vidéos à fusionner */
.merge-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.45rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.merge-item-idx {
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--blue-dim); color: var(--blue);
  font-size: 0.68rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.merge-item-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.merge-item-dur { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; }

/* LECTEUR VIDEO APERÇU — player natif stylisé DA */
.video-preview-wrap {
  border: 1px solid var(--border); border-radius: 10px; overflow: hidden;
  background: #0a0a0a; margin-top: 0.2rem;
}
.video-preview-wrap video {
  width: 100%; display: block; max-height: 420px; object-fit: contain;
}
.video-preview-label {
  font-size: 0.58rem; font-weight: 500; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--muted);
  padding: 0.35rem 0.85rem; background: var(--white);
  border-bottom: 1px solid var(--border);
}
.video-preview-info {
  padding: 0.3rem 0.85rem; background: var(--white);
  border-top: 1px solid var(--border);
  font-size: 0.68rem; color: var(--muted); display: flex; gap: 1rem;
}
.video-preview-info b { color: var(--blue); font-weight: 600; }

/* OUTIL SON — options audio */
.audio-option-row {
  display: flex; gap: 0.5rem; margin-bottom: 0.8rem;
}
.audio-chip {
  flex: 1; text-align: center; padding: 0.45rem 0.5rem;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 0.75rem; color: var(--sub); background: var(--bg);
  cursor: pointer; transition: all 0.12s;
}
.audio-chip.active {
  border-color: var(--blue); background: var(--blue-dim); color: var(--blue); font-weight: 500;
}

/* OUTIL RECADRAGE — grille de presets */
.crop-presets {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem; margin-bottom: 0.8rem;
}
.crop-preset-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.5rem 0.3rem; border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); cursor: pointer; transition: all 0.12s; gap: 0.2rem;
}
.crop-preset-btn:hover { border-color: var(--blue); background: var(--blue-dim); }
.crop-preset-icon {
  background: var(--border-mid); border-radius: 2px;
}
.crop-preset-label { font-size: 0.65rem; color: var(--sub); font-weight: 500; }
.crop-preset-btn.active {
  border-color: var(--blue); background: var(--blue-dim);
}
.crop-preset-btn.active .crop-preset-label { color: var(--blue); }
.crop-preset-btn.active .crop-preset-icon { background: var(--blue); }

</style>
""", unsafe_allow_html=True)


# HEADER HTML
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_b64.b64encode(open(LOGO_FILE, "rb").read()).decode()}" />
  <div class="site-header-right">STUDIO D'ÉDITION VIDÉO RAPIDE</div>
</div>
""", unsafe_allow_html=True)


# --- FONCTIONS UTILITAIRES ---

def get_video_info(path):
    # Récupère dimensions, durée, fps via ffprobe
    cmd = [
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,duration",
        "-of", "default=noprint_wrappers=1:nokey=1", path
    ]
    res = subprocess.run(cmd, capture_output=True, text=True).stdout.splitlines()
    if not res: return {"width": 0, "height": 0, "fps": 0, "duration": 0}
    w = int(res[0])
    h = int(res[1])
    # fps est souvent une fraction "30/1"
    fps_raw = res[2].split('/')
    fps = round(float(fps_raw[0])/float(fps_raw[1]), 2) if len(fps_raw)>1 else float(res[2])
    dur = float(res[3]) if res[3] != "N/A" else 0.0
    return {"width": w, "height": h, "fps": fps, "duration": dur}

def fmt_time(s):
    # Formate secondes en MM:SS.ms
    m = int(s // 60)
    sec = s % 60
    return f"{m:02d}:{sec:05.2f}"

def get_default_logo():
    return Image.open(DEFAULT_WM_FILE).convert("RGBA")

def composite_logo(base_img, logo_img, pos="Bas-Droite", size_pct=15, opacity=0.8, padding=3):
    # Applique le filigrane sur une Image PIL
    base_img = base_img.convert("RGBA")
    W, H = base_img.size
    
    # Calcul taille logo proportionnel à la largeur de l'image
    target_w = int(W * (size_pct / 100))
    aspect = logo_img.width / logo_img.height
    target_h = int(target_w / aspect)
    logo_res = logo_img.resize((target_w, target_h), Image.LANCZOS)
    
    # Opacité
    if opacity < 1.0:
        alpha = logo_res.getchannel("A")
        alpha = alpha.point(lambda p: int(p * opacity))
        logo_res.putalpha(alpha)
        
    px = int(W * (padding / 100))
    py = int(H * (padding / 100))
    
    if pos == "Haut-Gauche":  coords = (px, py)
    elif pos == "Haut-Droite": coords = (W - target_w - px, py)
    elif pos == "Bas-Gauche":  coords = (px, H - target_h - py)
    else:                      coords = (W - target_w - px, H - target_h - py)
    
    overlay = Image.new("RGBA", base_img.size, (0, 0, 0, 0))
    overlay.paste(logo_res, coords, logo_res)
    return Image.alpha_composite(base_img, overlay)

def extract_frame(video_path, t):
    # Extrait une frame à l'instant t pour l'aperçu
    with tempfile.NamedTemporaryFile(suffix=".png") as tmp:
        subprocess.run([
            "ffmpeg", "-y", "-ss", str(t), "-i", video_path,
            "-frames:v", "1", "-q:v", "2", tmp.name
        ], capture_output=True)
        return Image.open(tmp.name).copy()


# --- UI COMPONENTS ---

def watermark_options_ui(key_pfx):
    # Groupe de contrôles communs aux outils de watermark
    st.markdown('<p class="section-label-mt">Réglages filigrane</p>', unsafe_allow_html=True)
    pos = st.selectbox("Position", ["Bas-Droite", "Bas-Gauche", "Haut-Droite", "Haut-Gauche"], key=f"{key_pfx}_pos")
    col1, col2 = st.columns(2)
    with col1:
        size = st.slider("Taille (%)", 5, 50, 18, key=f"{key_pfx}_size")
    with col2:
        alpha = st.slider("Opacité", 0.1, 1.0, 0.9, 0.1, key=f"{key_pfx}_alpha")
    return {"pos": pos, "size_pct": size, "opacity": alpha}


# SESSION STATE — initialisation des variables persistantes entre reruns
for k in ["thumbnail", "rendered_bytes", "_last_video_name", 
          "cut_bytes", "_last_cut_name", "merge_bytes", 
          "audio_bytes", "_last_audio_name", "crop_bytes", "_last_crop_name"]:
    if k not in st.session_state: st.session_state[k] = None

tab_v, tab_p, tab_s, tab_cut, tab_merge, tab_audio, tab_crop = st.tabs([
    "Watermark vidéo", "Watermark photo", "Capture d'écran", "✂️ Couper", "⊕ Fusionner", "🔇 Son", "📐 Recadrer"
])


# ═══════════════════════════════════════════════════════════════════
# ONGLET 1 — WATERMARK VIDÉO
# ═══════════════════════════════════════════════════════════════════
with tab_v:
    col_ctrl, col_prev = st.columns([4, 6], gap="large")
    
    with col_ctrl:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader(
            "Déposez votre vidéo ici", type=["mp4", "mov", "avi", "mkv", "webm"], 
            key="vu", label_visibility="collapsed"
        )
        
        if video_file:
            # RESET si l'utilisateur change de fichier
            if st.session_state._last_video_name != video_file.name:
                st.session_state.rendered_bytes = None
                st.session_state.thumbnail = None
                st.session_state._last_video_name = video_file.name
                
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(video_file.name)[1]) as t:
                t.write(video_file.read())
                info = get_video_info(t.name)
                
                # Bande specs
                st.markdown(f"""
                <div class="specs-row">
                  <div class="spec-cell"><span class="spec-k">Format</span><span class="spec-v">{info['width']}×{info['height']}</span></div>
                  <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(info['duration'])}</span></div>
                  <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{info['fps']}</span></div>
                </div>
                """, unsafe_allow_html=True)
                
                wm_opts = watermark_options_ui("v")
                
                # Aperçu (frame au milieu de la vidéo)
                if st.session_state.thumbnail is None:
                    st.session_state.thumbnail = extract_frame(t.name, info['duration']/2)
                
                logo = get_default_logo()
                prev_img = composite_logo(st.session_state.thumbnail, logo, **wm_opts)
                
                st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
                
                if not st.session_state.rendered_bytes:
                    if st.button("Lancer l'encodage", key="v_btn"):
                        out_p = os.path.join(tempfile.gettempdir(), "out_wm.mp4")
                        ph = st.empty()
                        ph.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Calcul des vecteurs et incrustation…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>', unsafe_allow_html=True)
                        
                        # Commande FFMPEG complexe pour overlay
                        # On prépare les variables pour l'injection FFMPEG
                        # calcul pos en px pour ffmpeg
                        W, H = info['width'], info['height']
                        lw = int(W * (wm_opts['size_pct']/100))
                        pad = int(W * (3/100)) # padding fixe 3%
                        
                        mapping = {
                            "Bas-Droite": f"main_w-overlay_w-{pad}:main_h-overlay_h-{pad}",
                            "Bas-Gauche": f"{pad}:main_h-overlay_h-{pad}",
                            "Haut-Droite": f"main_w-overlay_w-{pad}:{pad}",
                            "Haut-Gauche": f"{pad}:{pad}"
                        }
                        f_pos = mapping[wm_opts['pos']]
                        
                        with tempfile.NamedTemporaryFile(suffix=".png") as l_tmp:
                            logo.save(l_tmp.name)
                            cmd = [
                                "ffmpeg", "-y", "-i", t.name, "-i", l_tmp.name,
                                "-filter_complex", f"[1][0]scale2ref=w=iw*{wm_opts['size_pct']/100}:h=ow/mdar[wm][main];[wm]format=rgba,colorchannelmixer=aa={wm_opts['opacity']}[wm_op];[main][wm_op]overlay={f_pos}",
                                "-c:v", "libx264", "-preset", "faster", "-crf", "22", "-c:a", "copy", out_p
                            ]
                            result = subprocess.run(cmd, capture_output=True)
                            if result.returncode == 0:
                                ph.empty()
                                with open(out_p, "rb") as f:
                                    st.session_state.rendered_bytes = f.read()
                                st.rerun()
                            else:
                                ph.markdown(f'<div class="status status-err">Erreur FFMPEG : {result.stderr.decode()}</div>', unsafe_allow_html=True)
                else:
                    st.download_button("↓ Télécharger la vidéo", data=st.session_state.rendered_bytes, file_name="luluflix_video.mp4", mime="video/mp4")
                    st.markdown('<div class="status status-ok">✓ Encodage terminé avec succès.</div>', unsafe_allow_html=True)

    with col_prev:
        st.markdown('<p class="section-label">Aperçu du rendu</p>', unsafe_allow_html=True)
        if video_file:
            st.markdown('<div class="preview-wrap"><div class="preview-bar">FRAME DE RÉFÉRENCE</div>', unsafe_allow_html=True)
            st.image(prev_img, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/>
              </svg>
              Déposez une vidéo pour<br/>générer l'aperçu dynamique.
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 2 — WATERMARK PHOTO (BATCH)
# ═══════════════════════════════════════════════════════════════════
with tab_p:
    col_ctrl_p, col_prev_p = st.columns([4, 6], gap="large")
    
    with col_ctrl_p:
        st.markdown('<p class="section-label">Sources (Batch supporté)</p>', unsafe_allow_html=True)
        photo_files = st.file_uploader(
            "Déposez vos images ici", type=["png", "jpg", "jpeg"], key="pu", 
            label_visibility="collapsed", accept_multiple_files=True
        )
        
        if photo_files:
            lp2 = get_default_logo()
            with col_ctrl_p:
                # LISTE DES FICHIERS IMPORTÉS avec dimensions
                st.markdown('<p class="section-label-mt">Fichiers importés</p>', unsafe_allow_html=True)
                for pf in photo_files:
                    img_tmp = Image.open(pf)
                    W_tmp, H_tmp = img_tmp.size
                    pf.seek(0)
                    st.markdown(
                        f'<div class="photo-batch-item">'
                        f'<span class="photo-batch-name">📷 {pf.name}</span>'
                        f'<span class="photo-batch-dim">{W_tmp} × {H_tmp} px</span>'
                        f'</div>', unsafe_allow_html=True
                    )
                
                wm_opts_p = watermark_options_ui("p")
                
                def build_photo_output(pf, opts):
                    # GÉNÈRE LE FICHIER FINAL watermarké pour une image donnée
                    pf.seek(0)
                    base = Image.open(pf)
                    result = composite_logo(base, lp2, **opts)
                    buf = io.BytesIO()
                    ext = pf.name.rsplit(".", 1)[-1].lower()
                    if ext == "png":
                        result.save(buf, format="PNG")
                        return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.png", "image/png"
                    else:
                        result.convert("RGB").save(buf, format="JPEG", quality=90)
                        return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.jpg", "image/jpeg"

                st.markdown("<div style='margin-top:1.5rem;'></div>", unsafe_allow_html=True)
                if len(photo_files) == 1:
                    b, n, m = build_photo_output(photo_files[0], wm_opts_p)
                    st.download_button("↓ Télécharger l'image", data=b, file_name=n, mime=m)
                else:
                    # Création d'un ZIP pour le batch
                    if st.button(f"Générer le ZIP ({len(photo_files)} photos)"):
                        zip_buf = io.BytesIO()
                        with zipfile.ZipFile(zip_buf, "w") as zf:
                            for pf in photo_files:
                                b, n, m = build_photo_output(pf, wm_opts_p)
                                zf.writestr(n, b)
                        st.download_button("↓ Télécharger le pack .ZIP", data=zip_buf.getvalue(), file_name="luluflix_photos.zip")

    with col_prev_p:
        st.markdown('<p class="section-label">Aperçu du rendu (Dernière image)</p>', unsafe_allow_html=True)
        if photo_files:
            last_img = Image.open(photo_files[-1])
            photo_files[-1].seek(0)
            st.markdown('<div class="preview-wrap"><div class="preview-bar">PRÉVISUALISATION DIRECTE</div>', unsafe_allow_html=True)
            st.image(composite_logo(last_img, lp2, **wm_opts_p), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/>
              </svg>
              Déposez une ou plusieurs photos<br/>pour configurer le marquage.
            </div>
            """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 3 — CAPTURE D'ÉCRAN
# ═══════════════════════════════════════════════════════════════════
with tab_s:
    col_ctrl_s, col_prev_s = st.columns([4, 6], gap="large")
    with col_ctrl_s:
        st.markdown('<p class="section-label">Source Vidéo</p>', unsafe_allow_html=True)
        scr_file = st.file_uploader("Vidéo pour capture", type=["mp4","mov","avi"], key="su", label_visibility="collapsed")
        
        if scr_file:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tf:
                sp = tf.name
            with open(sp, "wb") as f:
                f.write(scr_file.read())
            
            nfo_s = get_video_info(sp)
            dur_s = nfo_s["duration"]
            
            with col_ctrl_s:
                st.markdown(f"""
                <div class="specs-row">
                  <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo_s['width']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo_s['height']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(dur_s)}</span></div>
                  <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo_s['fps']}</span></div>
                </div>""", unsafe_allow_html=True)
                
                st.markdown('<p class="section-label">Timecode (secondes)</p>', unsafe_allow_html=True)
                timecode = st.number_input("tc", min_value=0.0, max_value=float(dur_s), value=float(st.session_state.get("cap_tc_ni", 0.0)), step=0.1, format="%.2f", key="cap_tc_ni", label_visibility="collapsed")
                
                with st.spinner(""):
                    frame = extract_frame(sp, timecode)
                
                with col_ctrl_s:
                    buf_s = io.BytesIO()
                    frame.save(buf_s, format="PNG")
                    st.download_button("↓ Enregistrer la capture (.png)", data=buf_s.getvalue(), file_name=f"screenshot_{timecode}.png", mime="image/png")

    with col_prev_s:
        st.markdown('<p class="section-label">Frame extraite</p>', unsafe_allow_html=True)
        if scr_file:
            st.markdown('<div class="preview-wrap"><div class="preview-bar">INSTANT T = ' + str(timecode) + 's</div>', unsafe_allow_html=True)
            st.image(frame, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="preview-placeholder">Uploadez une vidéo pour extraire une frame haute qualité.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 4 — COUPER (TRIM)
# ═══════════════════════════════════════════════════════════════════
with tab_cut:
    col_ctrl_c, col_prev_c = st.columns([4, 6], gap="large")
    with col_ctrl_c:
        st.markdown('<p class="section-label">Source à découper</p>', unsafe_allow_html=True)
        cut_file = st.file_uploader("Vidéo à couper", type=["mp4","mov","avi"], key="cu", label_visibility="collapsed")
        
        if cut_file:
            if st.session_state._last_cut_name != cut_file.name:
                st.session_state.cut_bytes = None
                st.session_state._last_cut_name = cut_file.name

            tmp_c = tempfile.gettempdir()
            cp = os.path.join(tmp_c, "to_cut.mp4")
            with open(cp, "wb") as f: f.write(cut_file.read())
            
            nfo_c = get_video_info(cp)
            dur_c = nfo_c["duration"]
            
            st.markdown('<p class="section-label-mt">Sélection de la plage</p>', unsafe_allow_html=True)
            # Utilisation du slider Streamlit natif (sans surcharge bleue forcée)
            t_range = st.slider("trim_range", 0.0, float(dur_c), (0.0, float(dur_c)), step=0.1, label_visibility="collapsed")
            t_start, t_end = t_range
            
            st.markdown(f"""
            <div class="cut-info-row">
              <div class="cut-info-cell"><span>Début</span>{fmt_time(t_start)}</div>
              <div class="cut-info-cell"><span>Fin</span>{fmt_time(t_end)}</div>
              <div class="cut-info-cell"><span>Durée finale</span><b>{fmt_time(t_end - t_start)}</b></div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            
            if not st.session_state.cut_bytes:
                if st.button("Valider la découpe", key="cut_btn"):
                    out_c = os.path.join(tmp_c, "cut_output.mp4")
                    ph_c = st.empty()
                    ph_c.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Extraction du segment sans perte…</span></div>', unsafe_allow_html=True)
                    
                    cmd = ["ffmpeg", "-y", "-ss", str(t_start), "-i", cp, "-t", str(t_end - t_start), "-c", "copy", out_c]
                    try:
                        subprocess.run(cmd, capture_output=True, check=True)
                        ph_c.empty()
                        with open(out_c, "rb") as f:
                            st.session_state.cut_bytes = f.read()
                        st.rerun()
                    except Exception as e:
                        ph_c.markdown(f'<div class="status status-err">Erreur : {e}</div>', unsafe_allow_html=True)
            else:
                st.download_button("↓ Télécharger le segment", data=st.session_state.cut_bytes, file_name="segment_coupe.mp4", mime="video/mp4", key="cut_dl")
                st.markdown('<div class="status status-ok">✓ Découpage terminé.</div>', unsafe_allow_html=True)

    with col_prev_c:
        st.markdown('<p class="section-label">Aperçu vidéo — segment sélectionné</p>', unsafe_allow_html=True)
        if cut_file:
            with open(cp, "rb") as _vf:
                _vb64 = _b64.b64encode(_vf.read()).decode()
            _ext = os.path.splitext(cut_file.name)[1].lower().lstrip(".")
            _mime = "video/mp4" if _ext in ("mp4", "m4v") else f"video/{_ext}"
            
            components.html(f"""
            <div style="border:1px solid #e4e4e4;border-radius:10px;overflow:hidden;background:#0a0a0a;">
              <video id="v" controls style="width:100%;display:block;max-height:420px;" autoplay muted loop>
                <source src="data:{_mime};base64,{_vb64}#t={t_start},{t_end}" type="{_mime}">
              </video>
            </div>
            <script>
               var v = document.getElementById('v');
               v.onpause = function() {{ if(v.currentTime >= {t_end} || v.currentTime < {t_start}) v.currentTime = {t_start}; }};
            </script>
            """, height=440)
        else:
            st.markdown('<div class="preview-placeholder">Déposez une vidéo pour utiliser les outils de coupe précise.</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 5 — FUSIONNER (CONCAT)
# ═══════════════════════════════════════════════════════════════════
with tab_merge:
    col_ctrl_m, col_prev_m = st.columns([4, 6], gap="large")
    with col_ctrl_m:
        st.markdown('<p class="section-label">Fichiers à assembler</p>', unsafe_allow_html=True)
        merge_files = st.file_uploader("Vidéos à fusionner", type=["mp4","mov","avi"], key="mu", label_visibility="collapsed", accept_multiple_files=True)
        
        if merge_files and len(merge_files) > 1:
            tmp_m = tempfile.gettempdir()
            nfo_list = []
            total_dur = 0
            
            # Analyse des sources
            for idx, mf in enumerate(merge_files):
                p = os.path.join(tmp_m, f"m_{idx}.mp4")
                with open(p, "wb") as f: f.write(mf.read())
                ni = get_video_info(p)
                nfo_list.append(ni)
                total_dur += ni["duration"]
                st.markdown(f'<div class="merge-item"><div class="merge-item-idx">{idx+1}</div><div class="merge-item-name">{mf.name}</div><div class="merge-item-dur">{fmt_time(ni["duration"])}</div></div>', unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="specs-row" style="margin-top:0.8rem;">
              <div class="spec-cell"><span class="spec-k">Fichiers</span><span class="spec-v">{len(merge_files)}</span></div>
              <div class="spec-cell"><span class="spec-k">Durée totale</span><span class="spec-v">{fmt_time(total_dur)}</span></div>
              <div class="spec-cell"><span class="spec-k">Résolution</span><span class="spec-v">{nfo_list[0]['width']}×{nfo_list[0]['height']}</span></div>
            </div>""", unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top:1rem;'></div>", unsafe_allow_html=True)
            
            # Reset si la liste change
            merge_sig = tuple(mf.name for mf in merge_files)
            if st.session_state.get("_merge_sig") != merge_sig:
                st.session_state.merge_bytes = None
                st.session_state["_merge_sig"] = merge_sig
                
            if not st.session_state.merge_bytes:
                if st.button("Fusionner les vidéos", key="merge_btn"):
                    out_m = os.path.join(tmp_m, "fusion_output.mp4")
                    ph_m = st.empty()
                    ph_m.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Fusion en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>', unsafe_allow_html=True)
                    
                    list_txt = os.path.join(tmp_m, "list.txt")
                    with open(list_txt, "w") as f:
                        for i in range(len(merge_files)):
                            f.write(f"file 'm_{i}.mp4'\n")
                    
                    cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_txt, "-c", "copy", out_m]
                    subprocess.run(cmd, capture_output=True)
                    ph_m.empty()
                    with open(out_m, "rb") as f:
                        st.session_state.merge_bytes = f.read()
                    st.rerun()
            else:
                st.download_button("↓ Télécharger la fusion", data=st.session_state.merge_bytes, file_name="luluflix_fusion.mp4")
                st.markdown('<div class="status status-ok">✓ Fusion terminée (Stream Copy).</div>', unsafe_allow_html=True)

    with col_prev_m:
        st.markdown('<p class="section-label">Aide Fusion</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="preview-placeholder" style="padding: 2rem;">
          <div style="font-size: 1.2rem; color: var(--blue); margin-bottom: 0.5rem;">⊕</div>
          Le mode fusion utilise le <b>Stream Copy</b>.<br/><br/>
          <span style="font-size: 0.72rem; opacity: 0.8;">
          Pour un résultat optimal, assurez-vous que toutes vos vidéos ont exactement <br/>
          les mêmes dimensions et le même encodage.
          </span>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 6 — SON (AUDIO)
# ═══════════════════════════════════════════════════════════════════
with tab_audio:
    col_ctrl_a, col_prev_a = st.columns([4, 6], gap="large")
    with col_ctrl_a:
        st.markdown('<p class="section-label">Source Vidéo</p>', unsafe_allow_html=True)
        audio_vid_file = st.file_uploader("Vidéo à traiter", type=["mp4","mov","avi"], key="au", label_visibility="collapsed")
        
        if audio_vid_file:
            tmp_a = tempfile.gettempdir()
            ap = os.path.join(tmp_a, "src_audio.mp4")
            with open(ap, "wb") as f: f.write(audio_vid_file.read())
            
            st.markdown('<p class="section-label-mt">Action Audio</p>', unsafe_allow_html=True)
            audio_action = st.radio("action", ["Supprimer le son", "Remplacer l'audio par un fichier"], label_visibility="collapsed")
            
            audio_replace_file = None
            if "Remplacer" in audio_action:
                audio_replace_file = st.file_uploader("Fichier audio (.mp3, .wav)", type=["mp3","wav","m4a"], key="aru")
                audio_loop = st.checkbox("Boucler l'audio si plus court que la vidéo", value=True, key="audio_loop")
            
            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            
            audio_sig = (audio_vid_file.name, audio_action, audio_replace_file.name if audio_replace_file else None)
            if st.session_state.get("_audio_sig") != audio_sig:
                st.session_state.audio_bytes = None
                st.session_state["_audio_sig"] = audio_sig
            
            can_go = ("Supprimer" in audio_action) or ("Remplacer" in audio_action and audio_replace_file)
            
            if not st.session_state.audio_bytes:
                btn_lbl = "Supprimer le son" if "Supprimer" in audio_action else "Remplacer l'audio"
                if can_go:
                    if st.button(btn_lbl, key="audio_btn"):
                        out_a = os.path.join(tmp_a, "audio_output.mp4")
                        ph_a = st.empty()
                        ph_a.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Traitement audio en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>', unsafe_allow_html=True)
                        
                        if "Supprimer" in audio_action:
                            cmd = ["ffmpeg", "-y", "-i", ap, "-an", "-vcodec", "copy", out_a]
                        else:
                            rp = os.path.join(tmp_a, "new_audio.mp3")
                            with open(rp, "wb") as f: f.write(audio_replace_file.read())
                            if audio_loop:
                                cmd = ["ffmpeg", "-y", "-i", ap, "-stream_loop", "-1", "-i", rp, "-map", "0:v:0", "-map", "1:a:0", "-shortest", "-c:v", "copy", "-c:a", "aac", out_a]
                            else:
                                cmd = ["ffmpeg", "-y", "-i", ap, "-i", rp, "-map", "0:v:0", "-map", "1:a:0", "-shortest", "-c:v", "copy", "-c:a", "aac", out_a]
                        
                        subprocess.run(cmd, capture_output=True)
                        ph_a.empty()
                        with open(out_a, "rb") as f:
                            st.session_state.audio_bytes = f.read()
                        st.rerun()
            else:
                st.download_button("↓ Télécharger le résultat", data=st.session_state.audio_bytes, file_name="luluflix_audio_fix.mp4")
                st.markdown('<div class="status status-ok">✓ Audio traité.</div>', unsafe_allow_html=True)

    with col_prev_a:
        st.markdown('<p class="section-label">Aide Son</p>', unsafe_allow_html=True)
        st.markdown("""
        <div class="preview-placeholder">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
            <path d="M11 5L6 9H2v6h4l5 4V5zM15.54 8.46a5 5 0 0 1 0 7.07M19.07 4.93a10 10 0 0 1 0 14.14"/>
          </svg>
          Gérez les pistes audio de vos vidéos.<br/>
          Remplacement ou suppression totale du signal.
        </div>
        """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# ONGLET 7 — RECADRER (CROP)
# ═══════════════════════════════════════════════════════════════════
with tab_crop:
    col_ctrl_r, col_prev_r = st.columns([4, 6], gap="large")
    with col_ctrl_r:
        st.markdown('<p class="section-label">Source à recadrer</p>', unsafe_allow_html=True)
        crop_file = st.file_uploader("Vidéo à crop", type=["mp4","mov","avi"], key="cru", label_visibility="collapsed")
        
        if crop_file:
            tmp_r = tempfile.gettempdir()
            rp_in = os.path.join(tmp_r, "crop_in.mp4")
            with open(rp_in, "wb") as f: f.write(crop_file.read())
            nfo_r = get_video_info(rp_in)
            W_r, H_r = nfo_r["width"], nfo_r["height"]
            
            st.markdown('<p class="section-label-mt">Format cible</p>', unsafe_allow_html=True)
            CROP_PRESETS = [
                ("9:16 (TikTok/Reels)", 9, 16),
                ("1:1 (Carré)", 1, 1),
                ("4:5 (Instagram Feed)", 4, 5),
                ("16:9 (YouTube)", 16, 9)
            ]
            preset_choice_idx = st.selectbox(
                "Format", range(len(CROP_PRESETS)), 
                format_func=lambda x: CROP_PRESETS[x][0],
                key="crop_preset", label_visibility="collapsed"
            )
            chosen = CROP_PRESETS[preset_choice_idx]
            rw, rh = chosen[1], chosen[2]
            
            target_ratio = rw / rh
            src_ratio = W_r / H_r
            
            if src_ratio > target_ratio:
                out_w = int(H_r * target_ratio); out_h = H_r
            else:
                out_w = W_r; out_h = int(W_r / target_ratio)
            
            out_w -= out_w % 2; out_h -= out_h % 2
            
            st.markdown('<p class="section-label-mt">Position du cadre</p>', unsafe_allow_html=True)
            # Utilisation du slider Streamlit natif pour le centrage
            crop_pos = st.slider("Position", 0, 100, 50, key="crop_pos_slider", help="Centrer à gauche (0) ou à droite (100)")
            
            if src_ratio > target_ratio:
                max_x = W_r - out_w
                cx = int(max_x * (crop_pos / 100))
                cy = 0
            else:
                cx = 0
                max_y = H_r - out_h
                cy = int(max_y * (crop_pos / 100))
            
            st.markdown(f'<div class="status">Cadrage final : {out_w}×{out_h} px</div>', unsafe_allow_html=True)
            
            crop_sig = (crop_file.name, preset_choice_idx, crop_pos)
            if st.session_state.get("_crop_sig") != crop_sig:
                st.session_state.crop_bytes = None
                st.session_state["_crop_sig"] = crop_sig
                
            if not st.session_state.crop_bytes:
                if st.button("Calculer le recadrage"):
                    out_r = os.path.join(tmp_r, "crop_out.mp4")
                    ph_r = st.empty()
                    ph_r.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Recadrage et ré-encodage…</span></div>', unsafe_allow_html=True)
                    cmd = ["ffmpeg", "-y", "-i", rp_in, "-filter:v", f"crop={out_w}:{out_h}:{cx}:{cy}", "-c:a", "copy", out_r]
                    subprocess.run(cmd, capture_output=True)
                    ph_r.empty()
                    with open(out_r, "rb") as f:
                        st.session_state.crop_bytes = f.read()
                    st.rerun()
            else:
                st.download_button("↓ Télécharger la vidéo", data=st.session_state.crop_bytes, file_name="luluflix_recadre.mp4")

    with col_prev_r:
        if crop_file:
            st.markdown('<p class="section-label">Aperçu du cadrage</p>', unsafe_allow_html=True)
            from PIL import ImageDraw
            def cap_image_for_preview(im):
                # Resize pour l'UI tout en gardant l'aspect
                max_disp = 800
                w, h = im.size
                if w > max_disp:
                    new_h = int(h * (max_disp/w))
                    return im.resize((max_disp, new_h))
                return im

            prev_r = extract_frame(rp_in, nfo_r["duration"]/2)
            pw, ph_img = prev_r.size
            
            # Dessin de l'overlay de crop
            overlay = Image.new("RGBA", (pw, ph_img), (0, 0, 0, 0))
            draw_ov = ImageDraw.Draw(overlay)
            cw = out_w; ch = out_h
            # Masque sombre autour de la zone de crop
            draw_ov.rectangle([0, 0, pw, ph_img], fill=(0, 0, 0, 110))
            draw_ov.rectangle([cx, cy, cx + cw, cy + ch], fill=(0, 0, 0, 0))
            prev_r = prev_r.convert("RGBA")
            prev_r = Image.alpha_composite(prev_r, overlay).convert("RGB")
            draw2 = ImageDraw.Draw(prev_r)
            draw2.rectangle([cx, cy, cx + cw - 1, cy + ch - 1], outline=(0, 104, 177), width=3)
            st.image(cap_image_for_preview(prev_r), caption=f"{chosen[0]} — {out_w}×{out_h} px — {crop_pos}", use_container_width=True)

    else:
        with col_ctrl_r:
            st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)
        with col_prev_r:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M6 2H2v4M18 2h4v4M6 22H2v-4M18 22h4v-4"/>
                <path d="M7 12h10M12 7v10"/>
              </svg>
              Outil de recadrage intelligent.<br/>
              Choisissez un format (TikTok, Insta...) et ajustez le centre.
            </div>
            """, unsafe_allow_html=True)


# FOOTER HTML
st.markdown("""
<div class="site-footer">
  <div>© 2024 <span class="footer-name">Luluflix</span> — Studio d'édition vidéo simplifié</div>
  <div>Propulsé par FFMPEG & Streamlit</div>
</div>
""", unsafe_allow_html=True)
