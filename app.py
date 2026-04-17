import streamlit as st
import streamlit.components.v1 as components
import subprocess
import tempfile
import base64 as _b64
import os
import math
import io
import zipfile
from PIL import Image, ImageDraw, ImageFont, ImageOps

# FICHIERS STATIQUES
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

# CSS GLOBAL
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');
:root {
  --blue:        #0068B1;
  --blue-dim:    #e8f2fb;
  --white:       #ffffff;
  --bg:          #fafafa;
  --ink:         #111111;
  --sub:         #555555;
  --muted:       #999999;
  --border:      #e4e4e4;
  --header-h:    64px;
  --footer-h:    52px;
}
html, body, [data-testid="stAppViewContainer"] {
  background: var(--white) !important;
  font-family: 'Roboto', sans-serif !important;
}
.block-container { padding: 0 2.5rem 2rem !important; max-width: 100% !important; }
#MainMenu, footer, header, [data-testid="stToolbar"] { display: none !important; }

.site-header {
  height: var(--header-h);
  border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.site-header img { height: 38px; }

/* Onglets style Canva/Minimal */
div[data-testid="stTabs"] [data-baseweb="tab-list"] { background: transparent !important; }
div[data-testid="stTabs"] [data-baseweb="tab"] { font-size: 0.85rem !important; }

.section-label { font-size: 0.68rem; font-weight: 500; color: var(--muted); text-transform: uppercase; margin-bottom: 0.5rem; }
.preview-placeholder {
  display: flex; align-items: center; justify-content: center; flex-direction: column;
  min-height: 400px; border: 1px dashed var(--border); border-radius: 10px; background: var(--bg); color: var(--muted);
}
.status { font-size: 0.78rem; padding: 0.5rem 0; }
.status-ok { color: #166534; }
.status-idle { color: #999999; }
</style>
""", unsafe_allow_html=True)

# HEADER
with open(LOGO_FILE, "rb") as f:
    logo_b64 = _b64.b64encode(f.read()).decode()
st.markdown(f'<div class="site-header"><img src="data:image/png;base64,{logo_b64}" /><span>v3.0</span></div>', unsafe_allow_html=True)

# --- FONCTIONS UTILES ---

def generate_social_visual(bg_image, surtitre, titre, wm_img, wm_pos, img_y_offset, img_scale):
    canvas_w, canvas_h = 1080, 1350
    canvas = Image.new("RGB", (canvas_w, canvas_h), "#FFFFFF")

    # Image de fond (Mode "Cover" avec offset et scale)
    img_w, img_h = bg_image.size
    ratio = max(canvas_w/img_w, canvas_h/img_h) * img_scale
    new_w, new_h = int(img_w * ratio), int(img_h * ratio)
    resized_img = bg_image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    x_offset = (canvas_w - new_w) // 2
    y_offset = (canvas_h - new_h) // 2 + img_y_offset
    canvas.paste(resized_img, (x_offset, y_offset))

    draw = ImageDraw.Draw(canvas)
    blue_color = "#0068B1"
    
    # Polices
    try:
        font_surtitre = ImageFont.truetype("Roboto-Bold.ttf", 40)
        font_titre = ImageFont.truetype("Roboto-Bold.ttf", 55)
    except:
        font_surtitre = font_titre = ImageFont.load_default()

    # Dessin des cartouches
    padding = 21
    radius = 72
    margin_left = 60
    current_y = 900 # Position de base pour les textes en bas

    def draw_block(text, font, t_col, b_col, y):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
        w, h = tw + padding*2.5, th + padding*2.5
        draw.rounded_rectangle([margin_left, y, margin_left+w, y+h], radius=radius, fill=b_col)
        draw.text((margin_left + padding*1.2, y + padding*0.6), text, font=font, fill=t_col)
        return h

    if surtitre:
        h_sur = draw_block(surtitre.upper(), font_surtitre, blue_color, "#FFFFFF", current_y)
        current_y += h_sur + 15
    if titre:
        draw_block(titre, font_titre, "#FFFFFF", blue_color, current_y)

    # Watermark
    if wm_img:
        wm_img.thumbnail((220, 220))
        ww, wh = wm_img.size
        m = 50
        pos_map = {
            "Haut gauche": (m, m), "Haut droite": (canvas_w-ww-m, m),
            "Bas gauche": (m, canvas_h-wh-m), "Bas droite": (canvas_w-ww-m, canvas_h-wh-m)
        }
        canvas.paste(wm_img, pos_map.get(wm_pos, (m, m)), wm_img if wm_img.mode == 'RGBA' else None)
    
    return canvas

# --- INTERFACE ---

# Initialisation session_state
for k in ["canva_result_bytes"]:
    if k not in st.session_state: st.session_state[k] = None

tabs = st.tabs(["Watermark Vidéo", "Capture", "Fusion", "Canva 1080x1350"])

# ONGLETS SIMPLIFIÉS POUR L'EXEMPLE (Focus sur Canva)
with tabs[3]: # Onglet Canva
    col_ctrl, col_prev = st.columns([4, 6], gap="large")
    
    with col_ctrl:
        st.markdown('<p class="section-label">Image de fond</p>', unsafe_allow_html=True)
        up_img = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"], key="canva_up", label_visibility="collapsed")
        
        st.markdown('<p class="section-label">Textes</p>', unsafe_allow_html=True)
        surtitre = st.text_input("Surtitre (blanc)", value="LE PROGRÈS")
        titre = st.text_area("Titre (bleu)", value="Votre titre ici")
        
        st.markdown('<p class="section-label">Ajustements Image</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        scale = c1.slider("Zoom", 1.0, 2.5, 1.0, 0.05)
        y_off = c2.slider("Position Y", -600, 600, 0)
        
        st.markdown('<p class="section-label">Watermark</p>', unsafe_allow_html=True)
        wm_pos = st.selectbox("Position du logo", ["Haut droite", "Haut gauche", "Bas droite", "Bas gauche"])
        
        if up_img:
            if st.button("Générer le visuel", use_container_width=True):
                with st.spinner("Création..."):
                    img_bg = Image.open(up_img).convert("RGB")
                    try: wm_icon = Image.open(DEFAULT_WM_FILE).convert("RGBA")
                    except: wm_icon = None
                    
                    res = generate_social_visual(img_bg, surtitre, titre, wm_icon, wm_pos, y_off, scale)
                    
                    buf = io.BytesIO()
                    res.save(buf, format="PNG")
                    st.session_state.canva_result_bytes = buf.getvalue()

    with col_prev:
        if st.session_state.canva_result_bytes:
            st.image(st.session_state.canva_result_bytes, use_container_width=True)
            st.download_button("↓ Télécharger (PNG)", st.session_state.canva_result_bytes, "visuel.png", "image/png")
        else:
            st.markdown("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/></svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>
            """, unsafe_allow_html=True)

# FOOTER
st.markdown(f"""
<div class="site-footer">
  <span class="footer-name">Dernière màj le <i>17/04/2026</i></span>
  <span>Contact : lucas.bessonnat@leprogres.fr</span>
</div>
""", unsafe_allow_html=True)
