# Review: iteration 2
**Overall score: 5.5/10** (best so far: 5.5/10 in iter 2; iter 1 was 4.5) · mean IoU: 0.761 (iter 1: 0.815)

Setup: TRELLIS with **force_multiimage** (the first run that is really multi-image), 8 preprocessed views at 0–315° in
45° steps, multidiffusion, 25/25 steps, tex 2048. Framing is correct: the front is at 0° and the back at 180°, so no `--yaw` is needed.

**The bug finding holds up.** The control `run_a_single_image_bug/` reproduces iter 1 almost exactly: per-angle IoU
0.888/0.724/0.772/0.716/0.876/0.863/0.856/0.813 against iter 1's 0.888/0.724/0.772/0.715/0.876/0.864/0.857/0.820, with the
same navy front and the same black back. Its GLB bytes differ from iter 1's, but the result is effectively identical, so iter 1 was single-image. The scores below are the first ones for a real multi-image model.

## Checking the claim that IoU fell because of the jeans
I tested this on the saved crops and did not rely on design.md. For each angle I removed the bottom k% of the render
mask, re-cropped it with the same `crop_square` rule and re-scored it against the target mask:

| angle | target h/w | iter1 h/w | iter2 h/w | iter1 IoU → best cut | iter2 IoU → best cut |
|---|---|---|---|---|---|
| 0 | 1.71 | 1.83 | 2.07 | 0.888 → 0.951 (6%) | 0.778 → 0.926 (18%) |
| 45 | 1.87 | 2.06 | 2.46 | 0.724 → 0.796 (18%) | 0.691 → 0.813 (26%) |
| 90 | 3.03 | 3.45 | 4.07 | 0.772 → 0.791 (8%) | 0.723 → 0.796 (18%) |
| 135 | 2.35 | 2.07 | 2.38 | 0.715 → 0.733 (6%) | 0.692 → 0.747 (24%) |
| 180 | 1.71 | 1.76 | 2.03 | 0.876 → 0.915 (6%) | 0.802 → 0.929 (14%) |
| 225 | 2.00 | 2.08 | 2.40 | 0.864 → 0.911 (8%) | 0.787 → 0.907 (16%) |
| 270 | 3.45 | 3.45 | 4.00 | 0.857 → 0.904 (6%) | 0.791 → 0.931 (18%) |
| 315 | 2.34 | 2.08 | 2.36 | 0.820 → 0.826 (2%) | 0.823 → 0.874 (6%) |
| **mean** | | | | **0.815 → 0.853** | **0.761 → 0.865** |

**Verdict: mostly true, with two corrections.**
- Extra height below the hips explains the IoU drop. The iter 2 render is 15–20% taller relative to its width at 6 of 8
  angles. With the bottom about 16–18% removed, iter 2 scores slightly *above* iter 1 under the same treatment (0.865 vs 0.853).
  This is a per-angle best-case cut, so read it as an upper bound, but the gap is large and consistent.
- **It is more than the jeans.** The visible denim stub (`renders/_grid.png`, below the hem at every angle) is only
  about 5–7% of the figure height. The rest is the full hem, the cuffs and the fists below the video's bottom edge. In `targets/angle_000.png`
  the frame cuts through the hands and the hem, so the target ends at the frame and not at the hem. iter 1 had the same issue on a
  smaller scale (it needed a ~6% cut).
- **The 90° profile is also thin.** After the cut, the 90° aspect is still about 4.07×0.82 ≈ 3.3 against 3.03 for the target, and its IoU stops
  at 0.796. 135° only reaches 0.747. Those two angles are worse than the framing alone explains.

| Criterion | Score | Evidence |
|---|---|---|
| Silhouette & proportions | 6 | Raw IoU is 0.761, but about 0.865 once the extent below the hips is removed (table above). That is the best upper-body fit so far. The 0° torso width and shoulders now match once the bottom is cut (0.926). The 90° profile is too thin and flat (h/w 4.07), and 135° is the weakest angle (0.692 raw, 0.747 cut). Hair volume is close, but the top is flat and sharp-edged. |
| Front fidelity | 6 | Better than iter 1: the eyes, brows and nose are now readable (iter 1 had dark blobs), the red tee and collar are clean, and both chest pockets are present. The beard and hair are still jet black and heavier than the target's dark grey-brown. The skin is pale and grey, not warm tan. The fists are now skin-coloured shapes rather than mitts. |
| Side & back fidelity | 5 | This was the main defect in iter 1 and it is now partly fixed. The back shows a real purple/white plaid with correct check scale (@180°, @225°), where iter 1 was near-black. It is still far too dark: mean subject RGB @180° is about (28,24,31) against (83,74,86) for the target. iter 1 was (14,14,15). The front is (62,47,55) against (102,79,87). So the back is about 2.8× too dark and the front about 1.6×, which means a front-to-back falloff is still baked in. The colour diff at 135° (53.8) and 180° (53.6) is still about 23 points worse than at 0° (30.3). 90° regressed (diff 29.2 → 41.9) and looks muddier than in iter 1. |
| Texture & colour | 5 | The hue moved from navy to purple, which is correct. Saturation and contrast are still too high: the white bands are bright and the purple bands are deep violet-black, while the target is soft lavender and grey-white. Brightness is low everywhere (see above). The red tee is correct. The hair and beard are pure black. |
| Mesh quality | 6 | No floaters or holes are visible. The model ends with a jeans stub and a full hem below where the video cuts off, which fails the requirement that the cut-off at the hips match the video. The white hem specks from iter 1 are gone. The hands are small fists, still not real hands. The back of the head has a blocky low-poly facet. |

## What improved / regressed vs previous
- **Improved:** the back and sides have real plaid for the first time (colour diff 180°: 67.7 → 53.6, 225°: 64.0 → 47.8,
  270°: 61.6 → 48.9, 315°: 59.1 → 43.7). The front hue moved from navy to purple (diff 39.1 → 30.3). The face is more
  readable. The upper-body silhouette is slightly better once the extent below the hips is removed (0.865 vs 0.853).
- **Regressed:** the raw IoU dropped to 0.761 because the model extends further below the hips (hem, fists and jeans). The 90° profile is thinner and
  its colour diff rose to 41.9. Everything is still uniformly too dark and too saturated.
- **Process:** the force_multiimage fix is the most important finding so far. Every earlier conclusion about `stochastic` and `multidiffusion` and about view
  count was untested, so treat iter 1's recommendations 1 and 3 as re-opened.

## Top 3 recommendations for the next iteration (most impactful first)
1. **Clip the mesh at the video's bottom edge** with a post-process in `generate.py` (a horizontal plane cut on the GLB, keeping
   everything above it), so the model ends where the video ends. Set the cut height from the target's 0° frame: the target bottom
   (frame edge) sits about **82% down** the render's height (best cut 18% at 0°, 90° and 270°, 14–16% at 180° and 225°). A configurable
   `"clip_bottom_frac": 0.17` measured from the top of the head is enough. Do this on the mesh, not in `render.py`, because the rubric requires the
   model to stop at the hips. Expected mean IoU is about 0.86, with no texture change. Without this, IoU cannot be compared across iterations.
2. **Fix the baked dark falloff from front to back.** The back texels are about 2.8× darker than the target and the front about 1.6× darker. First check the inputs: if
   `inputs/back.png` and `inputs/pre_back.png` are bright (iter 1's `pre_back` mean was about 77), the darkening comes from TRELLIS.
   Then try (a) putting `back` first in `views` to check whether the primary image dominates the appearance, and (b) as a cheap fallback,
   a texture post-process that applies +gamma or brightness lift weighted by −Z normals plus about −20% saturation on the baked texture. Success test: colour diff
   below 40 at 135° and 180°, and the white plaid bands at the back as bright as at the front.
3. **Run the 4-view vs 8-view ablation with force_multiimage on** (0/90/180/270, multidiffusion, same seed). The longer
   extent and the thin 90° profile both appeared only once multi-image was actually used. The 4 in-between views come from frames where
   the character is mid-turn, and inconsistent views may be stretching or thinning the volume. Compare the 90° and 135° IoU *after the
   clip from rec 1*, and keep whichever view set has the better 90°/135° fit and the brighter back.
