"""Generate a GLB from the target video using a free Hugging Face Space.

Usage: python scripts/generate.py iterations/iter_N/config.json

config.json:
{
  "backend": "trellis" | "hunyuan",
  "views": {"front": 0, "left": 90, "back": 180, "right": 270},   # name -> turntable angle (deg)
  "crop_pad": 0.08,            # padding around subject when cropping to square
  "input_size": 1024,
  "params": {...},             # passed straight to the Space endpoint (overrides defaults)
  "preprocess_all": false      # trellis only: run every multi-image through the Space's /preprocess_image
                               # (background removal + centring) instead of sending raw grey-bg crops
  "force_multiimage": false    # trellis only: select the Space's "Multiple Images" tab (/lambda_1) first.
                               # The Space keeps is_multiimage in a gr.State that defaults to False, so
                               # without this, /generate_and_extract_glb IGNORES multiimages and runs
                               # single-image on the primary image (true for every run before iter_2 fix).
  "post": {                    # optional mesh/texture post-process (iter_3). The raw Space output is kept as
                               # model_raw.glb and model.glb is the processed result. Re-run only this step with
                               # `generate.py <config> --post-only` (reads model_raw.glb, no Space call).
    "clip_bottom_frac": 0.17,  # cut away the bottom fraction of the mesh height (video ends at the hips)
    "tex_gamma_front": 1.0,    # sRGB gamma lift (>1 brightens darks) for front-facing (+Z) texels ...
    "tex_gamma_back": 1.0,     # ... and back-facing (-Z) texels; blended by w = (1 - n_z) / 2
    "tex_gain": 1.0,           # multiplier after gamma
    "tex_sat": 1.0,            # saturation (1 = unchanged)
    # --- iter_4 additions (all optional; omitted = no-op) ---
    "body_scale_xz": [1, 1],   # scale x (width) / z (depth) of vertices below the neck, about the torso axis
    "neck_frac": 0.22,         # neck height as fraction of (post-clip) height measured from the top
    "neck_ramp": 0.05,         # smoothstep ramp (fraction of height) from scale 1 at the neck to full scale
    "shoulder_extra_x": 0.0,   # extra width factor added in a gaussian band at shoulder height ...
    "shoulder_frac": 0.32,     # ... centred this far down from the top (fraction of height) ...
    "shoulder_width": 0.08,    # ... with this sigma (fraction of height)
    "skin_protect": false,     # exclude skin texels (head region, skin hue) from gamma/sat/sharpen ...
    "skin_head_frac": 0.26,    # ... only texels on faces above this fraction from the top
    "skin_gain": [1, 1, 1],    # RGB multiplier applied to skin texels instead (warm shift)
    "skin_gamma": 1.0,         # gamma lift applied to skin texels
    "tex_sharpen": 0.0,        # unsharp-mask amount (radius 2 px) on non-skin texels (0 = off)
    # --- iter_5 additions (all optional; omitted = old behaviour) ---
    "skin_min_cc": 0,          # drop skin-mask connected components smaller than this many texels (seam strokes)
    "skin_dilate": 1,          # mask dilation radius in px (old behaviour: MaxFilter(3) = 1)
    "skin_feather": 2,         # gaussian feather of the mask in px (old: 2)
    "skin_sat": 1.0,           # saturation applied to skin texels (after skin_gamma / skin_gain)
    "back_hi_lift": 1.0,       # highlight-only lift on back-facing texels: x(1+(k-1)*w*smoothstep(lo,hi,luma))
    "back_hi_lo": 0.45, "back_hi_hi": 0.8
  }
}
For trellis, every view is sent as a multi-image (first one is the primary).
For hunyuan, view names must be front/back/left/right (any subset; front required).
"""
import json
import shutil
import sys
import time
from pathlib import Path

from gradio_client import Client, handle_file
from huggingface_hub import get_token
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import angle_to_time, crop_square, extract_frame

TRELLIS_DEFAULTS = dict(seed=0, ss_guidance_strength=7.5, ss_sampling_steps=12, slat_guidance_strength=3.0,
                        slat_sampling_steps=12, multiimage_algo="stochastic", mesh_simplify=0.95, texture_size=1024)
HUNYUAN_DEFAULTS = dict(caption=None, steps=30, guidance_scale=5.0, seed=1234, octree_resolution=256,
                        check_box_rembg=True, num_chunks=8000, randomize_seed=False)


def prepare_inputs(cfg, out_dir: Path) -> dict[str, Path]:
    paths = {}
    for name, deg in cfg["views"].items():
        raw = extract_frame(angle_to_time(deg), out_dir / "inputs" / f"raw_{name}.png")
        img = crop_square(Image.open(raw), pad=cfg.get("crop_pad", 0.08), size=cfg.get("input_size", 1024))
        p = out_dir / "inputs" / f"{name}.png"
        img.save(p)
        paths[name] = p
    return paths


def find_glb(result) -> str:
    items = result if isinstance(result, (list, tuple)) else [result]
    for it in items:
        if isinstance(it, dict):
            it = it.get("value") or it.get("path") or it.get("video")
        if isinstance(it, str) and it.lower().endswith(".glb"):
            return it
    raise RuntimeError(f"no GLB in result: {result!r}")


def run_trellis(inputs, params, preprocess_all=False, out_dir=None, force_multiimage=False):
    c = Client("trellis-community/TRELLIS", verbose=False, token=get_token())
    c.predict(api_name="/start_session")
    if force_multiimage:
        c.predict(api_name="/lambda_1")  # multi-image tab .select -> is_multiimage=True for this session
    imgs = list(inputs.values())
    pre = c.predict(image=handle_file(str(imgs[0])), api_name="/preprocess_image")
    if preprocess_all:
        pres = [pre] + [c.predict(image=handle_file(str(p)), api_name="/preprocess_image") for p in imgs[1:]]
        if out_dir is not None:
            for name, pp in zip(inputs, pres):
                shutil.copy(pp, out_dir / "inputs" / f"pre_{name}.png")
        multi = [{"image": handle_file(pp), "caption": None} for pp in pres]
    else:
        multi = [{"image": handle_file(str(p)), "caption": None} for p in imgs]
    p = {**TRELLIS_DEFAULTS, **params}
    res = c.predict(image=handle_file(pre), multiimages=multi, api_name="/generate_and_extract_glb", **p)
    return find_glb(res)


def run_hunyuan(inputs, params):
    c = Client(params.pop("space", "tencent/Hunyuan3D-2"), verbose=False, token=get_token())
    p = {**HUNYUAN_DEFAULTS, **params}
    kw = {"image": handle_file(str(inputs["front"])) if "front" in inputs and len(inputs) == 1 else None}
    for v in ("front", "back", "left", "right"):
        kw[f"mv_image_{v}"] = handle_file(str(inputs[v])) if v in inputs and len(inputs) > 1 else None
    res = c.predict(api_name="/generation_all", **kw, **p)
    return find_glb(res)


def _texel_weight_map(mesh, size):
    """Per-texel back-facing weight w = (1 - n_z)/2 (0 front, 0.5 side, 1 back), rasterised in UV space."""
    from PIL import ImageDraw, ImageFilter
    import numpy as np
    W, H = size
    acc = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(acc)
    uv = mesh.visual.uv
    w = (1.0 - mesh.face_normals[:, 2]) / 2.0
    for f, wf in zip(mesh.faces, w):
        pts = [(float(uv[i, 0]) * W, (1.0 - float(uv[i, 1])) * H) for i in f]
        v = int(round(np.clip(wf, 0, 1) * 254)) + 1  # 0 = unpainted
        d.polygon(pts, fill=v, outline=v, width=3)
    a = np.asarray(acc).astype(np.float32)
    painted = a > 0
    wm = np.where(painted, (a - 1) / 254.0, 0.5)
    blur = np.asarray(Image.fromarray((wm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3))) / 255.0
    return blur


def _texel_face_map(mesh, size, values, blur=0):
    """Rasterise a per-face scalar in [0,1] into UV space (unpainted texels -> 0)."""
    from PIL import ImageDraw, ImageFilter
    import numpy as np
    W, H = size
    acc = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(acc)
    uv = mesh.visual.uv
    for f, vf in zip(mesh.faces, values):
        pts = [(float(uv[i, 0]) * W, (1.0 - float(uv[i, 1])) * H) for i in f]
        v = int(round(float(np.clip(vf, 0, 1)) * 255))
        d.polygon(pts, fill=v, outline=v, width=3)
    if blur:
        acc = acc.filter(ImageFilter.GaussianBlur(blur))
    return np.asarray(acc).astype(np.float32) / 255.0


def _skin_mask(c, mesh, size, head_frac, min_cc=0, dilate=1, feather=2):
    """Soft skin mask: skin-like hue/sat/value on faces in the top `head_frac` of the mesh height."""
    import numpy as np
    from PIL import ImageFilter
    y = mesh.triangles_center[:, 1]
    y0, y1 = mesh.bounds[0, 1], mesh.bounds[1, 1]
    head = _texel_face_map(mesh, size, (y > y1 - head_frac * (y1 - y0)).astype(float))
    mx, mn = c.max(-1), c.min(-1)
    sat = (mx - mn) / np.maximum(mx, 1e-6)
    r, g, b = c[..., 0], c[..., 1], c[..., 2]
    hue_ok = (r >= g) & (g >= b * 0.9)          # roughly 0-45 deg (orange/tan), excludes purple/blue
    m = hue_ok & (sat > 0.12) & (sat < 0.6) & (mx > 0.35) & (head > 0.5)
    if min_cc > 0:
        from scipy import ndimage
        lab, n = ndimage.label(m)
        sizes = ndimage.sum(m, lab, range(1, n + 1))
        m = np.isin(lab, 1 + np.flatnonzero(sizes >= min_cc))
    m = Image.fromarray((m * 255).astype(np.uint8))
    if dilate > 0:
        m = m.filter(ImageFilter.MaxFilter(2 * dilate + 1))
    if feather > 0:
        m = m.filter(ImageFilter.GaussianBlur(feather))
    return np.asarray(m).astype(np.float32)[..., None] / 255.0


def _body_scale(mesh, post):
    import numpy as np
    sx, sz = post.get("body_scale_xz", [1.0, 1.0])
    extra = post.get("shoulder_extra_x", 0.0)
    if (sx, sz, extra) == (1.0, 1.0, 0.0):
        return mesh
    v = mesh.vertices.copy()
    y0, y1 = mesh.bounds[0, 1], mesh.bounds[1, 1]
    h = y1 - y0
    neck = y1 - post.get("neck_frac", 0.22) * h
    ramp = max(post.get("neck_ramp", 0.05) * h, 1e-6)
    t = np.clip((neck - v[:, 1]) / ramp, 0, 1)
    t = t * t * (3 - 2 * t)                       # smoothstep
    below = v[:, 1] < neck - ramp
    cx, cz = v[below, 0].mean(), v[below, 2].mean()
    ys = y1 - post.get("shoulder_frac", 0.32) * h
    band = np.exp(-0.5 * ((v[:, 1] - ys) / (post.get("shoulder_width", 0.08) * h)) ** 2)
    fx = 1 + t * (sx - 1 + extra * band)
    fz = 1 + t * (sz - 1)
    v[:, 0] = cx + (v[:, 0] - cx) * fx
    v[:, 2] = cz + (v[:, 2] - cz) * fz
    mesh.vertices = v
    print(f"body scale: x {sx} z {sz} (+{extra} at shoulders) below y={neck:.3f}, axis ({cx:.3f},{cz:.3f})")
    return mesh


def postprocess(raw: Path, out: Path, post: dict):
    import numpy as np
    import trimesh
    mesh = trimesh.load(str(raw), force="mesh", process=False)
    frac = post.get("clip_bottom_frac", 0.0)
    if frac > 0:
        y0, y1 = mesh.bounds[0, 1], mesh.bounds[1, 1]
        cut = y0 + frac * (y1 - y0)
        mesh = mesh.slice_plane([0, cut, 0], [0, 1, 0], cap=False)
        print(f"clip: removed y < {cut:.3f} ({frac:.0%} of height) -> {len(mesh.faces)} faces")
    mesh = _body_scale(mesh, post)
    gf, gb = post.get("tex_gamma_front", 1.0), post.get("tex_gamma_back", 1.0)
    gain, sat = post.get("tex_gain", 1.0), post.get("tex_sat", 1.0)
    sharpen, skin = post.get("tex_sharpen", 0.0), post.get("skin_protect", False)
    if (gf, gb, gain, sat, sharpen, skin) != (1.0, 1.0, 1.0, 1.0, 0.0, False):
        from PIL import ImageFilter
        mat = mesh.visual.material
        tex = mat.baseColorTexture.convert("RGB")
        c0 = np.asarray(tex).astype(np.float32) / 255.0
        w = _texel_weight_map(mesh, tex.size)[..., None]
        gamma = gf + (gb - gf) * w
        c = np.clip(c0, 0, 1) ** (1.0 / gamma) * gain
        luma = (c * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
        c = np.clip(luma + sat * (c - luma), 0, 1)
        k = post.get("back_hi_lift", 1.0)
        if k != 1.0:
            lo, hi = post.get("back_hi_lo", 0.45), post.get("back_hi_hi", 0.8)
            l2 = (c * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
            t = np.clip((l2 - lo) / (hi - lo), 0, 1)
            c = np.clip(c * (1 + (k - 1) * w * t * t * (3 - 2 * t)), 0, 1)
        if sharpen > 0:
            im = Image.fromarray((c * 255 + 0.5).astype(np.uint8))
            im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=int(sharpen * 100), threshold=0))
            c = np.asarray(im).astype(np.float32) / 255.0
        if skin:
            m = _skin_mask(c0, mesh, tex.size, post.get("skin_head_frac", 0.26), post.get("skin_min_cc", 0),
                           post.get("skin_dilate", 1), post.get("skin_feather", 2))
            cs = np.clip(c0, 0, 1) ** (1.0 / post.get("skin_gamma", 1.0)) * np.array(post.get("skin_gain", [1, 1, 1]), np.float32)
            ls = (cs * np.array([0.299, 0.587, 0.114], np.float32)).sum(-1, keepdims=True)
            cs = ls + post.get("skin_sat", 1.0) * (cs - ls)
            c = np.clip(m * cs + (1 - m) * c, 0, 1)
            Image.fromarray((m[..., 0] * 255).astype(np.uint8)).save(out.parent / "skin_mask_uv.png")
            print(f"skin: {float((m > 0.5).mean()):.2%} of texels protected")
        mat.baseColorTexture = Image.fromarray((c * 255 + 0.5).astype(np.uint8))
        print(f"texture: gamma front {gf} back {gb}, gain {gain}, sat {sat}, sharpen {sharpen}")
    mesh.export(str(out))


def main():
    cfg_path = Path(sys.argv[1]).resolve()
    out_dir = cfg_path.parent
    cfg = json.loads(cfg_path.read_text())
    if "--post-only" in sys.argv:
        postprocess(out_dir / "model_raw.glb", out_dir / "model.glb", cfg.get("post", {}))
        print(f"OK post-only -> {out_dir / 'model.glb'}")
        return
    inputs = prepare_inputs(cfg, out_dir)
    runner = {"trellis": run_trellis, "hunyuan": run_hunyuan}[cfg["backend"]]
    t0 = time.time()
    if cfg["backend"] == "trellis":
        glb = run_trellis(inputs, dict(cfg.get("params", {})), cfg.get("preprocess_all", False), out_dir,
                          cfg.get("force_multiimage", False))
    else:
        glb = runner(inputs, dict(cfg.get("params", {})))
    if cfg.get("post"):
        shutil.copy(glb, out_dir / "model_raw.glb")
        postprocess(out_dir / "model_raw.glb", out_dir / "model.glb", cfg["post"])
    else:
        shutil.copy(glb, out_dir / "model.glb")
    print(f"OK {cfg['backend']} in {time.time() - t0:.0f}s -> {out_dir / 'model.glb'}")


if __name__ == "__main__":
    main()
