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

# ─── Configuration ────────────────────────────────────────────────────────────

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
    initial_sidebar_state="expanded",
)

# ─── CSS ─────────────────────────────────────────────────────────────────────

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
}

*, *::before, *::after { box-sizing: border-box; }

html, body, .main, section.main {
  background: var(--white) !important;
  color: var(--ink) !important;
  font-family: 'Roboto', sans-serif !important;
}

/* Wide mode: remove max-width constraint */
.block-container {
  background: var(--white) !important;
  padding: 1.5rem 2.5rem 4rem !important;
  max-width: 100% !important;
}

/* Sidebar */
section[data-testid="stSidebar"] {
  background: var(--bg) !important;
  border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] .block-container {
  padding: 1.5rem 1.2rem 3rem !important;
}

#MainMenu, footer, header { display: none !important; }

/* ── Site header ── */
.site-header {
  padding: 0 0 1.2rem;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.site-header img { height: 40px; width: auto; display: block; }
.site-header-right { font-size: 0.68rem; color: var(--muted); letter-spacing: 0.01em; }

/* ── Tabs ── */
div[data-testid="stTabs"] [data-baseweb="tab-list"] {
  background: transparent !important;
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important; margin-bottom: 1.5rem !important; padding: 0 !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"] {
  background: transparent !important;
  border: none !important;
  border-bottom: 2px solid transparent !important;
  margin-bottom: -1px !important;
  color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important;
  font-weight: 400 !important;
  padding: 0.55rem 1.4rem 0.55rem 0 !important;
  transition: color 0.12s !important;
}
div[data-testid="stTabs"] [aria-selected="true"] {
  color: var(--ink) !important;
  font-weight: 500 !important;
  border-bottom: 2px solid var(--blue) !important;
}
div[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: var(--sub) !important; }
div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
div[data-testid="stTabs"] [data-baseweb="tab-border"] { display: none !important; }

/* ── File uploader ── */
[data-testid="stFileUploader"] { background: transparent !important; margin-bottom: 0.8rem !important; }
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
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.8rem !important;
}
[data-testid="stFileUploader"] button {
  background: var(--white) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--sub) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.76rem !important;
  padding: 0.25rem 0.8rem !important;
  border-radius: 999px !important;
}
[data-testid="stFileUploader"] button:hover { border-color: var(--blue) !important; color: var(--blue) !important; }
[data-testid="stFileUploaderFileName"] { color: var(--ink) !important; font-weight: 500 !important; font-size: 0.8rem !important; }

/* ── Labels ── */
.section-label {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 0;
}
.section-label-mt {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 1.2rem;
}

/* ── Specs row ── */
.specs-row {
  display: flex; border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden; margin-bottom: 1.2rem; background: var(--bg);
}
.spec-cell {
  flex: 1; padding: 0.65rem 0.9rem; border-right: 1px solid var(--border);
  display: flex; flex-direction: column; gap: 0.15rem;
}
.spec-cell:last-child { border-right: none; }
.spec-k { font-size: 0.58rem; font-weight: 500; text-transform: uppercase; letter-spacing: 0.07em; color: var(--muted); }
.spec-v { font-size: 0.9rem; font-weight: 500; color: var(--ink); line-height: 1.2; }

/* ── Preview ── */
.preview-wrap {
  border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; background: #f0f0f0; height: 100%;
}
.preview-bar {
  padding: 0.32rem 0.85rem; border-bottom: 1px solid var(--border);
  background: var(--white); font-size: 0.6rem; color: var(--muted);
  font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;
}

/* ── Buttons ── */
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

div.stDownloadButton > button {
  width: 100% !important; background: #16a34a !important; border: none !important;
  color: #fff !important; font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  padding: 0 1.4rem !important; height: 38px !important; border-radius: 999px !important;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 2px rgba(22,163,74,0.18), 0 2px 6px rgba(22,163,74,0.1) !important;
}
div.stDownloadButton > button:hover { background: #15803d !important; transform: translateY(-1px) !important; }
div.stDownloadButton > button:active { transform: translateY(0) !important; }

div[data-testid="stProgress"] { display: none !important; }

/* ── Loading states ── */
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

.status { font-size: 0.78rem; padding: 0.5rem 0; margin: 0.5rem 0; color: var(--muted); line-height: 1.4; }
.status-ok  { color: var(--green); }
.status-err { color: var(--red); }
.status-idle { color: var(--muted); }

/* ── Footer ── */
.site-footer {
  margin-top: 3rem; padding-top: 1rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.68rem; color: var(--muted);
}
.footer-name { color: var(--sub); font-weight: 500; }

/* ── Sidebar selectbox / number input tweaks ── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: var(--border) !important; border-radius: 6px !important; font-size: 0.84rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--blue) !important; }

/* ── Photo batch list ── */
.photo-batch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.photo-batch-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim  { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

/* ── Trim time inputs in sidebar ── */
.trim-time-row {
  display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.6rem;
}
</style>
""", unsafe_allow_html=True)

# ─── Logo header ─────────────────────────────────────────────────────────────

import base64 as _b64h
with open(LOGO_FILE, "rb") as _f:
    _logo_b64 = _b64h.b64encode(_f.read()).decode()
st.markdown(f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64}" alt="Luluflix" />
  <span class="site-header-right">N'hésitez pas à me faire remonter les bugs par mail !</span>
</div>
""", unsafe_allow_html=True)


# ─── Helpers ─────────────────────────────────────────────────────────────────

POSITIONS = [
    "Haut gauche", "Haut centre", "Haut droite",
    "Milieu gauche", "Centre", "Milieu droite",
    "Bas gauche", "Bas centre", "Bas droite",
    "Coordonnées personnalisées",
]
DEFAULT_POSITION = "Haut droite"

QUALITY_PRESETS = {
    "Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)":         {"crf": "12", "preset": "slow"},
    "Sans perte (CRF 0)":             {"crf": "0",  "preset": "ultrafast"},
}


def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int,
               custom_x: int = 0, custom_y: int = 0,
               margin_pct: float = 0.05) -> tuple[int, int]:
    mx = int(W * margin_pct)
    my = int(H * margin_pct)
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
    logo_h = int(logo.height * (logo_w / logo.width))
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)   # toujours LANCZOS
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)
    out = base.convert("RGBA")
    layer = Image.new("RGBA", out.size, (0, 0, 0, 0))
    layer.paste(logo, (x, y), logo)
    return Image.alpha_composite(out, layer)


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
    data = _json.loads(subprocess.run(cmd, capture_output=True, text=True).stdout)
    stream = data.get("streams", [{}])[0]
    w, h = int(stream.get("width", 0)), int(stream.get("height", 0))
    dur   = float(data.get("format", {}).get("duration", 0))
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
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ], capture_output=True)
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def make_thumbnail(video_path: str, logo_path: str, info: dict,
                   position: str = DEFAULT_POSITION,
                   custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1",
    ], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(
        frame, logo_path,
        position=position, custom_x=custom_x, custom_y=custom_y,
        force_w=info["width"], force_h=info["height"],
    ).convert("RGB")


def render_video(
    video_path: str, logo_path: str, output_path: str, info: dict,
    position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0,
    quality_key: str = "Standard (CRF 18 — recommandé)",
    progress_cb=None,
):
    W, H = info["width"], info["height"]
    logo_w = int(math.sqrt(W**2 + H**2) * 0.1307)
    logo_orig = Image.open(logo_path).convert("RGBA")
    logo_h = int(logo_orig.height * (logo_w / logo_orig.width))
    logo_scaled = logo_orig.resize((logo_w, logo_h), Image.LANCZOS)
    x, y = compute_xy(position, W, H, logo_w, logo_h, custom_x, custom_y)

    with tempfile.TemporaryDirectory() as tmp_logo_dir:
        tmp_logo_path = os.path.join(tmp_logo_dir, "wm_prescaled.png")
        logo_scaled.save(tmp_logo_path, format="PNG")

        q = QUALITY_PRESETS.get(quality_key, QUALITY_PRESETS["Standard (CRF 18 — recommandé)"])
        cmd = [
            "ffmpeg", "-y",
            "-i", video_path, "-i", tmp_logo_path,
            "-filter_complex", f"[0:v][1:v]overlay={x}:{y}",
            "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"],
            "-c:a", "copy", "-movflags", "+faststart",
            "-progress", "pipe:1", output_path,
        ]
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        total = info["duration"]
        for line in process.stdout:
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
        output_path,
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())


# ─── Session state ────────────────────────────────────────────────────────────

for k, v in {
    "thumbnail": None,
    "rendered_bytes": None,
    "trim_bytes": None,
    "_last_video_name": None,
    "_last_trim_name": None,
    "trim_t_start": 0.0,
    "trim_t_end": 0.0,
}.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─── Sidebar: shared controls ─────────────────────────────────────────────────

with st.sidebar:
    try:
        st.image(LOGO_FILE, width=130)
    except Exception:
        st.markdown("### Luluflix")

    st.markdown("---")
    st.markdown('<p class="section-label">Fichier source</p>', unsafe_allow_html=True)

    # Each tab has its own uploader — we expose a mode selector in the sidebar
    # so users know which tab is active. The actual uploaders live in each tab.
    st.markdown("**Upload le fichier dans l'onglet correspondant →**")
    st.markdown("---")

    st.markdown('<p class="section-label">Position du watermark</p>', unsafe_allow_html=True)
    sidebar_position = st.selectbox(
        "Position",
        POSITIONS,
        index=POSITIONS.index(DEFAULT_POSITION),
        key="sb_pos",
        label_visibility="collapsed",
    )
    sidebar_custom_x, sidebar_custom_y = 0, 0
    if sidebar_position == "Coordonnées personnalisées":
        sidebar_custom_x = st.number_input("X (px depuis gauche)", min_value=0, value=0, step=1, key="sb_cx")
        sidebar_custom_y = st.number_input("Y (px depuis haut)",   min_value=0, value=0, step=1, key="sb_cy")

    st.markdown("---")
    st.markdown('<p class="section-label">Qualité d\'export vidéo</p>', unsafe_allow_html=True)
    sidebar_quality = st.selectbox(
        "Qualité",
        list(QUALITY_PRESETS.keys()),
        key="sb_quality",
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown('<p class="section-label">Découpe vidéo</p>', unsafe_allow_html=True)
    sb_t_start = st.number_input(
        "Début (s)", min_value=0.0, value=float(st.session_state.trim_t_start),
        step=0.1, format="%.2f", key="sb_t_start",
    )
    sb_t_end = st.number_input(
        "Fin (s)", min_value=0.0, value=max(float(st.session_state.trim_t_end), 0.1),
        step=0.1, format="%.2f", key="sb_t_end",
    )
    st.caption("Les curseurs du lecteur mettent à jour ces valeurs automatiquement.")


# Convenience dict for watermark options
wm_opts_shared = {
    "position": sidebar_position,
    "custom_x": int(sidebar_custom_x),
    "custom_y": int(sidebar_custom_y),
}


# ─── Tabs ─────────────────────────────────────────────────────────────────────

tab_v, tab_p, tab_s, tab_t = st.tabs([
    "Watermark vidéo", "Watermark photo", "Capture d'écran", "Couper une vidéo (βêta)",
])


# ═══════════════════════════════════════════════════════════════════
# TAB 1 — WATERMARK VIDÉO
# ═══════════════════════════════════════════════════════════════════

with tab_v:
    col_params, col_prev = st.columns([2, 3], gap="large")

    with col_params:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        video_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="vu", label_visibility="collapsed",
        )

    if video_file:
        if st.session_state._last_video_name != video_file.name:
            st.session_state.thumbnail = None
            st.session_state.rendered_bytes = None
            st.session_state._last_video_name = video_file.name

        lp = DEFAULT_WM_FILE

        with tempfile.TemporaryDirectory() as tmp:
            vp = os.path.join(tmp, "src" + os.path.splitext(video_file.name)[1])
            with open(vp, "wb") as f:
                f.write(video_file.read())
            nfo = get_video_info(vp)

            with col_params:
                st.markdown(f"""
                <div class="specs-row">
                  <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo['width']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo['height']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(nfo['duration'])}</span></div>
                  <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo['fps']}</span></div>
                </div>""", unsafe_allow_html=True)
                st.caption("💡 Position et qualité : panneau latéral →")

            # Invalidate thumbnail if sidebar options changed
            opts_sig = (sidebar_position, sidebar_custom_x, sidebar_custom_y)
            if st.session_state.get("_v_opts_sig") != opts_sig:
                st.session_state.thumbnail = None
                st.session_state.rendered_bytes = None
                st.session_state["_v_opts_sig"] = opts_sig

            if st.session_state.thumbnail is None:
                with st.spinner("Génération de l'aperçu…"):
                    st.session_state.thumbnail = make_thumbnail(vp, lp, nfo, **wm_opts_shared)

            with col_prev:
                st.markdown('<div class="preview-wrap"><div class="preview-bar">Aperçu watermark</div>', unsafe_allow_html=True)
                st.image(st.session_state.thumbnail, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_params:
                if not st.session_state.rendered_bytes:
                    if st.button("Générer le rendu", key="vbtn"):
                        out = os.path.join(tmp, "video_ready_to_post.mp4")
                        ph = st.empty()
                        ph.markdown(
                            '<div class="encoding-wrap"><div class="encoding-ring"></div>'
                            '<span class="encoding-text">Encodage en cours…</span></div>'
                            '<div class="fake-progress-wrap"><div class="fake-progress-track">'
                            '<div class="fake-progress-bar"></div></div></div>',
                            unsafe_allow_html=True,
                        )
                        try:
                            render_video(vp, lp, out, nfo, quality_key=sidebar_quality, **wm_opts_shared)
                            ph.empty()
                            with open(out, "rb") as f:
                                st.session_state.rendered_bytes = f.read()
                            st.rerun()
                        except Exception as e:
                            ph.markdown(f'<div class="status status-err">Erreur : {e}</div>', unsafe_allow_html=True)
                else:
                    st.download_button(
                        "↓  Télécharger la vidéo",
                        data=st.session_state.rendered_bytes,
                        file_name="video_ready_to_post.mp4",
                        mime="video/mp4",
                        key="vdl",
                    )
    else:
        st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 2 — WATERMARK PHOTO
# ═══════════════════════════════════════════════════════════════════

with tab_p:
    col_p_params, col_p_prev = st.columns([2, 3], gap="large")

    with col_p_params:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        photo_files = st.file_uploader(
            "Déposez vos images ici",
            type=["png", "jpg", "jpeg"],
            key="pu",
            label_visibility="collapsed",
            accept_multiple_files=True,
        )

    if photo_files:
        lp2 = DEFAULT_WM_FILE

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

        with col_p_params:
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
            st.caption("💡 Position : panneau latéral →")

        # Preview first image
        first = photo_files[0]
        first.seek(0)
        base_prev = Image.open(first)
        result_prev = composite_logo(base_prev, lp2, **wm_opts_shared)

        with col_p_prev:
            st.markdown('<div class="preview-wrap"><div class="preview-bar">Aperçu — ' + first.name + '</div>', unsafe_allow_html=True)
            st.image(result_prev.convert("RGB"), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_p_params:
            st.markdown('<p class="section-label-mt">Téléchargement</p>', unsafe_allow_html=True)
            if len(photo_files) == 1:
                data, fname, mime = build_photo_output(photo_files[0], wm_opts_shared)
                st.download_button("↓  Télécharger la photo", data=data, file_name=fname, mime=mime, key="pdl_single")
            else:
                for i, pf in enumerate(photo_files):
                    data, fname, mime = build_photo_output(pf, wm_opts_shared)
                    st.download_button(f"↓  {pf.name}", data=data, file_name=fname, mime=mime, key=f"pdl_{i}")
                zip_buf = io.BytesIO()
                with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_STORED) as zf:
                    for pf in photo_files:
                        data, fname, _ = build_photo_output(pf, wm_opts_shared)
                        zf.writestr(fname, data)
                st.download_button(
                    "↓  Tout télécharger (.zip)",
                    data=zip_buf.getvalue(),
                    file_name="photos_watermark.zip",
                    mime="application/zip",
                    key="pdl_zip",
                )
    else:
        st.markdown('<div class="status status-idle">Déposez une ou plusieurs images via "Upload".</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 3 — CAPTURE D'ÉCRAN
# ═══════════════════════════════════════════════════════════════════

with tab_s:
    col_s_params, col_s_prev = st.columns([2, 3], gap="large")

    with col_s_params:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        scr_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="su", label_visibility="collapsed",
        )

    if scr_file:
        with tempfile.TemporaryDirectory() as tmp_s:
            sp = os.path.join(tmp_s, "src" + os.path.splitext(scr_file.name)[1])
            with open(sp, "wb") as f:
                f.write(scr_file.read())
            nfo_s = get_video_info(sp)
            dur_s = nfo_s["duration"]

            with col_s_params:
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
                    key="cap_tc_ni", label_visibility="collapsed",
                )

            frame = extract_frame(sp, timecode)

            with col_s_prev:
                st.markdown(f'<div class="preview-wrap"><div class="preview-bar">Aperçu — {fmt_time(timecode)} / {fmt_time(dur_s)}</div>', unsafe_allow_html=True)
                st.image(frame, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_s_params:
                buf_s = io.BytesIO()
                frame.save(buf_s, format="PNG")
                st.download_button(
                    "↓  Télécharger la capture",
                    data=buf_s.getvalue(),
                    file_name=f"capture_{fmt_time(timecode).replace(':', '-')}.png",
                    mime="image/png",
                    key="sdl",
                )
    else:
        st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# TAB 4 — COUPER UNE VIDÉO
# ═══════════════════════════════════════════════════════════════════

with tab_t:
    col_t_params, col_t_player = st.columns([2, 3], gap="large")

    with col_t_params:
        st.markdown('<p class="section-label">Source</p>', unsafe_allow_html=True)
        trim_file = st.file_uploader(
            "Déposez votre vidéo ici",
            type=["mp4", "mov", "avi", "mkv", "webm"],
            key="tu", label_visibility="collapsed",
        )

    if trim_file:
        if st.session_state._last_trim_name != trim_file.name:
            st.session_state.trim_bytes = None
            st.session_state._last_trim_name = trim_file.name
            st.session_state.trim_t_start = 0.0
            st.session_state.trim_t_end = 0.0

        with tempfile.TemporaryDirectory() as tmp_t:
            tp = os.path.join(tmp_t, "src" + os.path.splitext(trim_file.name)[1])
            with open(tp, "wb") as f:
                f.write(trim_file.read())
            nfo_t = get_video_info(tp)
            dur_t = nfo_t["duration"]

            # Initialise t_end au chargement d'un nouveau fichier
            if st.session_state.trim_t_end == 0.0:
                st.session_state.trim_t_end = float(dur_t)

            with col_t_params:
                st.markdown(f"""
                <div class="specs-row">
                  <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo_t['width']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo_t['height']} px</span></div>
                  <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time(dur_t)}</span></div>
                  <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo_t['fps']}</span></div>
                </div>""", unsafe_allow_html=True)
                st.caption(
                    f"⏱ Utilisez les curseurs du lecteur **ou** les champs "
                    f"**Début / Fin** dans la barre latérale pour définir la sélection."
                )

            # Read sidebar values as the authoritative trim points
            t_start = float(st.session_state.get("sb_t_start", 0.0))
            t_end   = float(st.session_state.get("sb_t_end",   dur_t))
            t_start = max(0.0, min(t_start, dur_t))
            t_end   = max(t_start + 0.1, min(t_end, dur_t))

            # ── Player HTML with postMessage bridge ──────────────────────────
            with open(tp, "rb") as f:
                vid_b64 = _b64.b64encode(f.read()).decode()
            ext_mime = "video/mp4"
            if tp.endswith(".mov"):  ext_mime = "video/quicktime"
            elif tp.endswith(".webm"): ext_mime = "video/webm"

            dur_str   = str(round(dur_t, 4))
            dur_fmt   = fmt_time(dur_t)
            t_start_s = str(round(t_start, 4))
            t_end_s   = str(round(t_end,   4))

            # The iframe sends {tS, tE} to the parent via postMessage.
            # A tiny JS snippet in the parent page forwards to Streamlit query params
            # through a hidden text_input updated by the component — the cleanest
            # approach without a custom component package.
            trim_html = f"""<!DOCTYPE html><html><head>
<meta charset='utf-8'>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#fff;padding:0 0 20px;}}
video{{width:100%;border-radius:10px;background:#111;display:block;max-height:260px;object-fit:contain;}}
.pbar{{display:flex;align-items:center;gap:10px;margin-top:10px;}}
.pbtn{{width:34px;height:34px;border-radius:50%;border:1.5px solid #e4e4e4;background:#fff;cursor:pointer;display:flex;align-items:center;justify-content:center;flex-shrink:0;transition:border-color .12s;outline:none;}}
.pbtn:hover{{border-color:#0068B1;}}
.pbtn svg{{width:11px;height:11px;fill:#444;pointer-events:none;}}
.tdisp{{font-size:11px;color:#999;flex-shrink:0;min-width:78px;text-align:right;font-variant-numeric:tabular-nums;}}
.pwrap{{flex:1;position:relative;height:32px;display:flex;align-items:center;cursor:pointer;}}
.ptrack,.ctrack{{position:absolute;left:0;right:0;height:3px;background:#ebebeb;border-radius:99px;}}
.psel{{position:absolute;height:3px;background:#d4e6f5;border-radius:99px;pointer-events:none;z-index:1;}}
.pfill{{position:absolute;height:3px;background:#0068B1;border-radius:99px;pointer-events:none;z-index:2;}}
.pmark-s,.pmark-e{{position:absolute;top:50%;transform:translateY(-50%);width:1px;height:10px;background:#0068B1;opacity:.5;pointer-events:none;z-index:3;}}
.ph{{position:absolute;top:50%;transform:translate(-50%,-50%);width:4px;height:16px;background:#0068B1;border-radius:99px;cursor:grab;z-index:5;}}
.ph:hover{{height:20px;}} .ph:active{{cursor:grabbing;opacity:.75;}}
.sect{{margin-top:22px;}}
.sect-top{{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;}}
.clbl{{font-size:10px;font-weight:500;color:#aaa;letter-spacing:.06em;text-transform:uppercase;}}
.srange{{font-size:12px;font-weight:500;color:#555;font-variant-numeric:tabular-nums;}}
.srange em{{font-style:normal;color:#0068B1;font-weight:600;}}
.cwrap{{position:relative;height:40px;display:flex;align-items:center;user-select:none;touch-action:none;margin:0 8px;}}
.csel{{position:absolute;height:3px;background:#0068B1;opacity:.25;border-radius:99px;pointer-events:none;}}
.chandle{{position:absolute;top:50%;transform:translate(-50%,-50%);width:6px;height:22px;background:#0068B1;border-radius:99px;cursor:ew-resize;z-index:3;}}
.chandle:hover,.chandle.dragging{{width:8px;}}
.dur-chip{{display:inline-block;background:#eef5fb;color:#0068B1;font-size:10px;font-weight:600;padding:2px 7px;border-radius:99px;margin-left:7px;}}
.info-bar{{font-size:10px;color:#aaa;text-align:center;margin-top:14px;}}
</style></head><body>
<video id='vid' src='data:{ext_mime};base64,{vid_b64}' preload='metadata'></video>
<div class='pbar'>
  <button class='pbtn' id='pbtn' onclick='togglePlay()'>
    <svg id='psvg' viewBox='0 0 24 24'><polygon id='ico_play' points='5,3 19,12 5,21'/><rect id='ico_p1' x='6' y='4' width='4' height='16' style='display:none'/><rect id='ico_p2' x='14' y='4' width='4' height='16' style='display:none'/></svg>
  </button>
  <div class='pwrap' id='pw'>
    <div class='ptrack'></div><div class='psel' id='ps'></div><div class='pfill' id='pf'></div>
    <div class='pmark-s' id='pms'></div><div class='pmark-e' id='pme'></div>
    <div class='ph' id='ph' style='left:0%'></div>
  </div>
  <div class='tdisp' id='td'>0:00 / {dur_fmt}</div>
</div>
<div class='sect'>
  <div class='sect-top'>
    <span class='clbl'>Sélection<span class='dur-chip' id='durChip'>0:00</span></span>
    <span class='srange' id='srange'><em>0:00</em> → <em>{dur_fmt}</em></span>
  </div>
  <div class='cwrap' id='cw'>
    <div class='ctrack'></div><div class='csel' id='cs'></div>
    <div class='chandle' id='hs' style='left:0%'></div>
    <div class='chandle' id='he' style='left:100%'></div>
  </div>
</div>
<p class='info-bar'>Faites glisser les curseurs, puis mettez à jour Début/Fin dans la barre latérale.</p>
<script>
var vid=document.getElementById('vid'),dur={dur_str},tS={t_start_s},tE={t_end_s},dr=null;
function fT(s){{var m=Math.floor(s/60),sc=Math.floor(s%60);return m+':'+(sc<10?'0':'')+sc;}}
function pct(t){{return(t/dur*100).toFixed(4)+'%';}}
function updC(){{
  var hs=document.getElementById('hs'),he=document.getElementById('he');
  hs.style.left=pct(tS); he.style.left=pct(tE);
  document.getElementById('cs').style.left=pct(tS);
  document.getElementById('cs').style.width=((tE-tS)/dur*100).toFixed(4)+'%';
  document.getElementById('ps').style.left=pct(tS);
  document.getElementById('ps').style.width=((tE-tS)/dur*100).toFixed(4)+'%';
  document.getElementById('pms').style.left=pct(tS);
  document.getElementById('pme').style.left=pct(tE);
  document.getElementById('srange').innerHTML='<em>'+fT(tS)+'</em> → <em>'+fT(tE)+'</em>';
  document.getElementById('durChip').textContent=fT(tE-tS);
  updPlayheadFill();
}}
function updPlayheadFill(){{
  var ct=vid.currentTime,ps=tS/dur*100,pc=Math.max(ps,Math.min(tE/dur*100,ct/dur*100));
  document.getElementById('pf').style.left=ps.toFixed(4)+'%';
  document.getElementById('pf').style.width=(pc-ps).toFixed(4)+'%';
}}
vid.addEventListener('timeupdate',function(){{
  document.getElementById('ph').style.left=(vid.currentTime/dur*100).toFixed(4)+'%';
  updPlayheadFill();
  document.getElementById('td').textContent=fT(vid.currentTime)+' / '+fT(dur);
  if(vid.currentTime>=tE){{vid.pause();vid.currentTime=tE;}}
}});
function setPlayIcon(p){{
  document.getElementById('ico_play').style.display=p?'none':'block';
  document.getElementById('ico_p1').style.display=p?'block':'none';
  document.getElementById('ico_p2').style.display=p?'block':'none';
}}
function togglePlay(){{if(vid.paused){{if(vid.currentTime<tS||vid.currentTime>=tE)vid.currentTime=tS;vid.play();}}else{{vid.pause();}}}}
vid.addEventListener('pause',function(){{setPlayIcon(false);}});
vid.addEventListener('play',function(){{setPlayIcon(true);}});
function posE(e,el){{var r=el.getBoundingClientRect(),x=(e.touches?e.touches[0].clientX:e.clientX)-r.left;return Math.max(0,Math.min(1,x/r.width))*dur;}}
document.getElementById('ph').addEventListener('mousedown',function(e){{e.preventDefault();dr='head';}});
document.getElementById('ph').addEventListener('touchstart',function(){{dr='head';}},{{passive:true}});
document.getElementById('pw').addEventListener('click',function(e){{if(dr)return;var t=Math.max(tS,Math.min(tE,posE(e,this)));vid.currentTime=t;}});
document.getElementById('hs').addEventListener('mousedown',function(e){{e.preventDefault();dr='s';this.classList.add('dragging');}});
document.getElementById('he').addEventListener('mousedown',function(e){{e.preventDefault();dr='e';this.classList.add('dragging');}});
document.getElementById('hs').addEventListener('touchstart',function(){{dr='s';this.classList.add('dragging');}},{{passive:true}});
document.getElementById('he').addEventListener('touchstart',function(){{dr='e';this.classList.add('dragging');}},{{passive:true}});
function onMove(e){{
  if(!dr)return;
  if(dr==='head'){{var t=Math.max(tS,Math.min(tE,posE(e,document.getElementById('pw'))));vid.currentTime=t;}}
  else if(dr==='s'){{tS=Math.min(posE(e,document.getElementById('cw')),tE-0.1);updC();}}
  else{{tE=Math.max(posE(e,document.getElementById('cw')),tS+0.1);updC();}}
}}
document.addEventListener('mousemove',onMove);
document.addEventListener('touchmove',onMove,{{passive:true}});
document.addEventListener('mouseup',function(){{
  if(dr==='s')document.getElementById('hs').classList.remove('dragging');
  if(dr==='e')document.getElementById('he').classList.remove('dragging');
  dr=null;
}});
document.addEventListener('touchend',function(){{
  document.getElementById('hs').classList.remove('dragging');
  document.getElementById('he').classList.remove('dragging');
  dr=null;
}});
updC();
</script></body></html>"""

            with col_t_player:
                components.html(trim_html, height=430, scrolling=False)

            with col_t_params:
                st.markdown(
                    f"**Sélection actuelle :** `{fmt_time(t_start)}` → `{fmt_time(t_end)}` "
                    f"({fmt_time(t_end - t_start)})"
                )

                if not st.session_state.trim_bytes:
                    if st.button("Couper la vidéo", key="tbtn"):
                        out_t = os.path.join(tmp_t, "video_coupee.mp4")
                        ph_t = st.empty()
                        ph_t.markdown(
                            '<div class="encoding-wrap"><div class="encoding-ring"></div>'
                            '<span class="encoding-text">Coupe en cours…</span></div>'
                            '<div class="fake-progress-wrap"><div class="fake-progress-track">'
                            '<div class="fake-progress-bar"></div></div></div>',
                            unsafe_allow_html=True,
                        )
                        try:
                            trim_video(tp, out_t, t_start, t_end)
                            ph_t.empty()
                            with open(out_t, "rb") as f:
                                st.session_state.trim_bytes = f.read()
                            st.rerun()
                        except Exception as e:
                            ph_t.markdown(f'<div class="status status-err">Erreur : {e}</div>', unsafe_allow_html=True)
                else:
                    st.download_button(
                        "↓  Télécharger la vidéo",
                        data=st.session_state.trim_bytes,
                        file_name="video_coupee.mp4",
                        mime="video/mp4",
                        key="tdl",
                    )
                    if st.button("Nouvelle découpe", key="t_reset"):
                        st.session_state.trim_bytes = None
                        st.rerun()
    else:
        st.markdown('<div class="status status-idle">Déposez une vidéo via "Upload".</div>', unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────

st.markdown("""
<div class="site-footer">
  <span class="footer-name">lucas.bessonnat@leprogres.fr</span>
  <span>v3.0 — Wide mode. Aucune donnée n'est conservée sur un serveur.</span>
</div>
""", unsafe_allow_html=True)
