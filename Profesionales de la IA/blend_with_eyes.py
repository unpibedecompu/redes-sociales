#!/usr/bin/env python3
# Requirements: pip install mediapipe opencv-python Pillow numpy
# Usage: python "Profesionales de la IA/blend_with_eyes.py" <input> [output]
#
# Applies the luminosity ghost blend to the full image, then composites the
# original (sharp, fully opaque) eye region on top at its correct position.

import argparse
import math
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision
import numpy as np
from PIL import Image

# ── blend constants ──────────────────────────────────────────────────────────
BG_COLOR      = (240, 232, 255)
GHOST_OPACITY = 0.30

# ── landmark model ───────────────────────────────────────────────────────────
MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/"
    "face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
MODEL_PATH = Path(__file__).parent.parent / "templates" / "face_landmarker.task"

IDX_IRIS_LEFT  = 468
IDX_IRIS_RIGHT = 473
IDX_EAR_LEFT   = 234
IDX_EAR_RIGHT  = 454
EYEBROW_INDICES = [
    46, 53, 52, 65, 55, 70, 63, 105, 66, 107,
    276, 283, 282, 295, 285, 300, 293, 334, 296, 336,
]


# ── helpers ──────────────────────────────────────────────────────────────────
def ensure_model():
    if not MODEL_PATH.exists():
        print("Downloading face landmarker model (~3 MB)...")
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print("Model downloaded.")


def dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)


def _hls_channel(m1, m2, hue):
    hue = hue % 1.0
    return np.where(hue < 1/6, m1 + (m2 - m1) * hue * 6,
           np.where(hue < 0.5, m2,
           np.where(hue < 2/3, m1 + (m2 - m1) * (2/3 - hue) * 6, m1)))


def rgb_to_hls(r, g, b):
    cmax  = np.maximum(np.maximum(r, g), b)
    cmin  = np.minimum(np.minimum(r, g), b)
    delta = cmax - cmin
    l = (cmax + cmin) / 2.0
    s = np.where(delta == 0, 0.0,
        np.where(l < 0.5, delta / (cmax + cmin), delta / (2.0 - cmax - cmin)))
    with np.errstate(invalid="ignore", divide="ignore"):
        rc = np.where(delta > 0, (cmax - r) / delta, 0.0)
        gc = np.where(delta > 0, (cmax - g) / delta, 0.0)
        bc = np.where(delta > 0, (cmax - b) / delta, 0.0)
        h  = np.where(cmax == r, bc - gc,
             np.where(cmax == g, 2.0 + rc - bc, 4.0 + gc - rc))
        h  = np.where(delta == 0, 0.0, (h / 6.0) % 1.0)
    return h, l, s


def hls_to_rgb(h, l, s):
    m2 = np.where(l <= 0.5, l * (1.0 + s), l + s - l * s)
    m1 = 2.0 * l - m2
    r  = np.where(s == 0, l, _hls_channel(m1, m2, h + 1/3))
    g  = np.where(s == 0, l, _hls_channel(m1, m2, h))
    b  = np.where(s == 0, l, _hls_channel(m1, m2, h - 1/3))
    return np.clip(r, 0, 1), np.clip(g, 0, 1), np.clip(b, 0, 1)


def luminosity_blend(backdrop, source):
    bh, _,  bs = rgb_to_hls(backdrop[..., 0], backdrop[..., 1], backdrop[..., 2])
    _,  sl, _  = rgb_to_hls(source[..., 0],   source[..., 1],   source[..., 2])
    rr, rg, rb = hls_to_rgb(bh, sl, bs)
    return np.stack([rr, rg, rb], axis=-1)


# ── main pipeline ─────────────────────────────────────────────────────────────
def process(input_path: Path, output_path: Path):
    ensure_model()

    # --- blend full image ---
    photo_pil = Image.open(input_path).convert("RGBA")
    pw, ph = photo_pil.size
    photo_arr   = np.array(photo_pil)
    photo_rgb_f = photo_arr[..., :3].astype(np.float64) / 255.0
    photo_alpha = photo_arr[..., 3:4].astype(np.float64) / 255.0

    bg_f = np.full((ph, pw, 3), BG_COLOR, dtype=np.float64) / 255.0
    lum  = luminosity_blend(bg_f, photo_rgb_f)

    blended = np.zeros((ph, pw, 4), dtype=np.uint8)
    blended[..., :3] = (lum * 255).astype(np.uint8)
    blended[..., 3]  = (photo_alpha[..., 0] * GHOST_OPACITY * 255).astype(np.uint8)

    # --- detect eye crop box ---
    img_cv = cv2.imread(str(input_path))
    rgb_cv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)

    options = vision.FaceLandmarkerOptions(
        base_options=mp_python.BaseOptions(model_asset_path=str(MODEL_PATH)),
        num_faces=1,
    )
    with vision.FaceLandmarker.create_from_options(options) as landmarker:
        results = landmarker.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_cv))

    if not results.face_landmarks:
        print("No face detected — saving blend only.")
        Image.fromarray(blended, "RGBA").save(output_path)
        return

    lm     = results.face_landmarks[0]
    iris_l = lm[IDX_IRIS_LEFT]
    iris_r = lm[IDX_IRIS_RIGHT]
    ear_l  = lm[IDX_EAR_LEFT]
    ear_r  = lm[IDX_EAR_RIGHT]

    brow_top_y = min(lm[i].y for i in EYEBROW_INDICES)
    iris_cy    = (iris_l.y + iris_r.y) / 2
    bottom_y   = iris_cy + (iris_cy - brow_top_y)

    x1 = max(0,  int((iris_l.x - dist(iris_l, ear_l) * 3/4) * pw))
    x2 = min(pw, int((iris_r.x + dist(iris_r, ear_r) * 3/4) * pw))
    y1 = max(0,  int(brow_top_y * ph))
    y2 = min(ph, int(bottom_y   * ph))

    print(f"Eye crop box: x1={x1} x2={x2} y1={y1} y2={y2}  =>  {x2-x1}x{y2-y1}")

    # --- paste original eye pixels (fully opaque) onto blended canvas ---
    eye_rgb  = photo_arr[y1:y2, x1:x2, :3]
    eye_alpha = photo_arr[y1:y2, x1:x2, 3:4]  # keep original alpha channel

    blended[y1:y2, x1:x2, :3] = eye_rgb
    blended[y1:y2, x1:x2, 3]  = eye_alpha[..., 0]

    Image.fromarray(blended, "RGBA").save(output_path)
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Ghost blend + sharp eye crop composite")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", nargs="?", help="Output path (default: <stem>_composed.png)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = (
        Path(args.output)
        if args.output
        else input_path.parent / f"{input_path.stem}_composed.png"
    )

    process(input_path, output_path)


if __name__ == "__main__":
    main()
