# Design: iteration 5 (small-step loop, round 1)

## Brief
- iter_4 review: fix the skin (too dark/orange, target median ~(155,128,109)), the neck streaks, and the dark back cloth.
- Orchestrator: add silhouette fit + video projection. Smoke test showed projection gives real colours everywhere,
  BUT face/hands ghosted and plaid doubled. Fix that first (power, region, edge_erode, angles_step, mix).

## Tool changes (scripts/refine.py, additive, defaults unchanged)
- `project.head_frac`: region split by height (texels above `y_top - head_frac*height` = head) + a strict skin-tone
  test (g >= 0.5 r, not dark) for hands. The old colour-only test classed the **red tee** (r>=g>=0.9b) and, once
  the post gamma lift was removed, the **dark plaid stripes** (max<0.25) as "skin", so region "cloth" left them
  unprojected.
- `project.sharpen` / `sharpen_sigma`: unsharp mask on projected texels only.

## Step log
| step | change | mean IoU | kept? | what I saw |
|---|---|---|---|---|
| 1 | baseline: iter_4 post + fit (iters 2, str 0.7) | 0.849 | yes | = smoke test |
| 2 | + projection power 8, region all, unlit | 0.848 | no | face still ghosted/patchy - higher power doesn't help |
| 3 | region cloth | 0.849 | yes | generated face kept, but red tee faded (classified as skin), hair brown-grey |
| 4 | unlit off | 0.848 | no | everything double-shaded: shirt and face far too dark |
| 5 | region all, power 40 | 0.848 | no | face still patchwork: it's frame-to-frame misregistration, not blending (cos10°^8=0.89 but power 40 changes nothing) |
| 6 | post tex_gamma 1.45/2.0 -> 1.0 (from 3) | 0.848 | yes* | hair now black; but dark plaid stripes stopped being projected (47% coverage) -> led to step 7 |
| 7 | new head_frac 0.2 | 0.849 | yes | tee correct red, plaid lavender/white like the video, coverage 79% |
| 8 | head_frac 0.24 | 0.849 | yes | beard bottom no longer ghosted at 45/90 |
| 9 | skin_sat 0.8 | 0.849 | yes | skin hue right, ~8 levels dark |
| 10 | skin_gamma 1.1 | 0.849 | yes | skin median 0°: (156,129,109) vs target (156,126,104); 315°: (153,125,105) vs (159,130,104) |
| 11 | power 8 -> 20 | 0.848 | no | no sharper, coverage drops to 69% (min_weight) |
| 12 | edge_erode 2 -> 4 | 0.849 | yes | marginal, no harm |
| 13 | **sharpen 0.8 sigma 3 (new)** | **0.849** | **yes (final)** | plaid slightly crisper at 180, no halos |
| 14 | angles_step 10 -> 5 | 0.849 | no | not visibly different, 2x time |
| 15 | fit strength 0.85 | 0.848 | no | 225/315 unchanged (see issues) |
| 16 | fit iters 3 | 0.846 | no | worse at 0/135 |
| 17 | sharpen 1.3 | 0.000 | - | renderer returned empty images (flake), rerun as 18 |
| 18 | sharpen 1.3 | 0.849 | no | speckle + white streak halo at 45 |

Stopped after 4 non-improving steps (14-18). Final = step 13.

## Final recipe (iterations/iter_5/recipe.json)
- base iter_4/model_raw.glb; post = iter_4 but tex_gamma_front/back 1.0, skin_sat 0.8, skin_gamma 1.1
- fit {iters 2, strength 0.7, angles_step 10}
- project {power 8, mix 1, min_weight 0.15, edge_erode 4, region "cloth", head_frac 0.24, both_halves, angles_step 10,
  sharpen 0.8, sharpen_sigma 3}; unlit true
- mean IoU 0.849 (0: .939, 45: .844, 90: .894, 135: .824, 180: .900, 225: .778, 270: .846, 315: .763)

## Known issues
- **Face projection does not work** with the current camera alignment: any power gives a patchwork/ghosted face
  (misregistration between frames, ±a few px). So the face is the generated texture, which is blurry: no eyes
  visible, flat under unlit (no shading). Colour now matches the target, detail does not.
- Plaid is still softer than the video, especially at 270 (grazing sleeve) and 45; some doubled lines remain.
- Hands are the generated (pale tan, low-detail) ones; faint tan smears at cuff/hem at 0 and 180.
- 225/315 IoU (0.78/0.76) look limited by the harness, not geometry: the render at nominal 225 is more back-facing
  and at 315 more 3/4 than the target frames (the target's real yaw differs, dyaw). Fit strength/iters can't fix it.
- Renderer flake: occasionally returns empty images (step 17, and the first re-render after a `--revert`); rerun fixes it.
- IoU is flat (0.849) across all texture work; all gains this round are visual (colours).

## Orchestrator note (harness fixes after this round)
- The 8 scoring frames are now picked from an eye-verified angle table (common.py ANGLE_KEYS: 45→2.08 s, 90→3.5 s,
  135→5.58 s, 225→15.3 s, 270→13.67 s, 315→12.58 s), fixing the pose mismatch at 45/135/225/315 noted above.
- render.py now fails loudly when headless Chrome returns an empty render (no more silent IoU 0.0 steps).
- All iterations re-scored on this harness: iter_1 0.825, iter_2 0.747, iter_3 0.862, iter_4 0.897, **iter_5 0.901**.
  steps.jsonl values were logged on the old harness (relative deltas inside the log are still valid).
