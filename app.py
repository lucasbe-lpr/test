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

# --- CONFIGURATION & THEME ---
LOGO_FILE       = "luluflix.png"
DEFAULT_WM_FILE = "lpr.png"
FAVICON_FILE    = "favicon.png"

try:
    _fav_img = Image.open(FAVICON_FILE)
except Exception:
    _fav_img = "▶"

st.set_page_config(
    page_title="Luluflix - Studio",
    page_icon=_fav_img,
    layout="wide", # Passage en mode large pour optimiser l'espace
    initial_sidebar_state="collapsed",
)

# --- CSS CUSTOM (UI/UX REVISITED) ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

:root {
  --blue:      #0068B1;
  --blue-hover:#005fa8;
  --blue-dim:  #f0f7ff;
  --white:     #ffffff;
  --bg:        #f8fafc;
  --ink:       #0f172a;
  --sub:       #475569;
  --muted:     #94a3b8;
  --border:    #e2e8f0;
}

/* Global Reset */
html, body, [data-testid="stAppViewContainer"] {
  background: var(--bg) !important;
  color: var(--ink) !important;
  font-family: 'Roboto', sans-serif !important;
}

/* Suppression du bandeau rouge Streamlit */
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stHeader"] { background: rgba(0,0,0,0) !important; }
#MainMenu, footer { display: none !important; }

/* Conteneur principal */
.block-container {
  padding: 1.5rem 3rem !important;
  max-width: 1400px !important;
}

/* Header */
.site-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2rem;
}
.site-header img { height: 40px; }
.site-header-right { font-size: 0.8rem; color: var(--muted); }

/* Sidebar-like Control Panel */
.control-panel {
  background: var(--white);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 1px 3px rgba(0,0,0,0.02);
}

/* Onglets style SaaS */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  gap: 8px !important;
  background: transparent !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: var(--white) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px 8px 0 0 !important;
  padding: 0.5rem 1.5rem !important;
  color: var(--muted) !important;
  font-weight: 500 !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--blue) !important;
  border-bottom: 2px solid var(--blue) !important;
  background: var(--blue-dim) !important;
}

/* Éradication du orange/rouge Streamlit sur les inputs */
input:focus, textarea:focus, select:focus {
  border-color: var(--blue) !important;
  box-shadow: 0 0 0 1px var(--blue) !important;
}
[data-baseweb="base-input"] {
    border-color: var(--border) !important;
}
[data-baseweb="base-input"]:focus-within {
    border-color: var(--blue) !important;
}

/* Boutons */
div.stButton > button {
  width: 100% !important;
  background: var(--blue) !important;
  color: white !important;
  border: none !important;
  border-radius: 8px !important;
  height: 42px !important;
  font-weight: 600 !important;
  transition: all 0.2s !important;
}
div.stButton > button:hover {
  background: var(--blue-hover) !important;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,104,177,0.2);
}

/* Preview Box */
.preview-card {
  background: #1e293b;
  border-radius: 12px;
  padding: 10px;
  position: relative;
  border: 1px solid var(--border);
}
.preview-label {
  position: absolute;
  top: 20px;
  left: 20px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 4px 12px;
  border-radius: 4px;
  font-size: 0.7rem;
  text-transform: uppercase;
  z-index: 10;
}

/* Specs */
.spec-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
  margin-bottom: 1.5rem;
}
.spec-item {
  background: var(--bg);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--border);
}
.spec-label { font-size: 0.65rem; color: var(--muted); text-transform: uppercase; display: block; }
.spec-value { font-size: 0.9rem; font-weight: 600; color: var(--ink); }

/* Status & Progress */
.encoding-wrap {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 1rem;
  background: var(--blue-dim);
  border-radius: 8px;
  margin-top: 1rem;
}
.encoding-ring {
  width: 18px; height: 18px; border: 2px solid var(--border);
  border-top-color: var(--blue); border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

</style>
""", unsafe_allow_html=True)

# --- HEADER ---
import base64 as _b64h
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">Studio de Marquage Interne — v2.5</span>
</div>
""", unsafe_allow_html=True)


# ─── FONCTIONS LOGIQUES (INCHANGÉES) ──────────────────────────────────────────

def get_default_logo() -> str:
    return DEFAULT_WM_FILE

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
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,tags=rotate", "-show_entries", "stream_side_data=rotation", "-show_entries", "format=duration", "-of", "json", path]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = _json.loads(result.stdout)
    stream = data.get("streams", [{}])[0]
    w, h = int(stream.get("width", 0)), int(stream.get("height", 0))
    dur = float(data.get("format", {}).get("duration", 0))
    fps_raw = stream.get("r_frame_rate", "25/1")
    try:
        num, den = fps_raw.split("/")
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
    "Standard (CRF 18)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)": {"crf": "12", "preset": "slow"},
    "Sans perte (CRF 0)": {"crf": "0", "preset": "ultrafast"},
}

def render_video(video_path: str, logo_path: str, output_path: str, info: dict, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0, quality_key: str = "Standard (CRF 18)", progress_cb=None):
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
    q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18)"])
    cmd = ["ffmpeg", "-y", "-i", video_path, "-i", tmp_logo_path, "-filter_complex", filter_complex, "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"], "-c:a", "copy", "-movflags", "+faststart", "-progress", "pipe:1", output_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    total = info["duration"]
    while True:
        line = process.stdout.readline()
        if not line: break
        if line.strip().startswith("out_time_ms="):
            try:
                ms = int(line.strip().split("=")[1])
                if total > 0 and progress_cb: progress_cb(min(ms / 1_000_000 / total, 1.0))
            except: pass
    process.wait()

# ─── UI HELPERS ──────────────────────────────────────────────────────────────

def watermark_options_ui(key_prefix: str) -> dict:
    st.markdown('<p style="font-size:0.75rem; font-weight:700; color:#94a3b8; text-transform:uppercase; margin-bottom:10px;">Configuration Watermark</p>', unsafe_allow_html=True)
    position = st.selectbox("Position prédéfinie", POSITIONS, index=POSITIONS.index(DEFAULT_POSITION), key=f"{key_prefix}_pos")
    custom_x, custom_y = 0, 0
    if position == "Coordonnées personnalisées":
        c1, c2 = st.columns(2)
        with c1: custom_x = st.number_input("X (px)", min_value=0, value=0, key=f"{key_prefix}_cx")
        with c2: custom_y = st.number_input("Y (px)", min_value=0, value=0, key=f"{key_prefix}_cy")
    return {"position": position, "custom_x": int(custom_x), "custom_y": int(custom_y)}

# --- SESSION STATE ---
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state: st.session_state[k] = None

# --- TABS ---
tab_v, tab_p, tab_s = st.tabs(["🎥 Vidéo", "📷 Photo", "🖼️ Capture"])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 — VIDÉO
# ═══════════════════════════════════════════════════════════════════
with tab_v:
    col_ctrl, col_main = st.columns([1, 1.8], gap="large")
    
    with col_ctrl:
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        video_file = st.file_uploader("Fichier vidéo", type=["mp4", "mov", "avi", "mkv"], key="vu")
        
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

            st.markdown(f"""
            <div class="spec-grid">
                <div class="spec-item"><span class="spec-label">Résolution</span><span class="spec-value">{nfo['width']}×{nfo['height']}</span></div>
                <div class="spec-item"><span class="spec-label">Durée</span><span class="spec-value">{fmt_time(nfo['duration'])}</span></div>
            </div>""", unsafe_allow_html=True)

            wm_opts = watermark_options_ui("v")
            quality_key = st.selectbox("Qualité d'export", list(QUALITY_PRESETS.keys()), key="v_quality")

            if st.button("Lancer le rendu", key="vbtn"):
                out = os.path.join(tmp, "render.mp4")
                ph = st.empty()
                ph.markdown('<div class="encoding-wrap"><div class="encoding-ring"></div><span style="color:#0068B1; font-weight:600;">Encodage en cours...</span></div>', unsafe_allow_html=True)
                render_video(vp, lp, out, nfo, quality_key=quality_key, **wm_opts)
                with open(out, "rb") as f: st.session_state.rendered_bytes = f.read()
                ph.empty()
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main:
        if video_file:
            if st.session_state.thumbnail is None:
                st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, **wm_opts)
            
            st.markdown('<div class="preview-card"><div class="preview-label">Aperçu du marquage</div>', unsafe_allow_html=True)
            st.image(st.session_state.thumbnail, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if st.session_state.rendered_bytes:
                st.success("Vidéo prête !")
                st.download_button("💾 Télécharger la vidéo finalisée", data=st.session_state.rendered_bytes, file_name="video_luluflix.mp4", mime="video/mp4")
        else:
            st.info("En attente d'une vidéo pour l'aperçu...")

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — PHOTO
# ═══════════════════════════════════════════════════════════════════
with tab_p:
    col_ctrl_p, col_main_p = st.columns([1, 1.8], gap="large")
    
    with col_ctrl_p:
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        photo_files = st.file_uploader("Images (Batch)", type=["png", "jpg", "jpeg"], accept_multiple_files=True, key="pu")
        if photo_files:
            st.write(f"📁 {len(photo_files)} fichier(s) chargé(s)")
            wm_opts_p = watermark_options_ui("p")
        st.markdown('</div>', unsafe_allow_html=True)

    with col_main_p:
        if photo_files:
            lp2 = get_default_logo()
            # Preview first
            base_prev = Image.open(photo_files[0])
            res_prev = composite_logo(base_prev, lp2, **wm_opts_p)
            st.markdown('<div class="preview-card"><div class="preview-label">Aperçu : '+photo_files[0].name+'</div>', unsafe_allow_html=True)
            st.image(res_prev.convert("RGB"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Build Output
            def process_img(pf, opts):
                pf.seek(0)
                res = composite_logo(Image.open(pf), lp2, **opts)
                buf = io.BytesIO()
                res.convert("RGB").save(buf, format="JPEG", quality=95)
                return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm.jpg"

            if len(photo_files) > 1:
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w") as zf:
                    for pf in photo_files:
                        data, name = process_img(pf, wm_opts_p)
                        zf.writestr(name, data)
                st.download_button("💾 Télécharger tout le pack (.zip)", data=zip_buf.getvalue(), file_name="pack_photos.zip")
            else:
                data, name = process_img(photo_files[0], wm_opts_p)
                st.download_button(f"💾 Télécharger {name}", data=data, file_name=name)

# ═══════════════════════════════════════════════════════════════════
# TAB 3 — CAPTURE
# ═══════════════════════════════════════════════════════════════════
with tab_s:
    col_ctrl_s, col_main_s = st.columns([1, 1.8], gap="large")
    with col_ctrl_s:
        st.markdown('<div class="control-panel">', unsafe_allow_html=True)
        scr_file = st.file_uploader("Vidéo source", type=["mp4", "mov"], key="su")
        if scr_file:
            tmp_s = tempfile.mkdtemp()
            sp = os.path.join(tmp_s, "src" + os.path.splitext(scr_file.name)[1])
            with open(sp, "wb") as f: f.write(scr_file.read())
            nfo_s = get_video_info(sp)
            timecode = st.number_input("Timecode (sec)", min_value=0.0, max_value=float(nfo_s["duration"]), step=0.1, format="%.2f")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col_main_s:
        if scr_file:
            frame = extract_frame(sp, timecode)
            st.markdown('<div class="preview-card">', unsafe_allow_html=True)
            st.image(frame, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            buf_s = io.BytesIO()
            frame.save(buf_s, format="PNG")
            st.download_button("💾 Extraire cette image (PNG)", data=buf_s.getvalue(), file_name=f"capture_{timecode}.png")

# --- FOOTER ---
st.markdown("""
<div style="margin-top: 5rem; padding: 2rem; border-top: 1px solid #e2e8f0; text-align: center; color: #94a3b8; font-size: 0.8rem;">
  Compte : <strong>lucas.bessonnat@leprogres.fr</strong><br>
  Propulsé par Luluflix Engine. Les fichiers ne quittent jamais votre navigateur.
</div>
""", unsafe_allow_html=True)
