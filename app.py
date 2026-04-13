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
    layout="wide", # Mode large pour éviter l'étroit
    initial_sidebar_state="collapsed",
)

# ─── STYLE CSS (Respect DA + Fix UI) ──────────────────────────────────────────
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

/* Global resets */
[data-testid="stAppViewContainer"], [data-testid="stMain"] {
  background: var(--white) !important;
  font-family: 'Roboto', sans-serif !important;
}

.block-container {
  padding: 1rem 4rem 5rem !important;
  max-width: 1200px !important;
}

#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

/* Suppression des barres rouges/oranges du menu tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 2rem !important;
  border-bottom: 1px solid var(--border) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
  display: none !important; /* Supprime la barre de focus par défaut */
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

/* Layout Columns */
.section-label {
  font-size: 0.7rem; font-weight: 700; color: var(--muted);
  letter-spacing: 0.05em; text-transform: uppercase; margin: 1rem 0 0.8rem;
}

/* Preview constraints: pour éviter les "3km de long" */
.preview-wrap {
  border: 1px solid var(--border); border-radius: 12px;
  overflow: hidden; background: #f9f9f9;
  max-height: 650px; /* Limite la longueur max de l'aperçu */
  display: flex; flex-direction: column;
}
.preview-bar {
  padding: 0.5rem 1rem; border-bottom: 1px solid var(--border);
  background: var(--white); font-size: 0.65rem; color: var(--sub);
  font-weight: 600; text-transform: uppercase;
}
.preview-content img {
  max-height: 580px !important; /* Hauteur max de l'image interne */
  width: auto !important;
  margin: 0 auto;
  object-fit: contain;
}

/* Elements UI */
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

# ─── LOGIQUE FONCTIONNELLE (STRICTEMENT INCHANGÉE) ───────────────────────────
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

def extract_frame(video_path: str, timecode: float) -> Image.Image:
    result = subprocess.run(["ffmpeg", "-y", "-ss", str(timecode), "-i", video_path, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"], capture_output=True)
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")

def make_thumbnail(video_path: str, logo_path: str, info: dict, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run(["ffmpeg", "-y", "-i", video_path, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(frame, logo_path, position=position, custom_x=custom_x, custom_y=custom_y, force_w=info["width"], force_h=info["height"]).convert("RGB")

QUALITY_PRESETS = {
    "Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)":         {"crf": "12", "preset": "slow"},
}

def render_video(video_path: str, logo_path: str, output_path: str, info: dict, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0, quality_key: str = "Standard (CRF 18 — recommandé)", progress_cb=None):
    W, H = info["width"], info["height"]
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo_orig = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo_orig.height * (logo_w / logo_orig.width))
    logo_scaled = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    tmp_logo_dir = tempfile.mkdtemp()
    tmp_logo_path = os.path.join(tmp_logo_dir, "wm_prescaled.png")
    logo_scaled.save(tmp_logo_path, format="PNG")
    q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])
    cmd = ["ffmpeg", "-y", "-i", video_path, "-i", tmp_logo_path, "-filter_complex", f"[0:v][1:v]overlay={x}:{y}", "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"], "-c:a", "copy", "-movflags", "+faststart", "-progress", "pipe:1", output_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    while True:
        line = process.stdout.readline()
        if not line: break
    process.wait()

def watermark_options_ui(key_prefix: str) -> dict:
    st.markdown('<p class="section-label">Position du watermark</p>', unsafe_allow_html=True)
    position = st.selectbox("Position", POSITIONS, index=POSITIONS.index(DEFAULT_POSITION), key=f"{key_prefix}_pos", label_visibility="collapsed")
    custom_x, custom_y = 0, 0
    if position == "Coordonnées personnalisées":
        c1, c2 = st.columns(2)
        custom_x = c1.number_input("X", min_value=0, value=0, key=f"{key_prefix}_cx")
        custom_y = c2.number_input("Y", min_value=0, value=0, key=f"{key_prefix}_cy")
    return {"position": position, "custom_x": int(custom_x), "custom_y": int(custom_y)}

# ─── SESSION STATE ────────────────────────────────────────────────────────
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state: st.session_state[k] = None

# Suppression de l'onglet Coupe (tab_t)
tab_v, tab_p, tab_s = st.tabs(["Watermark vidéo", "Watermark photo", "Capture d'écran"])

# ─── TAB 1 : VIDÉO ────────────────────────────────────────────────────────
with tab_v:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">1. Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader("Vidéo", type=["mp4", "mov", "avi", "mkv", "webm"], key="vu", label_visibility="collapsed")
        if video_file:
            if st.session_state._last_video_name != video_file.name:
                st.session_state.thumbnail, st.session_state.rendered_bytes = None, None
                st.session_state._last_video_name = video_file.name
            
            lp = get_default_logo()
            tmp = tempfile.mkdtemp()
            vp = os.path.join(tmp, "src" + os.path.splitext(video_file.name)[1])
            with open(vp, "wb") as f: f.write(video_file.read())
            nfo = get_video_info(vp)

            st.markdown(f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Format</span><span class="spec-v">{nfo['width']}x{nfo['height']}</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo['duration'])}</span></div>
            </div>""", unsafe_allow_html=True)

            wm_opts = watermark_options_ui("v")
            st.markdown('<p class="section-label">2. Qualité</p>', unsafe_allow_html=True)
            quality_key = st.selectbox("Qualité", list(QUALITY_PRESETS.keys()), key="v_quality", label_visibility="collapsed")

            if st.button("Lancer le rendu", key="vbtn", use_container_width=True):
                out = os.path.join(tmp, "render.mp4")
                with st.spinner("Rendu en cours..."):
                    render_video(vp, lp, out, nfo, quality_key=quality_key, **wm_opts)
                    with open(out, "rb") as f: st.session_state.rendered_bytes = f.read()
                st.rerun()
    
    with col_r:
        if video_file:
            st.markdown('<p class="section-label">Aperçu</p>', unsafe_allow_html=True)
            opts_sig = (wm_opts["position"], wm_opts["custom_x"], wm_opts["custom_y"])
            if st.session_state.get("_v_opts_sig") != opts_sig or st.session_state.thumbnail is None:
                st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, **wm_opts)
                st.session_state["_v_opts_sig"] = opts_sig
            
            st.markdown('<div class="preview-wrap"><div class="preview-bar">Frame de référence</div><div class="preview-content">', unsafe_allow_html=True)
            st.image(st.session_state.thumbnail, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

            if st.session_state.rendered_bytes:
                st.success("Rendu terminé !")
                st.download_button("↓ Télécharger la vidéo", data=st.session_state.rendered_bytes, file_name="luluflix_video.mp4", mime="video/mp4", use_container_width=True)

# ─── TAB 2 : PHOTO ────────────────────────────────────────────────────────
with tab_p:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">1. Source</p>', unsafe_allow_html=True)
        photo_files = st.file_uploader("Images", type=["png", "jpg", "jpeg"], key="pu", label_visibility="collapsed", accept_multiple_files=True)
        if photo_files:
            wm_opts_p = watermark_options_ui("p")
    
    with col_r:
        if photo_files:
            lp2 = get_default_logo()
            first = photo_files[0]
            first.seek(0)
            st.markdown(f'<p class="section-label">Aperçu ({first.name})</p>', unsafe_allow_html=True)
            result_prev = composite_logo(Image.open(first), lp2, **wm_opts_p)
            st.markdown('<div class="preview-wrap"><div class="preview-bar">Aperçu Photo</div><div class="preview-content">', unsafe_allow_html=True)
            st.image(result_prev.convert("RGB"), use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

            def build_photo_output(pf, opts):
                pf.seek(0)
                base = Image.open(pf)
                result = composite_logo(base, lp2, **opts)
                buf = io.BytesIO()
                ext = pf.name.rsplit(".", 1)[-1].lower()
                fmt = "PNG" if ext == "png" else "JPEG"
                result.convert("RGB").save(buf, format=fmt, quality=100)
                return buf.getvalue(), f"{pf.name.rsplit('.', 1)[0]}_wm.{ext.replace('jpeg','jpg')}"

            if len(photo_files) == 1:
                data, fname = build_photo_output(photo_files[0], wm_opts_p)
                st.download_button("↓ Télécharger", data=data, file_name=fname, use_container_width=True)
            else:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w") as zf:
                    for pf in photo_files:
                        data, fname = build_photo_output(pf, wm_opts_p)
                        zf.writestr(fname, data)
                st.download_button("↓ Tout télécharger (.zip)", data=zip_buf.getvalue(), file_name="luluflix_photos.zip", use_container_width=True)

# ─── TAB 3 : CAPTURE ──────────────────────────────────────────────────────
with tab_s:
    col_l, col_r = st.columns([1, 1], gap="large")
    with col_l:
        st.markdown('<p class="section-label">1. Source</p>', unsafe_allow_html=True)
        scr_file = st.file_uploader("Vidéo", type=["mp4", "mov", "avi", "mkv", "webm"], key="su", label_visibility="collapsed")
        if scr_file:
            tmp_s = tempfile.mkdtemp()
            sp = os.path.join(tmp_s, "src" + os.path.splitext(scr_file.name)[1])
            with open(sp, "wb") as f: f.write(scr_file.read())
            nfo_s = get_video_info(sp)
            st.markdown('<p class="section-label">2. Seconde exacte</p>', unsafe_allow_html=True)
            timecode = st.number_input("tc", min_value=0.0, max_value=float(nfo_s["duration"]), value=0.0, step=0.1, label_visibility="collapsed")
    
    with col_r:
        if scr_file:
            frame = extract_frame(sp, timecode)
            st.markdown(f'<p class="section-label">Capture à {fmt_time(timecode)}</p>', unsafe_allow_html=True)
            st.markdown('<div class="preview-wrap"><div class="preview-bar">Capture d\'écran</div><div class="preview-content">', unsafe_allow_html=True)
            st.image(frame, use_container_width=True)
            st.markdown('</div></div>', unsafe_allow_html=True)
            buf_s = io.BytesIO()
            frame.save(buf_s, format="PNG")
            st.download_button("↓ Télécharger l'image", data=buf_s.getvalue(), file_name=f"capture_{timecode}.png", use_container_width=True)

# ─── FOOTER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="site-footer">
  <span class="footer-name">Luluflix v2.2 • Le Progrès</span>
  <span>Aucune donnée n'est conservée.</span>
</div>
""", unsafe_allow_html=True)
