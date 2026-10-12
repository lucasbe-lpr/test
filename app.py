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

LOGO_FILE = "luluflix.png"
DEFAULT_WM_FILE = "lpr.png"
FAVICON_FILE = "favicon.png"

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

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* ============================================================
   THÈME — variables globales
   ============================================================ */
:root {
  --blue:        #0068B1;
  --blue-dark:   #005494;
  --blue-soft:   #e8f2fb;
  --blue-line:   #cfe3f5;
  --white:       #ffffff;
  --bg:          #f6f8fb;
  --bg-soft:     #f0f3f8;
  --ink:         #0f172a;
  --sub:         #475569;
  --muted:       #94a3b8;
  --border:      #e2e8f0;
  --border-mid:  #cbd5e1;
  --green:       #16a34a;
  --green-dark:  #15803d;
  --red:         #dc2626;
  --red-bg:      #fef2f2;
  --radius-sm:   8px;
  --radius-md:   12px;
  --radius-lg:   16px;
  --radius-pill: 999px;
  --shadow-sm:   0 1px 2px rgba(15,23,42,0.04), 0 1px 3px rgba(15,23,42,0.06);
  --shadow-md:   0 4px 12px rgba(15,23,42,0.06), 0 2px 4px rgba(15,23,42,0.04);
  --header-h:    68px;
}

*, *::before, *::after { box-sizing: border-box; }

/* ============================================================
   BASE
   ============================================================ */
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
.main {
  background: var(--white) !important;
  color: var(--ink) !important;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
  font-weight: 400 !important;
  overflow-x: hidden !important;
  -webkit-font-smoothing: antialiased;
}

.block-container {
  background: var(--white) !important;
  padding: 0 2.5rem 3rem !important;
  max-width: 100% !important;
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* ============================================================
   HEADER
   ============================================================ */
.site-header {
  height: var(--header-h);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0;
}
.site-header img { height: 36px; width: auto; display: block; flex-shrink: 0; }
.site-header-right {
  font-size: 0.7rem;
  color: var(--muted);
  letter-spacing: 0.02em;
  white-space: nowrap;
  font-weight: 500;
}

/* ============================================================
   ONGLETS
   ============================================================ */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0.25rem !important;
  margin-bottom: 0 !important;
  padding: 0 !important;
  overflow-x: auto !important;
  flex-wrap: nowrap !important;
  scrollbar-width: none !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -1px !important;
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.01em;
  padding: 0.7rem 1.5rem 0.7rem 0 !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  transition: color 0.15s ease !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--ink) !important;
  font-weight: 600 !important;
  border-bottom: 2px solid var(--blue) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--sub) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.8rem !important; }

/* ============================================================
   COLONNES
   ============================================================ */
[data-testid="stHorizontalBlock"] {
  align-items: flex-start !important;
  row-gap: 1.6rem !important;
}
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] {
  min-height: 0 !important;
  padding-top: 0 !important;
}

/* ============================================================
   FILE UPLOADER
   ============================================================ */
[data-testid="stFileUploader"] { background: transparent !important; margin-bottom: 1.4rem !important; }
[data-testid="stFileUploader"] section {
  background: var(--bg) !important;
  border: 1.5px dashed var(--border-mid) !important;
  border-radius: var(--radius-md) !important;
  padding: 1.4rem 1rem !important;
  transition: border-color 0.2s, background 0.2s !important;
}
[data-testid="stFileUploader"] section:hover,
[data-testid="stFileUploader"] section:focus-within {
  border-color: var(--blue) !important;
  background: var(--blue-soft) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.82rem !important;
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
  padding: 0.32rem 1rem !important;
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
  border-radius: 4px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button:hover {
  color: var(--red) !important;
  background: var(--red-bg) !important;
}

/* ============================================================
   LABELS DE SECTION
   ============================================================ */
.section-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.55rem;
  margin-top: 0;
}
.section-label-mt {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--muted);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  margin-bottom: 0.55rem;
  margin-top: 1.4rem;
}

/* ============================================================
   SPECS ROW
   ============================================================ */
.specs-row {
  display: flex;
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  overflow: hidden;
  margin-bottom: 1.4rem;
  background: var(--bg);
}
.spec-cell {
  flex: 1;
  padding: 0.7rem 0.95rem;
  border-right: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.spec-cell:last-child { border-right: none; }
.spec-k {
  font-size: 0.6rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--muted);
}
.spec-v {
  font-size: 0.9rem;
  font-weight: 600;
  color: var(--ink);
  line-height: 1.2;
}

/* ============================================================
   BOUTONS
   ============================================================ */
div.stButton > button {
  width: 100% !important;
  background: var(--blue) !important;
  border: none !important;
  color: var(--white) !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  padding: 0 1.4rem !important;
  height: 42px !important;
  border-radius: var(--radius-pill) !important;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s !important;
  box-shadow: 0 1px 2px rgba(0,104,177,0.2), 0 2px 8px rgba(0,104,177,0.15) !important;
  cursor: pointer !important;
}
div.stButton > button:hover {
  background: var(--blue-dark) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(0,104,177,0.25) !important;
}
div.stButton > button:active { transform: translateY(0) !important; }
div.stButton > button:disabled {
  background: var(--border) !important;
  color: var(--muted) !important;
  box-shadow: none !important;
  cursor: default !important;
  transform: none !important;
}

/* ============================================================
   BOUTONS DE TÉLÉCHARGEMENT
   ============================================================ */
div.stDownloadButton > button,
div[data-testid="stDownloadButton"] > button {
  width: 100% !important;
  background: var(--green) !important;
  border: none !important;
  color: #fff !important;
  font-family: 'Inter', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.01em;
  padding: 0 1.4rem !important;
  height: 42px !important;
  border-radius: var(--radius-pill) !important;
  transition: background 0.15s, transform 0.1s, box-shadow 0.15s !important;
  box-shadow: 0 1px 2px rgba(22,163,74,0.2), 0 2px 8px rgba(22,163,74,0.15) !important;
}
div.stDownloadButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  background: var(--green-dark) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 12px rgba(22,163,74,0.25) !important;
}
div.stDownloadButton > button:active,
div[data-testid="stDownloadButton"] > button:active { transform: translateY(0) !important; }

div[data-testid="stProgress"] { display: none !important; }

/* ============================================================
   ENCODAGE — spinner + barre
   ============================================================ */
.encoding-wrap {
  display: flex;
  align-items: center;
  gap: 0.7rem;
  padding: 0.6rem 0;
  margin: 0.5rem 0;
}
.encoding-ring {
  width: 16px; height: 16px;
  border: 2px solid var(--border);
  border-top-color: var(--blue);
  border-radius: 50%;
  flex-shrink: 0;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.encoding-text { font-size: 0.8rem; color: var(--sub); font-weight: 500; }

.fake-progress-wrap { margin: 0.6rem 0 0.4rem; }
.fake-progress-track {
  height: 3px;
  background: var(--border);
  border-radius: 99px;
  overflow: hidden;
}
.fake-progress-bar {
  height: 100%;
  border-radius: 99px;
  background: linear-gradient(90deg, var(--blue-soft), var(--blue), var(--blue-soft));
  background-size: 200% 100%;
  animation: indeterminate 1.4s ease-in-out infinite;
}
@keyframes indeterminate {
  0% { background-position: 200% center; }
  100% { background-position: -200% center; }
}

/* ============================================================
   STATUTS
   ============================================================ */
.status {
  font-size: 0.78rem;
  padding: 0.55rem 0;
  margin: 0.5rem 0;
  color: var(--muted);
  line-height: 1.5;
}
.status-ok   { color: var(--green); font-weight: 500; }
.status-err  { color: var(--red); font-weight: 500; }
.status-idle { color: var(--muted); }

div[data-testid="stSpinner"] p {
  font-size: 0.78rem !important;
  color: var(--muted) !important;
  font-family: 'Inter', sans-serif !important;
}

/* ============================================================
   NUMBER INPUT
   ============================================================ */
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
  border-radius: 6px !important;
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
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-soft) !important;
}
[data-testid="stNumberInput"] input:focus { outline: none !important; box-shadow: none !important; }

/* ============================================================
   SELECT BOX
   ============================================================ */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--blue) !important; }

/* ============================================================
   TEXT INPUT / TEXTAREA / RADIO
   ============================================================ */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border-color: var(--border) !important;
  border-radius: var(--radius-sm) !important;
  font-size: 0.85rem !important;
  font-family: 'Inter', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 3px var(--blue-soft) !important;
}
[data-testid="stRadio"] label { font-size: 0.85rem !important; }

/* ============================================================
   LISTE PHOTO IMPORTÉE
   ============================================================ */
.photo-batch-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  margin-bottom: 0.4rem;
  background: var(--bg);
  font-size: 0.78rem;
  color: var(--ink);
}
.photo-batch-name {
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.photo-batch-dim {
  font-size: 0.7rem;
  color: var(--muted);
  flex-shrink: 0;
  margin-left: 0.5rem;
}

/* ============================================================
   PLACEHOLDER APERÇU
   ============================================================ */
.preview-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-direction: column;
  gap: 0.7rem;
  min-height: 280px;
  border: 1.5px dashed var(--border-mid);
  border-radius: var(--radius-lg);
  background: var(--bg);
  color: var(--muted);
  font-size: 0.82rem;
  text-align: center;
  margin-top: 1.8rem;
  font-weight: 500;
}
.preview-placeholder svg { opacity: 0.3; }

/* ============================================================
   RESPONSIVE — tablette
   ============================================================ */
@media (max-width: 900px) {
  .block-container { padding: 0 1.5rem 2rem !important; }
  .specs-row { flex-wrap: wrap !important; }
  .spec-cell {
    flex: 1 1 45% !important;
    border-bottom: 1px solid var(--border);
  }
}

/* ============================================================
   RESPONSIVE — mobile
   ============================================================ */
@media (max-width: 640px) {
  :root { --header-h: 58px; }
  .block-container { padding: 0 1rem 1.5rem !important; }

  .site-header img { height: 28px; }
  .site-header-right { display: none; }

  div[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size: 0.8rem !important;
    padding: 0.6rem 1.1rem 0.6rem 0 !important;
  }
  div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding-top: 1.2rem !important; }

  [data-testid="stHorizontalBlock"] { row-gap: 1.25rem !important; }

  .specs-row { flex-wrap: wrap !important; }
  .spec-cell {
    flex: 1 1 50% !important;
    border-right: 1px solid var(--border) !important;
  }
  .spec-cell:nth-child(2n) { border-right: none !important; }
  .spec-cell:nth-last-child(-n+2) { border-bottom: none; }

  div.stButton > button,
  div.stDownloadButton > button,
  div[data-testid="stDownloadButton"] > button {
    height: 44px !important;
    font-size: 0.88rem !important;
  }

  .preview-placeholder { min-height: 200px; margin-top: 1rem; }
}
</style>
""",
    unsafe_allow_html=True,
)

import base64 as _b64h

with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()
st.markdown(
    f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">version <code>1.2</code></span>
</div>
""",
    unsafe_allow_html=True,
)

PREVIEW_MAX_W = 680
PREVIEW_MAX_H = 500


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
    return img.resize((w, h), Image.LANCZOS)


def get_default_logo() -> str:
    return DEFAULT_WM_FILE


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
) -> tuple[int, int]:
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


def get_video_info(path: str) -> dict:
    import json as _json

    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,tags=rotate",
        "-show_entries", "stream_side_data=rotation",
        "-show_entries", "format=duration",
        "-of", "json", path,
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
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-ss", str(timecode), "-i", video_path,
            "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
        ],
        capture_output=True,
    )
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def make_thumbnail(
    video_path: str,
    logo_path: str,
    info: dict,
    position: str = DEFAULT_POSITION,
    custom_x: int = 0,
    custom_y: int = 0,
) -> Image.Image:
    result = subprocess.run(
        [
            "ffmpeg", "-y", "-i", video_path, "-vframes", "1",
            "-f", "image2pipe", "-vcodec", "png", "pipe:1",
        ],
        capture_output=True,
    )
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
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
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo_orig = Image.open(logo_path).convert("RGBA")
    ratio = logo_w / logo_orig.width
    logo_h = int(logo_orig.height * ratio)
    logo_scaled = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)

    tmp_logo_dir = tempfile.mkdtemp()
    tmp_logo_path = os.path.join(tmp_logo_dir, "wm_prescaled.png")
    logo_scaled.save(tmp_logo_path, format="PNG")

    filter_complex = f"[0:v][1:v]overlay={x}:{y}"
    q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-i", tmp_logo_path,
        "-filter_complex", filter_complex,
        "-c:v", "libx264",
        "-crf", q["crf"],
        "-preset", q["preset"],
        "-c:a", "copy",
        "-movflags", "+faststart",
        "-progress", "pipe:1",
        output_path,
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    total = info["duration"]
    while True:
        line = process.stdout.readline()
        if not line:
            break
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


def watermark_options_ui(key_prefix: str) -> dict:
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
# SESSION STATE
# ============================================================
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state:
        st.session_state[k] = None

# ============================================================
# ONGLETS — VID / IMG / RS
# ============================================================
tab_v, tab_p, tab_canva = st.tabs(["WATERMARK VID", "WATERMARK IMG", "TEMPLATE"])

# ============================================================
# ONGLET VID
# ============================================================
with tab_v:
    col_ctrl, col_prev = st.columns([4, 6], gap="large")

    with col_ctrl:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="vu",
            label_visibility="collapsed",
        )

    if video_file:
        if st.session_state._last_video_name != video_file.name:
            st.session_state.thumbnail = None
            st.session_state.rendered_bytes = None
            st.session_state._last_video_name = video_file.name

        lp = get_default_logo()
        tmp = tempfile.mkdtemp()
        vp = os.path.join(tmp, "src" + os.path.splitext(video_file.name)[1])
        with open(vp, "wb") as f:
            f.write(video_file.read())
        nfo = get_video_info(vp)

        with col_ctrl:
            st.markdown(
                f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo['duration'])}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo['fps']}</span></div>
            </div>""",
                unsafe_allow_html=True,
            )

            wm_opts = watermark_options_ui("v")

            st.markdown(
                '<p class="section-label-mt">Qualité d\'export</p>',
                unsafe_allow_html=True,
            )
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

            if st.session_state.thumbnail is None:
                with st.spinner("Génération de l'aperçu…"):
                    st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, **wm_opts)

            st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)
            if not st.session_state.rendered_bytes:
                if st.button("Générer le rendu", key="vbtn"):
                    out = os.path.join(tmp, "video_ready_to_post.mp4")
                    ph = st.empty()
                    ph.markdown(
                        '<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Encodage en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',
                        unsafe_allow_html=True,
                    )
                    try:
                        render_video(vp, lp, out, nfo, quality_key=quality_key, **wm_opts)
                        ph.empty()
                        with open(out, "rb") as f:
                            st.session_state.rendered_bytes = f.read()
                        st.rerun()
                    except Exception as e:
                        ph.markdown(
                            f'<div class="status status-err">Erreur : {e}</div>',
                            unsafe_allow_html=True,
                        )
            else:
                st.download_button(
                    "↓  Télécharger la vidéo",
                    data=st.session_state.rendered_bytes,
                    file_name="video_ready_to_post.mp4",
                    mime="video/mp4",
                    key="vdl",
                )

        with col_prev:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            st.image(cap_image_for_preview(st.session_state.thumbnail))

    else:
        with col_ctrl:
            st.markdown(
                '<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',
                unsafe_allow_html=True,
            )
        with col_prev:
            st.markdown(
                """
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",
                unsafe_allow_html=True,
            )

# ============================================================
# ONGLET IMG
# ============================================================
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
            st.markdown(
                '<p class="section-label-mt">Fichiers importés</p>',
                unsafe_allow_html=True,
            )
            for pf in photo_files:
                img_tmp = Image.open(pf)
                W_tmp, H_tmp = img_tmp.size
                pf.seek(0)
                st.markdown(
                    f'<div class="photo-batch-item">'
                    f'<span class="photo-batch-name">{pf.name}</span>'
                    f'<span class="photo-batch-dim">{W_tmp} × {H_tmp} px</span>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

            wm_opts_p = watermark_options_ui("p")

        def build_photo_output(pf, opts):
            pf.seek(0)
            base = Image.open(pf)
            result = composite_logo(base, lp2, **opts)
            buf = io.BytesIO()
            ext = pf.name.rsplit(".", 1)[-1].lower()
            if ext == "png":
                result.save(buf, format="PNG")
                return (buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.png", "image/png")
            else:
                result.convert("RGB").save(buf, format="JPEG", quality=100, subsampling=0)
                return (buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.jpg", "image/jpeg")

        with col_prev_p:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            grid_cols = st.columns(2)
            for idx, pf in enumerate(photo_files):
                pf.seek(0)
                base_prev = Image.open(pf)
                result_prev = composite_logo(base_prev, lp2, **wm_opts_p)
                with grid_cols[idx % 2]:
                    st.image(
                        cap_image_for_preview(result_prev.convert("RGB")),
                        caption=pf.name,
                        use_container_width=True,
                    )

        with col_ctrl_p:
            if len(photo_files) == 1:
                data, fname, mime = build_photo_output(photo_files[0], wm_opts_p)
                st.download_button(
                    "↓  Télécharger la photo",
                    data=data,
                    file_name=fname,
                    mime=mime,
                    key="pdl_single",
                )
            else:
                st.markdown(
                    '<p class="section-label-mt">Téléchargement</p>',
                    unsafe_allow_html=True,
                )

                for i in range(0, len(photo_files), 2):
                    row_files = photo_files[i : i + 2]
                    btn_cols = st.columns(len(row_files), gap="small")
                    for j, pf in enumerate(row_files):
                        data, fname, mime = build_photo_output(pf, wm_opts_p)
                        with btn_cols[j]:
                            st.download_button(
                                f"↓  {pf.name}",
                                data=data,
                                file_name=fname,
                                mime=mime,
                                key=f"pdl_{i + j}",
                            )

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
            st.markdown(
                '<div class="status status-idle">Déposez une ou plusieurs images via <i>Upload</i>.</div>',
                unsafe_allow_html=True,
            )
        with col_prev_p:
            st.markdown(
                """
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",
                unsafe_allow_html=True,
            )

# ============================================================
# ONGLET RS (Template réseaux sociaux)
# ============================================================
with tab_canva:
    try:
        with open(DEFAULT_WM_FILE, "rb") as _wm_f:
            _wm_b64_canva = _b64h.b64encode(_wm_f.read()).decode()
        _wm_mime_canva = "image/png"
    except Exception:
        _wm_b64_canva = ""
        _wm_mime_canva = "image/png"

    col_ctrl_cv, col_prev_cv = st.columns([4, 6], gap="large")

    st.markdown(
        """
    <style>
    [data-testid="stSlider"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }
    [data-testid="stSlider"] > div { padding-bottom: 0 !important; }
    [data-testid="stColorPicker"] { margin-bottom: 0 !important; }
    [data-testid="stColorPicker"] label { font-size: 0.72rem !important; margin-bottom: 2px !important; }
    </style>
    """,
        unsafe_allow_html=True,
    )

    _CV_DEFAULTS = {"canva_y": 72, "canva_imgzoom": 100}
    for _k, _v in _CV_DEFAULTS.items():
        if _k not in st.session_state:
            st.session_state[_k] = _v

    if st.session_state.get("_cv_reset_y"):
        st.session_state["canva_y"] = _CV_DEFAULTS["canva_y"]
        st.session_state["_cv_reset_y"] = False
    if st.session_state.get("_cv_reset_zoom"):
        st.session_state["canva_imgzoom"] = _CV_DEFAULTS["canva_imgzoom"]
        st.session_state["_cv_reset_zoom"] = False

    with col_ctrl_cv:
        _cr1, _cr2, _cr3 = st.columns(3)
        with _cr1:
            st.markdown('<p class="section-label">Arrière-plan</p>', unsafe_allow_html=True)
            canva_bg_file = st.file_uploader(
                "Déposez votre image ici",
                type=["png", "jpg", "jpeg", "webp"],
                key="canva_bg",
                label_visibility="collapsed",
            )
        with _cr2:
            st.markdown('<p class="section-label">Format</p>', unsafe_allow_html=True)
            canva_format = st.selectbox(
                "Format",
                [
                    "1080×1350 — Portrait",
                    "1080×1080 — Carré",
                    "1080×1920 — Stories",
                ],
                key="canva_format",
                label_visibility="collapsed",
            )
        with _cr3:
            st.markdown('<p class="section-label">Watermark</p>', unsafe_allow_html=True)
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

        _fmt_map = {
            "1080×1350 — Portrait": (1080, 1350),
            "1080×1080 — Carré": (1080, 1080),
            "1080×1920 — Stories": (1080, 1920),
        }
        canva_w, canva_h = _fmt_map[canva_format]

        _canva_offset_sig = (canva_bg_file.name if canva_bg_file else None, canva_format)
        if st.session_state.get("_canva_offset_sig") != _canva_offset_sig:
            st.session_state["canva_offset"] = "0,0"
            st.session_state["_canva_offset_sig"] = _canva_offset_sig
        if "canva_offset" not in st.session_state:
            st.session_state["canva_offset"] = "0,0"

        st.markdown(
            """<style>
        div[data-testid="stTextInput"]:has(input[aria-label="canva_offset_bridge"]) {
          position:fixed !important; top:-9999px !important; left:-9999px !important;
          width:1px !important; height:1px !important; min-height:0 !important;
          overflow:hidden !important; opacity:0 !important; margin:0 !important; padding:0 !important;
        }
        </style>""",
            unsafe_allow_html=True,
        )
        canva_offset_raw = st.text_input(
            "canva_offset_bridge", key="canva_offset", label_visibility="collapsed"
        )
        try:
            _cox_s, _coy_s = canva_offset_raw.split(",")
            canva_off_x = float(_cox_s)
            canva_off_y = float(_coy_s)
        except Exception:
            canva_off_x, canva_off_y = 0.0, 0.0

        st.markdown('<p class="section-label">Surtitre</p>', unsafe_allow_html=True)
        canva_sur = st.text_input(
            "Surtitre",
            value="Modifier le surtitre",
            key="canva_sur",
            label_visibility="collapsed",
        )

        st.markdown('<p class="section-label">Titre principal</p>', unsafe_allow_html=True)
        canva_title = st.text_area(
            "Titre",
            value="Modifier le titre (il est possible de faire des retours à la ligne grâce à la touche Entrée)",
            key="canva_title",
            label_visibility="collapsed",
            height=80,
        )

        canva_block_color = "#0068B1"
        canva_text_color = "#ffffff"
        canva_sur_bg = "#ffffff"
        canva_sur_color = "#0068B1"

        st.markdown(
            '<p class="section-label" style="margin-top:10px;">Position du texte</p>',
            unsafe_allow_html=True,
        )
        canva_y = st.slider(
            "Position Y",
            min_value=5,
            max_value=95,
            key="canva_y",
            label_visibility="collapsed",
        )

        if canva_bg_file:
            st.markdown(
                '<p class="section-label" style="margin-top:6px;">Zoom photo</p>',
                unsafe_allow_html=True,
            )
            canva_img_zoom = st.slider(
                "Zoom photo",
                min_value=100,
                max_value=300,
                key="canva_imgzoom",
                label_visibility="collapsed",
            )
        else:
            canva_img_zoom = 100

        canva_wm_size = 13
        canva_wm_opac = 100

        st.markdown("<div style='margin-top:1.2rem;'></div>", unsafe_allow_html=True)

        st.markdown(
            """
<div style="margin-top:1.2rem; padding:0.85rem 1.1rem; background:#e8f2fb; border:1px solid #cfe3f5; border-radius:10px; font-size:0.82rem; color:#0068B1; line-height:1.6;">
  Pour télécharger le visuel, <b>faites un clic droit sur l'aperçu</b> puis sélectionnez <code>Enregistrer l'image sous…</code>
</div>""",
            unsafe_allow_html=True,
        )

    with col_prev_cv:
        st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)

        if not canva_bg_file:
            st.markdown(
                """
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>Glissez une image pour voir l'aperçu</span>
            </div>""",
                unsafe_allow_html=True,
            )
        else:
            canva_bg_file.seek(0)
            _canva_bg_b64 = _b64h.b64encode(canva_bg_file.read()).decode()
            _ext = canva_bg_file.name.rsplit(".", 1)[-1].lower()
            _canva_bg_mime = (
                "image/png"
                if _ext == "png"
                else ("image/webp" if _ext == "webp" else "image/jpeg")
            )

            import json as _json

            _js_title = _json.dumps(canva_title)
            _js_sur = _json.dumps(canva_sur)

            _preview_h = min(700, int(560 * canva_h / canva_w))
            components.html(
                f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8">
<style>
  html,body{{margin:0;padding:0;background:#eef1f5;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:8px;box-sizing:border-box;height:100%;overflow:hidden;}}
  #canvasWrap{{box-shadow:0 4px 24px rgba(0,0,0,0.18);display:inline-block;}}
  canvas{{display:block;}}
</style>
</head>
<body>
<div id="canvasWrap"><canvas id="c"></canvas></div>
<script>
const CANVAS_W = {canva_w};
const CANVAS_H = {canva_h};
const BG_B64   = "{_canva_bg_b64}";
const BG_MIME  = "{_canva_bg_mime}";
const WM_B64   = "{_wm_b64_canva}";
const WM_MIME  = "{_wm_mime_canva}";
const TITLE    = {_js_title};
const SURTITRE = {_js_sur};
const Y_PCT    = {canva_y} / 100;
const X_PCT    = 50 / 100;
const IMG_ZOOM = {canva_img_zoom} / 100;
const BLOCK_COLOR = "{canva_block_color}";
const TEXT_COLOR  = "{canva_text_color}";
const SUR_BG      = "{canva_sur_bg}";
const SUR_COLOR   = "{canva_sur_color}";
const WM_SIZE_PCT = 13 / 100;
const WM_OPAC     = 1.0;
const WM_POS      = "{wm_opts_cv["position"]}";
const WM_CX       = {wm_opts_cv["custom_x"]};
const WM_CY       = {wm_opts_cv["custom_y"]};
const MARGIN_R    = 0.04;
const INIT_OFF_X  = {canva_off_x};
const INIT_OFF_Y  = {canva_off_y};

const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');

const AVAIL_H   = {_preview_h} - 52;
const PREVIEW_W = Math.min(Math.floor(AVAIL_H * CANVAS_W / CANVAS_H), window.innerWidth - 20);
const UI_ZOOM   = PREVIEW_W / CANVAS_W;
canvas.width  = CANVAS_W;
canvas.height = CANVAS_H;
canvas.style.width  = (CANVAS_W * UI_ZOOM) + 'px';
canvas.style.height = (CANVAS_H * UI_ZOOM) + 'px';

let bgImg = null, wmImg = null;
let bgOffX = INIT_OFF_X, bgOffY = INIT_OFF_Y;
let isDragging = false, dragSX, dragSY, dragBX, dragBY;

function clampOffset() {{
  if (!bgImg) return;
  const scaleX = CANVAS_W / bgImg.naturalWidth;
  const scaleY = CANVAS_H / bgImg.naturalHeight;
  const base   = Math.max(scaleX, scaleY) * IMG_ZOOM;
  const dw = bgImg.naturalWidth  * base;
  const dh = bgImg.naturalHeight * base;
  const maxOffX = dw / 2 - CANVAS_W / 2;
  const maxOffY = dh / 2 - CANVAS_H / 2;
  bgOffX = Math.max(-maxOffX, Math.min(maxOffX, bgOffX));
  bgOffY = Math.max(-maxOffY, Math.min(maxOffY, bgOffY));
}}

function roundRect(c, x, y, w, h, r, fill) {{
  c.beginPath();
  c.moveTo(x+r,y); c.lineTo(x+w-r,y); c.arcTo(x+w,y,x+w,y+r,r);
  c.lineTo(x+w,y+h-r); c.arcTo(x+w,y+h,x+w-r,y+h,r);
  c.lineTo(x+r,y+h); c.arcTo(x,y+h,x,y+h-r,r);
  c.lineTo(x,y+r); c.arcTo(x,y,x+r,y,r);
  c.closePath(); c.fillStyle=fill; c.fill();
}}

function render() {{
  ctx.clearRect(0,0,CANVAS_W,CANVAS_H);
  ctx.fillStyle='#222'; ctx.fillRect(0,0,CANVAS_W,CANVAS_H);

  if (bgImg) {{
    const scaleX = CANVAS_W / bgImg.naturalWidth;
    const scaleY = CANVAS_H / bgImg.naturalHeight;
    const base   = Math.max(scaleX, scaleY) * IMG_ZOOM;
    const dw = bgImg.naturalWidth  * base;
    const dh = bgImg.naturalHeight * base;
    const dx = (CANVAS_W - dw) / 2 + bgOffX;
    const dy = (CANVAS_H - dh) / 2 + bgOffY;
    ctx.drawImage(bgImg, dx, dy, dw, dh);
  }}

  const fs     = Math.round(CANVAS_W * 0.056);
  const fsSur  = Math.round(CANVAS_W * 0.043);
  const pad    = Math.round(CANVAS_W * 0.017);
  const radius = Math.round(CANVAS_W * 0.019);
  const lh     = Math.round(fs * 1.25);
  const overlap= Math.round(CANVAS_W * 0.003);
  const cx     = X_PCT * CANVAS_W;

  function wrapSegment(text, maxLen) {{
    const words = text.split(' ');
    const segs = []; let cur = '';
    words.forEach(function(w) {{
      if ((cur+w).length < maxLen) {{ cur += (cur?' ':'')+w; }}
      else {{ if(cur) segs.push(cur); cur=w; }}
    }});
    if(cur) segs.push(cur);
    return segs.length ? segs : [''];
  }}
  const lines = [];
  TITLE.split('\\n').forEach(function(seg) {{
    var wrapped = wrapSegment(seg, 34);
    for(var _i=0;_i<wrapped.length;_i++) lines.push(wrapped[_i]);
  }});

  ctx.font = `bold ${{fs}}px 'Inter','Roboto Condensed',sans-serif`;
  const lineWidths = lines.map(l => ctx.measureText(l).width + pad*2);

  ctx.font = `bold ${{fsSur}}px 'Inter',sans-serif`;
  const surW = ctx.measureText(SURTITRE).width + pad*2;
  const surH = fsSur + Math.round(pad*0.8);

  const totalH  = lh * lines.length;
  const blockTop = CANVAS_H * Y_PCT - totalH/2;

  const off = document.createElement('canvas');
  off.width = CANVAS_W; off.height = CANVAS_H;
  const octx = off.getContext('2d');
  octx.font = `bold ${{fs}}px 'Inter','Roboto Condensed',sans-serif`;
  lines.forEach((line,i) => {{
    const lw = lineWidths[i];
    const lx = cx - lw/2;
    const ly = blockTop + i*lh - (i>0?overlap:0);
    roundRect(octx, lx, ly, lw, lh+overlap, radius, BLOCK_COLOR);
  }});

  const off2 = document.createElement('canvas');
  off2.width=CANVAS_W; off2.height=CANVAS_H;
  const o2=off2.getContext('2d');
  o2.filter='blur(10px)';
  o2.drawImage(off,0,0);
  o2.filter='none';
  const id=o2.getImageData(0,0,CANVAS_W,CANVAS_H);
  const px=id.data;
  const [br,bg2,bb] = hexToRgb(BLOCK_COLOR);
  for(let i=0;i<px.length;i+=4){{
    if(px[i+3]>60){{ px[i]=br; px[i+1]=bg2; px[i+2]=bb; px[i+3]=255; }}
    else px[i+3]=0;
  }}
  o2.putImageData(id,0,0);
  ctx.drawImage(off2,0,0);

  const surX = cx - surW/2;
  const surY = blockTop - surH - Math.round(CANVAS_W*-0.000);
  roundRect(ctx, surX, surY, surW, surH, radius, SUR_BG);
  ctx.fillStyle = SUR_COLOR;
  ctx.font = `bold ${{fsSur}}px 'Inter',sans-serif`;
  ctx.textAlign='left'; ctx.textBaseline='middle';
  ctx.fillText(SURTITRE, surX+pad, surY+surH/2);

  ctx.font = `bold ${{fs}}px 'Inter','Roboto Condensed',sans-serif`;
  ctx.fillStyle = TEXT_COLOR;
  ctx.textAlign='left'; ctx.textBaseline='middle';
  lines.forEach((line,i)=>{{
    const lw=lineWidths[i];
    const lx=cx-lw/2;
    const ly=blockTop+i*lh-(i>0?overlap:0);
    ctx.fillText(line, lx+pad, ly+lh/2);
  }});

  if(wmImg) {{
    const diag = Math.sqrt(CANVAS_W**2+CANVAS_H**2);
    const wmW  = diag * WM_SIZE_PCT;
    const wmH  = (wmImg.naturalHeight/wmImg.naturalWidth)*wmW;
    const mx   = CANVAS_W*MARGIN_R, my=CANVAS_H*MARGIN_R;
    let wx,wy;
    const posMap={{
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
    }};
    [wx,wy] = posMap[WM_POS] || [CANVAS_W-wmW-mx, CANVAS_H-wmH-my];
    ctx.globalAlpha = WM_OPAC;
    ctx.drawImage(wmImg, wx, wy, wmW, wmH);
    ctx.globalAlpha = 1.0;
  }}
}}

function hexToRgb(hex) {{
  const r=parseInt(hex.slice(1,3),16);
  const g=parseInt(hex.slice(3,5),16);
  const b=parseInt(hex.slice(5,7),16);
  return [r,g,b];
}}

let loaded = 0;
const toLoad = (BG_B64?1:0) + (WM_B64?1:0);
function onLoad() {{ loaded++; if(loaded>=toLoad||toLoad===0) {{ clampOffset(); render(); }} }}
if(!toLoad) render();

if(BG_B64){{
  bgImg = new Image();
  bgImg.onload = onLoad;
  bgImg.src = 'data:'+BG_MIME+';base64,'+BG_B64;
}}
if(WM_B64){{
  wmImg = new Image();
  wmImg.onload = onLoad;
  wmImg.src = 'data:'+WM_MIME+';base64,'+WM_B64;
}}

canvas.addEventListener('mousedown', e=>{{
  if(!bgImg) return;
  isDragging=true; dragSX=e.clientX; dragSY=e.clientY; dragBX=bgOffX; dragBY=bgOffY;
  canvas.style.cursor='grabbing';
}});
window.addEventListener('mousemove', e=>{{
  if(!isDragging) return;
  const scale = 1/UI_ZOOM;
  bgOffX = dragBX+(e.clientX-dragSX)*scale;
  bgOffY = dragBY+(e.clientY-dragSY)*scale;
  clampOffset();
  render();
}});
window.addEventListener('mouseup',()=>{{
  if(!isDragging) return;
  isDragging=false;
  canvas.style.cursor=bgImg?'grab':'default';
  syncOffsetToStreamlit();
}});
if(bgImg) canvas.style.cursor='grab';

function syncOffsetToStreamlit() {{
  try {{
    const bridge = window.parent.document.querySelector('input[aria-label="canva_offset_bridge"]');
    if (!bridge) return;
    const newVal = Math.round(bgOffX) + ',' + Math.round(bgOffY);
    if (bridge.value === newVal) return;
    const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLInputElement.prototype, 'value').set;
    bridge.focus();
    nativeInputValueSetter.call(bridge, newVal);
    bridge.dispatchEvent(new Event('input', {{bubbles: true}}));
    bridge.blur();
  }} catch(e) {{}}
}}

</script>
</body>
</html>""",
                height=_preview_h + 52,
                scrolling=False,
            )
