import subprocess
import tempfile
import json
import math
import io
import os
import shutil
from PIL import Image

# Constantes
DEFAULT_WM_FILE = "lpr.png"
POSITIONS = [
    "Haut gauche", "Haut centre", "Haut droite",
    "Milieu gauche", "Centre", "Milieu droite",
    "Bas gauche", "Bas centre", "Bas droite",
    "Coordonnées personnalisées",
]
DEFAULT_POSITION = "Haut droite"

QUALITY_PRESETS = {
    "Standard (CRF 18 — recommandé)": {"crf": "18", "preset": "fast"},
    "Haute qualité (CRF 12)": {"crf": "12", "preset": "slow"},
    "Sans perte (CRF 0)": {"crf": "0", "preset": "ultrafast"},
}

CROP_PRESETS = [
    ("9:16", 9, 16, "Stories"),
    ("1:1", 1, 1, "Carré"),
    ("16:9", 16, 9, "Comme à la télé"),
    ("4:5", 4, 5, "Portrait"),
    ("4:3", 4, 3, "Presque carré"),
    ("21:9", 21, 9, "Comme au ciné"),
]

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

def compute_xy(position: str, W: int, H: int, logo_w: int, logo_h: int,
               custom_x: int = 0, custom_y: int = 0,
               margin_pct: float = 0.05) -> tuple:
    mx = int(W * margin_pct)
    my = int(H * margin_pct)
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

def composite_logo(base: Image.Image, logo_path: str,
                   position: str = DEFAULT_POSITION,
                   custom_x: int = 0, custom_y: int = 0,
                   force_w: int = None, force_h: int = None) -> Image.Image:
    W = force_w if force_w else base.size[0]
    H = force_h if force_h else base.size[1]
    logo_w = int(math.sqrt(W ** 2 + H ** 2) * 0.1307)
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
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate,tags=rotate",
        "-show_entries", "stream_side_data=rotation",
        "-show_entries", "format=duration",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    data = json.loads(result.stdout)
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
    result = subprocess.run([
        "ffmpeg", "-y", "-ss", str(timecode), "-i", video_path,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"
    ], capture_output=True)
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")

def make_thumbnail(video_path: str, logo_path: str, info: dict,
                   position: str = DEFAULT_POSITION,
                   custom_x: int = 0, custom_y: int = 0) -> Image.Image:
    result = subprocess.run([
        "ffmpeg", "-y", "-i", video_path,
        "-vframes", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"
    ], capture_output=True)
    frame = Image.open(io.BytesIO(result.stdout)).convert("RGBA")
    return composite_logo(
        frame, logo_path,
        position=position, custom_x=custom_x, custom_y=custom_y,
        force_w=info["width"], force_h=info["height"]
    ).convert("RGB")

def render_video(video_path: str, logo_path: str, output_path: str, info: dict,
                 position: str = DEFAULT_POSITION, custom_x: int = 0, custom_y: int = 0,
                 quality_key: str = "Standard (CRF 18 — recommandé)",
                 progress_cb=None):
    W, H = info["width"], info["height"]
    logo_w = int(math.sqrt(W ** 2 + H ** 2) * 0.1307)
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
        "-i", video_path, "-i", tmp_logo_path,
        "-filter_complex", filter_complex,
        "-c:v", "libx264", "-crf", q["crf"], "-preset", q["preset"],
        "-c:a", "copy", "-movflags", "+faststart",
        "-progress", "pipe:1", output_path
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
    shutil.rmtree(tmp_logo_dir, ignore_errors=True)

def trim_video(video_path: str, output_path: str, t_start: float, t_end: float):
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(t_start), "-to", str(t_end),
        "-i", video_path,
        "-c", "copy", "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

def merge_videos(video_paths: list, output_path: str):
    tmp_list = tempfile.mktemp(suffix=".txt")
    with open(tmp_list, "w") as f:
        for p in video_paths:
            f.write(f"file '{p}'\n")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat", "-safe", "0",
        "-i", tmp_list,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    os.unlink(tmp_list)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

def remove_audio(video_path: str, output_path: str):
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-c:v", "copy", "-an",
        "-movflags", "+faststart", output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

def replace_audio(video_path: str, audio_path: str, output_path: str, loop_audio: bool = True):
    loop_flag = ["-stream_loop", "-1"] if loop_audio else []
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        *loop_flag, "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "-map", "0:v:0", "-map", "1:a:0",
        "-movflags", "+faststart", output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

def crop_video(video_path: str, output_path: str,
               ratio_w: int, ratio_h: int,
               position: str = "Centre"):
    info = get_video_info(video_path)
    W, H = info["width"], info["height"]
    target_ratio = ratio_w / ratio_h
    src_ratio = W / H
    if src_ratio > target_ratio:
        new_w = int(H * target_ratio)
        new_h = H
    else:
        new_w = W
        new_h = int(W / target_ratio)
    new_w = new_w - (new_w % 2)
    new_h = new_h - (new_h % 2)

    if position == "Haut":
        x_off, y_off = (W - new_w) // 2, 0
    elif position == "Bas":
        x_off, y_off = (W - new_w) // 2, H - new_h
    elif position == "Gauche":
        x_off, y_off = 0, (H - new_h) // 2
    elif position == "Droite":
        x_off, y_off = W - new_w, (H - new_h) // 2
    else:
        x_off, y_off = (W - new_w) // 2, (H - new_h) // 2
    vf = f"crop={new_w}:{new_h}:{x_off}:{y_off}"
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", vf,
        "-c:v", "libx264", "-crf", "18", "-preset", "fast",
        "-c:a", "copy",
        "-movflags", "+faststart", output_path
    ]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.decode())

# Fonction utilitaire pour nettoyer un dossier temporaire
def cleanup_temp_dir(dir_path: str):
    if dir_path and os.path.exists(dir_path):
        shutil.rmtree(dir_path, ignore_errors=True)