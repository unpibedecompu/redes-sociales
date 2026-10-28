"""Shared helpers for the video -> 3D experiment."""
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "input" / "target.mp4"
# The turntable does a full 360 every ~10 s, starting facing the camera.
SECONDS_PER_TURN = 10.0


# The motion is NOT a one-way 360 spin (measured on frames/profiles_check.png):
#  - 0-10 s turns front -> back and returns on the SAME side (3.5 s and 8.6 s both show the character's right side);
#  - the character's left side only appears in the second half (~13.5 s), back again at ~16.5 s.
# So 0-180 deg comes from the first half and 180-360 deg from the second half; the spin eases in/out, hence keyframes.
# Every 45 deg keyframe below was checked by eye against the frames (cache/angle_check*.png).
ANGLE_KEYS = [(0, 0.0), (45, 2.083), (90, 3.5), (135, 5.583), (180, 6.5),                    # first half
              (180.001, 16.5), (225, 15.3), (270, 13.667), (315, 12.583), (360, 10.0)]   # second half


def angle_to_time(deg: float) -> float:
    d = deg % 360
    for (a0, t0), (a1, t1) in zip(ANGLE_KEYS, ANGLE_KEYS[1:]):
        if a0 <= d <= a1:
            return t0 + (d - a0) / (a1 - a0) * (t1 - t0)
    return 6.5


def extract_frame(t: float, out: Path) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(VIDEO), "-frames:v", "1", str(out)],
        check=True,
    )
    return out


_SESSION = None


def subject_mask(img: Image.Image) -> np.ndarray:
    """Foreground mask via rembg (u2net), used for both video frames and renders."""
    global _SESSION
    from rembg import new_session, remove
    if _SESSION is None:
        _SESSION = new_session("u2net")
    alpha = np.asarray(remove(img.convert("RGB"), session=_SESSION, only_mask=True))
    return alpha > 127


def crop_square(img: Image.Image, pad: float = 0.08, size: int = 1024, mask: np.ndarray | None = None) -> Image.Image:
    m = subject_mask(img) if mask is None else mask
    ys, xs = np.where(m)
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    side = int(max(x1 - x0, y1 - y0) * (1 + 2 * pad))
    cx, cy = (x0 + x1) // 2, (y0 + y1) // 2
    box = (cx - side // 2, cy - side // 2, cx + side // 2, cy + side // 2)
    bgc = tuple(int(v) for v in np.asarray(img.convert("RGB"))[5, 5])
    canvas = Image.new("RGB", (side, side), bgc)
    src = img.convert("RGB")
    ix0, iy0 = max(box[0], 0), max(box[1], 0)
    ix1, iy1 = min(box[2], src.width), min(box[3], src.height)
    canvas.paste(src.crop((ix0, iy0, ix1, iy1)), (ix0 - box[0], iy0 - box[1]))
    return canvas.resize((size, size), Image.LANCZOS)
