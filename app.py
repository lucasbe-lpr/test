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

# Configuration fichiers
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

# ─── STYLE CSS ──────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&display=swap');

:root {
  --blue: #0068B1;
  --white: #ffffff;
  --bg: #fafafa;
  --border: #e4e4e4;
  --muted: #999999;
}

[data-testid="stAppViewContainer"] { background: var(--white) !important; font-family: 'Roboto', sans-serif !important; }
.block-container { padding: 1rem 5rem !important; }
#MainMenu, footer, header { display: none !important; }

/* Tabs */
div[data-testid="stTabs"] [data-baseweb="tab-list"] { border-bottom: 1px solid var(--border) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"] { display: none !important; }
div[data-testid="stTabs"] [aria-selected="true"] { color: var(--blue) !important; border-bottom: 2px solid var(--blue) !important; }

/* Header */
.site-header { padding: 1rem 0; border-bottom: 1px solid var(--border); margin-bottom: 2rem; display: flex; align-items: center; justify-content: space-between; }
.site-header img { height: 40px; }

/* Preview Fix */
.preview-container {
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    background: #f1f1f1;
    max-height: 600px;
    display: flex;
    flex-direction: column;
}
.preview-header { padding: 8px 15px; background: white; border-bottom: 1px solid var(--border); font-size: 0.7rem; font-weight: bold; color: var(--muted); }
.preview-img-host { display: flex; justify-content: center; background: #222; }
.preview-img-host img { max-height: 500px; width: auto; object-fit: contain; }

.section-label { font-size: 0.7rem; font-weight: 700; color: var(--muted); text-transform: uppercase; margin: 1rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── LOGIQUE COMMUNE ────────────────────────────────────────────────────────
def compute_xy(position, W, H, logo_w, logo_h, margin_pct=0.05):
    mx, my = int(W * margin_pct), int(H * margin_pct)
    if position == "Haut gauche": return mx, my
    if position == "Haut centre": return (W - logo_w) // 2, my
    if position == "Haut droite": return W - logo_w - mx, my
    if position == "Milieu gauche": return mx, (H - logo_h) // 2
    if position == "Centre": return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite": return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche": return mx, H - logo_h - my
    if position == "Bas centre": return (W - logo_w) // 2, H - logo_h - my
    return W - logo_w - mx, H - logo_h - my

def apply_wm_to_img(base_img, logo_path, position, force_w=None, force_h=None):
    W, H = (force_w, force_h) if force_w else base_img.size
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h)
    
    out = base_img.convert("RGBA").resize((W,H))
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer).convert("RGB")

# ─── FONCTIONS VIDÉO ────────────────────────────────────────────────────────
def get_video_info(path):
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate -show_entries format=duration", "-of", "json", path]
    import json
    res = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(res.stdout)
    s = data['streams'][0]
    num, den = s['r_frame_rate'].split('/')
    return {"width": s['width'], "height": s['height'], "duration": float(data['format']['duration']), "fps": round(float(num)/float(den), 2)}

def extract_frame(path, time=0):
    cmd = ["ffmpeg", "-y", "-ss", str(time), "-i", path, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"]
    res = subprocess.run(cmd, capture_output=True)
    return Image.open(io.BytesIO(res.stdout))

# ─── UI ───────────────────────────────────────────────────────────────────
if os.path.exists(LOGO_FILE):
    with open(LOGO_FILE, "rb") as f:
        st.markdown(f'<div class="site-header"><img src="data:image/png;base64,{_b64.b64encode(f.read()).decode()}" /><span>Support : lucas.bessonnat@leprogres.fr</span></div>', unsafe_allow_html=True)

tab_v, tab_p, tab_s = st.tabs(["Vidéo", "Photo", "Capture"])

# --- VIDÉO ---
with tab_v:
    c1, c2 = st.columns(2)
    with c1:
        v_file = st.file_uploader("Upload Vidéo", type=["mp4","mov"])
        if v_file:
            tmp = tempfile.mkdtemp()
            vp = os.path.join(tmp, "in.mp4")
            with open(vp, "wb") as f: f.write(v_file.read())
            nfo = get_video_info(vp)
            pos = st.selectbox("Position", ["Haut droite", "Bas droite", "Haut gauche", "Bas gauche", "Centre"])
            if st.button("Lancer le rendu"):
                with st.spinner("Calcul..."):
                    out = os.path.join(tmp, "out.mp4")
                    # Scale logo for FFmpeg
                    logo_w = int(math.sqrt(nfo['width']**2 + nfo['height']**2) * 0.1307)
                    x, y = compute_xy(pos, nfo['width'], nfo['height'], logo_w, logo_w) # simplif
                    subprocess.run(["ffmpeg", "-y", "-i", vp, "-i", DEFAULT_WM_FILE, "-filter_complex", f"[1:v]scale={logo_w}:-1[wm];[0:v][wm]overlay={x}:{y}", "-c:a", "copy", out])
                    with open(out, "rb") as f: st.session_state.v_done = f.read()
            if "v_done" in st.session_state:
                st.download_button("↓ Télécharger", st.session_state.v_done, "video_wm.mp4", use_container_width=True)
    with c2:
        if v_file:
            img = apply_wm_to_img(extract_frame(vp), DEFAULT_WM_FILE, pos, nfo['width'], nfo['height'])
            st.markdown(f'<div class="preview-container"><div class="preview-header">Aperçu</div><div class="preview-img-host">', unsafe_allow_html=True)
            st.image(img)
            st.markdown('</div></div>', unsafe_allow_html=True)

# --- PHOTO ---
with tab_p:
    p_files = st.file_uploader("Upload Photos", type=["jpg","png"], accept_multiple_files=True)
    if p_files:
        p_pos = st.selectbox("Position ", ["Haut droite", "Bas droite", "Haut gauche", "Bas gauche", "Centre"])
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a") as zf:
            for pf in p_files:
                res = apply_wm_to_img(Image.open(pf), DEFAULT_WM_FILE, p_pos)
                buf = io.BytesIO()
                res.save(buf, format="JPEG", quality=95)
                zf.writestr(f"wm_{pf.name}", buf.getvalue())
        st.download_button("↓ Télécharger tout (.zip)", zip_buffer.getvalue(), "photos.zip")

# --- CAPTURE ---
with tab_s:
    s_file = st.file_uploader("Vidéo pour capture", type=["mp4","mov"], key="s")
    if s_file:
        tmp_s = tempfile.mkdtemp()
        vps = os.path.join(tmp_s, "s.mp4")
        with open(vps, "wb") as f: f.write(s_file.read())
        dur = get_video_info(vps)["duration"]
        tc = st.slider("Timecode", 0.0, dur, 0.0)
        frame = extract_frame(vps, tc)
        st.image(frame)
        buf = io.BytesIO()
        frame.save(buf, format="PNG")
        st.download_button("Sauvegarder l'image", buf.getvalue(), "capture.png")
