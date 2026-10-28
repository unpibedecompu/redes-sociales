# Review: iteration 6 (small-step loop, round 2)
**Overall score: 7.5/10** (best so far: 7.5/10 in iter 6; previous best was iter 4 at 7.0) · mean IoU: 0.901 (iter_5 0.901, iter_4 0.897)

Setup: iter_5's recipe plus two changes. First, a dense optical-flow registration pass (Farneback flow from the consensus render to each frame, clipped at 6 px) applied before blending the texture projection. Second, `region: "all"`, which projects onto the face and hands as well as the cloth. All gains this round are in the texture; the geometry is unchanged.

How I compared: target, iter_4, iter_5, `ctrl_off` and iter_6 side by side at 0°, 45°, 90°, 135°, 180°, 270° and 315°. I also zoomed in on the faces (4×) and on the front and back torso (3×). One caveat about `iter_4/renders`: they were made with the old angle table, so iter_4's 45° and 315° renders show the opposite three-quarter view. I judged iter_4 on 0°, 90°, 180° and 270° only.

| Criterion | Score | Evidence |
|---|---|---|
| Silhouette & proportions | 7.5 | Unchanged from iter_5 (per-angle IoU identical to ±0.001). There are no regressions, but the weak angles, 270° (0.881) and 315° (0.883), weren't touched. |
| Front fidelity | 7.5 | **Big win on the face.** For the first time it has eyes with whites and pupils, brows, a moustache shape and the video's shading. At 315° and 270° it reads as the target's character, where iter_5 and `ctrl_off` show a blank beige mask and iter_4 a brown face without eyes. **At 0° the face is ghosted:** the brows and upper lids are doubled and the eyes sit too high and too wide, giving a startled, worried look, while the target looks calm and slightly downcast. There are also light skin-coloured streaks inside the beard below the mouth. The pocket flaps are back at 0° (both flaps visible; they were lost in iter_5). The red tee sliver on the left lapel/placket remains at 0°, and so does the dark vertical placket line. |
| Side & back fidelity | 7.5 | **The 180° back is the best yet.** The checks are single, square blocks with the target's deep purple and lavender, with no doubling. That beats iter_5 (smeared), `ctrl_off` (grey-lilac) and iter_4 (washed-out). 135° is also much crisper. **There is a regression at 90°:** a wide red band runs down the whole front edge of the shirt, where the target shows a thin sliver plus a plaid lapel and pocket. It is the same tee-on-placket leak as at 0°, seen edge-on, and it is now the most visible error in the turntable. The sleeve plaid at 270° is crisper than iter_5 but still shows diagonal streaks. At 135° and 270° there are tan/skin streaks on the hair and neck where projected skin landed on hair texels. |
| Texture & colour | 6.5 | The hue is right everywhere and crispness is clearly up on iter_5: the designer's vertical gradient rose 4.1→4.7 at 0°, 3.9→4.5 at 180° and 4.0→4.8 at 270° (target 5.5 / 4.9 / 4.4). The front plaid at 0° and 45° is still softer and more streaky than `ctrl_off` and iter_4, with some checks smeared vertically on the left chest. **The darks are lifted:** p5 is about 40 vs 30 in the target, so the dark stripes look grey-purple rather than near-black. There are cyan/blue specks in the hair at 0° and 315° (upper-left of the head) and on the cheek. |
| Mesh quality | 7 | Unchanged. The back of the head is faceted, and the hands are melted stubs; now that they carry the video's skin colour, they show up more at 0° and 45°. There are no new spikes or dents. |

**Why 7.5.** Head-to-head with iter_4 (7.0): iter_6 wins clearly on the face (identity, eyes, brows), the back (crisp, correct hue) and overall colour. It loses slightly on front crispness and has the 90° red band and the 0° face ghosting. Against iter_5 it is better on every axis. It is the new best, but not yet at 8 because of the 0° face expression, the tee leak, the lifted darks and the specks.

## Step-log audit
- **Step 2 (the control): exactly what was asked, and well read.** `ctrl_off` confirms the trade-off: crisp checks and pockets but the wrong hue. It made every later keep/revert decision meaningful.
- **Steps 3–4 (detail transfer): correctly rejected, but tested in the wrong order.** They ran *before* registration, when the low band still carried two misaligned plaids. They were never retried on top of step 5/8. With registered frames, a mid lowpass (sigma about 10–12) might now restore front crispness without doubling.
- **Step 5 (registration): the key step, correctly kept.** The back at 180° visibly changes from doubled to single square checks. The median flow of 3.2 px proves the misalignment was real.
- **Step 6: honest reject.** But the flow *growing* on pass 2 (3.16→3.46 px) is a signal: the residual is flow-estimation noise against a soft consensus render, not a correctable offset. That is worth noting in the tool.
- **Step 7 (winner-take-all): correctly rejected.** It produced seams and specks.
- **Step 8 (region all): the round's biggest visible win, correctly kept.**
- **Steps 9–12: mostly wasted.** Three of the four were "visually identical" knob nudges (reg_max, reg_smooth/winsize, both_halves). Meanwhile the design.md "Known issues" already listed three concrete, unaddressed artefacts: the tee sliver/placket, lifted darks and 0° face ghosting. The stop rule (4 non-improving steps) fired on low-information sweeps rather than on exhausted ideas. Next round should spend steps on the known issues, not on parameters the flow is insensitive to.
- IoU is flat across all 12 steps, so every decision was visual. The designer's per-angle luminance table is the right supplement; keep it.

## What improved / regressed vs previous
- **Improved:**
  - The face now has eyes, brows, moustache and shading, a real likeness at 270° and 315°.
  - The back plaid is crisp and correctly coloured.
  - The pocket flaps are back.
  - Plaid gradients are up at all measured angles.
  - The orange cuff smears are now plausible hand colour, because the hands are projected too.
  - The `step.py` metrics-parse crash is fixed.
- **Regressed or new:**
  - A wide red band down the shirt front at 90°.
  - The 0° face has doubled brows and a startled expression.
  - Cyan specks in the hair and skin streaks on the hair/neck at 135° and 270°.
- **Unchanged:**
  - Lifted darks.
  - Dark placket line.
  - Faceted back of the head.
  - IoU.

## Top 3 recommendations for the next round (most impactful first)
1. **Mask tee and skin boundaries in image space before projecting.** This fixes the 90° red band, the 0°/45° lapel sliver and the dark placket line.
   - In each projection frame, build a "tee" mask (red hue: H within ±15° of the tee red, S > 0.45) and a "skin" mask, then dilate both by 3–4 px.
   - Use each texel's class in the *generated* texture (red tee vs plaid vs skin) and only accept frame pixels of the same class. Shirt texels reject tee and skin pixels, tee texels accept only tee pixels, and head/hand texels reject the plaid.
   - Leave texels with no valid sample at the generated texture value.
   - Step plan: (a) a tee mask only, checked at 90° and 0°; (b) add the skin/hair class gating. This also removes the skin streaks on the hair at 135° and 270°.
   - Success test: at 90° the red is a thin sliver like the target, at 0° the left placket is plaid up to the edge, and there are no tan streaks on the hair.
2. **Un-ghost the 0° face with sharper per-region frame selection.**
   - Add a per-region `power` (or `select`) override: head `power` 30–40 with `min_weight` 0.02, or winner-take-all restricted to the head with about 3-texel feathering. Step 7's seams were on the placket; on the head, where the frames are near-frontal, winner-take-all may behave.
   - Alternatively, for head texels, restrict frames to those within ±25° of each texel's best view.
   - Judge only at 4× face zoom against target 0° and 315°. Success means single brows, eyes at the target's height and a calm expression. Also median-filter (3×3) the head texels to kill the cyan specks.
3. **Restore contrast with a histogram/levels match, then retry detail transfer on registered frames.**
   - (a) After projection, remap the cloth texels per channel so the rendered torso p5/p95 matches the target (about 30/129 at 0°). That means levels on the projected texture, not sharpening.
   - (b) Retry `lowpass_sigma` of about 10–12 with `detail_gain` 0.5–0.8 *on top of registration*, comparing 0° front crispness against `ctrl_off` at 3× zoom.
   - Keep the change only if the front checks get closer to `ctrl_off` crispness without bringing back the doubling at 180°.
