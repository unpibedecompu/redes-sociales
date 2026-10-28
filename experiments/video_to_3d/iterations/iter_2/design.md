# Iteration 2 — design

## Hypothesis
Review rec 1 + 2: use `multiimage_algo: "multidiffusion"` and add the in-between views 45/135/225/315 (8 views, all
preprocessed), so the back/side texture stops being dark and the uncovered 45°/135° silhouettes improve.

## Key finding: multi-image mode was never active (bug, now fixed)
The first run of this config gave metrics identical to iter_1 to 3 decimals (IoU 0.814 vs 0.815, same colour diffs),
even with 8 views and a different algorithm. Reading the Space's `app.py` showed why: `generate_and_extract_glb`
takes an `is_multiimage` flag. The flag lives in a `gr.State(False)` that only flips when the UI's "Multiple Images" tab
is selected. Over the API it stays False, so the Space **ignores `multiimages` and runs single-image TRELLIS on the
primary (front) image**. That applies to **every earlier TRELLIS run, iter_1 included**. iter_1's "dark back" was simply
TRELLIS hallucinating the back from the front view. Neither `preprocess_all` nor the angle remap affected the texture.

**Code change:** `scripts/generate.py` has a new optional config key `"force_multiimage": true` (trellis only, default
false = old behaviour). It calls the tab-select handler `/lambda_1` in the same client session before generating, which
sets `is_multiimage=True`. The single-image run is kept in `run_a_single_image_bug/` as a control.

## Config (`config.json`)
trellis · views front 0, fr45 45, right 90, br135 135, back 180, bl225 225, left 270, fl315 315 · crop_pad 0.08 ·
input 1024 · preprocess_all · **force_multiimage** · seed 0 · **multidiffusion** · ss/slat steps 25 · tex 2048 ·
mesh_simplify 0.95 (default).

## Result
- Generation 118 s (1 run with the fix; the control run took 99 s).
- **Mean IoU 0.761** (iter_1 0.815). Per-angle IoU / colour diff:
  0°: 0.778/30.3 · 45°: 0.691/30.5 · 90°: 0.723/41.9 · 135°: 0.692/53.8 · 180°: 0.802/53.6 · 225°: 0.787/47.8 ·
  270°: 0.791/48.9 · 315°: 0.823/43.7.
- Colour diff fell at every back/side angle (180°: 67.7 → 53.6, 225°: 64.0 → 47.8, 270°: 61.6 → 48.9, 315°: 59.1 → 43.7)
  and at the front (39.1 → 30.3). It rose at 90° (29.2 → 41.9).
- Visual: the **back now shows a clear purple/white plaid** where iter_1 was near-black. The hue moved from navy toward
  purple. The face is sharper (brows and eyes visible). The back is still darker and more saturated than the target.
- **Why IoU fell:** the mesh now includes **jeans/upper legs below the shirt hem** (visible at every angle). The video
  cuts off at the hips, so the model is taller and render.py's fit scales it smaller, which costs IoU everywhere.
  The 0° figure is also narrower than the target. So the IoU drop is mostly framing/extent, not worse texture.

## Known issues / next steps
- **Leg extension:** clip the mesh below the target's hem line (post-process in generate.py), or make render.py fit
  the model's top portion to the target bbox. Either should recover IoU without losing the texture gain.
- Back/sides still darker and more saturated than the target. Possible fixes: brighten input frames, or adjust the
  texture's colour in post-processing.
- Check whether 8 views over-constrain multidiffusion. A 4-view multidiffusion run with force_multiimage would isolate
  the effect of the extra views (not run here to save quota).
- 90° profile is thin/flat (IoU 0.723) and its colour diff worsened.
