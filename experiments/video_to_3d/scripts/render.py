"""Render a GLB at the 8 turntable angles and compare against the matching video frames.

Usage: python scripts/render.py iterations/iter_N [--yaw DEG]
Needs the local server: python -m http.server 8765 (run from experiments/video_to_3d).

Writes into the iteration folder:
  renders/angle_XXX.png    model render per angle
  targets/angle_XXX.png    matching video frame, cropped the same way
  comparison.png           target (top) vs render (bottom) per angle
  metrics.json             silhouette IoU / aspect / colour error per angle
"""
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, angle_to_time, crop_square, extract_frame, subject_mask

CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
ANGLES = [0, 45, 90, 135, 180, 225, 270, 315]
CELL = 360
BG = (0, 255, 0)  # green screen so white/grey texture is never mistaken for background


def render_copy(glb: Path, max_tex: int = 1024) -> Path:
    """Headless SwiftShader stalls on large textures; render from a copy with the texture capped at max_tex."""
    import io
    from pygltflib import GLTF2
    g = GLTF2().load(str(glb))
    blob = bytearray(g.binary_blob())
    changed = False
    for img in g.images:
        bv = g.bufferViews[img.bufferView]
        data = bytes(blob[bv.byteOffset or 0:(bv.byteOffset or 0) + bv.byteLength])
        im = Image.open(io.BytesIO(data))
        if max(im.size) <= max_tex:
            continue
        buf = io.BytesIO()
        im.resize((max_tex, max_tex), Image.LANCZOS).save(buf, "PNG")
        new = buf.getvalue()
        # append the smaller image at the end of the blob and point the view at it
        off = (len(blob) + 3) // 4 * 4
        blob.extend(bytes(off - len(blob)))
        bv.byteOffset, bv.byteLength = off, len(new)
        blob.extend(new)
        changed = True
    out = glb.with_name("_render.glb")
    if changed:
        g.buffers[0].byteLength = len(blob)
        g.set_binary_blob(bytes(blob))
        g.save(str(out))
    else:
        out.write_bytes(glb.read_bytes())
    return out


def calibrated_yaws(glb: Path, limit: float = 35.0):
    """The video's spin speed is uneven, so the frame picked for angle `a` may really show a+d. Fit d per angle
    (camera.fit_camera against that frame's mask) and render the model at the same pose, so pairs are comparable."""
    import trimesh
    from camera import fit_camera, frame_rgb_and_mask
    m = trimesh.load(str(glb), force="mesh", process=False)
    out = []
    for a in ANGLES:
        _, mask = frame_rgb_and_mask(angle_to_time(a))
        cam, _ = fit_camera(m.vertices, m.faces, a, mask)
        out.append(float(np.clip(cam[3], -limit, limit)))
    return out


def screenshot(url: str, out: Path, budget_ms: int = 60000):
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([CHROME, "--headless=new", f"--user-data-dir={prof}", "--hide-scrollbars",
                        "--use-angle=swiftshader", "--enable-unsafe-swiftshader", f"--window-size={CELL * 4},{CELL * 2}",
                        f"--virtual-time-budget={budget_ms}", f"--screenshot={out}", url],
                       check=True, capture_output=True, timeout=300)


def screenshot_until_loaded(url: str, out: Path):
    """Large textures can still be decoding when the budget expires; retry with a longer budget if empty."""
    for budget in (25000, 60000, 60000, 120000):
        screenshot(url, out, budget)
        if render_mask(Image.open(out)).sum() > 5000:
            return
    sys.exit("ERROR: render still empty after retries (headless Chrome did not load the model) - rerun")


def render_mask(img: Image.Image) -> np.ndarray:
    # renders sit on a flat background, so a colour-distance key is exact
    a = np.asarray(img.convert("RGB")).astype(np.int16)
    # anti-aliased edges blend with the green screen; any clearly green-dominant pixel is background
    greenness = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
    return (np.abs(a - np.array(BG)).max(axis=2) > 40) & (greenness < 40)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iter_dir")
    ap.add_argument("--yaw", type=float, default=0.0)
    ap.add_argument("--exposure", type=float, default=1.0)
    ap.add_argument("--calib-yaw", action="store_true", help="fit a yaw offset per angle (experimental)")
    args = ap.parse_args()
    it = Path(args.iter_dir).resolve()
    rel = it.relative_to(ROOT).as_posix()
    (it / "renders").mkdir(exist_ok=True)
    (it / "targets").mkdir(exist_ok=True)

    render_copy(it / "model.glb")
    grid_png = it / "renders" / "_grid.png"
    # per-angle yaw fitting is opt-in: silhouettes alone can confuse front/back (e.g. 135 deg)
    yaws = calibrated_yaws(it / "_render.glb") if args.calib_yaw else [0.0] * len(ANGLES)
    url = (f"http://localhost:8765/render.html?glb=/{rel}/_render.glb&yaw={args.yaw}"
           f"&yaws={','.join(f'{y:.1f}' for y in yaws)}"
           f"&exposure={args.exposure}&angles={','.join(map(str, ANGLES))}")
    screenshot_until_loaded(url, grid_png)
    grid = Image.open(grid_png).convert("RGB")

    metrics, pairs = {}, []
    for i, a in enumerate(ANGLES):
        # inset by a few px to drop the cell seams
        cell = grid.crop(((i % 4) * CELL + 12, (i // 4) * CELL + 12, (i % 4 + 1) * CELL - 12, (i // 4 + 1) * CELL - 12))
        rmask = render_mask(cell)
        tgt_raw = Image.open(extract_frame(angle_to_time(a), it / "targets" / f"raw_{a:03d}.png"))
        tmask = subject_mask(tgt_raw)
        S = 256
        tgt = crop_square(tgt_raw, size=S, mask=tmask)
        tgt.save(it / "targets" / f"angle_{a:03d}.png")
        if rmask.sum() < 50:
            ren = cell.resize((S, S))
            iou, note = 0.0, "empty render"
        else:
            ren = crop_square(cell, size=S, mask=rmask)
            # recompute masks on normalised crops (same framing rule both sides)
            tm = subject_mask(tgt)
            rm = render_mask(ren)
            iou = float((tm & rm).sum() / max((tm | rm).sum(), 1))
            note = ""
        rm_full = render_mask(ren)
        shown = np.asarray(ren).copy()
        shown[~rm_full] = (154, 154, 154)
        ren = Image.fromarray(shown)
        ren.save(it / "renders" / f"angle_{a:03d}.png")
        ta = np.asarray(tgt).astype(float)
        ra = np.asarray(ren).astype(float)
        both = subject_mask(tgt) & render_mask(ren)
        col = float(np.abs(ta[both].mean(0) - ra[both].mean(0)).mean()) if both.sum() > 50 else None
        metrics[str(a)] = {"silhouette_iou": round(iou, 3), "mean_color_diff": None if col is None else round(col, 1),
                           "note": note}
        pairs.append((tgt, ren, a))

    ious = [m["silhouette_iou"] for m in metrics.values()]
    metrics["mean_silhouette_iou"] = round(float(np.mean(ious)), 3)
    metrics["yaw_offsets"] = dict(zip(map(str, ANGLES), [round(y, 1) for y in yaws]))
    (it / "metrics.json").write_text(json.dumps(metrics, indent=2))

    S = 256
    sheet = Image.new("RGB", (S * len(pairs), S * 2 + 20), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for i, (t, r, a) in enumerate(pairs):
        sheet.paste(t, (i * S, 20))
        sheet.paste(r, (i * S, 20 + S))
        d.text((i * S + 4, 4), f"{a} deg  IoU {metrics[str(a)]['silhouette_iou']}", fill=(0, 0, 0))
    sheet.save(it / "comparison.png")
    print(json.dumps({"mean_silhouette_iou": metrics["mean_silhouette_iou"], "comparison": str(it / "comparison.png")}))


if __name__ == "__main__":
    main()
