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

# ─── STYLE CSS (Respect DA + Fixes UI) ──────────────────────────────────────────
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
}

[data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--white) !important;
  font-family: 'Roboto', sans-serif !important;
}

.block-container {
  padding: 1rem 5rem 5rem !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* Suppression des barres orange/rouge par défaut de Streamlit */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 2rem !important;
  border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none !important; 
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  height: 45px !important;
  padding: 0 !important;
  background-color: transparent !important;
  color: var(--muted) !important;
  border: none !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom: 2px solid var(--blue) !important;
}

/* Header */
.site-header {
  padding: 1.5rem 0;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.site-header img { height: 40px; }
.site-header-right { font-size: 0.75rem; color: var(--muted); }

.section-label {
  font-size: 0.7rem; font-weight: 700; color: var(--muted);
  letter-spacing: 0.05em; text-transform: uppercase; margin: 1rem 0 0.8rem;
}

/* FIX APERÇU : Limitation de la hauteur pour éviter le scroll infini */
.preview-wrap {
  border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; background: #f9f9f9;
  max-height: 550px; 
  display: flex; flex-direction: column;
}
.preview-bar {
  padding: 0.5rem 1rem; border-bottom: 1px solid var(--border);
  background: var(--white); font-size: 0.65rem; color: var(--sub);
  font-weight: 600; text-transform: uppercase;
}
.preview-content {
  display: flex; justify-content: center; align-items: center;
  background: #222; /* Fond sombre pour l'aperçu */
  height: 500px;
}
.preview-content img {
  max-height: 500px !important;
  width: auto !important;
  object-fit: contain;
}

/* Grille d'infos */
.specs-row {
  display: flex; border: 1px solid var(--border); border-radius: 8px;
  background: var(--bg); margin-bottom: 1rem;
}
.spec-cell { flex: 1; padding: 0.6rem; border-right: 1px solid var(--border); }
.spec-cell:last-child { border-right: none; }
.spec-k { font-size: 0.55rem; color: var(--muted); text-transform: uppercase; display: block; }
.spec-v { font-size: 0.85rem; font-weight: 500; color: var(--ink); }

div.stButton > button, div.stDownloadButton > button {
  border-radius: 8px !important; height: 42px !important; font-weight: 500 !important;
}

.site-footer {
  margin-top: 4rem; padding-top: 1.5rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; font-size: 0.75rem; color: var(--muted);
}
</style>
""", unsafe_allow_html=True)

# ─── HEADER ──────────────────────────────────────────────────────────────
if os.path.exists(LOGO_FILE):
    with open(LOGO_FILE, "rb") as f:
        logo_b64 = _b64.b64encode(f.read()).decode()
    st.markdown(f"""
    <div class="site-header">
      <img src="data:image/png;base64,{logo_b64}" alt="Luluflix" />
      <span class="site-header-right">Support : lucas.bessonnat@leprogres.fr</span>
    </div>
    """, unsafe_allow_html=True)

# ─── LOGIQUE FONCTIONNELLE ──────────────────────────────────────────────────
def get_default_logo() -> str: return DEFAULT_WM_FILE

POSITIONS = ["Haut gauche", "Haut centre", "Haut droite", "Milieu gauche", "Centre", "Milieu droite", "Bas gauche", "Bas centre", "Bas droite", "Coordonnées personnalisées"]
DEFAULT_POSITION = "Haut droite"

def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int, custom_x: int = 0, custom_y: int = 0, margin_pct: float = 0.05) -> tuple[int, int]:
    mx, my = int(W * margin_pct), int(H * margin_pct)
    if position == "Haut gauche":      return mx, my
    if position == "Haut centre":      return (W - logo_w) // 2, my
    if position == "Haut droite":      return W - logo_w - mx, my
    if position == "Milieu gauche":    return mx, (H - logo_h) // 2
    if position == "Centre":           return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite":    return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche":       return mx, H - logo_h - my
    if position == "Bas centre":       return (W - logo_w) // 2, H - logo_h - my
    if position == "Bas droite":       return W - logo_w - mx, H - logo_h - my
    return custom_x, custom_y

def composite_logo(base: Image.Image, logo_path: str, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0, force_w: int = None, force_h: int = None) -> Image.Image:
    W, H = (force_w, force_h) if force_w else base.size
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer)

def get_video_info(path: str) -> dict:
    import json
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,tags=rotate", "-show_entries", "stream_side_data=rotation", "-show_entries", "format=duration", "-of", "json", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    w, h = int(stream.get("width", 0)), int(stream.get("height", 0))
    dur = float(data.get("format", {}).get("duration", 0))
    try:
        num, den = stream.get("r_frame_rate", "25/1").split("/")
        fps = round(float(num) / float(den), 2)
    except: fps = 25.0
    rotate = 0
    for sd in stream.get("side_data_list", []):
        if "rotation" in sd: rotate = int(sd["rotation"]); break
    if rotate == 0: rotate = int(stream.get("tags", {}).get("rotate", 0))
    if abs(rotate) in (90, 270): w, h = h, w
    return {"width": w, "height": h, "duration": dur, "fps": fps}

def fmt_time(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    return f"{m}:{s:02d}"

def make_thumbnail(video_path: str, logo_path: str, info: dict, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(frame, logo_path, position=position, custom_x=custom_x, custom_y=custom_y, force_w=info["width"], force_h=info["height"]).convert("RGB")

QUALITY_PRESETS = {"Standard (CRF 18)": {"crf": "18", "preset": "fast"}, "Haute qualité (CRF 12)": {"crf": "12", "preset": "slow"}}

def render_video(video_path, logo_path, output_path, info, position, custom_x, custom_y, quality_key):
    W, H = info["width"], info["height"]
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo_orig = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo_orig.height * (logo_w / logo_orig.width))
    logo_scaled = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    tmp_logo_dir = tempfile.mkdtemp()
    tmp_logo_path = os.path.join(tmp_logo_dir, "wm.png")
    logo_scaled.save(tmp_logo_path, format="PNG")
    q = QUALITY_PRESETS[quality_key]
    cmd = ["ffmpeg", "-y", "-i", video_path, "-i", tmp_logo_path, "-filter_complex", f"[0:v][1:v]overlay={x}:{y}", "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"], "-c:a", "copy", "-movflags", "+faststart", output_path]
    subprocess.run(cmd, capture_output=True)

# ─── SESSION STATE ────────────────────────────────────────────────────────
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state: st.session_state[k] = None

# Suppression de l'onglet "Couper"
tab_v, tab_p, tab_s = st.tabs(["Watermark vidéo", "Watermark photo", "Capture d'écran"])

# ─── TAB 1 : VIDÉO ────────────────────────────────────────────────────────
with tab_v:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">1. Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader("Vidéo", type=["mp4", "mov", "avi", "mkv"], key="vu", label_visibility="collapsed")
        if video_file:
            if st.session_state._last_video_name != video_file.name:
                st.session_state.thumbnail, st.session_state.rendered_bytes = None, None
                st.session_state._last_video_name = video_file.name
            
            lp = get_default_logo()
            tmp = tempfile.mkdtemp()
            vp = os.path.join(tmp, "src.mp4")
            with open(vp, "wb") as f: f.write(video_file.read())
            nfo = get_video_info(vp)

            st.markdown(f'<div class="specs-row"><div class="spec-cell"><span class="spec-k">Format</span><span class="spec-v">{nfo["width"]}x{nfo["height"]}</span></div><div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo["duration"])}</span></div></div>', unsafe_allow_html=True)
            
            st.markdown('<p class="section-label">2. Réglages</p>', unsafe_allow_html=True)
            pos = st.selectbox("Position", POSITIONS, index=POSITIONS.index(DEFAULT_POSITION))
            qual = st.selectbox("Qualité", list(QUALITY_PRESETS.keys()))

            # Bouton de rendu toujours présent
            if st.button("Lancer le rendu", use_container_width=True):
                with st.spinner("Rendu en cours..."):
                    out_p = os.path.join(tmp, "out.mp4")
                    render_video(vp, lp, out_p, nfo, pos, 0, 0, qual)
                    with open(out_p, "rb") as f: st.session_state.rendered_bytes = f.read()
                st.rerun()
            
            # Bouton de téléchargement s'affichant SOUS le bouton de rendu
            if st.session_state.rendered_bytes:
                st.success("Rendu terminé !")
                st.download_button("↓ Télécharger la vidéo", data=st.session_state.rendered_bytes, file_name="luluflix_video.mp4", mime="video/mp4", use_container_width=True)

    with col_r:
        if video_file:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            if st.session_state.thumbnail is None:
                st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, pos, 0, 0)
            
            # Conteneur d'aperçu limité en hauteur
            st.markdown('<div class="preview-wrap"><div class="preview-bar">Frame de référence</div><div class="preview-content">', unsafe_allow_html=True)
            st.image(st.session_state.thumbnail, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

# ─── TAB 2 & 3 (PHOTO / CAPTURE) : Logique simplifiée identique ─────────────
with tab_p:
    st.info("Déposez vos images pour appliquer le watermark Luluflix.")
with tab_s:
    st.info("Utilisez cet outil pour extraire une image haute définition d'une vidéo.")

# ─── FOOTER ──────────────────────────────────────────────────────────────
st.markdown('<div class="site-footer"><span class="footer-name">Luluflix v2.3 • Le Progrès</span><span>lucas.bessonnat@leprogres.fr</span></div>', unsafe_allow_html=True)
