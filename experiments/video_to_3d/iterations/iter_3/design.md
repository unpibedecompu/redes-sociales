# Iteration 3: design

## Hypothesis
iter_2 review brief:
- **Rec 1:** clip the mesh where the video frame ends.
- **Rec 2:** fix the dark falloff from front to back that is baked into the texture.
- **Rec 3:** run a 4-view vs 8-view ablation with force_multiimage.

Rec 3 needed a new generation, but none was possible. This iteration therefore tests recs 1 and 2 as mesh/texture
post-processing, applied to the iter_2 raw model (same geometry, same seed).

## Generation attempts (all failed, so no new model this iteration)
- **TRELLIS, 4 views (rec 3).** Config `config_trellis_4view_quota_failed.json`: 0/90/180/270, multidiffusion,
  force_multiimage, 25/25 steps, tex 2048. It failed twice with `ZeroGPU quota exceeded (120s requested vs. 166s
  left). Try again in 23:42`. Logs are `generate_trellis_quota*.log`. The quota was already used up when this
  iteration started.
- **Hunyuan3D-2mv fallback** (`hunyuan_failed/`). It failed with `PyMeshLabException`, the same error as in iter_1.

**The 4-view vs 8-view ablation is still open.** It is the first thing to run once the quota resets (about 24 h).
Its config is ready to use and already includes the new `post` block.

## Code change (`scripts/generate.py`, backwards compatible)
- New optional config key `"post"`. When it is present, the raw Space output is saved as `model_raw.glb`, and
  `model.glb` becomes the processed result. That is the file `render.py` and `_render.glb` read.
  - `clip_bottom_frac`: a horizontal plane cut that removes the bottom fraction of the mesh height. It uses
    `trimesh.slice_plane`, which keeps the UVs, and leaves the cut uncapped.
  - `tex_gamma_front` / `tex_gamma_back`: an sRGB gamma lift on the baked texture. It blends per texel by
    w = (1 − n_z)/2, so the front is 0, the sides 0.5 and the back 1. Each face normal is rasterised into UV space,
    then blurred over a 3 px radius.
  - `tex_gain` and `tex_sat`: a brightness multiplier and a saturation factor, applied after the gamma lift.
- New CLI flag: `generate.py <config> --post-only` re-runs only the post-process on `model_raw.glb`. It makes no
  Space call and uses no quota.

## Config (`config.json`)
- Source: `model_raw.glb` = `iter_2/model.glb` (TRELLIS, 8 views, multidiffusion, force_multiimage).
- Post-process: `clip_bottom_frac 0.17`, `tex_gamma_front 1.45`, `tex_gamma_back 2.0`, `tex_sat 0.85`.

## Result
The post-process runs in seconds. Mesh faces: 6890 → 5170 after the clip.

| angle | iter_2 IoU / col | clip only IoU / col | **iter_3 (clip + texture) IoU / col** |
|---|---|---|---|
| 0 | 0.778 / 30.3 | 0.924 / 31.9 | **0.904 / 2.5** |
| 45 | 0.691 / 30.5 | 0.756 / 29.5 | **0.744 / 6.8** |
| 90 | 0.723 / 41.9 | 0.763 / 39.6 | **0.745 / 3.5** |
| 135 | 0.692 / 53.8 | 0.704 / 52.1 | **0.690 / 2.7** |
| 180 | 0.802 / 53.6 | 0.913 / 51.8 | **0.891 / 1.3** |
| 225 | 0.787 / 47.8 | 0.894 / 45.1 | **0.880 / 1.8** |
| 270 | 0.791 / 48.9 | 0.870 / 45.2 | **0.855 / 3.1** |
| 315 | 0.823 / 43.7 | 0.824 / 42.4 | **0.816 / 6.2** |
| **mean** | **0.761** | **0.831** | **0.816** |

- **The clip works.** Mean IoU went from 0.761 to 0.831. The model now ends at the hem/hips like the video, and the
  jeans stub is gone. The reviewer's upper bound (0.865) assumed a cut tuned per angle; a single 17% cut gives 0.831.
- **The texture is fixed in mean colour.** Subject mean RGB at 180° went from (29,25,32) to (80,72,83); the target is
  (83,74,86). At 0° it went from (64,48,56) to (99,80,88); the target is (102,79,87). The back and the front are now
  equally bright relative to the target. Visually, the back plaid is lavender/grey-white instead of violet-black, and
  the hair and beard are dark brown instead of pure black.
- **Why IoU drops from 0.831 to 0.816 after brightening: this is an artefact of the metric.** `render.py` keys the
  render against the grey background (154,154,154) with a threshold of 6. The lifted grey-white plaid bands now fall
  inside that key, so they show up as holes in the render mask. Filling the holes (`binary_fill_holes`) gives back
  about 0.02 at 0° (0.906 → 0.929) and at 180° (0.890 → 0.912). The geometry is identical to the clip-only run.
- **The colour-diff numbers are partly fitted.** I chose the 3 texture parameters by comparing per-angle subject means
  against the target over 2 calibration renders. A colour diff of about 1–7 therefore overstates fidelity. Judge the
  texture visually: plaid contrast, hue, and how the face looks.

## Known issues
- The 45°, 90° and 135° silhouettes are still the weakest (0.69–0.75). The profile is thin and flat. This is a
  geometry problem, so post-processing cannot fix it; the 4-view ablation is meant to test it.
- Contrast is still slightly above the target: subject luminance std is 54 against 49 at 0°. The skin is pale and
  greyish, not warm tan. The gamma lift also desaturates the skin.
- The cut at the hem is left open (no cap). It is visible only from below.
- To make IoU fair to lighter textures, `render.py` could fill holes in `render_mask`, or render on a background
  colour the model doesn't use. I didn't change it here because the metric belongs to the reviewer.
- Next generation, once the quota is available: run `config_trellis_4view_quota_failed.json` as is. Its `post` only
  clips; add the texture keys from `config.json`, or rerun `--post-only`. Then compare its 90° and 135° IoU with this
  iteration.

## Orchestrator note (harness fix after this iteration)
render.py now renders on a green screen (0,255,0) instead of grey, so bright plaid is no longer keyed out as background.
All iterations were re-scored with the same harness: iter_1 0.809, iter_2 0.754, **iter_3 0.828**.
