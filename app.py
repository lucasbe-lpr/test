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
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&family=Roboto+Condensed:wght@400;500;700&display=swap');

:root {
  --blue:      #0068B1;
  --blue-dim:  #e8f2fb;
  --white:     #ffffff;
  --bg:        #fafafa;
  --ink:       #111111;
  --sub:       #555555;
  --muted:     #999999;
  --border:    #e4e4e4;
  --border-mid:#d0d0d0;
  --green:     #166534;
  --red:       #991b1b;
  --red-bg:    #fff1f1;
  --header-h:  64px;
  --tabs-h:    48px;
  --footer-h:  52px;
  --panel-v-pad: 1.5rem;
}

*, *::before, *::after { box-sizing: border-box; }

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

/* Wide layout — full width, controlled padding */
.block-container {
  background: var(--white) !important;
  padding: 0 2.5rem 2rem !important;
  max-width: 100% !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ── Header ─────────────────────────────────────────── */
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

/* ── Tabs ────────────────────────────────────────────── */
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

/* Tab content: remove default padding */
div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  padding: 0 !important;
}

/* ── Two-column layout inside each tab ──────────────── */
/* Left panel: controls */
.col-controls {
  padding-top: var(--panel-v-pad);
  padding-right: 2rem;
  border-right: 1px solid var(--border);
  min-height: calc(100vh - var(--header-h) - var(--tabs-h) - var(--footer-h));
}
/* Right panel: preview */
.col-preview {
  padding-top: var(--panel-v-pad);
  padding-left: 2rem;
}

/* Make Streamlit columns fill height */
[data-testid="column"] {
  padding-top: 0 !important;
}

/* ── File uploader ───────────────────────────────────── */
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

/* ── Labels ─────────────────────────────────────────── */
.section-label {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 0;
}
.section-label-mt {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 1.2rem;
}

/* ── Specs row ──────────────────────────────────────── */
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

/* ── Colonnes : la droite ne dépasse jamais la gauche ── */
[data-testid="stHorizontalBlock"] {
  align-items: flex-start !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  min-height: 0 !important;
}

/* ── Preview wrap ────────────────────────────────────── */
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

/* ── Buttons ────────────────────────────────────────── */
div.stButton > button {
  width: 100% !important; background: var(--blue) !important; border: none !important;
  color: var(--white) !important; font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  padding: 0 1.4rem !important; height: 38px !important; border-radius: 50px !important;
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

/* ── Encoding / spinner ─────────────────────────────── */
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

/* ── Status messages ────────────────────────────────── */
.status { font-size: 0.78rem; padding: 0.5rem 0; margin: 0.5rem 0; color: var(--muted); line-height: 1.4; }
.status-ok  { color: var(--green); }
.status-err { color: var(--red); }
.status-idle { color: var(--muted); }

/* ── Footer ─────────────────────────────────────────── */
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

/* ── Number inputs ──────────────────────────────────── */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] [data-baseweb="base-input"] {
  align-items: center !important;
}
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  align-self: center !important;
  width: 28px !important;
  height: 28px !important;
  min-width: 28px !important;
  min-height: 28px !important;
  padding: 0 !important;
  margin: 0 2px !important;
  background: transparent !important;
  border: 1px solid var(--border) !important;
  border-radius: 4px !important;
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
[data-testid="stNumberInputStepUp"] svg {
  width: 12px !important;
  height: 12px !important;
  display: block !important;
}
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
  border-color: var(--border-mid) !important;
  box-shadow: none !important;
}
[data-testid="stNumberInput"] input:focus {
  outline: none !important;
  box-shadow: none !important;
}

/* ── Select box ─────────────────────────────────────── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: var(--border) !important;
  border-radius: 6px !important;
  font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover {
  border-color: var(--blue) !important;
}

/* ── Photo batch list ───────────────────────────────── */
.photo-batch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.photo-batch-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim  { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

/* ── Preview placeholder when no file uploaded ──────── */
.preview-placeholder {
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; gap: 0.6rem;
  min-height: 260px;
  border: 1px dashed var(--border); border-radius: 10px;
  background: var(--bg); color: var(--muted);
  font-size: 0.8rem; text-align: center;
}
.preview-placeholder svg { opacity: 0.25; }
</style>
""", unsafe_allow_html=True)

import base64 as _b64h
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">version 2.1</span>
</div>
""", unsafe_allow_html=True)


PREVIEW_MAX_W = 680   # largeur max approximative de la colonne droite en px (60% d'un écran ~1200px)
PREVIEW_MAX_H = 500   # garde-fou pour les images très verticales

def cap_image_for_preview(img: Image.Image) -> Image.Image:
    """
    Redimensionne l'image pour qu'elle tienne dans la colonne droite
    sans jamais déborder verticalement.
    On contraint d'abord par la largeur (colonne ~60%), puis par une
    hauteur max de sécurité pour les formats très verticaux.
    """
    w, h = img.size
    # 1. Contrainte largeur
    if w > PREVIEW_MAX_W:
        ratio = PREVIEW_MAX_W / w
        w = PREVIEW_MAX_W
        h = int(h * ratio)
    # 2. Garde-fou hauteur (vidéos très verticales)
    if h > PREVIEW_MAX_H:
        ratio = PREVIEW_MAX_H / h
        h = PREVIEW_MAX_H
        w = int(w * ratio)
    if (w, h) == img.size:
        return img
    return img.resize((w, h), Image.LANCZOS)


def get_default_logo() -> str:
    return DEFAULT_WM_FILE


# ─── Position helpers ───────────────────────────────────────────────────────

POSITIONS = [
    "Haut gauche", "Haut centre", "Haut droite",
    "Milieu gauche", "Centre", "Milieu droite",
    "Bas gauche", "Bas centre", "Bas droite",
    "Coordonnées personnalisées",
]
DEFAULT_POSITION = "Haut droite"

def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int,
               custom_x: int = 0, custom_y: int = 0,
               margin_pct: float = 0.05) -> tuple[int, int]:
    """Return (x, y) top-left corner for the logo given a named position."""
    mx = int(W * margin_pct)
    my = int(H * margin_pct)

    if position == "Haut gauche":      return mx, my
    if position == "Haut centre":      return (W - logo_w) // 2, my
    if position == "Haut droite":      return W - logo_w - mx, my
    if position == "Milieu gauche":    return mx, (H - logo_h) // 2
    if position == "Centre":           return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite":    return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche":       return mx, H - logo_h - my
    if position == "Bas centre":       return (W - logo_w) // 2, H - logo_h - my
    if position == "Bas droite":       return W - logo_w - mx, H - logo_h - my
    # Coordonnées personnalisées
    return custom_x, custom_y


# ─── Pillow composite ────────────────────────────────────────────────────────

def composite_logo(
    base: Image.Image, logo_path: str,
    position: str = DEFAULT_POSITION,
    custom_x: int = 0, custom_y: int = 0,
    force_w: int = None, force_h: int = None,
) -> Image.Image:
    W = force_w if force_w else base.size[0]
    H = force_h if force_h else base.size[1]

    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo = Image.open(logo_path).convert("RGBA")
    ratio = logo_w / logo.width
    logo_h = int(logo.height * ratio)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)

    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    out = Image.alpha_composite(out, layer)
    return out


# ─── Video helpers ───────────────────────────────────────────────────────────

def get_video_info(path: str) -> dict:
    import json as _json
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,tags=rotate",
        "-show_entries", "stream_side_data=rotation",
        "-show_entries", "format=duration",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = _json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    w = int(stream.get("width", 0))
    h = int(stream.get("height", 0))
    dur = float(data.get("format", {}).get("duration", 0))
    fps_raw = stream.get("r_frame_rate", "25/1")
    try:
        num, den = fps_raw.split("/")
        fps = round(float(num) / float(den), 2)
    except Exception:
        fps = 25.0
    rotate = 0
    for sd in stream.get("side_data_list", []):
        if "rotation" in sd:
            rotate = int(sd["rotation"])
            break
    if rotate == 0:
        rotate = int(stream.get("tags", {}).get("rotate", 0))
    if abs(rotate) in (90, 270):
        w, h = h, w
    return {"width": w, "height": h, "duration": dur, "fps": fps, "rotate": rotate}

def fmt_time(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    return f"{m}:{s:02d}"

def extract_frame(video_path: str, timecode: float) -> Image.Image:
    result = subprocess.run([
        "ffmpeg", "-y", "-ss", str(timecode), "-i", video_path,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"
    ], capture_output=True)
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")

def make_thumbnail(video_path: str, logo_path: str, info: dict,
                   position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"
    ], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(
        frame, logo_path,
        position=position, custom_x=custom_x, custom_y=custom_y,
        force_w=info["width"], force_h=info["height"]
    ).convert("RGB")


QUALITY_PRESETS = {
    "Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)":         {"crf": "12", "preset": "slow"},
    "Sans perte (CRF 0)":             {"crf": "0",  "preset": "ultrafast"},
}

def render_video(
    video_path: str, logo_path: str, output_path: str, info: dict,
    position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0,
    quality_key: str = "Standard (CRF 18 — recommandé)",
    progress_cb=None
):
    W, H = info["width"], info["height"]

    # ── Préparer le watermark en haute qualité avec Pillow ──────────────────
    # On calcule la taille cible du watermark en fonction de la diagonale vidéo,
    # puis on le redimensionne avec LANCZOS (Pillow) depuis le PNG source original.
    # FFmpeg ne touche PLUS à la qualité du watermark : il reçoit un PNG déjà
    # aux bonnes dimensions et le colle pixel-perfect sur la vidéo.
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo_orig = Image.open(logo_path).convert("RGBA")
    ratio = logo_w / logo_orig.width
    logo_h = int(logo_orig.height * ratio)
    logo_scaled = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)

    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)

    # Sauvegarder le watermark pré-scalé dans un fichier temporaire
    tmp_logo_dir = tempfile.mkdtemp()
    tmp_logo_path = os.path.join(tmp_logo_dir, "wm_prescaled.png")
    logo_scaled.save(tmp_logo_path, format="PNG")
    # ────────────────────────────────────────────────────────────────────────

    # FFmpeg reçoit le watermark déjà à la bonne taille → pas de dégradation
    filter_complex = f"[0:v][1:v]overlay={x}:{y}"

    q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])

    cmd = [
        "ffmpeg", "-y",
        "-i", video_path, "-i", tmp_logo_path,
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"],
        "-c:a", "copy", "-movflags", "+faststart",
        "-progress", "pipe:1", output_path
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    total = info["duration"]
    while True:
        line = process.stdout.readline()
        if not line: break
        if line.strip().startswith("out_time_ms="):
            try:
                ms = int(line.strip().split("=")[1])
                if total > 0 and progress_cb:
                    progress_cb(min(ms / 1_000_000 / total, 1.0))
            except Exception:
                pass
    process.wait()
    if process.returncode != 0:
        raise RuntimeError(process.stderr.read())

def trim_video(video_path: str, output_path: str, t_start: float, t_end: float):
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(t_start), "-to", str(t_end),
        "-i", video_path,
        "-c", "copy", "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())


# ─── Shared watermark options UI ─────────────────────────────────────────────

def watermark_options_ui(key_prefix: str) -> dict:
    """Render position controls. Returns dict of options."""
    st.markdown('<p class="section-label-mt">Watermark</p>', unsafe_allow_html=True)

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
            custom_x = st.number_input("X (px depuis gauche)", min_value=0, value=0, step=1, key=f"{key_prefix}_cx")
        with col_y:
            custom_y = st.number_input("Y (px depuis haut)", min_value=0, value=0, step=1, key=f"{key_prefix}_cy")

    return {
        "position": position,
        "custom_x": int(custom_x),
        "custom_y": int(custom_y),
    }


# ─── Session state ────────────────────────────────────────────────────────────

for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state:
        st.session_state[k] = None

tab_v, tab_p, tab_s = st.tabs([
    "Watermark vidéo", "Watermark photo", "Capture d'écran"
])


# ═══════════════════════════════════════════════════════════════════
# TAB 1 — WATERMARK VIDÉO
# ═══════════════════════════════════════════════════════════════════

with tab_v:
    col_ctrl, col_prev = st.columns([4, 6], gap="large")

    with col_ctrl:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="vu", label_visibility="collapsed"
        )

    if video_file:
        if st.session_state._last_video_name != video_file.name:
            st.session_state.thumbnail = None
            st.session_state.rendered_bytes = None
            st.session_state._last_video_name = video_file.name
        lp = get_default_logo()
        tmp = tempfile.mkdtemp()
        vp = os.path.join(tmp, "src" + os.path.splitext(video_file.name)[1])
        with open(vp, "wb") as f: f.write(video_file.read())
        nfo = get_video_info(vp)

        with col_ctrl:
            st.markdown(f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo['duration'])}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo['fps']}</span></div>
            </div>""", unsafe_allow_html=True)

            wm_opts = watermark_options_ui("v")

            st.markdown('<p class="section-label-mt">Qualité d\'export</p>', unsafe_allow_html=True)
            quality_key = st.selectbox(
                "Qualité",
                list(QUALITY_PRESETS.keys()),
                key="v_quality",
                label_visibility="collapsed",
            )

            # Invalidate thumbnail if options changed
            opts_sig = (wm_opts["position"], wm_opts["custom_x"], wm_opts["custom_y"])
            if st.session_state.get("_v_opts_sig") != opts_sig:
                st.session_state.thumbnail = None
                st.session_state.rendered_bytes = None
                st.session_state["_v_opts_sig"] = opts_sig

            if st.session_state.thumbnail is None:
                with st.spinner("Génération de l'aperçu…"):
                    st.session_state.thumbnail = make_thumbnail(
                        vp, lp, nfo, **wm_opts
                    )

            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            if not st.session_state.rendered_bytes:
                if st.button("Générer le rendu", key="vbtn"):
                    out = os.path.join(tmp, "video_ready_to_post.mp4")
                    ph = st.empty()
                    ph.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Encodage en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>', unsafe_allow_html=True)
                    try:
                        render_video(vp, lp, out, nfo, quality_key=quality_key, **wm_opts)
                        ph.empty()
                        with open(out, "rb") as f:
                            st.session_state.rendered_bytes = f.read()
                        st.rerun()
                    except Exception as e:
                        ph.markdown(f'<div class="status status-err">Erreur : {e}</div>', unsafe_allow_html=True)
            else:
                st.download_button("↓  Télécharger la vidéo", data=st.session_state.rendered_bytes,
                    file_name="video_ready_to_post.mp4", mime="video/mp4", key="vdl")

        with col_prev:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            st.image(cap_image_for_preview(st.session_state.thumbnail))
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        with col_ctrl:
            st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)
        with col_prev:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — WATERMARK PHOTO (multi-fichiers)
# ═══════════════════════════════════════════════════════════════════

with tab_p:
    col_ctrl_p, col_prev_p = st.columns([4, 6], gap="large")

    with col_ctrl_p:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        photo_files = st.file_uploader(
            "Déposez vos images ici",
            type=["png", "jpg", "jpeg"],
            key="pu",
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

    if photo_files:
        lp2 = get_default_logo()

        with col_ctrl_p:
            # List uploaded files
            st.markdown('<p class="section-label-mt">Fichiers importés</p>', unsafe_allow_html=True)
            for pf in photo_files:
                img_tmp = Image.open(pf)
                W_tmp, H_tmp = img_tmp.size
                pf.seek(0)
                st.markdown(
                    f'<div class="photo-batch-item">'
                    f'<span class="photo-batch-name">📷 {pf.name}</span>'
                    f'<span class="photo-batch-dim">{W_tmp} × {H_tmp} px</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

            wm_opts_p = watermark_options_ui("p")

        # Build outputs helper
        def build_photo_output(pf, opts):
            pf.seek(0)
            base = Image.open(pf)
            result = composite_logo(base, lp2, **opts)
            buf = io.BytesIO()
            ext = pf.name.rsplit(".", 1)[-1].lower()
            if ext == "png":
                result.save(buf, format="PNG")
                return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.png", "image/png"
            else:
                result.convert("RGB").save(buf, format="JPEG", quality=100, subsampling=0)
                return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.jpg", "image/jpeg"

        # Preview grid — 2 columns, all uploaded photos
        with col_prev_p:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            grid_cols = st.columns(2)
            for idx, pf in enumerate(photo_files):
                pf.seek(0)
                base_prev = Image.open(pf)
                result_prev = composite_logo(base_prev, lp2, **wm_opts_p)
                with grid_cols[idx % 2]:
                    st.image(cap_image_for_preview(result_prev.convert("RGB")),
                             caption=pf.name, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_ctrl_p:
            if len(photo_files) == 1:
                data, fname, mime = build_photo_output(photo_files[0], wm_opts_p)
                st.download_button("↓  Télécharger la photo", data=data,
                    file_name=fname, mime=mime, key="pdl_single")
            else:
                st.markdown('<p class="section-label-mt">Téléchargement</p>', unsafe_allow_html=True)

                # Individual downloads — 2 per row
                for i in range(0, len(photo_files), 2):
                    row_files = photo_files[i:i+2]
                    btn_cols = st.columns(len(row_files), gap="small")
                    for j, pf in enumerate(row_files):
                        data, fname, mime = build_photo_output(pf, wm_opts_p)
                        with btn_cols[j]:
                            st.download_button(
                                f"↓  {pf.name}",
                                data=data, file_name=fname, mime=mime,
                                key=f"pdl_{i+j}",
                            )

                # ZIP download — darker green via injected class
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_STORED) as zf:
                    for pf in photo_files:
                        data, fname, _ = build_photo_output(pf, wm_opts_p)
                        zf.writestr(fname, data)
                st.download_button(
                    "↓  Tout télécharger (.zip)",
                    data=zip_buf.getvalue(),
                    file_name="photos_watermark.zip",
                    mime="application/zip",
                    key="pdl_zip",
                )
    else:
        with col_ctrl_p:
            st.markdown('<div class="status status-idle">Déposez une ou plusieurs images via "Upload".</div>', unsafe_allow_html=True)
        with col_prev_p:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""", unsafe_allow_html=True)


with tab_s:
    col_ctrl_s, col_prev_s = st.columns([4, 6], gap="large")

    with col_ctrl_s:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        scr_file = st.file_uploader("Déposez votre vidéo ici", type=["mp4", "mov", "avi", "mkv", "webm"],
            key="su", label_visibility="collapsed")

    if scr_file:
        tmp_s = tempfile.mkdtemp()
        sp = os.path.join(tmp_s, "src" + os.path.splitext(scr_file.name)[1])
        with open(sp, "wb") as f: f.write(scr_file.read())
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
            timecode = st.number_input(
                "tc", min_value=0.0, max_value=float(dur_s),
                value=float(st.session_state.get("cap_tc_ni", 0.0)),
                step=0.1, format="%.2f",
                key="cap_tc_ni", label_visibility="collapsed")

        with st.spinner(""):
            frame = extract_frame(sp, timecode)

        with col_ctrl_s:
            buf_s = io.BytesIO()
            frame.save(buf_s, format="PNG")
            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            st.download_button("↓  Télécharger la capture", data=buf_s.getvalue(),
                file_name=f"capture_{fmt_time(timecode).replace(':', '-')}.png",
                mime="image/png", key="sdl")

        with col_prev_s:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            st.image(cap_image_for_preview(frame))
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        with col_ctrl_s:
            st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)
        with col_prev_s:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""", unsafe_allow_html=True)


st.markdown("""
<div class="site-footer">
  <span class="footer-name"></span>
  <span>MàJ 2.1 : choix de l'emplacement du watermark ; chargement de plusieurs photos ; qualité de l'export améliorée.</span>
</div>
""", unsafe_allow_html=True)
