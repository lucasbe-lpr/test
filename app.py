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

# --- CONFIGURATION ---
LOGO_FILE       = "luluflix.png"
DEFAULT_WM_FILE = "lpr.png"
FAVICON_FILE    = "favicon.png"

try:
    _fav_img = Image.open(FAVICON_FILE)
except Exception:
    _fav_img = "▶"

st.set_page_config(
    page_title="Luluflix | Professional Watermarking",
    page_icon=_fav_img,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --- STYLE CSS AVANCÉ ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --blue:      #0068B1;
  --blue-hover: #005691;
  --blue-soft:  #eef6fc;
  --white:      #ffffff;
  --bg:         #f8fafc;
  --ink:        #0f172a;
  --sub:        #475569;
  --muted:      #94a3b8;
  --border:     #e2e8f0;
  --success:    #10b981;
  --shadow:     0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  --card-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.05);
}

/* Base resets */
.main {
    background-color: var(--bg) !important;
}

div[data-testid="stAppViewContainer"] {
    background-color: var(--bg) !important;
    font-family: 'Inter', sans-serif !important;
}

.block-container {
    padding: 2rem 5rem !important;
}

/* Header & Branding */
.site-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 0;
    margin-bottom: 2rem;
    border-bottom: 1px solid var(--border);
}

.site-header img {
    height: 42px;
}

/* Tabs Styling */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: 8px !important;
    background-color: transparent !important;
}

div[data-testid="stTabs"] [data-baseweb="tab"] {
    height: 45px !important;
    border-radius: 8px 8px 0 0 !important;
    padding: 0 24px !important;
    background-color: transparent !important;
    color: var(--muted) !important;
    border: none !important;
    transition: all 0.2s ease !important;
}

div[data-testid="stTabs"] [aria-selected="true"] {
    background-color: var(--white) !important;
    color: var(--blue) !important;
    box-shadow: var(--shadow) !important;
    font-weight: 600 !important;
}

/* Card Styling for columns */
[data-testid="column"] {
    background: var(--white);
    padding: 2rem !important;
    border-radius: 12px;
    border: 1px solid var(--border);
    box-shadow: var(--card-shadow);
}

/* Custom File Uploader */
[data-testid="stFileUploader"] section {
    background-color: var(--bg) !important;
    border: 2px dashed var(--border) !important;
    border-radius: 12px !important;
    padding: 2rem !important;
}

[data-testid="stFileUploader"] section:hover {
    border-color: var(--blue) !important;
    background-color: var(--blue-soft) !important;
}

/* Buttons UI */
div.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, var(--blue) 0%, #004e85 100%) !important;
    border: none !important;
    color: white !important;
    padding: 12px 24px !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 12px rgba(0, 104, 177, 0.2) !important;
}

div.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 15px rgba(0, 104, 177, 0.3) !important;
}

div.stDownloadButton > button {
    width: 100% !important;
    background: var(--success) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Specs & Details */
.specs-row {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 12px;
    margin: 1.5rem 0;
}

.spec-cell {
    background: var(--bg);
    padding: 12px;
    border-radius: 8px;
    border: 1px solid var(--border);
}

.spec-k {
    font-size: 0.7rem;
    color: var(--muted);
    text-transform: uppercase;
    font-weight: 700;
}

.spec-v {
    font-size: 1rem;
    color: var(--ink);
    font-weight: 600;
}

/* Preview Wrap */
.preview-wrap {
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
    background: #000;
}

.preview-bar {
    background: var(--white);
    padding: 8px 16px;
    border-bottom: 1px solid var(--border);
    font-size: 0.75rem;
    color: var(--sub);
    font-weight: 600;
}

/* Status & Typography */
h3 {
    color: var(--ink) !important;
    font-weight: 700 !important;
    margin-bottom: 1.5rem !important;
}

.section-label {
    font-weight: 600;
    color: var(--ink);
    margin-bottom: 8px;
    display: block;
}

</style>
""", unsafe_allow_html=True)

# --- HEADER ---
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64.b64encode(_f.read()).decode()

st.markdown(f"""
<div class="site-header">
    <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
    <div style="text-align: right">
        <span style="display:block; font-weight:700; color:var(--ink); font-size:1.1rem;">Studio Watermark</span>
        <span style="color:var(--muted); font-size:0.8rem;">V 2.1 — Professional Edition</span>
    </div>
</div>
""", unsafe_allow_html=True)

# --- LOGIQUE FONCTIONNELLE (RAPPELÉE) ---
PREVIEW_MAX_W = 700
PREVIEW_MAX_H = 500

def cap_image_for_preview(img: Image.Image) -> Image.Image:
    w, h = img.size
    if w > PREVIEW_MAX_W:
        ratio = PREVIEW_MAX_W / w
        w, h = PREVIEW_MAX_W, int(h * ratio)
    if h > PREVIEW_MAX_H:
        ratio = PREVIEW_MAX_H / h
        h, w = PREVIEW_MAX_H, int(w * ratio)
    return img.resize((w, h), Image.LANCZOS)

def get_default_logo() -> str:
    return DEFAULT_WM_FILE

POSITIONS = ["Haut gauche", "Haut centre", "Haut droite", "Milieu gauche", "Centre", "Milieu droite", "Bas gauche", "Bas centre", "Bas droite", "Coordonnées personnalisées"]
DEFAULT_POSITION = "Haut droite"

def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int, custom_x: int = 0, custom_y: int = 0, margin_pct: float = 0.05) -> tuple[int, int]:
    mx, my = int(W * margin_pct), int(H * margin_pct)
    if position == "Haut gauche":   return mx, my
    if position == "Haut centre":   return (W - logo_w) // 2, my
    if position == "Haut droite":   return W - logo_w - mx, my
    if position == "Milieu gauche": return mx, (H - logo_h) // 2
    if position == "Centre":        return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite": return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche":    return mx, H - logo_h - my
    if position == "Bas centre":    return (W - logo_w) // 2, H - logo_h - my
    if position == "Bas droite":    return W - logo_w - mx, H - logo_h - my
    return custom_x, custom_y

def composite_logo(base: Image.Image, logo_path: str, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0, force_w: int = None, force_h: int = None) -> Image.Image:
    W, H = (force_w, force_h) if force_w else base.size
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo = Image.open(logo_path).convert("RGBA")
    ratio = logo_w / logo.width
    logo_h = int(logo.height * ratio)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer)

# --- HELPERS VIDÉO ---
def get_video_info(path: str) -> dict:
    import json as _json
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate", "-show_entries", "format=duration", "-of", "json", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = _json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    fps_raw = stream.get("r_frame_rate", "25/1")
    num, den = fps_raw.split("/")
    return {
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "duration": float(data.get("format", {}).get("duration", 0)),
        "fps": round(float(num) / float(den), 2)
    }

def make_thumbnail(video_path: str, logo_path: str, info: dict, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(frame, logo_path, position=position, custom_x=custom_x, custom_y=custom_y, force_w=info["width"], force_h=info["height"]).convert("RGB")

# --- UI TABS ---
tab_v, tab_p = st.tabs(["🎥 Vidéo", "🖼️ Photo"])

with tab_v:
    col_ctrl, col_prev = st.columns([1, 1.4], gap="large")
    
    with col_ctrl:
        st.markdown("### Configuration")
        video_file = st.file_uploader("Importer une vidéo", type=["mp4", "mov", "avi"], key="v_up")
        
        if video_file:
            # Gestion du fichier temporaire
            tmp = tempfile.mkdtemp()
            vp = os.path.join(tmp, video_file.name)
            with open(vp, "wb") as f: f.write(video_file.read())
            info = get_video_info(vp)
            
            st.markdown(f"""
            <div class="specs-row">
                <div class="spec-cell"><span class="spec-k">Résolution</span><br><span class="spec-v">{info['width']}x{info['height']}</span></div>
                <div class="spec-cell"><span class="spec-k">Durée</span><br><span class="spec-v">{int(info['duration'])}s</span></div>
            </div>
            """, unsafe_allow_html=True)
            
            pos = st.selectbox("Position du logo", POSITIONS, index=2)
            
            if st.button("Lancer le rendu"):
                with st.status("Traitement en cours...", expanded=True):
                    # Simu rendu (votre fonction render_video ici)
                    st.write("Encodage des pixels...")
                    st.write("Fusion du watermark...")
                st.success("Vidéo prête !")

    with col_prev:
        st.markdown("### Aperçu direct")
        if video_file:
            thumb = make_thumbnail(vp, get_default_logo(), info, position=pos)
            st.markdown('<div class="preview-wrap"><div class="preview-bar">FRAME_PREVIEW_001.PNG</div>', unsafe_allow_html=True)
            st.image(cap_image_for_preview(thumb), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("Veuillez uploader une vidéo pour voir l'aperçu.")

# --- FOOTER ---
st.markdown("""
<div style="margin-top: 5rem; padding: 2rem 0; border-top: 1px solid var(--border); text-align: center; color: var(--muted); font-size: 0.8rem;">
    Luluflix © 2024 — Outil de marquage professionnel.
</div>
""", unsafe_allow_html=True)
