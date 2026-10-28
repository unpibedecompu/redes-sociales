"""Per-frame camera calibration: align the mesh to a video frame's subject mask.

The video camera is approximated as orthographic. For a turntable angle `a` the model is rotated about +Y by
-(a + dyaw) (same convention as render.html), then projected: u = s*x + tx, v = -s*y + ty (pixels, 640x360).
(s, tx, ty, dyaw) are fitted per frame by maximising silhouette IoU against the rembg mask of that frame.
Masks and calibrations are cached in cache/ (masks per frame time; calibrations per mesh hash).
"""
import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

from common import ROOT, angle_to_time, extract_frame, subject_mask

CACHE = ROOT / "cache"


def rot_y(deg: float) -> np.ndarray:
    t = np.radians(deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def view_rotation(angle: float, dyaw: float = 0.0) -> np.ndarray:
    # matches render.html: orientation yaw = -(a + yaw)
    return rot_y(-(angle + dyaw))


def frame_rgb_and_mask(t: float):
    CACHE.mkdir(exist_ok=True)
    key = f"{t:.3f}"
    fp, mp = CACHE / f"frame_{key}.png", CACHE / f"mask_{key}.png"
    if not fp.exists():
        extract_frame(t, fp)
    rgb = np.asarray(Image.open(fp).convert("RGB"))
    if not mp.exists():
        Image.fromarray((subject_mask(Image.fromarray(rgb)) * 255).astype(np.uint8)).save(mp)
    mask = np.asarray(Image.open(mp)) > 127
    return rgb, mask


def project(verts, angle, cam):
    s, tx, ty, dyaw = cam
    p = verts @ view_rotation(angle, dyaw).T
    return np.stack([s * p[:, 0] + tx, -s * p[:, 1] + ty], 1), p[:, 2]


def silhouette(verts, faces, angle, cam, shape):
    uv, _ = project(verts, angle, cam)
    img = np.zeros(shape, np.uint8)
    # one call per triangle: a single multi-polygon fillPoly uses even-odd filling and leaves holes
    for tri in np.round(uv[faces] * 4).astype(np.int32):
        cv2.fillConvexPoly(img, tri, 1, lineType=cv2.LINE_8, shift=2)
    return img.astype(bool)


def iou(a, b):
    return float((a & b).sum() / max((a | b).sum(), 1))


def fit_camera(verts, faces, angle, mask, init=None):
    """Coordinate search over (s, tx, ty, dyaw); starts from a bbox-based guess."""
    H, W = mask.shape
    ys, xs = np.where(mask)
    if init is None:
        top, bottom = ys.min(), ys.max()
        h_mesh = verts[:, 1].max() - verts[:, 1].min()
        s = (bottom - top) / h_mesh
        ty = top + s * verts[:, 1].max()
        init = [s, float(xs.mean()), ty, 0.0]
    cam = list(init)
    best = iou(silhouette(verts, faces, angle, cam, mask.shape), mask)
    steps = [cam[0] * 0.04, 6.0, 6.0, 8.0]
    for _ in range(6):
        improved = True
        while improved:
            improved = False
            for k in range(4):
                for sign in (-1, 1):
                    c = list(cam)
                    c[k] += sign * steps[k]
                    sc = iou(silhouette(verts, faces, angle, c, mask.shape), mask)
                    if sc > best + 1e-4:
                        cam, best, improved = c, sc, True
        steps = [x / 2 for x in steps]
    return cam, best


def mesh_key(verts) -> str:
    return hashlib.md5(np.round(verts, 4).tobytes()).hexdigest()[:12]


def calibrate(verts, faces, angles, min_iou=0.75):
    """Fit a camera for each turntable angle. Returns {angle: dict(t, cam, iou)}; poorly fitting frames dropped."""
    CACHE.mkdir(exist_ok=True)
    cpath = CACHE / f"calib_{mesh_key(verts)}_{len(angles)}.json"
    if cpath.exists():
        return {float(k): v for k, v in json.loads(cpath.read_text()).items()}
    out, prev = {}, None
    for a in angles:
        t = angle_to_time(a)
        _, mask = frame_rgb_and_mask(t)
        # reuse scale/offset from the previous frame as a warm start (the subject barely moves)
        init = None if prev is None else [prev[0], prev[1], prev[2], 0.0]
        cam, sc = fit_camera(verts, faces, a, mask, init)
        if sc < 0.6 and init is not None:   # warm start went wrong, retry cold
            cam, sc = fit_camera(verts, faces, a, mask, None)
        prev = cam
        if sc >= min_iou:
            out[float(a)] = {"t": t, "cam": cam, "iou": round(sc, 3)}
    cpath.write_text(json.dumps(out, indent=1))
    return out
