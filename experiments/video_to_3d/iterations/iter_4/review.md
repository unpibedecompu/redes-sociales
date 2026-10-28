# Review: iteration 4
**Overall score: 7.0/10** (best so far: 7.0/10 in iter 4; previous best was iter 3 at 6.5) · mean IoU: 0.833 (final harness; iter_3 0.821, iter_2 0.737, iter_1 0.795)

Setup: no new generation (the 4-view ablation hit the ZeroGPU quota). This is iter_2's raw mesh with iter_3's post-processing plus three new steps: below-neck body scale (x1.05, z1.15) with a +0.10 shoulder band, a skin-protect UV mask, and an unsharp mask on the cloth. Framing is correct (front at 0°, back at 180°, no `--yaw` needed).

## Critical harness finding: the video is not a one-way 360° turn
The targets at 45°, 90° and 135° show **the same side of the character** as the targets at 315°, 270° and 225°, not the opposite side:
- Target 90 vs target 270: mean abs diff 7.6 as-is, 10.7 when mirrored. A rigid turntable would give the reverse, and the renders do: render 90 vs render 270 is 10.2 as-is and 5.2 mirrored.
- Target 135 vs 225: 10.3 as-is, 16.1 mirrored. Target 45 vs 315: 14.6 as-is, 16.1 mirrored.
- The contact sheet (2 fps, 0–10 s) shows the character turning to the back and then **turning back the same way**. Both "profiles" (t≈3.5 s and t≈8.6 s) face left with the red tee visible on the left. The frame at t=3.5 s is really the 270° view, t≈1.75 s is really 315°, and t≈5 s is really 225°. The character's other side never appears in the video.

**Consequences:**
1. **45°, 90° and 135° are scored against the wrong side.** If I score the renders against horizontally mirrored targets instead (a symmetry approximation, same masks), IoU rises by about +0.06 at 45°, +0.10 at 90° and +0.14 at 135° for iter_4. The control angle 270° drops by 0.08 when mirrored, as expected. So the "weak 45/90/135 band" that iterations 2–4 have chased is mostly a harness artefact, not a geometry error. The "back bulges at 135°" note in iter_3's review and this iteration's design.md is wrong for the same reason. Corrected estimate: iter_4 mean ≈ 0.87 and iter_3 ≈ 0.85; the ranking is unchanged.
2. **The body-scale sweep was partly fitted to wrong targets.** On the five valid angles only (0/180/225/270/315), the chosen variant is still the best of the sweep: 0.884, against 0.872 for the control and 0.880–0.882 for the runners-up. So the chosen config holds up, but the margins are small.
3. **The generation inputs were affected too.** iter_2's 8 "views" contain three duplicate pairs (fr45≈fl315, right≈left, br135≈bl225). Multidiffusion is pose-free, so this only reweights those views, but the model never saw the character's other side.

## Post-processing artefact check (zoomed 4× heads, 2× hem)
| Artefact | Found? | Evidence |
|---|---|---|
| Neck tearing / ramp seam | **No** | The neck–shoulder transition is smooth at every angle, with no step at the 0.22 / 0.05 ramp. |
| Hem flare | **No** | The hem at 0°, 135°, 180° and 315° has the same shape as iter_3, just slightly wider. The shoulder band kept width off the hem, as designed. |
| Skin mask bleeding into plaid or hair | **Minor** | No plaid or hair texels turn tan. But `skin_mask_uv.png` has dashed stray strokes across the shirt islands (seam lines). Also, the neck mask is patchy: some neck texels are protected and others got the cloth lift and desaturation. This shows as **light/dark streaks on the neck** at 45°, 90° and 315°. |
| Over-sharpening halos | **No** | No ringing on check edges. The vertical gradient energy in the torso is now at or slightly above the target (0°: 7.0 vs 6.4; 90°: 4.0 vs 3.9). Don't sharpen further. |
| **Skin overshoot (new problem)** | **Yes** | The skin went from chalky to **too dark and too orange**. Median warm-skin pixel colours, render vs target: 0° (140,105,77) vs (155,128,109); 45° (132,96,70) vs (140,114,95); 90° (114,71,47) vs (170,141,114); 315° (120,83,58) vs (157,125,97). The B/R ratio is 0.41–0.55 against 0.62–0.70 in the target, so the skin is over-saturated. It is also 10–55 levels too dark, worst on the side-lit neck and jaw. On the face at 0°, the eye sockets read as muddy dark smudges. The back of the neck at 180° and 225° now shows an orange strip under the hair; in the target it is barely visible. |

| Criterion | Score | Evidence |
|---|---|---|
| Silhouette & proportions | 7.5 | Valid-angle IoU went up: 0° 0.900→0.924, 225° 0.879→0.930, 270° 0.853→0.874, and 180° held at 0.895. The shoulders are visibly squarer at 0° and 180°, and the head-to-body ratio is less top-heavy. **There is one real regression, at 315°: 0.832→0.796.** At rows 95–120 (upper chest and shoulder) the render's right edge is 4–11 px wider than the target, so the shoulder band and x-scale over-widen the front 3/4 view. 45°, 90° and 135° are not trustworthy (see above). |
| Front fidelity | 6.5 | The red tee, open collar, pockets and plaid layout all still match. The face is no longer ghostly, but it is now too dark and orange, and the eyes are smudged, so the gain over iter_3 is partial. No hands at 0°, unchanged. |
| Side & back fidelity | 7 | As in iter_3: the back plaid is correct in hue and scale, and the sides read well. The back is still a little darker and greyer than the target: at 135° and 180° the torso's light checks reach a 95th-percentile luminance of 142 against 171–180 in the target. Back of the head is still a low-poly block. There is a new orange nape strip at 180° and 225°. |
| Texture & colour | 6.5 | The plaid is crisper at the front and sides with no halos, and tex_sat 0.9 gives cleaner whites. Skin hue is closer than iter_3 and saturation is overshot (numbers above). The back checks are still soft. The colour-diff column is still fitted, so I don't count it. |
| Mesh quality | 7 | No tearing, floaters or flare from the deformation, and the clip is clean. Neck texture streaks come from the patchy mask. The head silhouette is still faceted. |

## What improved / regressed vs previous
- **Improved:** the body volume. The shoulders are squarer and the profile is deeper, raising valid-angle IoU from 0.872 to 0.884. The skin is warm instead of grey, and the plaid is sharper. The deformation was implemented cleanly, with no neck or hem artefacts.
- **Regressed:** 315° IoU (−0.036, the shoulder band and x-scale over-widen it). The skin is now too dark and saturated, and there are streaks on the neck.
- **Unchanged:** the raw mesh, the soft back plaid, the low-poly back of the head, and the 4-view ablation (still open).

## Top 3 recommendations for iteration 5 (post-processing only, ranked by expected visible gain)
1. **Fix the skin colour and mask (largest visible gain; the face is the first thing a viewer looks at).** Keep skin_protect, but correct the protected texels towards the target. Raise the brightness by `skin_gamma` ≈ 1.25 or a gain of about [1.08, 1.18, 1.35], and reduce saturation to about 0.75, so the medians land within ±10 of **(155,128,109)** at 0° and the B/R ratio reaches about 0.68. Fit this on the 0° face only, not on the side-lit 90° neck. Also make the mask contiguous: dilate it by about 6–8 px in UV and feather it by about 4 px. Remove connected components under about 200 texels, which drops the dashed seam strokes across the shirt. That gets rid of the neck streaks. Success test: at 4× zoom, the face and neck at 0°, 45° and 315° read as one even tan with visible eye whites and no orange band. The 180° nape should not stand out from the hair edge.
2. **Fix the target angle mapping before any re-sweep (orchestrator or harness, free, changes what "best" means).** The video goes 0→180° and back along the same side. So, in render-angle terms, t=0–6.5 s maps to 0, 315, 270, 225, 180, and 6.5–10 s maps back from 180 to 0 on the same side. Option (a): score only 0/180/225/270/315. Option (b): score 45/90/135 against horizontally flipped 315/270/225 targets, which assumes left/right symmetry (the open shirt and red tee are close enough to symmetric). Re-score iter_1–4. Then **re-run the body-scale sweep on valid angles only**, adding a 315° guard (≥0.82). Try `shoulder_extra_x` 0.05–0.08 with x 1.00–1.05 and z 1.15–1.25. The current choice gives up 0.036 at 315° for 0.024 at 0°; a narrower shoulder band will probably recover most of 315° while keeping the squarer front. Stop trying to fix "135° too wide". It isn't, once mirrored.
3. **Lift the back cloth highlights (moderate visible gain on the back half of the turntable).** At 135° and 180°, the light checks are about 20% darker than the target (p95 luminance 142 vs 171–180), while the front matches (177 vs 176). Use either a highlight-only lift on back-facing texels (a levels curve that raises values above about 0.5 by ~1.15× and leaves the dark purple stripes alone) or tex_gamma_back 2.0→2.2, checked visually at 135° and 180° against the target. Use a light unsharp mask on the back only if the checks still look soft after the lift. Don't increase the global sharpen; the front is already at the target's edge contrast.

If quota does appear: rerun `ablation_4view/config_quota_failed.json`, but feed **0/315/270/225/180-equivalent frames only once each** (drop the duplicate 45/90/135 frames), and consider adding horizontally flipped frames as the unseen side.

> Orchestrator note (after review) — harness fix for the angle issue raised above:
> - Confirmed: 0–10 s turns to the back and returns on the SAME side; the character's left side only appears at ~13.5 s.
>   `scripts/common.py` now maps 0–180° to the first half (0/3.5/6.5 s) and 180–360° to the second half (16.5/13.5/10 s).
> - render.html also spun the model the opposite way to the video (hidden before because both "sides" were the same); fixed.
> - All iterations re-scored on this final harness: iter_1 0.788, iter_2 0.735, iter_3 0.822, **iter_4 0.843**.
> - Consequence for generation: every previous "270°/left" input view was actually a duplicate of the right side, so no model has seen the character's left side yet.
