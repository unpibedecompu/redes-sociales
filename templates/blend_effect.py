#!/usr/bin/env python3
# Requirements: pip install Pillow numpy
# Usage: python templates/blend_effect.py <input> [output]

import argparse
from pathlib import Path

from PIL import Image
import numpy as np

BG_COLOR      = (240, 232, 255)   # #f0e8ff — trayectoria slide
GHOST_OPACITY = 0.30


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
    """CSS mix-blend-mode: luminosity — backdrop hue/sat, source luminance."""
    bh, _,  bs = rgb_to_hls(backdrop[..., 0], backdrop[..., 1], backdrop[..., 2])
    _,  sl, _  = rgb_to_hls(source[..., 0],   source[..., 1],   source[..., 2])
    rr, rg, rb = hls_to_rgb(bh, sl, bs)
    return np.stack([rr, rg, rb], axis=-1)



def blend(input_path: Path, output_path: Path):
    photo = Image.open(input_path).convert("RGBA")
    w, h = photo.size

    bg_f        = np.full((h, w, 3), BG_COLOR, dtype=np.float64) / 255.0
    photo_arr   = np.array(photo)
    photo_rgb_f = photo_arr[..., :3].astype(np.float64) / 255.0
    photo_alpha = photo_arr[..., 3:4].astype(np.float64) / 255.0

    lum = luminosity_blend(bg_f, photo_rgb_f)
    lum_img = (lum * 255).astype(np.uint8)

    result_arr = np.zeros((h, w, 4), dtype=np.uint8)
    result_arr[..., :3] = lum_img
    result_arr[..., 3]  = (photo_alpha[..., 0] * GHOST_OPACITY * 255).astype(np.uint8)

    Image.fromarray(result_arr, "RGBA").save(output_path)
    print(f"Saved: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Luminosity blend + ghost opacity effect")
    parser.add_argument("input", help="Input image path")
    parser.add_argument("output", nargs="?", help="Output image path (default: <stem>_blended.png next to input)")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output) if args.output else input_path.parent / f"{input_path.stem}_blended.png"

    blend(input_path, output_path)


if __name__ == "__main__":
    main()
