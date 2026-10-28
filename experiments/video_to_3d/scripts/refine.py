"""Local (no GPU quota) refinement ops that use the target video directly.

fit_silhouette(mesh, cfg)   deforms the mesh so its outline matches the video masks at many angles.
    For every height slice and view direction the target "support" (how far the outline reaches) is read off the
    calibrated video masks and compared with the mesh's own; vertices are scaled radially about the slice centre
    by the smoothed ratio. cfg: {"iters": 2, "strength": 0.7, "y_bins": 40, "theta_bins": 36,
    "clamp": [0.85, 1.2], "smooth_y": 1.5, "smooth_theta": 2.0, "head_frac": 0.0, "angles_step": 10}
    head_frac > 0 freezes the top fraction of the mesh (e.g. 0.2 keeps the head untouched).

project_texture(mesh, cfg)  paints colours from the video frames onto the texture.
    Each texel is located in 3D, projected into every calibrated frame where it is visible, and frame colours are
    blended with weight (facing ratio)^power. cfg: {"angles_step": 10, "power": 3, "mix": 1.0, "min_weight": 0.15,
    "edge_erode": 2, "region": "all"|"cloth"|"skin_hair", "both_halves": true}
    mix < 1 blends with the existing texture; region limits which texels get replaced.
    Optional "head_frac" (e.g. 0.22): region split by height (above = head) + strict skin-tone test for hands,
    instead of the colour-only test (which also kept the red tee and dark plaid stripes as "skin").
    Optional "register_passes" (iter_6, e.g. 1-2): after a first projection, each frame is re-sampled through a dense
    optical flow from a render of the current texture to that frame (fixes few-px mesh-vs-video misalignment, so
    frames agree before blending). Knobs "reg_winsize" (15), "reg_max" px (6), "reg_smooth" sigma px (3).
    Optional "select": "blend" (default, weighted average) | "max" (winner-take-all: best-facing frame per texel).
    Optional "lowpass_sigma" (texels, e.g. 6): detail transfer - keep only the low frequencies of the projection
    and add the generated texture's high frequencies (scaled by "detail_gain", default 1).
    Optional "sharpen" (unsharp amount, e.g. 0.6) and "sharpen_sigma" (texels, default 1.5) on projected texels.

set_unlit(glb_path)  marks materials KHR_materials_unlit, so the renderer shows the baked video colours as-is.
"""
import json

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage

from camera import calibrate, frame_rgb_and_mask, project, view_rotation
from common import angle_to_time


def _angles(step):
    return [float(a) for a in np.arange(0, 360, step)]


# ---------------------------------------------------------------- silhouette fit
def _supports(points_xz, dirs):
    return (points_xz @ dirs.T).max(0) if len(points_xz) else np.full(len(dirs), np.nan)


def _target_extents(mask, cam, y_edges):
    """World-space left/right outline extents of the mask for each height bin (nan where not observed)."""
    s, tx, ty, _ = cam
    H, W = mask.shape
    out = np.full((len(y_edges) - 1, 2), np.nan)
    for i in range(len(y_edges) - 1):
        # world y -> image rows (v = -s*y + ty)
        v0, v1 = int(np.floor(-s * y_edges[i + 1] + ty)), int(np.ceil(-s * y_edges[i] + ty))
        v0, v1 = max(v0, 0), min(v1, H - 3)            # never trust rows touching the frame bottom
        if v1 <= v0:
            continue
        cols = np.where(mask[v0:v1].any(0))[0]
        if len(cols) < 2:
            continue
        out[i] = [(cols.min() - tx) / s, (cols.max() + 1 - tx) / s]
    return out


def fit_silhouette(mesh, cfg, log=print):
    iters = cfg.get("iters", 2)
    strength = cfg.get("strength", 0.7)
    nyb, ntb = cfg.get("y_bins", 40), cfg.get("theta_bins", 36)
    lo, hi = cfg.get("clamp", [0.85, 1.2])
    head_frac = cfg.get("head_frac", 0.0)
    angles = _angles(cfg.get("angles_step", 10))
    faces = mesh.faces
    for it in range(iters):
        v = mesh.vertices.copy()
        calib = calibrate(v, faces, angles)
        y0, y1 = v[:, 1].min(), v[:, 1].max()
        edges = np.linspace(y0, y1, nyb + 1)
        ybin = np.clip(np.digitize(v[:, 1], edges) - 1, 0, nyb - 1)
        centres = np.array([v[ybin == i][:, [0, 2]].mean(0) if (ybin == i).any() else [0, 0] for i in range(nyb)])
        ratio_sum = np.zeros((nyb, ntb))
        ratio_w = np.zeros((nyb, ntb))
        for a, c in calib.items():
            R = view_rotation(a, c["cam"][3])
            right = R.T @ np.array([1.0, 0, 0])          # model-space direction that maps to image +x
            d2 = np.array([right[0], right[2]])
            d2 /= np.linalg.norm(d2)
            _, mask = frame_rgb_and_mask(c["t"])
            tgt = _target_extents(mask, c["cam"], edges)
            for i in range(nyb):
                pts = v[ybin == i][:, [0, 2]]
                if len(pts) < 3 or np.isnan(tgt[i]).any():
                    continue
                cc = centres[i]
                for sign, t_ext in ((1, tgt[i, 1]), (-1, -tgt[i, 0])):
                    d = sign * d2
                    hm = (pts @ d).max() - cc @ d
                    ht = t_ext - cc @ d
                    if hm <= 1e-4 or ht <= 1e-4:
                        continue
                    th = int(((np.degrees(np.arctan2(d[1], d[0])) % 360) / 360) * ntb) % ntb
                    ratio_sum[i, th] += np.clip(ht / hm, lo, hi)
                    ratio_w[i, th] += 1
        ratio = np.where(ratio_w > 0, ratio_sum / np.maximum(ratio_w, 1), np.nan)
        filled = np.where(np.isnan(ratio), 1.0, ratio)
        wts = (~np.isnan(ratio)).astype(float)
        sy, st = cfg.get("smooth_y", 1.5), cfg.get("smooth_theta", 2.0)
        num = ndimage.gaussian_filter(filled * wts, (sy, st), mode=("nearest", "wrap"))
        den = ndimage.gaussian_filter(wts, (sy, st), mode=("nearest", "wrap"))
        ratio = np.where(den > 1e-3, num / np.maximum(den, 1e-3), 1.0)
        # per-vertex lookup (bilinear in y, nearest in theta)
        rel = v[:, [0, 2]] - centres[ybin]
        th = ((np.degrees(np.arctan2(rel[:, 1], rel[:, 0])) % 360) / 360 * ntb).astype(int) % ntb
        f = ratio[ybin, th]
        f = 1 + strength * (f - 1)
        if head_frac > 0:
            ycut = y1 - head_frac * (y1 - y0)
            ramp = np.clip((ycut - v[:, 1]) / (0.04 * (y1 - y0)), 0, 1)
            f = 1 + ramp * (f - 1)
        v[:, [0, 2]] = centres[ybin] + rel * f[:, None]
        mesh.vertices = v
        ious = [c["iou"] for c in calib.values()]
        log(f"fit_silhouette iter {it + 1}: {len(calib)} frames, calib IoU before {np.mean(ious):.3f}, "
            f"vertex scale range {f.min():.3f}..{f.max():.3f}")
    return mesh


# ---------------------------------------------------------------- texture projection
def _uv_face_map(mesh, size):
    """Texel -> face index (-1 where no face) plus barycentric coordinates, rasterised in UV space."""
    W, H = size
    uv = mesh.visual.uv
    pix = np.stack([uv[:, 0] * W, (1 - uv[:, 1]) * H], 1)
    fid = np.full((H, W), -1, np.int32)
    idimg = np.zeros((H, W, 3), np.uint8)
    for i, f in enumerate(mesh.faces):
        j = int(i) + 1
        col = (j & 255, (j >> 8) & 255, (j >> 16) & 255)
        cv2.fillConvexPoly(idimg, np.round(pix[f] * 4).astype(np.int32), col, lineType=cv2.LINE_8, shift=2)
    ids = idimg[..., 0].astype(np.int32) | (idimg[..., 1].astype(np.int32) << 8) | (idimg[..., 2].astype(np.int32) << 16)
    fid = ids - 1
    yy, xx = np.nonzero(fid >= 0)
    f = fid[yy, xx]
    tri = pix[mesh.faces[f]]                                # (n,3,2)
    p = np.stack([xx + 0.5, yy + 0.5], 1)
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    d = (v1[:, 1] - v2[:, 1]) * (v0[:, 0] - v2[:, 0]) + (v2[:, 0] - v1[:, 0]) * (v0[:, 1] - v2[:, 1])
    d = np.where(np.abs(d) < 1e-12, 1e-12, d)
    b0 = ((v1[:, 1] - v2[:, 1]) * (p[:, 0] - v2[:, 0]) + (v2[:, 0] - v1[:, 0]) * (p[:, 1] - v2[:, 1])) / d
    b1 = ((v2[:, 1] - v0[:, 1]) * (p[:, 0] - v2[:, 0]) + (v0[:, 0] - v2[:, 0]) * (p[:, 1] - v2[:, 1])) / d
    bary = np.clip(np.stack([b0, b1, 1 - b0 - b1], 1), 0, 1)
    bary /= bary.sum(1, keepdims=True)
    return yy, xx, f, bary


def _face_id_buffer(verts, faces, angle, cam, shape):
    """Painter's-algorithm visibility: which face is frontmost at each video pixel."""
    uv, z = project(verts, angle, cam)
    order = np.argsort(z[faces].mean(1))                  # far (small z) first, camera looks down -z
    img = np.zeros((*shape, 3), np.uint8)
    pts = np.round(uv[faces] * 4).astype(np.int32)
    for i in order:
        j = int(i) + 1
        col = (j & 255, (j >> 8) & 255, (j >> 16) & 255)
        cv2.fillConvexPoly(img, pts[i], col, lineType=cv2.LINE_8, shift=2)
    return (img[..., 0].astype(np.int32) | (img[..., 1].astype(np.int32) << 8) | (img[..., 2].astype(np.int32) << 16)) - 1


def _bilinear(img, u, v):
    H, W = img.shape[:2]
    u = np.clip(u - 0.5, 0, W - 1.001)
    v = np.clip(v - 0.5, 0, H - 1.001)
    x0, y0 = u.astype(int), v.astype(int)
    fx, fy = (u - x0)[:, None], (v - y0)[:, None]
    a = img[y0, x0] * (1 - fx) + img[y0, x0 + 1] * fx
    b = img[y0 + 1, x0] * (1 - fx) + img[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def _register_flow(ref, uvt, verts, faces, angle, cam, fb, rgb, mask, cfg):
    """Dense optical flow (pixels) from a render of texture `ref` in this frame's camera to the video frame.
    flow[y, x] = displacement so that render(y, x) ~ frame(y + fy, x + fx); clipped and smoothed."""
    Ht, Wt = ref.shape[:2]
    puv, _ = project(verts, angle, cam)
    ys, xs = np.nonzero(fb >= 0)
    fid = fb[ys, xs]
    tri = puv[faces[fid]]
    p = np.stack([xs + 0.5, ys + 0.5], 1)
    v0, v1, v2 = tri[:, 0], tri[:, 1], tri[:, 2]
    d = (v1[:, 1] - v2[:, 1]) * (v0[:, 0] - v2[:, 0]) + (v2[:, 0] - v1[:, 0]) * (v0[:, 1] - v2[:, 1])
    d = np.where(np.abs(d) < 1e-9, 1e-9, d)
    b0 = ((v1[:, 1] - v2[:, 1]) * (p[:, 0] - v2[:, 0]) + (v2[:, 0] - v1[:, 0]) * (p[:, 1] - v2[:, 1])) / d
    b1 = ((v2[:, 1] - v0[:, 1]) * (p[:, 0] - v2[:, 0]) + (v0[:, 0] - v2[:, 0]) * (p[:, 1] - v2[:, 1])) / d
    bary = np.clip(np.stack([b0, b1, 1 - b0 - b1], 1), 0, 1)
    bary /= np.maximum(bary.sum(1, keepdims=True), 1e-9)
    tc = (uvt[faces[fid]] * bary[:, :, None]).sum(1)
    col = _bilinear(ref, tc[:, 0] * Wt, (1 - tc[:, 1]) * Ht)
    rend = rgb.astype(np.float32).copy()
    rend[ys, xs] = col
    g_r = cv2.cvtColor(np.clip(rend, 0, 255).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    g_f = cv2.cvtColor(rgb.astype(np.uint8), cv2.COLOR_RGB2GRAY)
    flow = cv2.calcOpticalFlowFarneback(g_r, g_f, None, 0.5, 3, cfg.get("reg_winsize", 15), 3, 5, 1.2, 0)
    mx = cfg.get("reg_max", 6.0)
    mag = np.linalg.norm(flow, axis=2, keepdims=True)
    flow = flow * np.minimum(1.0, mx / np.maximum(mag, 1e-6))
    sg = cfg.get("reg_smooth", 3.0)
    if sg:
        valid = (fb >= 0).astype(np.float32)
        den = np.maximum(cv2.GaussianBlur(valid, (0, 0), sg), 1e-4)
        flow = np.stack([cv2.GaussianBlur(flow[..., k] * valid, (0, 0), sg) / den for k in range(2)], 2)
    flow[fb < 0] = 0
    return flow.astype(np.float32)


def _hsv01(rgb):
    hsv = cv2.cvtColor(np.clip(rgb, 0, 255).astype(np.uint8), cv2.COLOR_RGB2HSV_FULL).astype(np.float32)
    return hsv[..., 0] * 360 / 256, hsv[..., 1] / 255, hsv[..., 2] / 255


def _pixel_classes(rgb, mask, cfg):
    """Image-space classes of a video frame (iter_7): red tee, skin, dark (hair/beard), plaid (purple/white)."""
    h, s, v = _hsv01(rgb)
    tee = ((h < 20) | (h > 340)) & (s > 0.45) & (v > 0.2) & mask
    skin = (h >= 8) & (h <= 45) & (s > 0.18) & (s < 0.65) & (v > 0.35) & mask & ~tee
    plaid = (((h >= 220) & (h <= 330) & (s > 0.10)) | ((s < 0.15) & (v > 0.5))) & mask & ~tee & ~skin
    dark = (v < cfg.get("dark_v", 0.30)) & mask & ~tee & ~plaid
    d = cfg.get("gate_dilate", 3)
    k = np.ones((3, 3), np.uint8)
    dil = lambda m, n: cv2.dilate(m.astype(np.uint8), k, iterations=n).astype(bool) if n else m
    return {"tee": tee, "skin": skin, "plaid": plaid, "dark": dark, "teeD": dil(tee, d), "skinD": dil(skin, d),
            "skinH": dil(skin, cfg.get("hair_dilate", 2)), "darkD": dil(dark, cfg.get("dark_dilate", 0))}


def _texel_classes(tex_c, P, verts, cfg):
    """Classes of texels from the generated texture (iter_7): 0 cloth, 1 tee, 2 head skin, 3 head dark (hair/beard),
    4 hand skin. Head = above head_frac (geometric)."""
    h, s, v = _hsv01(tex_c[None])
    h, s, v = h[0], s[0], v[0]
    y0, y1 = verts[:, 1].min(), verts[:, 1].max()
    head = P[:, 1] > y1 - cfg.get("head_frac", 0.24) * (y1 - y0)
    tee = ((h < 20) | (h > 340)) & (s > 0.45) & (v > 0.2) & ~head
    skin = (h >= 8) & (h <= 50) & (s > 0.15) & (v > 0.3)
    cls = np.zeros(len(P), np.int8)
    cls[tee] = 1
    cls[head] = 2
    cls[head & (v < cfg.get("tex_dark_v", 0.30))] = 3
    cls[~head & ~tee & skin] = 4
    nb = cfg.get("neck_band", 0.0)
    if nb:
        neck = ~head & (P[:, 1] > y1 - (cfg.get("head_frac", 0.24) + nb) * (y1 - y0)) & ~tee
        cls[neck] = 5
    return cls, head


def _gate(cls, pc, vi, ui, cfg, vote=None):
    """Per-texel accept/reject of the frame pixel it samples, by class compatibility."""
    g = {k: m[vi, ui] for k, m in pc.items()}
    ok = np.ones(len(cls), bool)
    c = cls == 0
    ok[c] = ~(g["teeD"][c] | g["skinD"][c])
    c = cls == 1
    ok[c] = g["tee"][c]
    if not cfg.get("gate_head", True):
        return ok
    c = cls == 2
    r = g["teeD"] | g["plaid"]
    if cfg.get("skin_reject_dark"):
        r = r | g["darkD"]
    ok[c] = ~r[c]
    c = cls == 3
    ok[c] = g["dark"][c] if cfg.get("dark_only") else ~(g["skinH"] | g["teeD"] | g["plaid"])[c]
    c = cls == 4
    ok[c] = ~(g["teeD"] | g["plaid"])[c]
    c = cls == 5
    ok[c] = ~g["teeD"][c]
    if vote is not None:
        # majority vote (iter_7): head/neck texels whose samples are mostly dark (beard/hair) drop skin samples and
        # vice versa, so the beard edge follows the video consensus instead of blending into a tan band
        fd = vote
        th = cfg.get("vote_thresh", 0.6)
        hv = (cls == 2) | (cls == 3) | (cls == 5)
        ok[hv & (fd > th)] &= ~g["skinH"][hv & (fd > th)]
        ok[hv & (fd < 1 - th)] &= ~g["dark"][hv & (fd < 1 - th)]
    return ok


def project_texture(mesh, cfg, log=print, out_dir=None):
    power = cfg.get("power", 3)
    mix = cfg.get("mix", 1.0)
    min_w = cfg.get("min_weight", 0.15)
    erode = cfg.get("edge_erode", 2)
    region = cfg.get("region", "all")
    angles = _angles(cfg.get("angles_step", 10))
    mat = mesh.visual.material
    tex = np.asarray(mat.baseColorTexture.convert("RGB")).astype(np.float32)
    H, W = tex.shape[:2]
    verts, faces = mesh.vertices, mesh.faces
    calib = calibrate(verts, faces, angles)
    yy, xx, f, bary = _uv_face_map(mesh, (W, H))
    P = (verts[faces[f]] * bary[:, :, None]).sum(1)          # texel 3D positions
    N = mesh.face_normals[f]
    gate = cfg.get("class_gate", False)
    cls, headm = _texel_classes(tex[yy, xx], P, verts, cfg)
    pw = np.where(headm, cfg.get("head_power", power), power)
    mw = np.where(headm, cfg.get("head_min_weight", min_w), min_w)
    if out_dir is not None:
        pal = np.array([[120, 80, 160], [220, 30, 30], [230, 180, 140], [30, 30, 30], [60, 200, 60], [60, 160, 230]], np.uint8)
        ci = np.zeros((H, W, 3), np.uint8)
        ci[yy, xx] = pal[cls]
        Image.fromarray(ci).save(out_dir / "texel_classes_uv.png")
    # region mask (does not depend on the projection)
    rmask = np.ones(len(f))
    if region != "all":
        c0 = tex[yy, xx] / 255.0
        mx, mn = c0.max(1), c0.min(1)
        skinlike = (c0[:, 0] >= c0[:, 1]) & (c0[:, 1] >= c0[:, 2] * 0.9) & ((mx - mn) / np.maximum(mx, 1e-6) > 0.12)
        dark = mx < 0.25
        sk = skinlike | dark
        hf = cfg.get("head_frac")
        if hf is not None:
            # geometric head split (iter_5): everything above the neck line counts as skin/hair; below it only
            # real skin tones (excludes the red tee, g/r ~0.3, and dark plaid stripes, which the old test kept)
            y0, y1 = verts[:, 1].min(), verts[:, 1].max()
            head = P[:, 1] > y1 - hf * (y1 - y0)
            skin_tone = skinlike & (c0[:, 1] >= 0.5 * c0[:, 0]) & (mx > 0.25)
            sk = head | skin_tone
        rmask = ((~sk) if region == "cloth" else sk).astype(float)
    select = cfg.get("select", "blend")
    n_reg = cfg.get("register_passes", 0)
    uvt = mesh.visual.uv
    # frame list (with cameras) is fixed across passes
    frames = []
    for a, c in calib.items():
        ts = [c["t"]]
        if cfg.get("both_halves", True) and a <= 180:
            # the first half also passes this angle on the way back (ping-pong), use that frame as well
            t2 = 10.0 - c["t"] * (10.0 - 6.5) / 6.5 if c["t"] > 0 else None
            if t2 is not None and abs(t2 - c["t"]) > 0.3:
                ts.append(t2)
        for t in ts:
            cam = c["cam"]
            if t != c["t"]:          # re-fit the camera for the extra frame, warm-started
                from camera import fit_camera
                _, mask = frame_rgb_and_mask(t)
                cam, sc = fit_camera(verts, faces, a, mask, c["cam"])
                if sc < 0.75:
                    continue
            frames.append((a, t, cam))
    ref = None
    flow_stats = []
    lev = cfg.get("levels", 0.0)
    samples = []
    vote_prev = None
    for p_i in range(n_reg + 1):
        acc = np.zeros((len(f), 3))
        wsum = np.zeros(len(f))
        wd = np.zeros(len(f))
        wsk = np.zeros(len(f))
        wbest = np.zeros(len(f))
        cbest = np.zeros((len(f), 3))
        times = []
        mags = []
        for a, t, cam in frames:
            rgb, mask = frame_rgb_and_mask(t)
            m = ndimage.binary_erosion(mask, iterations=erode) if erode else mask
            fb = _face_id_buffer(verts, faces, a, cam, mask.shape)
            R = view_rotation(a, cam[3])
            uv, _ = project(P, a, cam)
            if ref is not None:
                # register (iter_6): render the current consensus texture into this frame's camera, then
                # optical flow render -> frame; sample the frame at uv + flow (fixes few-px misalignment)
                flow = _register_flow(ref, uvt, verts, faces, a, cam, fb, rgb, mask, cfg)
                fu = _bilinear(flow, uv[:, 0], uv[:, 1])
                uv = uv + fu
                mags.append(float(np.median(np.linalg.norm(flow[fb >= 0], axis=1))))
            nz = (N @ R.T)[:, 2]
            ui0 = np.clip((uv[:, 0]).astype(int), 0, mask.shape[1] - 1)
            vi0 = np.clip((uv[:, 1]).astype(int), 0, mask.shape[0] - 1)
            uvn, _ = project(P, a, cam)          # visibility tested at the unwarped position
            ui = np.clip(uvn[:, 0].astype(int), 0, mask.shape[1] - 1)
            vi = np.clip(uvn[:, 1].astype(int), 0, mask.shape[0] - 1)
            vis = np.zeros(len(f), bool)
            for du in (-1, 0, 1):
                for dv in (-1, 0, 1):
                    vis |= fb[np.clip(vi + dv, 0, mask.shape[0] - 1), np.clip(ui + du, 0, mask.shape[1] - 1)] == f
            ok = vis & (nz > 0.05) & m[vi0, ui0]
            if gate:
                pc = _pixel_classes(rgb, mask, cfg)
                ok &= _gate(cls, pc, vi0, ui0, cfg, vote_prev)
            w = np.where(ok, np.clip(nz, 0, 1) ** pw, 0.0)
            if gate:
                wd += w * pc["dark"][vi0, ui0]
                wsk += w * pc["skin"][vi0, ui0]
            col = _bilinear(rgb.astype(np.float32), uv[:, 0], uv[:, 1])
            if lev and p_i == n_reg:
                sel = ok & (cls == 0) & (nz > 0.7)
                samples.append(col[sel][:: max(1, sel.sum() // 4000)])
            acc += col * w[:, None]
            wsum += w
            better = w > wbest
            wbest[better] = w[better]
            cbest[better] = col[better]
            times.append(round(t, 2))
        if select == "max":
            proj = cbest
            alpha = np.clip(wbest / mw, 0, 1) * mix * rmask
        else:
            proj = acc / np.maximum(wsum, 1e-6)[:, None]
            alpha = np.clip(wsum / mw, 0, 1) * mix * rmask
        new = tex.copy()
        new[yy, xx] = tex[yy, xx] * (1 - alpha[:, None]) + proj * alpha[:, None]
        if mags:
            flow_stats.append(round(float(np.median(mags)), 2))
        ref = new
        if cfg.get("vote"):
            vote_prev = np.where(wd + wsk > 0, wd / np.maximum(wd + wsk, 1e-9), 0.5)
    med = cfg.get("head_median", 0)
    if med:
        # despeckle head texels (iter_7): median in UV space, only where projected
        mimg = cv2.medianBlur(np.clip(new, 0, 255).astype(np.uint8), med).astype(np.float32)
        sel = headm & (alpha > 0)
        new[yy[sel], xx[sel]] = mimg[yy[sel], xx[sel]]
    if lev and samples:
        # levels (iter_7): per-channel p_lo/p_hi of projected cloth texels -> those of single-frame video samples
        vs = np.concatenate(samples, 0)
        sel = (cls == 0) & (alpha > 0.5)
        cur = new[yy[sel], xx[sel]]
        lo_p, hi_p = cfg.get("levels_pct", [5, 95])
        a_lo, a_hi = np.percentile(cur, lo_p, 0), np.percentile(cur, hi_p, 0)
        b_lo, b_hi = np.percentile(vs, lo_p, 0), np.percentile(vs, hi_p, 0)
        mapped = (cur - a_lo) / np.maximum(a_hi - a_lo, 1) * (b_hi - b_lo) + b_lo
        new[yy[sel], xx[sel]] = cur + lev * (mapped - cur)
        log(f"project_texture: levels cloth p{lo_p}/p{hi_p} {a_lo.round().tolist()}/{a_hi.round().tolist()} -> "
            f"{b_lo.round().tolist()}/{b_hi.round().tolist()} (strength {lev})")
    ns = cfg.get("neck_shade", 0.0)
    if ns:
        # under-jaw shadow (iter_7): head skin texels whose normal faces down get darkened
        sel = headm & (cls == 2) & (N[:, 1] < 0)
        fac = 1 - ns * np.clip(-N[sel, 1], 0, 1)
        new[yy[sel], xx[sel]] *= fac[:, None]
    if flow_stats:
        log(f"project_texture: registration passes {n_reg}, median |flow| per pass {flow_stats} px")
    ls = cfg.get("lowpass_sigma", 0.0)
    if ls:
        # detail transfer (iter_6): low-frequency colour from the projection, high-frequency detail (plaid edges,
        # pockets) from the generated texture. Masked (normalised) blur so UV gutters don't leak in.
        valid = np.zeros((H, W), np.float32)
        valid[yy, xx] = 1.0
        den = np.maximum(cv2.GaussianBlur(valid, (0, 0), ls), 1e-4)[..., None]
        low = lambda img: cv2.GaussianBlur(img * valid[..., None], (0, 0), ls) / den
        gain = cfg.get("detail_gain", 1.0)
        dt = low(new) + gain * (tex - low(tex))
        a = np.clip(alpha, 0, 1)[:, None]
        new[yy, xx] = new[yy, xx] * (1 - a) + dt[yy, xx] * a
    amt = cfg.get("sharpen", 0.0)
    if amt:
        # unsharp mask on projected texels only (iter_5): counter the softness of multi-frame blending
        blur = cv2.GaussianBlur(new, (0, 0), cfg.get("sharpen_sigma", 1.5))
        sh = new + amt * (new - blur)
        a = np.clip(alpha, 0, 1)[:, None]
        new[yy, xx] = new[yy, xx] * (1 - a) + sh[yy, xx] * a
    # bleed projected colours a few texels into UV gutters to hide seams
    painted = np.zeros((H, W), bool)
    painted[yy, xx] = alpha > 0.5
    if painted.any():
        dil = cv2.dilate(new.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=2)
        gutter = np.ones((H, W), bool)
        gutter[yy, xx] = False
        new[gutter] = dil[gutter]
    mat.baseColorTexture = Image.fromarray(np.clip(new, 0, 255).astype(np.uint8))
    cov = float((alpha > 0.5).mean())
    log(f"project_texture: {len(times)} frames, {cov:.1%} of texels replaced (region={region}, mix={mix}, power={power})")
    if out_dir is not None:
        cov_img = np.zeros((H, W), np.uint8)
        cov_img[yy, xx] = (np.clip(alpha, 0, 1) * 255).astype(np.uint8)
        Image.fromarray(cov_img).save(out_dir / "projection_coverage_uv.png")
    return mesh


def set_unlit(glb_path):
    from pygltflib import GLTF2
    g = GLTF2().load(str(glb_path))
    for m in g.materials:
        m.extensions = dict(m.extensions or {})
        m.extensions["KHR_materials_unlit"] = {}
    g.extensionsUsed = sorted(set((g.extensionsUsed or []) + ["KHR_materials_unlit"]))
    g.save(str(glb_path))
