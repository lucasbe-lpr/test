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
  <span class="site-header-right">version <code>2.1</code></span>
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
# ONGLETS — VID / IMG / CAPTURE / TEMPLATE
# ============================================================
tab_v, tab_p, tab_s, tab_canva = st.tabs(
    ["WATERMARK VID", "WATERMARK IMG", "CAPTURE D'ÉCRAN", "TEMPLATE"]
)

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
              <div class="spec-cell"><span class="spec-k">Largeur</span
