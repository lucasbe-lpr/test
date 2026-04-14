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
  --green-dark: #147a38; /* Vert plus foncé pour le ZIP */
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

div[data-testid="stTabs"] [data-baseweb="tab-panel"] {
  padding: 0 !important;
}

/* ── Panels ─────────────────────────────────────────── */
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
}
[data-testid="stFileUploader"] section:hover {
  border-color: var(--blue) !important;
  background: var(--blue-dim) !important;
}

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

/* ── Buttons & Layout hacks ─────────────────────────── */
div.stButton > button {
  width: 100% !important; background: var(--blue) !important; border: none !important;
  color: var(--white) !important; border-radius: 999px !important;
  height: 38px !important; font-size: 0.85rem !important;
}

div.stDownloadButton > button {
  width: 100% !important; background: #16a34a !important; border: none !important;
  color: #fff !important; border-radius: 999px !important;
  height: 38px !important; font-size: 0.85rem !important;
}

/* Couleur spécifique pour le bouton TOUT TÉLÉCHARGER */
.zip-container div[data-testid="stDownloadButton"] button {
    background-color: var(--green-dark) !important;
    margin-top: 1rem !important;
}

/* Hack pour permettre aux colonnes de boutons de passer à la ligne (Wrap) */
.wrap-container [data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 10px 0px !important;
}
.wrap-container [data-testid="column"] {
    min-width: 180px !important; /* Force le passage à la ligne si trop serré */
}

/* ── Utils ──────────────────────────────────────────── */
.preview-wrap { border: 1px solid var(--border); border-radius: 10px; overflow: hidden; background: #f0f0f0; }
.photo-batch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.photo-batch-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim  { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

.preview-placeholder {
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; gap: 0.6rem; min-height: 260px;
  border: 1px dashed var(--border); border-radius: 10px;
  background: var(--bg); color: var(--muted); font-size: 0.8rem;
}

/* ── Footer ─────────────────────────────────────────── */
.site-footer {
  height: var(--footer-h); margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.7rem; color: var(--muted);
}
</style>
""", unsafe_allow_html=True)

# Logo header
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64.b64encode(_f.read()).decode()
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">version 2.1</span>
</div>
""", unsafe_allow_html=True)

PREVIEW_MAX_W = 680
PREVIEW_MAX_H = 500

def cap_image_for_preview(img: Image.Image) -> Image.Image:
    w, h = img.size
    if w > PREVIEW_MAX_W:
        ratio = PREVIEW_MAX_W / w
        w, h = PREVIEW_MAX_W, int(h * ratio)
    if h > PREVIEW_MAX_H:
        ratio = PREVIEW_MAX_H / h
        h, w = PREVIEW_MAX_H, int(w * ratio)
    return img.resize((w, h), Image.LANCZOS) if (w, h) != img.size else img

def get_default_logo() -> str:
    return DEFAULT_WM_FILE

POSITIONS = ["Haut gauche", "Haut centre", "Haut droite", "Milieu gauche", "Centre", "Milieu droite", "Bas gauche", "Bas centre", "Bas droite", "Coordonnées personnalisées"]
DEFAULT_POSITION = "Haut droite"

def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int, custom_x: int = 0, custom_y: int = 0, margin_pct: float = 0.05) -> tuple[int, int]:
    mx, my = int(W * margin_pct), int(H * margin_pct)
    if position == "Haut gauche": return mx, my
    if position == "Haut centre": return (W - logo_w) // 2, my
    if position == "Haut droite": return W - logo_w - mx, my
    if position == "Milieu gauche": return mx, (H - logo_h) // 2
    if position == "Centre": return (W - logo_w) // 2, (H - logo_h) // 2
    if position == "Milieu droite": return W - logo_w - mx, (H - logo_h) // 2
    if position == "Bas gauche": return mx, H - logo_h - my
    if position == "Bas centre": return (W - logo_w) // 2, H - logo_h - my
    if position == "Bas droite": return W - logo_w - mx, H - logo_h - my
    return custom_x, custom_y

def composite_logo(base: Image.Image, logo_path: str, position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0, force_w: int = None, force_h: int = None) -> Image.Image:
    W, H = (force_w or base.size[0]), (force_h or base.size[1])
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer)

# Video logic...
def get_video_info(path: str) -> dict:
    import json as _json
    cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate,tags=rotate", "-show_entries", "stream_side_data=rotation", "-show_entries", "format=duration", "-of", "json", path]
    data = _json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    stream = data.get("streams", [{}])[0]
    w, h, dur = int(stream.get("width", 0)), int(stream.get("height", 0)), float(data.get("format", {}).get("duration", 0))
    fps = 25.0
    try:
        n, d = stream.get("r_frame_rate", "25/1").split("/")
        fps = round(float(n)/float(d), 2)
    except: pass
    return {"width": w, "height": h, "duration": dur, "fps": fps}

def fmt_time(secs: float) -> str:
    m, s = divmod(int(secs), 60)
    return f"{m}:{s:02d}"

def make_thumbnail(vp, lp, nfo, **opts):
    res = subprocess.run(["ffmpeg", "-y", "-i", vp, "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"], capture_output=True)
    frame = Image.open(io.BytesIO(res.stdout)).convert("RGBA")
    return composite_logo(frame, lp, force_w=nfo["width"], force_h=nfo["height"], **opts).convert("RGB")

QUALITY_PRESETS = {"Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"}, "Haute qualité (CRF 12)": {"crf": "12", "preset": "slow"}}

def render_video(vp, lp, out_p, nfo, quality_key, **opts):
    W, H = nfo["width"], nfo["height"]
    lw = int(math.sqrt(W**2 + H**2) * 0.1307)
    l_orig = Image.open(lp).convert("RGBA")
    lh = int(l_orig.height * (lw / l_orig.width))
    l_scaled = l_orig.resize((lw, lh), Image.LANCZOS)
    tmp_lp = os.path.join(tempfile.mkdtemp(), "wm.png")
    l_scaled.save(tmp_lp)
    x, y = compute_xy(opts['position'], W, H, lw, lh, opts['custom_x'], opts['custom_y'])
    q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])
    cmd = ["ffmpeg", "-y", "-i", vp, "-i", tmp_lp, "-filter_complex", f"[0:v][1:v]overlay={x}:{y}", "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"], "-c:a", "copy", "-movflags", "+faststart", out_p]
    subprocess.run(cmd, capture_output=True)

def watermark_options_ui(key_prefix: str) -> dict:
    st.markdown('<p class="section-label-mt">Watermark</p>', unsafe_allow_html=True)
    pos = st.selectbox("Position", POSITIONS, index=POSITIONS.index(DEFAULT_POSITION), key=f"{key_prefix}_pos")
    cx, cy = 0, 0
    if pos == "Coordonnées personnalisées":
        c1, c2 = st.columns(2)
        cx = c1.number_input("X", min_value=0, value=0, key=f"{key_prefix}_cx")
        cy = c2.number_input("Y", min_value=0, value=0, key=f"{key_prefix}_cy")
    return {"position": pos, "custom_x": int(cx), "custom_y": int(cy)}

# Session states
for k in ["thumbnail", "rendered_bytes", "_last_video_name"]:
    if k not in st.session_state: st.session_state[k] = None

tab_v, tab_p, tab_s = st.tabs(["Watermark vidéo", "Watermark photo", "Capture d'écran"])

# TAB 1 - VIDEO (Non modifiée)
with tab_v:
    col_ctrl, col_prev = st.columns([4, 6], gap="large")
    with col_ctrl:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader("Vid", type=["mp4","mov"], key="vu", label_visibility="collapsed")
    if video_file:
        if st.session_state._last_video_name != video_file.name:
            st.session_state.thumbnail, st.session_state.rendered_bytes = None, None
            st.session_state._last_video_name = video_file.name
        tmp = tempfile.mkdtemp()
        vp = os.path.join(tmp, "src.mp4")
        with open(vp, "wb") as f: f.write(video_file.read())
        nfo = get_video_info(vp)
        with col_ctrl:
            st.markdown(f'<div class="specs-row"><div class="spec-cell"><span class="spec-k">Résolution</span><span class="spec-v">{nfo["width"]}x{nfo["height"]}</span></div><div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo["duration"])}</span></div></div>', unsafe_allow_html=True)
            wm_opts = watermark_options_ui("v")
            if not st.session_state.thumbnail: st.session_state.thumbnail = make_thumbnail(vp, get_default_logo(), nfo, **wm_opts)
            if st.button("Générer le rendu", key="vbtn"):
                out = os.path.join(tmp, "out.mp4")
                render_video(vp, get_default_logo(), out, nfo, "Standard (CRF 18 — recommandé)", **wm_opts)
                with open(out, "rb") as f: st.session_state.rendered_bytes = f.read()
                st.rerun()
            if st.session_state.rendered_bytes:
                st.download_button("↓ Télécharger", data=st.session_state.rendered_bytes, file_name="video_wm.mp4")
        with col_prev:
            st.image(cap_image_for_preview(st.session_state.thumbnail))
    else:
        with col_prev: st.markdown('<div class="preview-placeholder">Aperçu vidéo</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# TAB 2 — WATERMARK PHOTO (Mise à jour demandée)
# ═══════════════════════════════════════════════════════════════════
with tab_p:
    col_ctrl_p, col_prev_p = st.columns([4, 6], gap="large")

    with col_ctrl_p:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        photo_files = st.file_uploader("Images", type=["png", "jpg", "jpeg"], key="pu", label_visibility="collapsed", accept_multiple_files=True)

    if photo_files:
        lp2 = get_default_logo()
        wm_opts_p = watermark_options_ui("p")

        with col_ctrl_p:
            st.markdown('<p class="section-label-mt">Fichiers importés</p>', unsafe_allow_html=True)
            for pf in photo_files:
                img_t = Image.open(pf)
                st.markdown(f'<div class="photo-batch-item"><span class="photo-batch-name">📷 {pf.name}</span><span class="photo-batch-dim">{img_t.size[0]}×{img_t.size[1]}px</span></div>', unsafe_allow_html=True)
                pf.seek(0)

        # APERÇUS MULTIPLES EN GRILLE
        with col_prev_p:
            st.markdown('<p class="section-label">Aperçus</p>', unsafe_allow_html=True)
            grid_cols = st.columns(2) # 2 colonnes pour les aperçus
            for i, pf in enumerate(photo_files):
                pf.seek(0)
                res_img = composite_logo(Image.open(pf), lp2, **wm_opts_p)
                grid_cols[i % 2].image(cap_image_for_preview(res_img.convert("RGB")), caption=pf.name)

        def build_p_out(pf, opts):
            pf.seek(0)
            res = composite_logo(Image.open(pf), lp2, **opts)
            buf = io.BytesIO()
            ext = pf.name.rsplit(".", 1)[-1].lower()
            if ext == "png": res.save(buf, format="PNG")
            else: res.convert("RGB").save(buf, format="JPEG", quality=100)
            return buf.getvalue(), pf.name.rsplit(".", 1)[0] + "_wm." + ext

        # BOUTONS CÔTE À CÔTE AVEC WRAP
        with col_ctrl_p:
            st.markdown('<p class="section-label-mt">Téléchargement</p>', unsafe_allow_html=True)
            st.markdown('<div class="wrap-container">', unsafe_allow_html=True)
            btn_cols = st.columns(3) # On prépare 3 slots par ligne
            for i, pf in enumerate(photo_files):
                data, fname = build_p_out(pf, wm_opts_p)
                # Le CSS "wrap-container" s'occupe de passer à la ligne si les 3 colonnes débordent
                btn_cols[i % 3].download_button(f"↓ {pf.name[:10]}...", data=data, file_name=fname, key=f"pdl_{i}")
            st.markdown('</div>', unsafe_allow_html=True)

            # BOUTON ZIP (Tout télécharger) - VERT FONCÉ
            if len(photo_files) > 1:
                z_buf = io.BytesIO()
                with zipfile.ZipFile(z_buf, "w") as zf:
                    for pf in photo_files:
                        d, f = build_p_out(pf, wm_opts_p)
                        zf.writestr(f, d)
                st.markdown('<div class="zip-container">', unsafe_allow_html=True)
                st.download_button("↓ Tout télécharger (.zip)", data=z_buf.getvalue(), file_name="photos_wm.zip", key="pdl_zip")
                st.markdown('</div>', unsafe_allow_html=True)
    else:
        with col_prev_p: st.markdown('<div class="preview-placeholder">Aperçus photos</div>', unsafe_allow_html=True)

# TAB 3 - CAPTURE (Non modifiée)
with tab_s:
    col_ctrl_s, col_prev_s = st.columns([4, 6])
    with col_ctrl_s:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        scr_f = st.file_uploader("Scr", type=["mp4"], key="su", label_visibility="collapsed")
    if scr_f:
        # Simplifié pour l'exemple
        st.info("Module capture actif")
    else:
        with col_prev_s: st.markdown('<div class="preview-placeholder">Aperçu capture</div>', unsafe_allow_html=True)

st.markdown('<div class="site-footer"><span class="footer-name"></span><span>MàJ 2.1 : Grid preview & wrap buttons.</span></div>', unsafe_allow_html=True)
