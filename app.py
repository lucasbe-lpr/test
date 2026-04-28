import streamlit as st 
import streamlit .components .v1 as components 
import subprocess 
import tempfile 
import base64 as _b64 
import os 
import math 
import io 
import zipfile 
from PIL import Image 

LOGO_FILE ="luluflix.png"
DEFAULT_WM_FILE ="lpr.png"
FAVICON_FILE ="favicon.png"

try :
    _fav_img =Image .open (FAVICON_FILE )
except Exception :
    _fav_img ="▶"

st .set_page_config (
page_title ="Luluflix",
page_icon =_fav_img ,
layout ="wide",
initial_sidebar_state ="collapsed",
)

st .markdown ("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500&family=Roboto+Condensed:wght@400;500;700&display=swap');

/* VARIABLES DE COULEUR ET DE TAILLE — modifier ici pour changer le thème */
:root {
  --blue:        #0068B1;
  --blue-dim:    #e8f2fb;
  --white:       #ffffff;
  --bg:          #fafafa;
  --ink:         #111111;
  --sub:         #555555;
  --muted:       #999999;
  --border:      #e4e4e4;
  --border-mid:  #d0d0d0;
  --green:       #166534;
  --red:         #991b1b;
  --red-bg:      #fff1f1;
  --header-h:    64px;
  --tabs-h:      48px;
  --footer-h:    52px;
  --panel-v-pad: 1.5rem;
}

*, *::before, *::after { box-sizing: border-box; }

/* BASE — fond blanc, typo Roboto sur tout le body Streamlit */
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

/* LAYOUT PRINCIPAL — pleine largeur, padding horizontal uniquement */
.block-container {
  background: var(--white) !important;
  padding: 0 2.5rem 2rem !important;
  max-width: 100% !important;
}

/* MASQUER les éléments natifs Streamlit non souhaités */
#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { display: none !important; }

/* HEADER SITE */
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

/* ONGLETS — style minimaliste, soulignement bleu sur l'actif */
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
div[data-testid="stTabs"] [data-baseweb="tab-panel"] { padding: 0 !important; }

/* COLONNES — panneau gauche (contrôles) et panneau droit (aperçu) */
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
[data-testid="column"] { padding-top: 0 !important; }

/* COLONNES STREAMLIT — aligner en haut, pas de hauteur forcée */
[data-testid="stHorizontalBlock"] { align-items: flex-start !important; }
[data-testid="stHorizontalBlock"] > [data-testid="stColumn"] { min-height: 0 !important; }

/* FILE UPLOADER — zone de dépôt stylisée */
[data-testid="stFileUploader"] { background: transparent !important; margin-bottom: 1.4rem !important; }
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
[data-testid="stFileUploaderDropzoneInstructions"] { text-align: center !important; }
[data-testid="stFileUploaderDropzoneInstructions"] * {
  color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.82rem !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] span { color: var(--sub) !important; font-weight: 500 !important; }
[data-testid="stFileUploader"] button {
  background: var(--white) !important;
  border: 1px solid var(--border-mid) !important;
  color: var(--sub) !important;
  font-family: 'Roboto', sans-serif !important;
  font-size: 0.78rem !important;
  padding: 0.28rem 0.9rem !important;
  border-radius: 999px !important;
  box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
}
[data-testid="stFileUploader"] button:hover { border-color: var(--blue) !important; color: var(--blue) !important; }
[data-testid="stFileUploaderFileName"] { color: var(--ink) !important; font-weight: 500 !important; font-size: 0.82rem !important; }
[data-testid="stFileUploaderDeleteBtn"] button {
  background: transparent !important; border: none !important;
  color: var(--muted) !important; box-shadow: none !important; border-radius: 4px !important;
}
[data-testid="stFileUploaderDeleteBtn"] button:hover { color: var(--red) !important; background: var(--red-bg) !important; }

/* LABELS DE SECTION — petites caps grises au-dessus de chaque bloc */
.section-label {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 0;
}
.section-label-mt {
  font-size: 0.68rem; font-weight: 500; color: var(--muted);
  letter-spacing: 0.06em; text-transform: uppercase; margin-bottom: 0.5rem; margin-top: 1.2rem;
}

/* SPECS ROW — bande d'infos techniques (dimensions, durée, fps) */
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

/* PREVIEW WRAP — cadre autour de l'aperçu vidéo/image */
.preview-wrap {
  border: 1px solid var(--border); border-radius: 10px;
  overflow: hidden; background: #f0f0f0;
  display: flex; flex-direction: column;
}
.preview-bar {
  padding: 0.35rem 0.85rem; border-bottom: 1px solid var(--border);
  background: var(--white); font-size: 0.62rem; color: var(--muted);
  font-weight: 500; letter-spacing: 0.05em; text-transform: uppercase;
  flex-shrink: 0;
}
.preview-wrap [data-testid="stImage"],
.preview-wrap [data-testid="stImage"] > div,
.preview-wrap [data-testid="stImage"] figure {
  margin: 0 !important; padding: 0 !important;
  line-height: 0 !important; width: 100% !important;
}
.preview-wrap [data-testid="stImage"] img {
  width: 100% !important; height: auto !important;
  display: block !important; object-fit: contain !important;
}

/* BOUTONS — bleu pour les actions, vert pour les téléchargements */
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

/* BOUTONS DE TELECHARGEMENT — vert uniforme pour tous */
div.stDownloadButton > button,
div[data-testid="stDownloadButton"] > button {
  width: 100% !important; background: #16a34a !important; border: none !important;
  color: #fff !important; font-family: 'Roboto', sans-serif !important;
  font-size: 0.85rem !important; font-weight: 500 !important;
  padding: 0 1.4rem !important; height: 38px !important; border-radius: 999px !important;
  transition: background 0.15s, transform 0.1s !important;
  box-shadow: 0 1px 2px rgba(22,163,74,0.18), 0 2px 6px rgba(22,163,74,0.1) !important;
}
div.stDownloadButton > button:hover,
div[data-testid="stDownloadButton"] > button:hover {
  background: #15803d !important; transform: translateY(-1px) !important;
}
div.stDownloadButton > button:active,
div[data-testid="stDownloadButton"] > button:active { transform: translateY(0) !important; }

div[data-testid="stProgress"] { display: none !important; }

/* SPINNER D'ENCODAGE — anneau rotatif + barre de progression animée */
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

/* MESSAGES DE STATUT — ok / erreur / idle */
.status { font-size: 0.78rem; padding: 0.5rem 0; margin: 0.5rem 0; color: var(--muted); line-height: 1.4; }
.status-ok   { color: var(--green); }
.status-err  { color: var(--red); }
.status-idle { color: var(--muted); }

/* FOOTER */
.site-footer {
  height: var(--footer-h);
  margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);
  display: flex; justify-content: space-between; align-items: center;
  font-size: 0.7rem; color: var(--muted);
  text-align: right;
}
.footer-name { color: var(--sub); font-weight: 500; }

div[data-testid="stSpinner"] p {
  font-size: 0.78rem !important; color: var(--muted) !important;
  font-family: 'Roboto', sans-serif !important;
}

/* NUMBER INPUT — boutons +/- centrés et carrés */
[data-testid="stNumberInput"] > div,
[data-testid="stNumberInput"] [data-baseweb="base-input"] { align-items: center !important; }
[data-testid="stNumberInputStepDown"],
[data-testid="stNumberInputStepUp"] {
  display: flex !important; align-items: center !important;
  justify-content: center !important; align-self: center !important;
  width: 28px !important; height: 28px !important;
  min-width: 28px !important; min-height: 28px !important;
  padding: 0 !important; margin: 0 2px !important;
  background: transparent !important; border: 1px solid var(--border) !important;
  border-radius: 4px !important; color: var(--sub) !important;
  box-shadow: none !important; cursor: pointer !important;
}
[data-testid="stNumberInputStepDown"]:hover,
[data-testid="stNumberInputStepUp"]:hover {
  background: var(--bg) !important; border-color: var(--border-mid) !important;
  color: var(--ink) !important; box-shadow: none !important;
}
[data-testid="stNumberInputStepDown"] svg,
[data-testid="stNumberInputStepUp"] svg { width: 12px !important; height: 12px !important; display: block !important; }
[data-testid="stNumberInput"] [data-baseweb="base-input"]:focus-within {
  border-color: var(--border-mid) !important; box-shadow: none !important;
}
[data-testid="stNumberInput"] input:focus { outline: none !important; box-shadow: none !important; }

/* SELECT BOX */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {
  border-color: var(--border) !important; border-radius: 6px !important; font-size: 0.85rem !important;
}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:hover { border-color: var(--blue) !important; }

/* LISTE DES FICHIERS IMPORTÉS (onglet photo) */
.photo-batch-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 0.4rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.photo-batch-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.photo-batch-dim  { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; margin-left: 0.5rem; }

/* PLACEHOLDER APERÇU — affiché quand aucun fichier n'est uploadé */
.preview-placeholder {
  display: flex; align-items: center; justify-content: center;
  flex-direction: column; gap: 0.6rem; min-height: 260px;
  border: 1px dashed var(--border); border-radius: 10px;
  background: var(--bg); color: var(--muted);
  font-size: 0.8rem; text-align: center;
  margin-top: 1.8rem;
}
.preview-placeholder svg { opacity: 0.25; }

/* TIMELINE CUTTER — outil de découpe vidéo */
.timeline-wrap {
  position: relative; height: 52px; background: var(--bg);
  border: 1px solid var(--border); border-radius: 8px; overflow: hidden;
  margin: 0.6rem 0; cursor: pointer; user-select: none;
}
.timeline-track {
  position: absolute; top: 0; left: 0; right: 0; bottom: 0;
  background: repeating-linear-gradient(
    90deg, transparent 0px, transparent 18px,
    var(--border) 18px, var(--border) 19px
  );
}
.timeline-selection {
  position: absolute; top: 0; bottom: 0;
  background: rgba(0, 104, 177, 0.15);
  border-left: 2px solid var(--blue); border-right: 2px solid var(--blue);
}
.timeline-handle {
  position: absolute; top: 0; bottom: 0; width: 6px;
  background: var(--blue); border-radius: 2px; cursor: ew-resize;
  display: flex; align-items: center; justify-content: center;
}
.timeline-handle::after {
  content: ''; display: block; width: 2px; height: 16px;
  background: rgba(255,255,255,0.7); border-radius: 1px;
}
.timeline-time-label {
  position: absolute; top: -1.4rem; font-size: 0.62rem;
  color: var(--blue); font-weight: 600; white-space: nowrap;
  transform: translateX(-50%);
}
.cut-info-row {
  display: flex; gap: 0.5rem; margin-top: 0.4rem;
}
.cut-info-cell {
  flex: 1; background: var(--bg); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.4rem 0.7rem;
  font-size: 0.78rem; color: var(--ink);
}
.cut-info-cell span { display: block; font-size: 0.58rem; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; }

/* FUSION — liste des vidéos à fusionner */
.merge-item {
  display: flex; align-items: center; gap: 0.6rem;
  padding: 0.45rem 0.7rem; border: 1px solid var(--border);
  border-radius: 6px; margin-bottom: 0.35rem; background: var(--bg);
  font-size: 0.78rem; color: var(--ink);
}
.merge-item-idx {
  width: 22px; height: 22px; border-radius: 50%;
  background: var(--blue-dim); color: var(--blue);
  font-size: 0.68rem; font-weight: 700;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.merge-item-name { font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; flex: 1; }
.merge-item-dur { font-size: 0.68rem; color: var(--muted); flex-shrink: 0; }

/* LECTEUR VIDEO APERÇU — player natif stylisé DA */
.video-preview-wrap {
  border: 1px solid var(--border); border-radius: 10px; overflow: hidden;
  background: #0a0a0a; margin-top: 0.2rem;
}
.video-preview-wrap video {
  width: 100%; display: block; max-height: 420px; object-fit: contain;
}
.video-preview-label {
  font-size: 0.58rem; font-weight: 500; text-transform: uppercase;
  letter-spacing: 0.07em; color: var(--muted);
  padding: 0.35rem 0.85rem; background: var(--white);
  border-bottom: 1px solid var(--border);
}
.video-preview-info {
  padding: 0.3rem 0.85rem; background: var(--white);
  border-top: 1px solid var(--border);
  font-size: 0.68rem; color: var(--muted); display: flex; gap: 1rem;
}
.video-preview-info b { color: var(--blue); font-weight: 600; }

/* OUTIL SON — options audio */
.audio-option-row {
  display: flex; gap: 0.5rem; margin-bottom: 0.8rem;
}
.audio-chip {
  flex: 1; text-align: center; padding: 0.45rem 0.5rem;
  border: 1px solid var(--border); border-radius: 6px;
  font-size: 0.75rem; color: var(--sub); background: var(--bg);
  cursor: pointer; transition: all 0.12s;
}
.audio-chip.active {
  border-color: var(--blue); background: var(--blue-dim); color: var(--blue); font-weight: 500;
}

/* OUTIL RECADRAGE — grille de presets */
.crop-presets {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.4rem; margin-bottom: 0.8rem;
}
.crop-preset-btn {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  padding: 0.5rem 0.3rem; border: 1px solid var(--border); border-radius: 6px;
  background: var(--bg); cursor: pointer; transition: all 0.12s; gap: 0.2rem;
}
.crop-preset-btn:hover { border-color: var(--blue); background: var(--blue-dim); }
.crop-preset-icon {
  background: var(--border-mid); border-radius: 2px;
}
.crop-preset-label { font-size: 0.65rem; color: var(--sub); font-weight: 500; }
.crop-preset-ratio { font-size: 0.58rem; color: var(--muted); }

</style>
""",unsafe_allow_html =True )

import base64 as _b64h 
with open (LOGO_FILE ,"rb")as _f :
    _logo_b64 =_b64h .b64encode (_f .read ()).decode ()
st .markdown (f"""
<div class="site-header">
  <img src="data:image/png;base64,{_logo_b64 }" alt="Luluflix" />
  <span class="site-header-right">version <code>1.0</code></span>
</div>
""",unsafe_allow_html =True )

PREVIEW_MAX_W =680 
PREVIEW_MAX_H =500 

def cap_image_for_preview (img :Image .Image )->Image .Image :

    w ,h =img .size 
    if w >PREVIEW_MAX_W :
        ratio =PREVIEW_MAX_W /w 
        w =PREVIEW_MAX_W 
        h =int (h *ratio )
    if h >PREVIEW_MAX_H :
        ratio =PREVIEW_MAX_H /h 
        h =PREVIEW_MAX_H 
        w =int (w *ratio )
    if (w ,h )==img .size :
        return img 
    return img .resize ((w ,h ),Image .LANCZOS )

def get_default_logo ()->str :
    return DEFAULT_WM_FILE 

    
POSITIONS =[
"Haut gauche","Haut centre","Haut droite",
"Milieu gauche","Centre","Milieu droite",
"Bas gauche","Bas centre","Bas droite",
"Coordonnées personnalisées",
]
DEFAULT_POSITION ="Haut droite"

def compute_xy (position :str ,W :int ,H :int ,logo_w :int ,logo_h :int ,
custom_x :int =0 ,custom_y :int =0 ,
margin_pct :float =0.05 )->tuple [int ,int ]:

    mx =int (W *margin_pct )
    my =int (H *margin_pct )
    if position =="Haut gauche":return mx ,my 
    if position =="Haut centre":return (W -logo_w )//2 ,my 
    if position =="Haut droite":return W -logo_w -mx ,my 
    if position =="Milieu gauche":return mx ,(H -logo_h )//2 
    if position =="Centre":return (W -logo_w )//2 ,(H -logo_h )//2 
    if position =="Milieu droite":return W -logo_w -mx ,(H -logo_h )//2 
    if position =="Bas gauche":return mx ,H -logo_h -my 
    if position =="Bas centre":return (W -logo_w )//2 ,H -logo_h -my 
    if position =="Bas droite":return W -logo_w -mx ,H -logo_h -my 
    return custom_x ,custom_y 

def composite_logo (
base :Image .Image ,logo_path :str ,
position :str =DEFAULT_POSITION ,
custom_x :int =0 ,custom_y :int =0 ,
force_w :int =None ,force_h :int =None ,
)->Image .Image :

    W =force_w if force_w else base .size [0 ]
    H =force_h if force_h else base .size [1 ]
    logo_w =int (math .sqrt (W **2 +H **2 )*0.1307 )
    logo =Image .open (logo_path ).convert ("RGBA")
    ratio =logo_w /logo .width 
    logo_h =int (logo .height *ratio )
    logo =logo .resize ((logo_w ,logo_h ),Image .LANCZOS )
    x ,y =compute_xy (position ,W ,H ,logo_w ,logo_h ,custom_x ,custom_y )
    out =base .convert ("RGBA")
    layer =Image .new ("RGBA",out .size ,(0 ,0 ,0 ,0 ))
    layer .paste (logo ,(x ,y ),logo )
    out =Image .alpha_composite (out ,layer )
    return out 

def get_video_info (path :str )->dict :

    import json as _json 
    cmd =[
    "ffprobe","-v","error",
    "-select_streams","v:0",
    "-show_entries","stream=width,height,r_frame_rate,tags=rotate",
    "-show_entries","stream_side_data=rotation",
    "-show_entries","format=duration",
    "-of","json",path 
    ]
    result =subprocess .run (cmd ,capture_output =True ,text =True )
    data =_json .loads (result .stdout )
    stream =data .get ("streams",[{}])[0 ]
    w =int (stream .get ("width",0 ))
    h =int (stream .get ("height",0 ))
    dur =float (data .get ("format",{}).get ("duration",0 ))
    fps_raw =stream .get ("r_frame_rate","25/1")
    try :
        num ,den =fps_raw .split ("/")
        fps =round (float (num )/float (den ),2 )
    except Exception :
        fps =25.0 
    rotate =0 
    for sd in stream .get ("side_data_list",[]):
        if "rotation"in sd :
            rotate =int (sd ["rotation"])
            break 
    if rotate ==0 :
        rotate =int (stream .get ("tags",{}).get ("rotate",0 ))
    if abs (rotate )in (90 ,270 ):
        w ,h =h ,w 
    return {"width":w ,"height":h ,"duration":dur ,"fps":fps ,"rotate":rotate }

def fmt_time (secs :float )->str :
    m ,s =divmod (int (secs ),60 )
    return f"{m }:{s :02d}"

def extract_frame (video_path :str ,timecode :float )->Image .Image :

    result =subprocess .run ([
    "ffmpeg","-y","-ss",str (timecode ),"-i",video_path ,
    "-vframes","1","-f","image2pipe","-vcodec","png","pipe:1"
    ],capture_output =True )
    return Image .open (io .BytesIO (result .stdout )).convert ("RGB")

def make_thumbnail (video_path :str ,logo_path :str ,info :dict ,
position :str =DEFAULT_POSITION ,custom_x :int =0 ,custom_y :int =0 )->Image .Image :

    result =subprocess .run ([
    "ffmpeg","-y","-i",video_path ,
    "-vframes","1","-f","image2pipe","-vcodec","png","pipe:1"
    ],capture_output =True )
    frame =Image .open (io .BytesIO (result .stdout )).convert ("RGBA")
    return composite_logo (
    frame ,logo_path ,
    position =position ,custom_x =custom_x ,custom_y =custom_y ,
    force_w =info ["width"],force_h =info ["height"]
    ).convert ("RGB")

    
QUALITY_PRESETS ={
"Standard (CRF 18 — recommandé)":{"crf":"18","preset":"fast"},
"Haute qualité (CRF 12)":{"crf":"12","preset":"slow"},
"Sans perte (CRF 0)":{"crf":"0","preset":"ultrafast"},
}

def render_video (
video_path :str ,logo_path :str ,output_path :str ,info :dict ,
position :str =DEFAULT_POSITION ,custom_x :int =0 ,custom_y :int =0 ,
quality_key :str ="Standard (CRF 18 — recommandé)",
progress_cb =None 
):

    W ,H =info ["width"],info ["height"]
    logo_w =int (math .sqrt (W **2 +H **2 )*0.1307 )
    logo_orig =Image .open (logo_path ).convert ("RGBA")
    ratio =logo_w /logo_orig .width 
    logo_h =int (logo_orig .height *ratio )
    logo_scaled =logo_orig .resize ((logo_w ,logo_h ),Image .LANCZOS )
    x ,y =compute_xy (position ,W ,H ,logo_w ,logo_h ,custom_x ,custom_y )

    tmp_logo_dir =tempfile .mkdtemp ()
    tmp_logo_path =os .path .join (tmp_logo_dir ,"wm_prescaled.png")
    logo_scaled .save (tmp_logo_path ,format ="PNG")

    filter_complex =f"[0:v][1:v]overlay={x }:{y }"
    q =QUALITY_PRESETS .get (quality_key ,QUALITY_PRESETS ["Standard (CRF 18 — recommandé)"])
    cmd =[
    "ffmpeg","-y",
    "-i",video_path ,"-i",tmp_logo_path ,
    "-filter_complex",filter_complex ,
    "-c:v","libx264","-crf",q ["crf"],"-preset",q ["preset"],
    "-c:a","copy","-movflags","+faststart",
    "-progress","pipe:1",output_path 
    ]
    process =subprocess .Popen (cmd ,stdout =subprocess .PIPE ,stderr =subprocess .PIPE ,text =True )
    total =info ["duration"]
    while True :
        line =process .stdout .readline ()
        if not line :break 
        if line .strip ().startswith ("out_time_ms="):
            try :
                ms =int (line .strip ().split ("=")[1 ])
                if total >0 and progress_cb :
                    progress_cb (min (ms /1_000_000 /total ,1.0 ))
            except Exception :
                pass 
    process .wait ()
    if process .returncode !=0 :
        raise RuntimeError (process .stderr .read ())

def trim_video (video_path :str ,output_path :str ,t_start :float ,t_end :float ):

    cmd =[
    "ffmpeg","-y",
    "-ss",str (t_start ),"-to",str (t_end ),
    "-i",video_path ,
    "-c","copy","-movflags","+faststart",
    output_path 
    ]
    result =subprocess .run (cmd ,capture_output =True )
    if result .returncode !=0 :
        raise RuntimeError (result .stderr .decode ())

def watermark_options_ui (key_prefix :str )->dict :

    st .markdown ('<p class="section-label-mt">Watermark</p>',unsafe_allow_html =True )
    position =st .selectbox (
    "Position",POSITIONS ,
    index =POSITIONS .index (DEFAULT_POSITION ),
    key =f"{key_prefix }_pos",
    )
    custom_x ,custom_y =0 ,0 
    if position =="Coordonnées personnalisées":
        col_x ,col_y =st .columns (2 )
        with col_x :
            custom_x =st .number_input ("X (px depuis gauche)",min_value =0 ,value =0 ,step =1 ,key =f"{key_prefix }_cx")
        with col_y :
            custom_y =st .number_input ("Y (px depuis haut)",min_value =0 ,value =0 ,step =1 ,key =f"{key_prefix }_cy")
    return {"position":position ,"custom_x":int (custom_x ),"custom_y":int (custom_y )}

def merge_videos (video_paths :list ,output_path :str ):

    tmp_list =tempfile .mktemp (suffix =".txt")
    with open (tmp_list ,"w")as f :
        for p in video_paths :
            f .write (f"file '{p }'\n")
    cmd =[
    "ffmpeg","-y",
    "-f","concat","-safe","0",
    "-i",tmp_list ,
    "-c:v","libx264","-crf","18","-preset","fast",
    "-c:a","aac","-b:a","192k",
    "-movflags","+faststart",
    output_path 
    ]
    result =subprocess .run (cmd ,capture_output =True )
    os .unlink (tmp_list )
    if result .returncode !=0 :
        raise RuntimeError (result .stderr .decode ())

def remove_audio (video_path :str ,output_path :str ):

    cmd =[
    "ffmpeg","-y","-i",video_path ,
    "-c:v","copy","-an",
    "-movflags","+faststart",output_path 
    ]
    result =subprocess .run (cmd ,capture_output =True )
    if result .returncode !=0 :
        raise RuntimeError (result .stderr .decode ())

def replace_audio (video_path :str ,audio_path :str ,output_path :str ,loop_audio :bool =True ):

    loop_flag =["-stream_loop","-1"]if loop_audio else []
    cmd =[
    "ffmpeg","-y",
    "-i",video_path ,
    *loop_flag ,"-i",audio_path ,
    "-c:v","copy",
    "-c:a","aac","-b:a","192k",
    "-shortest",
    "-map","0:v:0","-map","1:a:0",
    "-movflags","+faststart",output_path 
    ]
    result =subprocess .run (cmd ,capture_output =True )
    if result .returncode !=0 :
        raise RuntimeError (result .stderr .decode ())

        
CROP_PRESETS =[
("9:16",9 ,16 ,"Stories"),
("1:1",1 ,1 ,"Carré"),
("16:9",16 ,9 ,"Comme à la télé"),
("4:5",4 ,5 ,"Portrait"),
("4:3",4 ,3 ,"Presque carré"),
("21:9",21 ,9 ,"Comme au ciné"),
]

def crop_video (video_path :str ,output_path :str ,
ratio_w :int ,ratio_h :int ,
position :str ="Centre"):

    info =get_video_info (video_path )
    W ,H =info ["width"],info ["height"]
    target_ratio =ratio_w /ratio_h 
    src_ratio =W /H 
    if src_ratio >target_ratio :
    
        new_w =int (H *target_ratio )
        new_h =H 
    else :
    
        new_w =W 
        new_h =int (W /target_ratio )
        
    new_w =new_w -(new_w %2 )
    new_h =new_h -(new_h %2 )
    
    if position =="Haut":
        x_off ,y_off =(W -new_w )//2 ,0 
    elif position =="Bas":
        x_off ,y_off =(W -new_w )//2 ,H -new_h 
    elif position =="Gauche":
        x_off ,y_off =0 ,(H -new_h )//2 
    elif position =="Droite":
        x_off ,y_off =W -new_w ,(H -new_h )//2 
    else :
        x_off ,y_off =(W -new_w )//2 ,(H -new_h )//2 
    vf =f"crop={new_w }:{new_h }:{x_off }:{y_off }"
    cmd =[
    "ffmpeg","-y","-i",video_path ,
    "-vf",vf ,
    "-c:v","libx264","-crf","18","-preset","fast",
    "-c:a","copy",
    "-movflags","+faststart",output_path 
    ]
    result =subprocess .run (cmd ,capture_output =True )
    if result .returncode !=0 :
        raise RuntimeError (result .stderr .decode ())

        
for k in ["thumbnail","rendered_bytes","_last_video_name",
"cut_bytes","_last_cut_name","merge_bytes",
"audio_bytes","_last_audio_name",
"crop_bytes","_last_crop_name"]:
    if k not in st .session_state :
        st .session_state [k ]=None 

tab_v ,tab_p ,tab_s ,tab_cut ,tab_merge ,tab_audio ,tab_crop ,tab_canva =st .tabs ([
"Watermark vidéo","Watermark photo","Capture d'écran",
"Couper","Fusionner","Son","Recadrer","Template RS"
])

with tab_v :
    col_ctrl ,col_prev =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        video_file =st .file_uploader (
        "Déposez votre vidéo ici",
        type =["mp4","mov","avi","mkv","webm"],
        key ="vu",label_visibility ="collapsed"
        )

    if video_file :
    
        if st .session_state ._last_video_name !=video_file .name :
            st .session_state .thumbnail =None 
            st .session_state .rendered_bytes =None 
            st .session_state ._last_video_name =video_file .name 

        lp =get_default_logo ()
        tmp =tempfile .mkdtemp ()
        vp =os .path .join (tmp ,"src"+os .path .splitext (video_file .name )[1 ])
        with open (vp ,"wb")as f :f .write (video_file .read ())
        nfo =get_video_info (vp )

        with col_ctrl :
            st .markdown (f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo ['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo ['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time (nfo ['duration'])}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo ['fps']}</span></div>
            </div>""",unsafe_allow_html =True )

            wm_opts =watermark_options_ui ("v")

            st .markdown ('<p class="section-label-mt">Qualité d\'export</p>',unsafe_allow_html =True )
            quality_key =st .selectbox (
            "Qualité",list (QUALITY_PRESETS .keys ()),
            key ="v_quality",label_visibility ="collapsed",
            )

            
            opts_sig =(wm_opts ["position"],wm_opts ["custom_x"],wm_opts ["custom_y"])
            if st .session_state .get ("_v_opts_sig")!=opts_sig :
                st .session_state .thumbnail =None 
                st .session_state .rendered_bytes =None 
                st .session_state ["_v_opts_sig"]=opts_sig 

            if st .session_state .thumbnail is None :
                with st .spinner ("Génération de l'aperçu…"):
                    st .session_state .thumbnail =make_thumbnail (vp ,lp ,nfo ,**wm_opts )

            st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )
            if not st .session_state .rendered_bytes :
                if st .button ("Générer le rendu",key ="vbtn"):
                    out =os .path .join (tmp ,"video_ready_to_post.mp4")
                    ph =st .empty ()
                    ph .markdown ('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Encodage en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',unsafe_allow_html =True )
                    try :
                        render_video (vp ,lp ,out ,nfo ,quality_key =quality_key ,**wm_opts )
                        ph .empty ()
                        with open (out ,"rb")as f :
                            st .session_state .rendered_bytes =f .read ()
                        st .rerun ()
                    except Exception as e :
                        ph .markdown (f'<div class="status status-err">Erreur : {e }</div>',unsafe_allow_html =True )
            else :
                st .download_button ("↓  Télécharger la vidéo",data =st .session_state .rendered_bytes ,
                file_name ="video_ready_to_post.mp4",mime ="video/mp4",key ="vdl")

        with col_prev :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            st .image (cap_image_for_preview (st .session_state .thumbnail ))
            st .markdown ('</div>',unsafe_allow_html =True )

    else :
        with col_ctrl :
            st .markdown ('<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_p :
    col_ctrl_p ,col_prev_p =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_p :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        photo_files =st .file_uploader (
        "Déposez vos images ici",
        type =["png","jpg","jpeg"],
        key ="pu",
        label_visibility ="collapsed",
        accept_multiple_files =True ,
        )

    if photo_files :
        lp2 =get_default_logo ()

        with col_ctrl_p :
        
            st .markdown ('<p class="section-label-mt">Fichiers importés</p>',unsafe_allow_html =True )
            for pf in photo_files :
                img_tmp =Image .open (pf )
                W_tmp ,H_tmp =img_tmp .size 
                pf .seek (0 )
                st .markdown (
                f'<div class="photo-batch-item">'
                f'<span class="photo-batch-name">📷 {pf .name }</span>'
                f'<span class="photo-batch-dim">{W_tmp } × {H_tmp } px</span>'
                f'</div>',
                unsafe_allow_html =True ,
                )

            wm_opts_p =watermark_options_ui ("p")

        def build_photo_output (pf ,opts ):
        
            pf .seek (0 )
            base =Image .open (pf )
            result =composite_logo (base ,lp2 ,**opts )
            buf =io .BytesIO ()
            ext =pf .name .rsplit (".",1 )[-1 ].lower ()
            if ext =="png":
                result .save (buf ,format ="PNG")
                return buf .getvalue (),pf .name .rsplit (".",1 )[0 ]+"_wm.png","image/png"
            else :
                result .convert ("RGB").save (buf ,format ="JPEG",quality =100 ,subsampling =0 )
                return buf .getvalue (),pf .name .rsplit (".",1 )[0 ]+"_wm.jpg","image/jpeg"

                
        with col_prev_p :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            grid_cols =st .columns (2 )
            for idx ,pf in enumerate (photo_files ):
                pf .seek (0 )
                base_prev =Image .open (pf )
                result_prev =composite_logo (base_prev ,lp2 ,**wm_opts_p )
                with grid_cols [idx %2 ]:
                    st .image (cap_image_for_preview (result_prev .convert ("RGB")),
                    caption =pf .name ,use_container_width =True )
            st .markdown ('</div>',unsafe_allow_html =True )

        with col_ctrl_p :
            if len (photo_files )==1 :
                data ,fname ,mime =build_photo_output (photo_files [0 ],wm_opts_p )
                st .download_button ("↓  Télécharger la photo",data =data ,
                file_name =fname ,mime =mime ,key ="pdl_single")
            else :
                st .markdown ('<p class="section-label-mt">Téléchargement</p>',unsafe_allow_html =True )

                
                for i in range (0 ,len (photo_files ),2 ):
                    row_files =photo_files [i :i +2 ]
                    btn_cols =st .columns (len (row_files ),gap ="small")
                    for j ,pf in enumerate (row_files ):
                        data ,fname ,mime =build_photo_output (pf ,wm_opts_p )
                        with btn_cols [j ]:
                            st .download_button (
                            f"↓  {pf .name }",
                            data =data ,file_name =fname ,mime =mime ,
                            key =f"pdl_{i +j }",
                            )

                            
                zip_buf =io .BytesIO ()
                with zipfile .ZipFile (zip_buf ,"w",zipfile .ZIP_STORED )as zf :
                    for pf in photo_files :
                        data ,fname ,_ =build_photo_output (pf ,wm_opts_p )
                        zf .writestr (fname ,data )
                st .download_button (
                "↓  Tout télécharger (.zip)",
                data =zip_buf .getvalue (),
                file_name ="photos_watermark.zip",
                mime ="application/zip",
                key ="pdl_zip",
                )

    else :
        with col_ctrl_p :
            st .markdown ('<div class="status status-idle">Déposez une ou plusieurs images via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_p :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_s :
    col_ctrl_s ,col_prev_s =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_s :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        scr_file =st .file_uploader ("Déposez votre vidéo ici",type =["mp4","mov","avi","mkv","webm"],
        key ="su",label_visibility ="collapsed")

    if scr_file :
        tmp_s =tempfile .mkdtemp ()
        sp =os .path .join (tmp_s ,"src"+os .path .splitext (scr_file .name )[1 ])
        with open (sp ,"wb")as f :f .write (scr_file .read ())
        nfo_s =get_video_info (sp )
        dur_s =nfo_s ["duration"]

        with col_ctrl_s :
            st .markdown (f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo_s ['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo_s ['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time (dur_s )}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo_s ['fps']}</span></div>
            </div>""",unsafe_allow_html =True )
            st .markdown ('<p class="section-label">Timecode (secondes)</p>',unsafe_allow_html =True )
            timecode =st .number_input (
            "tc",min_value =0.0 ,max_value =float (dur_s ),
            value =float (st .session_state .get ("cap_tc_ni",0.0 )),
            step =0.1 ,format ="%.2f",
            key ="cap_tc_ni",label_visibility ="collapsed")

        with st .spinner (""):
            frame =extract_frame (sp ,timecode )

        with col_ctrl_s :
            buf_s =io .BytesIO ()
            frame .save (buf_s ,format ="PNG")
            st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )
            st .download_button ("↓  Télécharger la capture",data =buf_s .getvalue (),
            file_name =f"capture_{fmt_time (timecode ).replace (':','-')}.png",
            mime ="image/png",key ="sdl")

        with col_prev_s :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            st .image (cap_image_for_preview (frame ))
            st .markdown ('</div>',unsafe_allow_html =True )

    else :
        with col_ctrl_s :
            st .markdown ('<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_s :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M23 7l-7 5 7 5V7z"/><rect x="1" y="5" width="15" height="14" rx="2"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_cut :
    col_ctrl_c ,col_prev_c =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_c :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        cut_file =st .file_uploader (
        "Déposez votre vidéo ici",
        type =["mp4","mov","avi","mkv","webm"],
        key ="cut_u",label_visibility ="collapsed"
        )

    if cut_file :
        if st .session_state ._last_cut_name !=cut_file .name :
            st .session_state .cut_bytes =None 
            st .session_state ._last_cut_name =cut_file .name 

        tmp_c =tempfile .mkdtemp ()
        cp =os .path .join (tmp_c ,"src"+os .path .splitext (cut_file .name )[1 ])
        with open (cp ,"wb")as f :f .write (cut_file .read ())
        nfo_c =get_video_info (cp )
        dur_c =nfo_c ["duration"]

        with col_ctrl_c :
            st .markdown (f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo_c ['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo_c ['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time (dur_c )}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo_c ['fps']}</span></div>
            </div>""",unsafe_allow_html =True )

            st .markdown ('<p class="section-label-mt">Début du segment</p>',unsafe_allow_html =True )
            t_start =st .slider (
            "Début",min_value =0.0 ,max_value =float (dur_c ),
            value =0.0 ,step =0.1 ,format ="%.1f s",
            key ="cut_start",label_visibility ="collapsed"
            )
            st .markdown ('<p class="section-label-mt">Fin du segment</p>',unsafe_allow_html =True )
            t_end =st .slider (
            "Fin",min_value =0.0 ,max_value =float (dur_c ),
            value =float (dur_c ),step =0.1 ,format ="%.1f s",
            key ="cut_end",label_visibility ="collapsed"
            )

            
            if t_end <=t_start :
                st .markdown ('<div class="status status-err">⚠ La fin doit être après le début.</div>',unsafe_allow_html =True )
                t_end =min (t_start +0.1 ,dur_c )

            seg_dur =t_end -t_start 
            st .markdown (f"""
            <div class="cut-info-row">
              <div class="cut-info-cell"><span>Début</span>{fmt_time (t_start )} ({t_start :.1f} s)</div>
              <div class="cut-info-cell"><span>Fin</span>{fmt_time (t_end )} ({t_end :.1f} s)</div>
              <div class="cut-info-cell"><span>Durée</span>{fmt_time (seg_dur )} ({seg_dur :.1f} s)</div>
            </div>""",unsafe_allow_html =True )

            st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )

            
            cut_sig =(t_start ,t_end ,cut_file .name )
            if st .session_state .get ("_cut_sig")!=cut_sig :
                st .session_state .cut_bytes =None 
                st .session_state ["_cut_sig"]=cut_sig 

            if not st .session_state .cut_bytes :
                if st .button ("Générer le découpage",key ="cut_btn"):
                    out_c =os .path .join (tmp_c ,"cut_output.mp4")
                    ph_c =st .empty ()
                    ph_c .markdown ('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Découpage en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',unsafe_allow_html =True )
                    try :
                        trim_video (cp ,out_c ,t_start ,t_end )
                        ph_c .empty ()
                        with open (out_c ,"rb")as f :
                            st .session_state .cut_bytes =f .read ()
                        st .rerun ()
                    except Exception as e :
                        ph_c .markdown (f'<div class="status status-err">Erreur : {e }</div>',unsafe_allow_html =True )
            else :
                st .download_button (
                "↓  Télécharger le segment",
                data =st .session_state .cut_bytes ,
                file_name ="segment_coupe.mp4",
                mime ="video/mp4",key ="cut_dl"
                )
                st .markdown ('<div class="status status-ok">Découpage terminé.</div>',unsafe_allow_html =True )

        with col_prev_c :
            st .markdown ('<p class="section-label">Aperçu du segment sélectionné</p>',unsafe_allow_html =True )
            
            
            with open (cp ,"rb")as _vf :
                _vb64 =_b64 .b64encode (_vf .read ()).decode ()
            _ext =os .path .splitext (cut_file .name )[1 ].lower ().lstrip (".")
            _mime ="video/mp4"if _ext in ("mp4","m4v")else f"video/{_ext }"
            components .html (f"""
<div style="border:1px solid #e4e4e4;border-radius:10px;overflow:hidden;background:#0a0a0a;">

  <video id="cutplayer" controls style="width:100%;display:block;max-height:380px;object-fit:contain;"
         src="data:{_mime };base64,{_vb64 }">
  </video>
</div>
<script>
  const p = document.getElementById('cutplayer');
  const tStart = {t_start };
  const tEnd = {t_end };
  p.addEventListener('loadedmetadata', () => {{ p.currentTime = tStart; }});
  p.addEventListener('timeupdate', () => {{
    if (p.currentTime >= tEnd) {{ p.pause(); p.currentTime = tStart; }}
  }});
  p.addEventListener('play', () => {{
    if (p.currentTime < tStart || p.currentTime >= tEnd) p.currentTime = tStart;
  }});
</script>""",height =460 )

    else :
        with col_ctrl_c :
            st .markdown ('<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_c :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <line x1="8" y1="3" x2="8" y2="21"/><line x1="16" y1="3" x2="16" y2="21"/>
                <rect x="1" y="5" width="22" height="14" rx="2"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_merge :
    col_ctrl_m ,col_prev_m =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_m :
        st .markdown ('<p class="section-label">Sources (dans l\'ordre de fusion)</p>',unsafe_allow_html =True )
        merge_files =st .file_uploader (
        "Déposez vos vidéos ici",
        type =["mp4","mov","avi","mkv","webm"],
        key ="merge_u",label_visibility ="collapsed",
        accept_multiple_files =True 
        )

    if merge_files and len (merge_files )>=2 :
    
        tmp_m =tempfile .mkdtemp ()
        merge_paths =[]
        total_dur =0.0 
        nfo_list =[]
        for i ,mf in enumerate (merge_files ):
            mp =os .path .join (tmp_m ,f"src_{i }"+os .path .splitext (mf .name )[1 ])
            with open (mp ,"wb")as f :f .write (mf .read ())
            merge_paths .append (mp )
            nfo_m =get_video_info (mp )
            nfo_list .append (nfo_m )
            total_dur +=nfo_m ["duration"]

        with col_ctrl_m :
            st .markdown ('<p class="section-label-mt">Fichiers à fusionner</p>',unsafe_allow_html =True )
            for i ,(mf ,nfo_m )in enumerate (zip (merge_files ,nfo_list )):
                st .markdown (
                f'<div class="merge-item">'
                f'<div class="merge-item-idx">{i +1 }</div>'
                f'<span class="merge-item-name">🎬 {mf .name }</span>'
                f'<span class="merge-item-dur">{fmt_time (nfo_m ["duration"])} — {nfo_m ["width"]}×{nfo_m ["height"]}</span>'
                f'</div>',
                unsafe_allow_html =True 
                )

            st .markdown (f"""
            <div class="specs-row" style="margin-top:0.8rem;">
              <div class="spec-cell"><span class="spec-k">Fichiers</span><span class="spec-v">{len (merge_files )}</span></div>
              <div class="spec-cell"><span class="spec-k">Durée totale</span><span class="spec-v">{fmt_time (total_dur )}</span></div>
              <div class="spec-cell"><span class="spec-k">Résolution</span><span class="spec-v">{nfo_list [0 ]['width']}×{nfo_list [0 ]['height']}</span></div>
            </div>""",unsafe_allow_html =True )

            st .markdown ("<div style='margin-top:1rem;'></div>",unsafe_allow_html =True )

            
            merge_sig =tuple (mf .name for mf in merge_files )
            if st .session_state .get ("_merge_sig")!=merge_sig :
                st .session_state .merge_bytes =None 
                st .session_state ["_merge_sig"]=merge_sig 

            if not st .session_state .merge_bytes :
                if st .button ("Fusionner les vidéos",key ="merge_btn"):
                    out_m =os .path .join (tmp_m ,"fusion_output.mp4")
                    ph_m =st .empty ()
                    ph_m .markdown ('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Fusion en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',unsafe_allow_html =True )
                    try :
                        merge_videos (merge_paths ,out_m )
                        ph_m .empty ()
                        with open (out_m ,"rb")as f :
                            st .session_state .merge_bytes =f .read ()
                        st .rerun ()
                    except Exception as e :
                        ph_m .markdown (f'<div class="status status-err">Erreur : {e }</div>',unsafe_allow_html =True )
            else :
                st .download_button (
                "↓  Télécharger la vidéo fusionnée",
                data =st .session_state .merge_bytes ,
                file_name ="fusion.mp4",
                mime ="video/mp4",key ="merge_dl"
                )
                st .markdown ('<div class="status status-ok">Fusion terminée.</div>',unsafe_allow_html =True )

        with col_prev_m :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            for i ,(mp ,mf )in enumerate (zip (merge_paths ,merge_files )):
                frame_m =extract_frame (mp ,0.0 )
                st .image (cap_image_for_preview (frame_m ),
                caption =f"{i +1 }. {mf .name }",use_container_width =True )

    elif merge_files and len (merge_files )==1 :
        with col_ctrl_m :
            st .markdown ('<div class="status status-idle">Ajoutez au moins une deuxième vidéo pour fusionner.</div>',unsafe_allow_html =True )
    else :
        with col_ctrl_m :
            st .markdown ('<div class="status status-idle">Déposez au moins <b>deux</b> vidéos via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_m :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M22 12H2M17 7l5 5-5 5M7 7l-5 5 5 5"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_audio :
    col_ctrl_a ,col_prev_a =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_a :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        audio_vid_file =st .file_uploader (
        "Déposez votre vidéo ici",
        type =["mp4","mov","avi","mkv","webm"],
        key ="audio_vid_u",label_visibility ="collapsed"
        )

    if audio_vid_file :
        if st .session_state ._last_audio_name !=audio_vid_file .name :
            st .session_state .audio_bytes =None 
            st .session_state ._last_audio_name =audio_vid_file .name 

        tmp_a =tempfile .mkdtemp ()
        avp =os .path .join (tmp_a ,"src"+os .path .splitext (audio_vid_file .name )[1 ])
        with open (avp ,"wb")as f :f .write (audio_vid_file .read ())
        nfo_a =get_video_info (avp )

        with col_ctrl_a :
            st .markdown (f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{nfo_a ['width']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{nfo_a ['height']} px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time (nfo_a ['duration'])}</span></div>
              <div class="spec-cell"><span class="spec-k">FPS</span><span class="spec-v">{nfo_a ['fps']}</span></div>
            </div>""",unsafe_allow_html =True )

            st .markdown ('<p class="section-label-mt">Action</p>',unsafe_allow_html =True )
            audio_action =st .radio (
            "Action audio",
            ["Supprimer le son","Remplacer par..."],
            key ="audio_action",label_visibility ="collapsed"
            )

            audio_replace_file =None 
            loop_audio =True 
            if "Remplacer"in audio_action :
                st .markdown ('<p class="section-label-mt">Fichier audio de remplacement</p>',unsafe_allow_html =True )
                audio_replace_file =st .file_uploader (
                "Déposez votre fichier audio",
                type =["mp3","wav","aac","m4a","ogg"],
                key ="audio_replace_u",label_visibility ="collapsed"
                )
                if audio_replace_file :
                    st .markdown ('<p class="section-label-mt">Options</p>',unsafe_allow_html =True )
                    loop_audio =st .checkbox ("Boucler l'audio si plus court que la vidéo",value =True ,key ="audio_loop")

            st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )

            audio_sig =(audio_vid_file .name ,audio_action ,
            audio_replace_file .name if audio_replace_file else None )
            if st .session_state .get ("_audio_sig")!=audio_sig :
                st .session_state .audio_bytes =None 
                st .session_state ["_audio_sig"]=audio_sig 

            can_go =("Supprimer"in audio_action )or ("Remplacer"in audio_action and audio_replace_file )

            if not st .session_state .audio_bytes :
                btn_lbl ="Supprimer le son"if "Supprimer"in audio_action else "Remplacer l'audio"
                if can_go :
                    if st .button (btn_lbl ,key ="audio_btn"):
                        out_a =os .path .join (tmp_a ,"audio_output.mp4")
                        ph_a =st .empty ()
                        ph_a .markdown ('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Traitement audio en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',unsafe_allow_html =True )
                        try :
                            if "Supprimer"in audio_action :
                                remove_audio (avp ,out_a )
                            else :
                                arp =os .path .join (tmp_a ,"audio_replace"+os .path .splitext (audio_replace_file .name )[1 ])
                                with open (arp ,"wb")as f :f .write (audio_replace_file .read ())
                                replace_audio (avp ,arp ,out_a ,loop_audio =loop_audio )
                            ph_a .empty ()
                            with open (out_a ,"rb")as f :
                                st .session_state .audio_bytes =f .read ()
                            st .rerun ()
                        except Exception as e :
                            ph_a .markdown (f'<div class="status status-err">Erreur : {e }</div>',unsafe_allow_html =True )
                else :
                    st .markdown ('<div class="status status-idle">Déposez un fichier audio pour continuer.</div>',unsafe_allow_html =True )
            else :
                st .download_button (
                "↓  Télécharger la vidéo",
                data =st .session_state .audio_bytes ,
                file_name ="video_audio_modifie.mp4",
                mime ="video/mp4",key ="audio_dl"
                )
                st .markdown ('<div class="status status-ok">Audio traité avec succès.</div>',unsafe_allow_html =True )

        with col_prev_a :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            with open (avp ,"rb")as _vf :
                _ab64 =_b64 .b64encode (_vf .read ()).decode ()
            _aext =os .path .splitext (audio_vid_file .name )[1 ].lower ().lstrip (".")
            _amime ="video/mp4"if _aext in ("mp4","m4v")else f"video/{_aext }"

            if "Supprimer"in audio_action :
            
                components .html (f"""
<div style="border:1px solid #e4e4e4;border-radius:10px;overflow:hidden;background:#0a0a0a;">
  <video controls muted style="width:100%;display:block;max-height:380px;object-fit:contain;"
         src="data:{_amime };base64,{_ab64 }"></video>
</div>
<p style="font-family:sans-serif;font-size:0.72rem;color:#999;text-align:center;margin:6px 0 0;">
  Mode muet — le son sera supprimé
</p>""",height =440 )

            elif "Remplacer"in audio_action and audio_replace_file :
            
                _aud_bytes =audio_replace_file .read ()
                _aud_b64 =_b64 .b64encode (_aud_bytes ).decode ()
                _aud_ext =os .path .splitext (audio_replace_file .name )[1 ].lower ().lstrip (".")
                _aud_mime_map ={"mp3":"audio/mpeg","wav":"audio/wav",
                "aac":"audio/aac","m4a":"audio/mp4","ogg":"audio/ogg"}
                _aud_mime =_aud_mime_map .get (_aud_ext ,"audio/mpeg")
                components .html (f"""
<div style="border:1px solid #e4e4e4;border-radius:10px;overflow:hidden;background:#0a0a0a;">
  <video id="prev_vid" controls muted style="width:100%;display:block;max-height:360px;object-fit:contain;"
         src="data:{_amime };base64,{_ab64 }"></video>
</div>
<audio id="prev_aud" src="data:{_aud_mime };base64,{_aud_b64 }" {"loop"if loop_audio else ""}></audio>
<p style="font-family:sans-serif;font-size:0.72rem;color:#999;text-align:center;margin:6px 0 0;">
  Avec le nouvel audio — <b>{audio_replace_file .name }</b>
</p>
<script>
  const vid = document.getElementById('prev_vid');
  const aud = document.getElementById('prev_aud');
  vid.addEventListener('play',  () => aud.play());
  vid.addEventListener('pause', () => aud.pause());
  vid.addEventListener('seeked', () => {{ aud.currentTime = vid.currentTime; }});
  vid.addEventListener('ended', () => {{ aud.pause(); aud.currentTime = 0; }});
</script>""",height =450 )

            else :
            
                components .html (f"""
<div style="border:1px solid #e4e4e4;border-radius:10px;overflow:hidden;background:#0a0a0a;">
  <video controls style="width:100%;display:block;max-height:380px;object-fit:contain;"
         src="data:{_amime };base64,{_ab64 }"></video>
</div>""",height =420 )

    else :
        with col_ctrl_a :
            st .markdown ('<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_a :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/>
                <line x1="2" y1="2" x2="22" y2="22" stroke="#0068B1" stroke-width="1.4"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_crop :
    col_ctrl_r ,col_prev_r =st .columns ([4 ,6 ],gap ="large")

    with col_ctrl_r :
        st .markdown ('<p class="section-label">Source</p>',unsafe_allow_html =True )
        crop_file =st .file_uploader (
        "Déposez votre vidéo ici",
        type =["mp4","mov","avi","mkv","webm"],
        key ="crop_u",label_visibility ="collapsed"
        )

    if crop_file :
        if st .session_state ._last_crop_name !=crop_file .name :
            st .session_state .crop_bytes =None 
            st .session_state ._last_crop_name =crop_file .name 

        tmp_r =tempfile .mkdtemp ()
        crp =os .path .join (tmp_r ,"src"+os .path .splitext (crop_file .name )[1 ])
        with open (crp ,"wb")as f :f .write (crop_file .read ())
        nfo_r =get_video_info (crp )
        W_r ,H_r =nfo_r ["width"],nfo_r ["height"]

        with col_ctrl_r :
            st .markdown (f"""
            <div class="specs-row">
              <div class="spec-cell"><span class="spec-k">Largeur</span><span class="spec-v">{W_r } px</span></div>
              <div class="spec-cell"><span class="spec-k">Hauteur</span><span class="spec-v">{H_r } px</span></div>
              <div class="spec-cell"><span class="spec-k">Durée</span><span class="spec-v">{fmt_time (nfo_r ['duration'])}</span></div>
              <div class="spec-cell"><span class="spec-k">Ratio actuel</span><span class="spec-v">{W_r }:{H_r }</span></div>
            </div>""",unsafe_allow_html =True )

            st .markdown ('<p class="section-label-mt">Ratio cible</p>',unsafe_allow_html =True )
            preset_choice_idx =st .radio (
            "Ratio",
            options =list (range (len (CROP_PRESETS ))),
            format_func =lambda i :f"{CROP_PRESETS [i ][0 ]}  —  {CROP_PRESETS [i ][3 ]}",
            key ="crop_preset",label_visibility ="collapsed"
            )
            chosen =CROP_PRESETS [preset_choice_idx ]
            rw ,rh =chosen [1 ],chosen [2 ]

            target_ratio =rw /rh 
            src_ratio =W_r /H_r 
            if src_ratio >target_ratio :
                out_w =int (H_r *target_ratio );out_h =H_r 
            else :
                out_w =W_r ;out_h =int (W_r /target_ratio )
            out_w -=out_w %2 ;out_h -=out_h %2 

            st .markdown ('<p class="section-label-mt">Position du cadre</p>',unsafe_allow_html =True )
            crop_pos =st .selectbox (
            "Position",["Centre","Haut","Bas","Gauche","Droite"],
            key ="crop_pos",label_visibility ="collapsed"
            )

            st .markdown (f"""
            <div class="cut-info-row">
              <div class="cut-info-cell"><span>Ratio</span>{chosen [0 ]}</div>
              <div class="cut-info-cell"><span>Résolution finale</span>{out_w } × {out_h } px</div>
              <div class="cut-info-cell"><span>Usage</span>{chosen [3 ]}</div>
            </div>""",unsafe_allow_html =True )

            st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )

            crop_sig =(crop_file .name ,preset_choice_idx ,crop_pos )
            if st .session_state .get ("_crop_sig")!=crop_sig :
                st .session_state .crop_bytes =None 
                st .session_state ["_crop_sig"]=crop_sig 

            if not st .session_state .crop_bytes :
                if st .button ("Recadrer la vidéo",key ="crop_btn"):
                    out_r =os .path .join (tmp_r ,"crop_output.mp4")
                    ph_r =st .empty ()
                    ph_r .markdown ('<div class="encoding-wrap"><div class="encoding-ring"></div><span class="encoding-text">Recadrage en cours…</span></div><div class="fake-progress-wrap"><div class="fake-progress-track"><div class="fake-progress-bar"></div></div></div>',unsafe_allow_html =True )
                    try :
                        crop_video (crp ,out_r ,rw ,rh ,position =crop_pos )
                        ph_r .empty ()
                        with open (out_r ,"rb")as f :
                            st .session_state .crop_bytes =f .read ()
                        st .rerun ()
                    except Exception as e :
                        ph_r .markdown (f'<div class="status status-err">Erreur : {e }</div>',unsafe_allow_html =True )
            else :
                st .download_button (
                "↓  Télécharger la vidéo recadrée",
                data =st .session_state .crop_bytes ,
                file_name =f"recadre_{chosen [0 ].replace (':','x')}.mp4",
                mime ="video/mp4",key ="crop_dl"
                )
                st .markdown ('<div class="status status-ok">Recadrage terminé.</div>',unsafe_allow_html =True )

        with col_prev_r :
            st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )
            with st .spinner (""):
                frame_r =extract_frame (crp ,0.0 )
            from PIL import ImageDraw 
            prev_r =frame_r .copy ()
            pw ,ph_img =prev_r .size 
            tratio =rw /rh 
            sratio =pw /ph_img 
            if sratio >tratio :
                cw =int (ph_img *tratio );ch =ph_img 
            else :
                cw =pw ;ch =int (pw /tratio )
            cw -=cw %2 ;ch -=ch %2 
            if crop_pos =="Haut":cx ,cy =(pw -cw )//2 ,0 
            elif crop_pos =="Bas":cx ,cy =(pw -cw )//2 ,ph_img -ch 
            elif crop_pos =="Gauche":cx ,cy =0 ,(ph_img -ch )//2 
            elif crop_pos =="Droite":cx ,cy =pw -cw ,(ph_img -ch )//2 
            else :cx ,cy =(pw -cw )//2 ,(ph_img -ch )//2 
            overlay =Image .new ("RGBA",prev_r .size ,(0 ,0 ,0 ,0 ))
            draw_ov =ImageDraw .Draw (overlay )
            draw_ov .rectangle ([0 ,0 ,pw ,ph_img ],fill =(0 ,0 ,0 ,110 ))
            draw_ov .rectangle ([cx ,cy ,cx +cw ,cy +ch ],fill =(0 ,0 ,0 ,0 ))
            prev_r =prev_r .convert ("RGBA")
            prev_r =Image .alpha_composite (prev_r ,overlay ).convert ("RGB")
            draw2 =ImageDraw .Draw (prev_r )
            draw2 .rectangle ([cx ,cy ,cx +cw -1 ,cy +ch -1 ],
            outline =(0 ,104 ,177 ),width =3 )
            st .image (cap_image_for_preview (prev_r ),
            caption =f"{chosen [0 ]} — {out_w }×{out_h } px — {crop_pos }")

    else :
        with col_ctrl_r :
            st .markdown ('<div class="status status-idle">Déposez une vidéo via <i>Upload</i>.</div>',unsafe_allow_html =True )
        with col_prev_r :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <path d="M6 2H2v4M18 2h4v4M6 22H2v-4M18 22h4v-4"/>
                <rect x="6" y="6" width="12" height="12" rx="1"/>
              </svg>
              <span>L'aperçu apparaîtra ici</span>
            </div>""",unsafe_allow_html =True )

            
            
            

with tab_canva :
    try :
        with open (DEFAULT_WM_FILE ,"rb")as _wm_f :
            _wm_b64_canva =_b64h .b64encode (_wm_f .read ()).decode ()
        _wm_mime_canva ="image/png"
    except Exception :
        _wm_b64_canva =""
        _wm_mime_canva ="image/png"

    col_ctrl_cv ,col_prev_cv =st .columns ([4 ,6 ],gap ="large")

    
    st .markdown ("""
    <style>
    /* Réduit l'espace autour des sliders dans l'onglet Canva */
    [data-testid="stSlider"] { margin-bottom: 0 !important; padding-bottom: 0 !important; }
    [data-testid="stSlider"] > div { padding-bottom: 0 !important; }
    /* Réduit la hauteur des color pickers */
    [data-testid="stColorPicker"] { margin-bottom: 0 !important; }
    [data-testid="stColorPicker"] label { font-size: 0.72rem !important; margin-bottom: 2px !important; }
    /* Bouton reset : petit, discret, pill */
    .cv-reset > button {
      height: 26px !important; min-height: 26px !important;
      font-size: 0.7rem !important; padding: 0 0.7rem !important;
      background: var(--bg, #fafafa) !important;
      border: 1px solid var(--border, #e4e4e4) !important;
      color: var(--muted, #999) !important;
      box-shadow: none !important;
      border-radius: 999px !important;
    }
    .cv-reset > button:hover { border-color: var(--blue, #0068B1) !important; color: var(--blue, #0068B1) !important; background: var(--blue-dim, #e8f2fb) !important; }
    </style>
    """,unsafe_allow_html =True )

    
    _CV_DEFAULTS ={"canva_y":72 ,"canva_imgzoom":100 }
    for _k ,_v in _CV_DEFAULTS .items ():
        if _k not in st .session_state :
            st .session_state [_k ]=_v 

            
    if st .session_state .get ("_cv_reset_y"):
        st .session_state ["canva_y"]=_CV_DEFAULTS ["canva_y"]
        st .session_state ["_cv_reset_y"]=False 
    if st .session_state .get ("_cv_reset_zoom"):
        st .session_state ["canva_imgzoom"]=_CV_DEFAULTS ["canva_imgzoom"]
        st .session_state ["_cv_reset_zoom"]=False 

    with col_ctrl_cv :

    
        _cr1 ,_cr2 ,_cr3 =st .columns (3 )
        with _cr1 :
            st .markdown ('<p class="section-label">Arrière-plan</p>',unsafe_allow_html =True )
            canva_bg_file =st .file_uploader (
            "Déposez votre image ici",
            type =["png","jpg","jpeg","webp"],
            key ="canva_bg",label_visibility ="collapsed"
            )
        with _cr2 :
            st .markdown ('<p class="section-label">Format</p>',unsafe_allow_html =True )
            canva_format =st .selectbox (
            "Format",[
            "1080×1350 — Portrait",
            "1080×1080 — Carré",
            "1080×1920 — Stories",
            ],
            key ="canva_format",label_visibility ="collapsed"
            )
        with _cr3 :
            st .markdown ('<p class="section-label">Watermark</p>',unsafe_allow_html =True )
            wm_opts_cv ={
            "position":st .selectbox (
            "Position watermark",POSITIONS ,
            index =POSITIONS .index (DEFAULT_POSITION ),
            key ="cv_pos",label_visibility ="collapsed"
            ),
            "custom_x":0 ,
            "custom_y":0 ,
            }
            if wm_opts_cv ["position"]=="Coordonnées personnalisées":
                _wx ,_wy =st .columns (2 )
                with _wx :
                    wm_opts_cv ["custom_x"]=int (st .number_input ("X",min_value =0 ,value =0 ,step =1 ,key ="cv_cx"))
                with _wy :
                    wm_opts_cv ["custom_y"]=int (st .number_input ("Y",min_value =0 ,value =0 ,step =1 ,key ="cv_cy"))

        _fmt_map ={
        "1080×1350 — Portrait":(1080 ,1350 ),
        "1080×1080 — Carré":(1080 ,1080 ),
        "1080×1920 — Stories":(1080 ,1920 ),
        }
        canva_w ,canva_h =_fmt_map [canva_format ]

        st .markdown ('<p class="section-label">Surtitre</p>',unsafe_allow_html =True )
        canva_sur =st .text_input ("Surtitre",value ="Modifier le surtitre",key ="canva_sur",label_visibility ="collapsed")

        st .markdown ('<p class="section-label">Titre principal</p>',unsafe_allow_html =True )
        canva_title =st .text_area (
        "Titre",value ="Modifier le titre",
        key ="canva_title",label_visibility ="collapsed",height =80 
        )

        canva_block_color ="#0068B1"
        canva_text_color ="#ffffff"
        canva_sur_bg ="#ffffff"
        canva_sur_color ="#0068B1"

        st .markdown ('<p class="section-label" style="margin-top:10px;">Position du texte</p>',unsafe_allow_html =True )
        canva_y =st .slider ("Position Y",min_value =5 ,max_value =95 ,key ="canva_y",label_visibility ="collapsed")

        if canva_bg_file :
            st .markdown ('<p class="section-label" style="margin-top:6px;">Zoom photo</p>',unsafe_allow_html =True )
            canva_img_zoom =st .slider ("Zoom photo",min_value =100 ,max_value =300 ,key ="canva_imgzoom",label_visibility ="collapsed")
        else :
            canva_img_zoom =100 

        canva_wm_size =13 
        canva_wm_opac =100 

        
        st .markdown ("<div style='margin-top:1.2rem;'></div>",unsafe_allow_html =True )

        def _hex_to_rgb (h ):
            h =h .lstrip ('#')
            return tuple (int (h [i :i +2 ],16 )for i in (0 ,2 ,4 ))

        def generate_canva_image ():
            from PIL import ImageDraw ,ImageFont 
            import math as _math 

            W ,H =canva_w ,canva_h 
            img =Image .new ("RGBA",(W ,H ),(34 ,34 ,34 ,255 ))

            if canva_bg_file :
                canva_bg_file .seek (0 )
                bg =Image .open (canva_bg_file ).convert ("RGBA")
                z =canva_img_zoom /100.0 
                scale_x =W /bg .width 
                scale_y =H /bg .height 
                base_scale =max (scale_x ,scale_y )*z 
                new_w =int (bg .width *base_scale )
                new_h =int (bg .height *base_scale )
                bg =bg .resize ((new_w ,new_h ),Image .LANCZOS )
                dx =(W -new_w )//2 
                dy =(H -new_h )//2 
                bg_canvas =Image .new ("RGBA",(W ,H ),(34 ,34 ,34 ,0 ))
                if dx >=0 and dy >=0 :
                    bg_canvas .paste (bg ,(dx ,dy ))
                else :
                    src_x =max (0 ,-dx )
                    src_y =max (0 ,-dy )
                    dst_x =max (0 ,dx )
                    dst_y =max (0 ,dy )
                    crop_w =min (new_w -src_x ,W -dst_x )
                    crop_h =min (new_h -src_y ,H -dst_y )
                    if crop_w >0 and crop_h >0 :
                        cropped =bg .crop ((src_x ,src_y ,src_x +crop_w ,src_y +crop_h ))
                        bg_canvas .paste (cropped ,(dst_x ,dst_y ))
                img =Image .alpha_composite (img ,bg_canvas )

            draw =ImageDraw .Draw (img ,"RGBA")

            
            fs =int (W *0.05 )
            fs_sur =int (W *0.03 )
            pad =int (W *0.017 )
            radius =int (W *0.019 )
            lh =int (fs *1.25 )
            overlap =int (W *0.003 )

            try :
                font_title =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",fs )
                font_sur =ImageFont .truetype ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",fs_sur )
            except Exception :
                font_title =ImageFont .load_default ()
                font_sur =ImageFont .load_default ()

                
            words =canva_title .split (' ')
            lines ,cur =[],''
            for w in words :
                if len (cur +w )<28 :
                    cur +=(' 'if cur else '')+w 
                else :
                    lines .append (cur )
                    cur =w 
            if cur :
                lines .append (cur )

            cx =int ((50 /100 )*W )
            total_h =lh *len (lines )
            block_top =int ((canva_y /100 )*H -total_h /2 )

            
            def measure (text ,font ):
                bb =font .getbbox (text )
                return bb [2 ]-bb [0 ]

            line_widths =[measure (l ,font_title )+pad *2 for l in lines ]
            sur_w =measure (canva_sur ,font_sur )+pad *2 
            sur_h =fs_sur +int (pad *0.8 )

            bc =_hex_to_rgb (canva_block_color )+(255 ,)
            tc =_hex_to_rgb (canva_text_color )+(255 ,)
            sbg =_hex_to_rgb (canva_sur_bg )+(255 ,)
            sc =_hex_to_rgb (canva_sur_color )+(255 ,)

            def draw_rounded_rect (d ,x ,y ,w ,h ,r ,fill ):
                d .rectangle ([x +r ,y ,x +w -r ,y +h ],fill =fill )
                d .rectangle ([x ,y +r ,x +w ,y +h -r ],fill =fill )
                d .ellipse ([x ,y ,x +2 *r ,y +2 *r ],fill =fill )
                d .ellipse ([x +w -2 *r ,y ,x +w ,y +2 *r ],fill =fill )
                d .ellipse ([x ,y +h -2 *r ,x +2 *r ,y +h ],fill =fill )
                d .ellipse ([x +w -2 *r ,y +h -2 *r ,x +w ,y +h ],fill =fill )

                
            sur_x =cx -sur_w //2 
            sur_y =block_top -sur_h -int (W *-0.000 )
            draw_rounded_rect (draw ,sur_x ,sur_y ,sur_w ,sur_h ,radius ,sbg )
            draw .text ((sur_x +pad ,sur_y +sur_h //2 -fs_sur //2 ),canva_sur ,font =font_sur ,fill =sc )

            
            for i ,line in enumerate (lines ):
                lw =line_widths [i ]
                lx =cx -lw //2 
                ly =block_top +i *lh -(overlap if i >0 else 0 )
                draw_rounded_rect (draw ,lx ,ly ,lw ,lh +overlap ,radius ,bc )

                
            for i ,line in enumerate (lines ):
                lw =line_widths [i ]
                lx =cx -lw //2 
                ly =block_top +i *lh -(overlap if i >0 else 0 )
                draw .text ((lx +pad ,ly +lh //2 -fs //2 ),line ,font =font_title ,fill =tc )

                
            result =composite_logo (
            img .convert ("RGB"),DEFAULT_WM_FILE ,
            position =wm_opts_cv ["position"],
            custom_x =wm_opts_cv ["custom_x"],
            custom_y =wm_opts_cv ["custom_y"],
            force_w =W ,force_h =H 
            )

            
            
            return result 

        st .markdown ("""
<div style="margin-top:1.2rem; padding:0.75rem 1rem; background:#e8f2fb; border:1px solid #b3d4f0; border-radius:8px; font-size:0.82rem; color:#0068B1; line-height:1.6;">
  Pour télécharger le visuel, <b>faites un clic droit sur l'aperçu</b> puis sélectionnez <code>Enregistrer l'image sous…</code>
</div>""",unsafe_allow_html =True )

            
    with col_prev_cv :
        st .markdown ('<p class="section-label">Aperçu</p>',unsafe_allow_html =True )

        if not canva_bg_file :
            st .markdown ("""
            <div class="preview-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#0068B1" stroke-width="1.2">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <circle cx="8.5" cy="8.5" r="1.5"/>
                <path d="M21 15l-5-5L5 21"/>
              </svg>
              <span>Glissez une image pour voir l'aperçu</span>
            </div>""",unsafe_allow_html =True )
        else :
            canva_bg_file .seek (0 )
            _canva_bg_b64 =_b64h .b64encode (canva_bg_file .read ()).decode ()
            _ext =canva_bg_file .name .rsplit (".",1 )[-1 ].lower ()
            _canva_bg_mime ="image/png"if _ext =="png"else ("image/webp"if _ext =="webp"else "image/jpeg")

            
            import json as _json 
            _js_title =_json .dumps (canva_title )
            _js_sur =_json .dumps (canva_sur )

            _preview_h =min (700 ,int (560 *canva_h /canva_w ))
            components .html (f"""<!DOCTYPE html>
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
const CANVAS_W = {canva_w };
const CANVAS_H = {canva_h };
const BG_B64   = "{_canva_bg_b64 }";
const BG_MIME  = "{_canva_bg_mime }";
const WM_B64   = "{_wm_b64_canva }";
const WM_MIME  = "{_wm_mime_canva }";
const TITLE    = {_js_title };
const SURTITRE = {_js_sur };
const Y_PCT    = {canva_y } / 100;
const X_PCT    = 50 / 100;
const IMG_ZOOM = {canva_img_zoom } / 100;
const BLOCK_COLOR = "{canva_block_color }";
const TEXT_COLOR  = "{canva_text_color }";
const SUR_BG      = "{canva_sur_bg }";
const SUR_COLOR   = "{canva_sur_color }";
const WM_SIZE_PCT = 13 / 100;
const WM_OPAC     = 1.0;
const WM_POS      = "{wm_opts_cv ["position"]}";
const WM_CX       = {wm_opts_cv ["custom_x"]};
const WM_CY       = {wm_opts_cv ["custom_y"]};
const MARGIN_R    = 0.04;

const canvas = document.getElementById('c');
const ctx    = canvas.getContext('2d');

const AVAIL_H   = {_preview_h } - 52;
const PREVIEW_W = Math.min(Math.floor(AVAIL_H * CANVAS_W / CANVAS_H), window.innerWidth - 20);
const UI_ZOOM   = PREVIEW_W / CANVAS_W;
canvas.width  = CANVAS_W;
canvas.height = CANVAS_H;
canvas.style.width  = (CANVAS_W * UI_ZOOM) + 'px';
canvas.style.height = (CANVAS_H * UI_ZOOM) + 'px';

let bgImg = null, wmImg = null;
let bgOffX = 0, bgOffY = 0;
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
  const fsSur  = Math.round(CANVAS_W * 0.04);
  const pad    = Math.round(CANVAS_W * 0.017);
  const radius = Math.round(CANVAS_W * 0.019);
  const lh     = Math.round(fs * 1.25);
  const overlap= Math.round(CANVAS_W * 0.003);
  const cx     = X_PCT * CANVAS_W;

  const words = TITLE.split(' ');
  let lines=[], cur='';
  words.forEach(w => {{
    if ((cur+w).length < 34) cur += (cur?' ':'')+w;
    else {{ lines.push(cur); cur=w; }}
  }});
  if(cur) lines.push(cur);

  ctx.font = `bold ${{fs}}px 'Roboto Condensed','Roboto',sans-serif`;
  const lineWidths = lines.map(l => ctx.measureText(l).width + pad*2);

  ctx.font = `bold ${{fsSur}}px 'Roboto',sans-serif`;
  const surW = ctx.measureText(SURTITRE).width + pad*2;
  const surH = fsSur + Math.round(pad*0.8);

  const totalH  = lh * lines.length;
  const blockTop = CANVAS_H * Y_PCT - totalH/2;

  const off = document.createElement('canvas');
  off.width = CANVAS_W; off.height = CANVAS_H;
  const octx = off.getContext('2d');
  octx.font = `bold ${{fs}}px 'Roboto Condensed','Roboto',sans-serif`;
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
  ctx.font = `bold ${{fsSur}}px 'Roboto',sans-serif`;
  ctx.textAlign='left'; ctx.textBaseline='middle';
  ctx.fillText(SURTITRE, surX+pad, surY+surH/2);

  ctx.font = `bold ${{fs}}px 'Roboto Condensed','Roboto',sans-serif`;
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
function onLoad() {{ loaded++; if(loaded>=toLoad||toLoad===0) {{ render(); setTimeout(exportCanvas, 100); }} }}
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
  isDragging=false;
  canvas.style.cursor=bgImg?'grab':'default';
  exportCanvas();
}});
if(bgImg) canvas.style.cursor='grab';

function exportCanvas() {{
  try {{
    const nativeCanvas = document.createElement('canvas');
    nativeCanvas.width  = CANVAS_W;
    nativeCanvas.height = CANVAS_H;
    nativeCanvas.getContext('2d').drawImage(canvas, 0, 0, CANVAS_W, CANVAS_H);
    const dataUrl = nativeCanvas.toDataURL('image/png');
    const allTA = window.parent.document.querySelectorAll('textarea');
    allTA.forEach(ta => {{
      if(ta.value === '' || ta.value.startsWith('data:image')) {{
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.parent.HTMLTextAreaElement.prototype, 'value').set;
        nativeInputValueSetter.call(ta, dataUrl);
        ta.dispatchEvent(new Event('input', {{bubbles: true}}));
      }}
    }});
  }} catch(e) {{}}
}}
</script>
</body>
</html>""",height =_preview_h +52 ,scrolling =False )

            
st .markdown ("""
<div class="site-footer">
  <span class="footer-name">Dernière màj le <i>27/04/2026</i></span>
  <span>Envoyez-moi <a href="mailto:lucas.bessonnat@leprogres.fr">les messages d'erreur par mail</a>.<br>
  Après plusieurs utilisations, appuyez sur la touche <code>F5</code> pour faire du bien au cache de l'app.</br>
  <b>Aucune donnée n'est envoyée sur un serveur</b> <i>(tout tourne localement dans votre navigateur).</i>
  </span>
</div>
""",unsafe_allow_html =True )
