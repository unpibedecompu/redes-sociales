"""Images -> clean low-poly GLB, one shot.

Usage (from experiments/images_to_3d):
    python scripts/build.py                 # prep + generate + lowpoly + preview
    python scripts/build.py --from lowpoly  # re-run from a stage (reuses output/model_raw.glb)
    python scripts/build.py --faces 2500 --colors 12

Stages:
  prep      crop every input view to a square around the subject (rembg mask)       -> output/inputs/*.png
  generate  TRELLIS multi-image on the free HF Space (reuses video_to_3d/generate)  -> output/model_raw.glb
  lowpoly   clean + decimate + one flat colour per face from a small palette       -> output/model.glb
  preview   flat-shaded software renders at 8 angles next to the inputs           -> output/preview.png
"""
import argparse
import json
import shutil
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output"
sys.path.insert(0, str(ROOT.parent / "video_to_3d" / "scripts"))
from common import crop_square  # noqa: E402

# Front first: TRELLIS uses the first image as the primary one.
VIEWS = {
    "front": "Gemini_Generated_Image_f1r4vkf1r4vkf1r4.jpg",
    "right": "Gemini_Generated_Image_ne4b4wne4b4wne4b.jpg",     # character's right side (nose to image right)
    "left": "Gemini_Generated_Image_t5lwngt5lwngt5lw.jpg",      # character's left side (nose to image left)
    "back": "Gemini_Generated_Image_wiojwnwiojwnwioj.jpg",
    "right_34": "Gemini_Generated_Image_nyix8snyix8snyix.jpg",
    "left_34": "Gemini_Generated_Image_fp8wfxfp8wfxfp8w.jpg",
    "right_back": "Gemini_Generated_Image_vws388vws388vws3.jpg",  # back 3/4, face peeking at image right
    "left_back": "Gemini_Generated_Image_41hhtt41hhtt41hh.jpg",   # back 3/4, face peeking at image left
}
STAGES = ["prep", "generate", "lowpoly", "preview"]


def prep():
    (OUT / "inputs").mkdir(parents=True, exist_ok=True)
    paths = {}
    for name, fn in VIEWS.items():
        img = crop_square(Image.open(ROOT / "input" / fn), pad=0.06, size=1024)
        p = OUT / "inputs" / f"{name}.png"
        img.save(p)
        paths[name] = p
        print(f"prep: {name} <- {fn}")
    return paths


def generate(params):
    from generate import run_trellis
    inputs = {n: OUT / "inputs" / f"{n}.png" for n in VIEWS}
    glb = run_trellis(inputs, params, preprocess_all=True, out_dir=OUT, force_multiimage=True)
    shutil.copy(glb, OUT / "model_raw.glb")
    print(f"generate: -> {OUT / 'model_raw.glb'}")


# ---------------------------------------------------------------- lowpoly

def _sample_texture(mesh, points):
    """Colour of the textured `mesh` at the surface point closest to each of `points` (N,3) -> (N,3) in [0,1]."""
    import trimesh
    tex = np.asarray(mesh.visual.material.baseColorTexture.convert("RGB")).astype(np.float32) / 255.0
    H, W = tex.shape[:2]
    closest, _, tri = trimesh.proximity.closest_point(mesh, points)
    bary = trimesh.triangles.points_to_barycentric(mesh.triangles[tri], closest)
    uv = (mesh.visual.uv[mesh.faces[tri]] * bary[:, :, None]).sum(1)
    x = np.clip((uv[:, 0] % 1.0) * (W - 1), 0, W - 1).astype(int)
    y = np.clip((1.0 - uv[:, 1] % 1.0) * (H - 1), 0, H - 1).astype(int)
    return tex[y, x]


VIEW_YAW = {"front": 0, "right_34": 45, "right": 90, "right_back": 135, "back": 180, "left_back": 225,
            "left": 270, "left_34": 315}


def _yaw(pts, yaw):
    a = np.radians(yaw)
    R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    return pts @ R.T


def _id_buffer(p2, depth, size):
    """Painter's rasterisation of projected triangles p2 (F,3,2 in px) -> int32 face-id image (-1 = empty)."""
    im = Image.new("I", (size, size), 0)
    d = ImageDraw.Draw(im)
    for i in np.argsort(depth):  # far -> near
        d.polygon([tuple(q) for q in p2[i]], fill=int(i) + 1)
    return np.asarray(im).astype(np.int64) - 1


def _silhouette(p2, size):
    im = Image.new("1", (size, size), 0)
    d = ImageDraw.Draw(im)
    for t in p2:
        d.polygon([tuple(q) for q in t], fill=1)
    return np.asarray(im, dtype=bool)


HEAD_FRAC = 0.55   # faces in the top 55% of the mesh height use the head-only fit


def _fit(xy, mask, x, size, rows):
    """Coordinate descent on (sx, sy, ox, oy) maximising silhouette IoU over image rows rows[0]:rows[1]."""
    m = mask[rows[0]:rows[1]]

    def iou_of(x):
        sil = _silhouette(xy * x[:2] + x[2:], size)[rows[0]:rows[1]]
        return (sil & m).sum() / max((sil | m).sum(), 1)

    best = iou_of(x)
    steps = np.array([0.08 * x[0], 0.08 * x[1], 0.04 * size, 0.04 * size])
    for _ in range(6):
        improved = True
        while improved:
            improved = False
            for k in range(4):
                for sgn in (1, -1):
                    y = x.copy()
                    y[k] += sgn * steps[k]
                    v = iou_of(y)
                    if v > best:
                        best, x, improved = v, y, True
        steps /= 2
    return x, best


def _project_views(tri, normals, size=512, sample=1024):
    """Per-face colour from the input views. Each view: rotate the mesh by its yaw, orthographic-project,
    fit scale/offset so the mesh silhouette best overlaps the image's subject mask (IoU grid search), then
    collect the image pixels each face covers (at `sample` px). Returns per-view median colour and a
    head-on weight (visible px * cos^8) per face."""
    from common import subject_mask
    from scipy import ndimage
    F = len(tri)
    cols, scores = [], []
    c0 = tri.reshape(-1, 3).mean(0)
    for name, yaw in VIEW_YAW.items():
        full = Image.open(OUT / "inputs" / f"{name}.png").convert("RGB")
        img = full.resize((size, size), Image.LANCZOS)
        rgb = np.asarray(full.resize((sample, sample), Image.LANCZOS)).astype(np.float32) / 255.0
        mask = subject_mask(img)
        t = _yaw(tri - c0, yaw)
        n = _yaw(normals, yaw)
        xy = t[..., :2] * [1, -1]                                   # image y points down
        # init from bounding boxes (top + horizontal centre + height), then coordinate descent on
        # (sx, sy, ox, oy) maximising silhouette IoU -- x and y scale separately, the Gemini views and the
        # TRELLIS mesh don't share proportions exactly
        ys, xs = np.where(mask)
        lo, hi = xy.reshape(-1, 2).min(0), xy.reshape(-1, 2).max(0)
        s0 = (ys.max() - ys.min()) / (hi[1] - lo[1])
        x = np.array([s0, s0, (xs.min() + xs.max()) / 2 - s0 * (lo[0] + hi[0]) / 2, ys.min() - s0 * lo[1]])

        x_all, _ = _fit(xy, mask, x, size, rows=(0, size))
        # head and body get separate fits on the top / bottom half of the silhouette: one global fit is
        # dominated by the shoulders and lands the drawn eyes and beard a few cm off on the mesh
        cut = int(ys.min() + 0.5 * (ys.max() - ys.min()))
        x_head, iou_head = _fit(xy, mask, x_all, size, rows=(0, cut))
        x_body, iou_body = _fit(xy, mask, x_all, size, rows=(cut, size))
        print(f"  view {name:8s} yaw {yaw:3d}: IoU body {iou_body:.3f} head {iou_head:.3f}")
        y3 = tri[:, :, 1].mean(1)
        head = y3 > y3.max() - HEAD_FRAC * (y3.max() - y3.min())
        p2 = np.where(head[:, None, None], xy * x_head[:2] + x_head[2:], xy * x_body[:2] + x_body[2:])
        k = sample / size
        ids = _id_buffer(p2 * k, t[:, :, 2].mean(1), sample)       # camera on +Z: small z = far
        big = np.asarray(Image.fromarray(mask).resize((sample, sample)))
        ids[~ndimage.binary_erosion(big, iterations=int(2 * k))] = -1   # ignore background / edge pixels
        flat = ids.ravel()
        keep = flat >= 0
        fid, pix = flat[keep], rgb.reshape(-1, 3)[keep]
        cnt = np.bincount(fid, minlength=F)
        order = np.argsort(fid, kind="stable")
        starts = np.concatenate([[0], np.cumsum(cnt)])
        cos = np.clip(n[:, 2], 0, 1)
        score = cnt * cos ** 8
        score[cnt < 3] = 0
        col = np.zeros((F, 3))
        for f in np.flatnonzero(score > 0):
            col[f] = np.median(pix[order[starts[f]:starts[f + 1]]], 0)
        cols.append(col)
        scores.append(score)
    return np.stack(cols), np.stack(scores)   # (V,F,3), (V,F)


def _kmeans(x, k, iters=30, seed=0):
    """k-means with k-means++ init, so small but distinct colours (purple shirt, red tee) get a cluster."""
    rng = np.random.default_rng(seed)
    c = [x[rng.integers(len(x))]]
    for _ in range(k - 1):
        d = ((x[:, None] - np.array(c)[None]) ** 2).sum(-1).min(1)
        c.append(x[rng.choice(len(x), p=d / d.sum())])
    c = np.array(c)
    for _ in range(iters):
        lab = ((x[:, None] - c[None]) ** 2).sum(-1).argmin(1)
        c = np.array([x[lab == i].mean(0) if (lab == i).any() else c[i] for i in range(k)])
    return c, lab


def lowpoly(target_faces, n_colors, clip_bottom, face_subdiv=2):
    import fast_simplification
    import trimesh
    src = trimesh.load(str(OUT / "model_raw.glb"), force="mesh", process=False)
    print(f"lowpoly: raw {len(src.faces)} faces, bounds {src.bounds.round(3).tolist()}")

    # geometry: merge seams, keep the biggest piece, flat-cut the ragged bottom and cap it
    geo = trimesh.Trimesh(src.vertices, src.faces, process=True)
    geo = max(geo.split(only_watertight=False), key=lambda m: len(m.faces))
    if clip_bottom > 0:
        y0, y1 = geo.bounds[0, 1], geo.bounds[1, 1]
        geo = geo.slice_plane([0, y0 + clip_bottom * (y1 - y0), 0], [0, 1, 0], cap=True)
    ratio = 1.0 - target_faces / len(geo.faces)
    v, f = fast_simplification.simplify(geo.vertices.astype(np.float32), geo.faces.astype(np.int32), ratio)
    lp = trimesh.Trimesh(v, f, process=True)
    trimesh.repair.fix_normals(lp)
    print(f"lowpoly: {len(geo.faces)} -> {len(lp.faces)} faces")
    # face detail: split the front of the head into smaller coplanar triangles (geometry unchanged) so the
    # eyes, brows, lips and beard edge get their own facets -- the same trick the reference drawings use
    for _ in range(face_subdiv):
        y = lp.triangles_center[:, 1]
        y0, y1 = lp.bounds[0, 1], lp.bounds[1, 1]
        sel = np.flatnonzero((y > y1 - HEAD_FRAC * (y1 - y0)) & (lp.face_normals[:, 2] > 0.1))
        v, f = trimesh.remesh.subdivide(lp.vertices, lp.faces, face_index=sel)
        lp = trimesh.Trimesh(v, f, process=True)
    if face_subdiv:
        print(f"lowpoly: face subdivided x{face_subdiv} -> {len(lp.faces)} faces")

    # colour: project the input views onto the faces; the TRELLIS texture is only a fallback for unseen faces
    tri = lp.triangles
    cen = tri.mean(1)
    vcol, vscore = _project_views(tri, lp.face_normals)
    seen = vscore.max(0) > 0
    print(f"lowpoly: {seen.mean():.1%} of faces seen by at least one input view")

    # clean: one palette (k-means, sRGB) over every (view, face) sample; each face takes the
    # palette entry with the highest head-on-weighted vote across views, so one misaligned view can't win
    F = len(lp.faces)
    samp = vscore > 0
    palette, _ = _kmeans(vcol[samp], n_colors)
    vlab = ((vcol[..., None, :] - palette) ** 2).sum(-1).argmin(-1)        # (V,F)
    # only views close to the face's best one vote: grazing views are where misalignment lives
    vscore = np.where(vscore >= 0.5 * vscore.max(0, keepdims=True), vscore, 0)
    votes = np.zeros((F, n_colors))
    for v in range(len(vcol)):
        np.add.at(votes, (np.arange(F), vlab[v]), vscore[v])
    lab = votes.argmax(1)
    if (~seen).any():                       # never-seen faces (under the chin, bottom cap): TRELLIS texture
        pts = [cen] + [cen + 0.6 * (tri[:, i] - cen) for i in range(3)]
        tex = np.median(np.stack([_sample_texture(src, p) for p in pts], 1), 1)
        lab[~seen] = ((tex[~seen, None] - palette) ** 2).sum(-1).argmin(-1)
    # mode filter: a face whose label disagrees with >= 2 of its 3 neighbours (that agree) takes theirs
    adj = lp.face_adjacency
    for _ in range(1):
        nb = np.zeros((F, n_colors))
        np.add.at(nb, (adj[:, 0], lab[adj[:, 1]]), 1)
        np.add.at(nb, (adj[:, 1], lab[adj[:, 0]]), 1)
        top = nb.argmax(1)
        flip = (nb[np.arange(F), top] >= 2) & (nb[np.arange(F), lab] == 0)
        lab = np.where(flip, top, lab)
    face_rgb = palette[lab]

    # export: unshared vertices so every face is flat-shaded with its own colour
    out = trimesh.Trimesh(lp.vertices[lp.faces].reshape(-1, 3), np.arange(len(lp.faces) * 3).reshape(-1, 3),
                          process=False)
    rgba = np.concatenate([np.repeat(face_rgb, 3, 0), np.ones((len(out.vertices), 1))], 1)
    out.visual = trimesh.visual.ColorVisuals(out, vertex_colors=(rgba * 255).astype(np.uint8))
    out.vertex_normals = np.repeat(lp.face_normals, 3, 0)
    out.export(str(OUT / "model.glb"))
    _palette_png(palette, np.bincount(lab, minlength=n_colors))
    meta = dict(faces=int(len(lp.faces)), colors=n_colors, palette=(palette * 255).round().astype(int).tolist())
    (OUT / "lowpoly.json").write_text(json.dumps(meta, indent=1))
    np.savez(OUT / "_lowpoly_cache.npz", tri=tri, rgb=face_rgb, n=lp.face_normals)
    print(f"lowpoly: -> {OUT / 'model.glb'}")


def _palette_png(palette, counts):
    im = Image.new("RGB", (60 * len(palette), 80), "white")
    d = ImageDraw.Draw(im)
    for i, (c, n) in enumerate(zip(palette, counts)):
        d.rectangle([i * 60, 0, i * 60 + 59, 59], fill=tuple(int(v * 255) for v in c))
        d.text((i * 60 + 4, 63), str(int(n)), fill="black")
    im.save(OUT / "palette.png")


# ---------------------------------------------------------------- preview

def _render(tri, rgb, normals, yaw, size=512):
    """Painter's-algorithm flat render, orthographic, camera on +Z looking at -Z, model rotated by `yaw` (deg)."""
    a = np.radians(yaw)
    R = np.array([[np.cos(a), 0, np.sin(a)], [0, 1, 0], [-np.sin(a), 0, np.cos(a)]])
    c = tri.reshape(-1, 3).mean(0)
    t = (tri - c) @ R.T
    n = normals @ R.T
    s = 0.9 * size / (np.abs(t[..., :2]).max() * 2)
    light = np.array([0.4, 0.6, 0.7]) / np.linalg.norm([0.4, 0.6, 0.7])
    shade = 0.45 + 0.55 * np.clip(n @ light, 0, 1)
    im = Image.new("RGB", (size, size), (150, 150, 150))
    d = ImageDraw.Draw(im)
    for i in np.argsort(t[:, :, 2].mean(1)):
        if n[i, 2] <= 0:
            continue
        pts = [(size / 2 + p[0] * s, size / 2 - p[1] * s) for p in t[i]]
        col = tuple(int(v) for v in np.clip(rgb[i] * shade[i] * 255, 0, 255))
        d.polygon(pts, fill=col, outline=col)
    return im


def preview():
    z = np.load(OUT / "_lowpoly_cache.npz")
    cell = 300
    angles = [0, 45, 90, 135, 180, 225, 270, 315]
    sheet = Image.new("RGB", (cell * len(angles), cell * 2), "white")
    refs = {a: n for n, a in VIEW_YAW.items()}
    for j, ang in enumerate(angles):
        if ang in refs and (OUT / "inputs" / f"{refs[ang]}.png").exists():
            sheet.paste(Image.open(OUT / "inputs" / f"{refs[ang]}.png").resize((cell, cell)), (j * cell, 0))
        sheet.paste(_render(z["tri"], z["rgb"], z["n"], ang).resize((cell, cell)), (j * cell, cell))
    sheet.save(OUT / "preview.png")
    print(f"preview: -> {OUT / 'preview.png'}  (top: inputs, bottom: model at {angles})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--from", dest="start", choices=STAGES, default="prep")
    ap.add_argument("--only", choices=STAGES)
    ap.add_argument("--faces", type=int, default=3500)
    ap.add_argument("--colors", type=int, default=16)
    ap.add_argument("--face-subdiv", type=int, default=2)
    ap.add_argument("--clip-bottom", type=float, default=0.03)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    run = [args.only] if args.only else STAGES[STAGES.index(args.start):]
    OUT.mkdir(exist_ok=True)
    if "prep" in run:
        prep()
    if "generate" in run:
        generate(dict(seed=args.seed, texture_size=1024, mesh_simplify=0.95))
    if "lowpoly" in run:
        lowpoly(args.faces, args.colors, args.clip_bottom, args.face_subdiv)
    if "preview" in run:
        preview()


if __name__ == "__main__":
    main()
