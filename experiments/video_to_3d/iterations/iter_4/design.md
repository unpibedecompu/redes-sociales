# Iteration 4: design

## Hypothesis
The brief is the iter_3 review:
- **Rec 1 (body volume, no quota):** the torso is about 20% too shallow at 90° and 270°, and the shoulders are about 20% too narrow at 0° and 180°. Add a non-uniform scale below the neck.
- **Rec 2 (skin, no quota):** keep skin out of the gamma lift and desaturation, cut the cloth desaturation to 0.9, and sharpen the plaid.
- **Rec 3 (4-view ablation):** spend the one allowed generation on it.

## Generation attempt (failed: quota)
`ablation_4view/config_quota_failed.json` is the 4-view run: views 0/90/180/270, the same seed and params as iter_2, multidiffusion, force_multiimage. It failed on the first try with `ZeroGPU quota exceeded (120s requested vs. 152s left). Try again in 23:33`. The log is `ablation_4view/generate.log`. As instructed, I did not retry. **The 4-view vs 8-view ablation is still open.**

So `model_raw.glb` is iter_2's model, the same raw mesh as iter_3, and everything below comes from post-processing (`--post-only`).

## Code change (`scripts/generate.py`, new optional `post` keys; all default to no-op)
- `body_scale_xz: [sx, sz]` scales x (width) and z (depth) of every vertex below `neck_frac` (measured from the top of the post-clip height). The scale is about the torso's mean x/z axis, with a smoothstep ramp over `neck_ramp` so the neck doesn't tear.
- `shoulder_extra_x` adds width in a gaussian band centred at `shoulder_frac` with sigma `shoulder_width`. This targets the narrow, sloped shoulders without widening the hem.
- `skin_protect` builds a UV skin mask from the **raw** texture: hue roughly 0–45° (R ≥ G ≥ 0.9·B), saturation 0.12–0.6, value above 0.35. It is optionally limited to faces in the top `skin_head_frac`, then dilated and feathered. Skin texels keep their raw colour, with optional `skin_gain`/`skin_gamma`. They skip the gamma lift, the desaturation and the sharpening. The mask is saved as `skin_mask_uv.png`.
- `tex_sharpen` applies an unsharp mask (radius 2 px) to the cloth texels.

## Config (`config.json`)
These settings are unchanged from iter_3: clip 0.17, gamma front 1.45 / back 2.0.

New settings:
- **body_scale_xz [1.05, 1.15]**
- shoulder_extra_x 0.10 at shoulder_frac 0.32 (sigma 0.08)
- neck 0.22, ramp 0.05
- tex_sat 0.9 (was 0.85)
- tex_sharpen 0.5
- skin_protect with skin_head_frac 1.0 and skin_gain 1/1/1. I added no warm shift because the raw TRELLIS skin is already tan.

The head limit is off. With 0.26 it missed neck and ear texels, and the mask is already hue-selective enough that the red tee and the purple plaid stay out of it.

## Geometry sweep (`sweep/`, same texture, IoU from the final harness)
The control with no scale reproduces iter_3 exactly: 0.821. **The texture changes do not move IoU.**

| variant | mean | 0 | 45 | 90 | 135 | 180 | 225 | 270 | 315 |
|---|---|---|---|---|---|---|---|---|---|
| ctrl (= iter_3) | 0.821 | .900 | .757 | .747 | .701 | .895 | .879 | .853 | .832 |
| x1.12 z1.20 (rec 1 start) | 0.818 | .904 | .774 | .781 | .672 | .869 | .924 | .859 | .763 |
| x1.0 z1.2 | 0.826 | .900 | .757 | .777 | .689 | .886 | .907 | .870 | .820 |
| x1.0 z1.2 +sh .12 | 0.828 | .911 | .756 | .777 | .692 | .888 | .915 | .870 | .816 |
| x1.08 z1.15 +sh .08 | 0.827 | .922 | .770 | .784 | .681 | .885 | .921 | .876 | .777 |
| x1.05 z1.2 +sh .15 | 0.830 | .927 | .767 | .783 | .684 | .896 | .932 | .866 | .787 |
| **x1.05 z1.15 +sh .10 (chosen)** | **0.833** | .924 | .767 | .784 | .692 | .895 | .930 | .874 | .796 |

## Result
- **Mean IoU 0.833**, up from 0.821 for iter_3 on the same harness. That is a small gain.
- **Gains:**
  - 90°: 0.747 → 0.784
  - 270°: 0.853 → 0.874
  - 225°: 0.879 → 0.930
  - 0°: 0.900 → 0.924
  - 180° is unchanged.
- **Losses:**
  - 315°: 0.832 → 0.796. It is the most sensitive angle to any x widening.
  - 135°: 0.701 → 0.692. It was already too wide, as the reviewer predicted.
- **The rec 1 success test was only partly met:** 90° rose but stays below 0.80.
- **Rec 1 as written over-widened the body.** Uniform x 1.12 made the hem flare and dropped 180° and 315°. The target is wide at the shoulders and narrow at the hips, which is why I moved the extra width into the shoulder band.
- **Visual:** the shoulders are squarer and the profile is deeper. The skin is now warm tan instead of chalky grey; see the front close-up, which reads close to the target. It may be slightly darker than the target. The plaid has crisper edges. The cloth hue and brightness are as in iter_3.
- **The colour-diff column is still not evidence.** The gamma values are inherited from iter_3's fitted values, and no texture parameter was tuned against the target means this iteration. The skin and sharpen settings were judged visually.

## Known issues
- 135° (0.69) and 315° (0.80) are now the weakest angles. A single symmetric x/z scale can't fix 3/4 views that disagree in opposite directions: the back bulges at 135° and the front-side is too wide at 315°. This might need a scale that differs between front and back (z>0 vs z<0), or a better raw mesh.
- The 4-view generation still needs quota. Rerun `ablation_4view/config_quota_failed.json` after adding iter_4's `post` keys to it.
- The open cut at the hem is unchanged. The back of the head is still low-poly.
