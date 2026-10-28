# Design: iteration 6 (small-step loop, round 2)

## Brief
- iter_5 review (6.5/10): the projection blurs and doubles the plaid, the pocket flaps are lost, and the face is flat and pale under unlit. The root cause is misregistration.
- Recommendations:
  1. Register each frame before blending, then winner-take-all; retry region "all" for the face.
  2. Run the missing control (projection OFF vs ON); use a frequency-split blend if registration fails.
  3. Clean the image-space inputs (cuffs, placket) and bring back face shading.
- Orchestrator hints:
  - The remaining blur is probably mesh-vs-video misalignment *within* a frame, which calibrate's (s, tx, ty, dyaw) can't fix.
  - Try flow alignment, argmax selection and detail transfer, each as its own step.

## Tool changes
- `scripts/step.py`: metrics.json now holds a non-angle dict, so the per-angle parse skips entries without `silhouette_iou`. Without this fix, step.py crashed.
- `scripts/refine.py` `project_texture` (all additive, defaults unchanged):
  - **`register_passes`** (new): after a first projection, every frame is re-sampled through a dense optical flow.
    - Pipeline: a render of the current consensus texture in that frame's calibrated camera → Farneback flow (render → frame) → clip (`reg_max`, 6 px) → masked Gaussian smoothing (`reg_smooth`, 3 px).
    - Texels then sample the frame at `uv + flow`. Visibility is still tested at the unwarped position.
    - New helper `_register_flow`.
  - **`select: "max"`**: winner-take-all (best-facing frame per texel) instead of a weighted blend.
  - **`lowpass_sigma` / `detail_gain`**: detail transfer. The low frequencies come from the projection and the high frequencies from the generated texture (masked blur, so UV gutters don't leak in).
  - The region mask is now computed once before the projection loop. Behaviour is unchanged.

## Step log
| step | change | mean IoU | kept? | what I saw |
|---|---|---|---|---|
| 1 | baseline = iter_5 final recipe | 0.901 | yes | same as iter_5 (renders saved in `ctrl_on/`) |
| 2 | **control: projection OFF** | 0.900 | no (reference) | `ctrl_off/`: crisp square checks and visible pocket flaps, but grey-lilac hue, washed-out back and flat face. Confirms the reviewer: the iter_5 projection traded crispness for hue. |
| 3 | detail transfer, lowpass_sigma 6, sharpen 0 | 0.901 | no | sigma 6 still contains the plaid period, so the two misaligned plaids overlap: worse doubling at 180°, and red bleeds across the placket |
| 4 | lowpass_sigma 25 | 0.900 | no | back crisp-ish with a better hue, but lower contrast, the tee red still bleeds onto the placket, tan cuffs remain. Partial win, beaten by step 5. |
| 5 | **register_passes 1** (power 8, region cloth) | 0.901 | yes | median flow 3.2 px, so the misalignment is real. At 180° the back checks become **single, square, crisp blocks** with the target's deep purple. The front is crisper and the pocket flaps are partly back. |
| 6 | register_passes 2 | 0.901 | no | near-identical to step 5 (flow did not shrink); costs +40 s |
| 7 | select "max" (winner-take-all) | 0.901 | no | seams and speckles (dark/cyan specks along the placket at 45°), no sharper |
| 8 | **region "all"** (project face and hands too) | **0.901** | **yes (final)** | **The face now has eyes, brows, moustache and the video's baked-in shading.** It reads as the target's face at 315° and 270°, where it was a flat beige mask before. Hands get video colours. Coverage 91%. |
| 9 | reg_max 6 → 10 | 0.901 | no | visually identical: the flow isn't hitting the clip |
| 10 | power 8 → 20, min_weight 0.05 | 0.901 | no | moustache marginally crisper, but coverage 91 → 84% and a dark notch at the collar |
| 11 | reg_smooth 1.5, winsize 11 | 0.901 | no | visually identical |
| 12 | both_halves off | 0.901 | no | visually identical with fewer frames, so I kept more frames for robustness |

I stopped after 4 consecutive non-improving steps (9–12). Final = step 8, and model.glb, recipe.json, comparison.png and metrics.json were re-rendered from it.

Rough torso numbers on the luminance of saturated pixels, as p5/p95/mean vertical gradient. This mask is different from the reviewer's, so compare columns, not against the review's figures:

| angle | target | proj OFF | iter_5 | **step 8** |
|---|---|---|---|---|
| 0° | 30/129/5.5 | 24/116/3.3 | 42/125/4.1 | 40/121/**4.7** |
| 180° | 29/114/4.9 | 20/80/2.5 | 44/107/3.9 | 40/111/**4.5** |
| 270° | 32/129/4.4 | 34/108/3.9 | 55/113/4.0 | 52/112/**4.8** |

The gradient (crispness) is up at every angle versus iter_5. The darks are still lifted (p5 about 40 vs 30).

## Final recipe (iterations/iter_6/recipe.json)
- base iter_4/model_raw.glb. post is the same as iter_5 (tex_gamma 1.0, skin_sat 0.8, skin_gamma 1.1).
- fit {iters 2, strength 0.7, angles_step 10}
- project {power 8, mix 1, min_weight 0.15, edge_erode 4, **region "all"**, head_frac 0.24, both_halves, angles_step 10, sharpen 0.8, sharpen_sigma 3, **register_passes 1**}; unlit true
- mean IoU 0.901 (0: .937, 45: .892, 90: .891, 135: .923, 180: .902, 225: .896, 270: .881, 315: .883)

## Known issues
- **The face at 0° is still slightly ghosted.** The brows and upper eyelids read doubled, which gives a "worried, looking-up" expression. The eyes sit a bit high, probably because the head's depth/shape is off, so parallax between frames isn't a 2D flow. 315° and 270° look much better.
- The darks are lifted (dark plaid stripes about 10 levels lighter than the target), so contrast is still below the video. Sharpen 0.8 is kept from iter_5; I didn't retune it this round.
- A red tee sliver remains on the left lapel/placket at 0° and 45°: the mesh's shirt edge sits where the video shows the tee. Registration doesn't fix that, and image-space boundary masking (review #3) is not implemented.
- The back of the head is still faceted (mesh). IoU is unchanged (0.901): all gains this round are texture.
- With registration + region "all", the face no longer needs head shading or unlit-off: the video's shading is baked in. That review item is superseded rather than done.
- `ctrl_off/` and `ctrl_on/` hold the renders of the control and the iter_5 baseline, for side-by-side review.
