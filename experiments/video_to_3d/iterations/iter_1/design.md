# Iteration 1 — design (NO MODEL PRODUCED)

## Hypothesis
Smoke test (trellis, default params, views 0/90/180/270): IoU ~0.70, dark/near-black back and sides, blurry plaid.
I found two input bugs that likely explain the dark back/sides:
1. **Multi-images were sent with their grey background.** `run_trellis` only ran `/preprocess_image` on the primary
   image. The Space calls `run_multi_image(..., preprocess_image=False)`, so the other views reached TRELLIS
   unsegmented: a grey square instead of a black-background cutout. That corrupts the conditioning for every non-front view.
2. **The nominal angles were wrong.** The turntable is not linear (it was obvious once the preprocessed cutouts were laid side by side):
   "180°" (5 s) is a 3/4 back view and "270°" (7.5 s) is the actual back.
   Measured on a 4 fps sheet: front 0 s, profile ≈3.5 s, back ≈6.5 s, other profile ≈8.6 s. With 10 s/turn
   these are nominal angles **0 / 126 / 234 / 310**. This mapping also affects render.py's per-angle IoU comparison,
   which assumes linear rotation, so the reviewer should keep it in mind.

Planned fix: preprocess every view, use the true views, and raise texture_size to 2048 and sampling steps to 25 for sharper plaid.

## Code change
`scripts/generate.py`: new optional config key `"preprocess_all": true` (trellis only, default false = old
behaviour). It runs every multi-image through the Space's `/preprocess_image` and saves `inputs/pre_<view>.png`.
I checked that it works: all 4 cutouts came back clean (518x518, black background).

## Config
- Planned (`config_trellis_failed.json`): trellis, views {front:0, right:126, back:234, left:310}, preprocess_all,
  seed 0, stochastic, ss/slat steps 25, texture_size 2048.
- Fallback (`config.json`): hunyuan, `tencent/Hunyuan3D-2mv`, same views, steps 30, seed 42, octree 384.

## Result
**Generation failed on every backend, so no model.glb and no render.**
- TRELLIS: `ZeroGPU quota exceeded (120s requested vs. 163s left). Try again in ~23:53` (2 attempts; the
  `/preprocess_image` calls succeeded). No HF token is configured. Setting `HF_TOKEN` would raise the quota.
- Hunyuan3D-2mv `/generation_all`: `PyMeshLabException` (2 attempts, seeds 1234 and 42, octree 256 and 384).
- Hunyuan3D-2 (single-view Space): rejects multi-view input ("Please provide either a caption or an image").

## Known issues / next steps
- Rerun the planned trellis config as soon as quota is available, or after adding an HF token. That run tests the
  hypothesis directly.
- Hunyuan3D-2mv: `/shape_generation` (geometry only) may work where `/generation_all` fails. It is untested and would give no texture.

## Rerun after HF login (orchestrator)
- `config_trellis_failed.json` was re-mapped to the corrected angle keyframes (`scripts/common.py` ANGLE_KEYS: front 0, right 90 = 3.5 s, back 180 = 6.5 s, left 270 = 8.6 s) and run as `config.json`.
- TRELLIS succeeded in 77 s. Mean silhouette IoU **0.815**.
- Visible: geometry/proportions close; front plaid OK but bluer than target; back and 135°/225° views still very dark despite `preprocess_all`.
- render.py now renders from `_render.glb` (texture capped at 1024 px for headless Chrome); `model.glb` is untouched.
