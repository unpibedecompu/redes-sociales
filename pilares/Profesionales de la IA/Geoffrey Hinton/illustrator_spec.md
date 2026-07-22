# Geoffrey Hinton — Illustrator Build Spec

A blank-canvas, Illustrator-oriented spec for replicating the 7 published slides in `slides/`. This is independent of the HTML implementation: it describes only what should appear on the page, in language and units suited to a vector design app (Illustrator, Affinity Designer, Photoshop with vector layers, or Adobe Express with manual layout).

The published deck has 7 slides (one Instagram carousel). Source images: `slides/01_portada.png` … `slides/07_final.png`.

---

## 1. Document setup

| Setting | Value |
|---|---|
| Number of artboards | 7 |
| Artboard size | 1080 × 1080 px |
| Layout | Square grid, 7 across with 100 px gutter (or however you prefer) |
| Color mode | RGB |
| Raster effects | High (300 ppi) |
| Bleed | 0 |
| Units | Pixels |

**Layer template (per artboard, bottom to top):**

1. `bg-color` — solid fill rectangle covering the artboard
2. `bg-photo` — profile picture treatment (clipped, blended)
3. `frame` — the inner stroked rectangle and any timeline-bracket line work
4. `text` — all type
5. `accents` — separator bars, pill tags, quote marks, decorative question marks

---

## 2. Color palette (Swatches panel)

Save these as Global Swatches.

| Swatch name | HEX | RGB | Use |
|---|---|---|---|
| `acc-violet` | `#9b5de5` | 155, 93, 229 | Cover background, frame stroke, year numerals, separator, accents |
| `bg-lavender-light` | `#f0e8ff` | 240, 232, 255 | Background of content slides (timeline, pregunta, final) |
| `bg-lavender-deep` | `#e4d4ff` | 228, 212, 255 | Background of the cita slide |
| `text-near-black` | `#1a1a1a` | 26, 26, 26 | All body and headline copy on light backgrounds |
| `white` | `#ffffff` | 255, 255, 255 | Headline on cover; pill tag stroke (40% opacity) |
| `white-70` | `rgba(255,255,255,.70)` | — | Cover label color |
| `white-85` | `rgba(255,255,255,.85)` | — | Cover bajada and pill tag text |
| `white-40` | `rgba(255,255,255,.40)` | — | Cover frame stroke and pill tag stroke |

Tip: in Illustrator use a single `acc-violet` global swatch and apply lower opacities at the layer/object level rather than baking new HEX values for every tint.

---

## 3. Typography

**Family:** Outfit (Google Fonts). Install all five weights below; the sans-serif used in the deck only ever varies by weight.

| Style name | Weight | Notes |
|---|---|---|
| `outfit-light` | 300 | Labels, tags, attribution, handle |
| `outfit-regular` | 400 | Body copy |
| `outfit-semibold` | 600 italic | Cita (slide 05) — use the regular Outfit and apply faux italic if the family has no true italic |
| `outfit-bold` | 700 | Year numerals, headlines, pregunta text |
| `outfit-black` | 900 | Cover name |

### Character styles to define

All sizes are in pixels for an artboard of 1080 × 1080.

| Style | Family/Weight | Size | Tracking (letter-spacing) | Leading (line-height) | Color | Case |
|---|---|---|---|---|---|---|
| Cover label | Outfit 300 | 41 px | 150 (em-units) ≈ +0.15 em | Auto | `white-70` | All caps |
| Cover name | Outfit 900 | 95 px | 0 | 1.10 × | `white` | Title case |
| Cover bajada | Outfit 400 | 54 px | 0 | 1.40 × | `white-85` | Sentence case |
| Cover pill text | Outfit 300 | 26 px | 0 | 1 | `white-85` | Title case |
| Section label (small caps) | Outfit 300 | 41 px | 150 ≈ +0.15 em | Auto | `acc-violet` | All caps |
| Year numeral | Outfit 700 | 75 px | 0 | 1 | `acc-violet` | — |
| Timeline body | Outfit 700 | 50 px | 0 | 1.45 × | `text-near-black` | Sentence case |
| Cita | Outfit 600 italic | 54 px | 0 | 1.50 × | `text-near-black` | Sentence case |
| Cita attribution | Outfit 300 | 36 px | 100 ≈ +0.10 em | 1.20 × | `acc-violet` | All caps |
| Pregunta headline | Outfit 700 | 65 px | 0 | 1.30 × | `text-near-black` | Sentence case |
| Final heading | Outfit 700 | 78 px | 0 | 1.30 × | `text-near-black` | Sentence case |
| Final body | Outfit 400 | 50 px | 0 | 1.50 × | `text-near-black @ 65%` | Sentence case |
| Handle (`@unpibedecompu`) | Outfit 300 | 41 px | 180 ≈ +0.18 em | 1 | `acc-violet` | All caps |

Notes:
- Outfit doesn't ship with a true italic. For the cita, apply Illustrator's "Faux Italic" or skew the text frame by −10° on the X axis if you want it to lean.
- The eye is forgiving; if a body line wraps awkwardly at the values above, drop the body 2–3 px.

---

## 4. Reusable components

Build these once as symbols / global components, then place per slide.

### 4.1 Frame (inner rounded border)

A single rounded rectangle, no fill, stroke only.

| Property | Value |
|---|---|
| Geometry | Rectangle inset 54 px from every edge of the artboard (i.e. 972 × 972 px, centered) |
| Corner radius | 22 px |
| Stroke weight | 8 px |
| Stroke alignment | Inside |
| Stroke color | `acc-violet` (on lavender slides) or `white-40` (on the cover) |
| Fill | None |

The "interior padding" inside the frame — i.e. the safe area for text — is **86 px** on every side (so text lives inside an 800 × 800 px box, centered on the artboard).

### 4.2 Separator bar

A short, thick rule used under headlines to set a rhythm.

| Property | Value |
|---|---|
| Width × Height | 130 × 8 px |
| Corner radius | 4 px |
| Fill | `acc-violet` |
| Stroke | None |

### 4.3 Pill tag (cover slide)

Used for credentials on the cover.

| Property | Value |
|---|---|
| Shape | Rounded rectangle, fully pill-shaped (corner radius = height/2) |
| Padding | 11 px vertical, 43 px horizontal |
| Stroke | 5 px solid, color `white-40`, alignment Inside |
| Fill | None |
| Text | Outfit 300, 26 px, color `white-85`, vertically centered |

Place tags in a horizontal row with 24 px gaps. They wrap to a second row only if they don't fit.

### 4.4 Timeline bracket (slides 02 / 03 / 04)

The timeline is a continuous line that traces a bracket along the inside of the frame on the timeline slides. On each slide it appears to enter from one edge and exit at another, suggesting a single line that wraps across all three slides.

Build it as a stroked open path:

| Property | Value |
|---|---|
| Stroke weight | 8 px |
| Stroke cap | Round |
| Stroke color | `acc-violet` |
| Fill | None |

Path geometry per slide:

- **Slide 02 (1986 / 2012 / 2018):** vertical line on the left, exiting the right edge at top and bottom. Corners rounded with the same 22 px radius as the frame so the bracket reads as part of the frame system.
- **Slide 03 (2022):** the bracket enters from the top-left, traces the inside of the slide, and exits the bottom-right.
- **Slide 04 (2023 / 2024):** mirror of slide 02 — vertical line on the left, with horizontal stubs entering top-right and exiting bottom-right.

On every event marker, place a **timeline dot**: a `acc-violet` filled circle, 40 px diameter, centered on the bracket line.

### 4.5 Profile-picture treatment ("violet ghost with eye band")

This is the signature visual of the deck. Each slide where Hinton's face appears uses the same recipe:

1. **Base portrait:** the original photo (`background/profile_picture.webp`) placed and scaled so the face sits where the slide composition needs it.
2. **Tint layer:** duplicate the portrait, set blend mode to **Luminosity**, opacity ~30%. Place a solid rectangle of `acc-violet` directly underneath. The combined effect is a violet-tinted bust whose lighting matches the source photo.
3. **Eye band (key detail):** duplicate the original portrait *unblended* and clip it to a horizontal rectangle covering only the eye area (roughly 120 px tall, full face width). This produces the "stripe across the eyes" effect — everything is violet except for the original eyes.
4. (Optional) **Soft fade:** a horizontal black-to-transparent gradient mask on the bust so it dissolves into the lavender background, used on the timeline and pregunta slides where the face peeks in.

Per-slide framing of the bust is detailed in §5.

---

## 5. Per-slide layout

All coordinates are in pixels measured from the top-left corner of the artboard. "Inside the frame" means inside the 86 px text safe area (i.e. the 800 × 800 box centered on the 1080 × 1080 artboard).

### Slide 01 — Portada

- **Background:** full-bleed `acc-violet`.
- **Photo:** full-bleed bust (recipe in §4.5). Face centered around (540, 540). Eye band horizontal, slightly above center.
- **Frame:** `white-40` stroke, 8 px, inside the 54 px outer margin. Corner radius 22 px.
- **Text block (anchored to the bottom of the frame's safe area, stack from bottom up):**
  1. Three pill tags in a row: `Nobel de Física 2024`, `Premio Turing 2018`, `Ex-Google` — gap 24 px.
  2. Bajada (3-line max, max width 800 px): "El científico que construyó la IA moderna — y ahora dice que puede destruir a la humanidad."
  3. Cover name: "Geoffrey Hinton" (Outfit 900, 95 px, white).
  4. Cover label: "PROFESIONALES DE LA IA" (Outfit 300, 41 px, white-70, +0.15 em tracking).
- **Vertical gaps in the stack:** 16 px (label → name), 43 px (name → bajada), 43 px (bajada → tags).

### Slide 02 — Trayectoria (1986 / 2012 / 2018)

- **Background:** full-bleed `bg-lavender-light`.
- **Frame / bracket:** the open bracket described in §4.4. The line is visible on the left and exits the right edge at the top and bottom of the artboard.
- **Photo:** small bust, top-right, mostly clipped — only the head and shoulders, with the eye band visible. Apply a soft horizontal fade so the bust dissolves out of the visible area.
- **Timeline column** (vertical bracket line at x ≈ 130, with three dots):
  - Dot 1 at y ≈ 280, year `1986`. Body: "Desarrolló el programa que hace posible que las máquinas aprendan. Sin él, no existiría ninguna IA actual."
  - Dot 2 at y ≈ 580, year `2012`. Body: "Logró enseñarle a las computadoras a identificar objetos en imágenes, dando inicio a la revolución de la IA."
  - Dot 3 at y ≈ 880, year `2018`. Body: "Recibió el Premio Turing — el «Nobel de la Computación»."
- **Year offset:** the year sits at the dot's vertical center, with body copy starting ~14 px below the year baseline. Body wraps inside a column of about 720 px.

### Slide 03 — El giro (2022)

- **Background:** full-bleed `bg-lavender-light`.
- **Frame / bracket:** continues the bracket from slide 02 — enters top-left, runs along the top of the safe area, drops down at the right and exits the bottom edge.
- **Photo:** centered bust at the bottom of the slide, hips up. Apply the violet ghost + eye band; soft fade at the bottom so it merges into the slide edge.
- **Timeline dot:** at the top of the slide on the bracket line, marking the year.
- **Text:**
  - Year `2022` (Outfit 700, 75 px, `acc-violet`), centered horizontally just below the top bracket line.
  - First sentence (Outfit 700, 50 px, `text-near-black`): "Una IA de Google le pudo explicar un chiste."
  - Paragraph break (~32 px).
  - Second paragraph (same character style): "En ese momento se dio cuenta que esta tecnología en pocos años se podría volver más inteligente que los humanos."

### Slide 04 — Trayectoria (2023 / 2024)

- **Background:** full-bleed `bg-lavender-light`.
- **Frame / bracket:** mirror of slide 02. Vertical line on the left, horizontal stubs entering top-right and exiting bottom-right.
- **Photo:** bust top-right, larger than slide 02. Hair top, eye band visible, shoulder cut by the right edge.
- **Timeline column** (left-aligned, two events):
  - Dot at y ≈ 380, year `2023`. Body: "Renunció a Google, declarando que lo hacía para poder hablar libremente sobre los riesgos de la IA."
  - Dot at y ≈ 740, year `2024`. Body: "Ganó el Premio Nobel de Física — y usó el discurso para advertirle al mundo sobre los peligros de la IA."

### Slide 05 — Cita

- **Background:** full-bleed `bg-lavender-deep`.
- **Frame:** standard inner frame in `acc-violet`.
- **Photo:** large bust on the right side of the safe area, head near the top. The face is visible (no eye band on this slide). Apply only the violet tint at lower opacity (~25%) so the portrait reads as a soft companion to the quote.
- **Decorative quote mark:** open-quote glyph (`"`), Outfit 900, 155 px, `acc-violet` at 20% opacity, anchored top-left of the safe area. Line-height 1.
- **Cita** (left column, max width 520 px so it wraps to the left of the bust): Outfit 600 italic, 54 px, `text-near-black`, line-height 1.5. Text: "Hay una amenaza existencial de más largo plazo que surgirá cuando creemos seres digitales más inteligentes que nosotros. No tenemos idea de si podemos mantenernos en control."
- **Separator:** §4.2, below the cita with 32 px gap.
- **Attribution:** Outfit 300, 36 px, `acc-violet`, all caps, +0.10 em tracking, line-height 1.2: "Geoffrey Hinton · Discurso del Nobel, diciembre 2024".

### Slide 06 — Pregunta

- **Background:** full-bleed `bg-lavender-light`.
- **Frame:** standard inner frame in `acc-violet`. Corner radius slightly larger here (use 32 px) — the published slide shows a more cushion-like frame than the others.
- **Decorative question marks:** two oversized glyphs `¿` and `?` stacked diagonally near the top-center of the safe area, Outfit 700, ~250 px tall, `acc-violet` at 35% opacity. These are decorative; do not let them overlap the headline.
- **Headline:** Outfit 700, 65 px, `text-near-black`, line-height 1.30, max width ~700 px, centered horizontally: "¿Es responsable seguir construyendo algo que sus propios creadores admiten que no pueden controlar?"
- **Separator:** §4.2, below the headline with 32 px gap, left-aligned with the headline.
- **Photo:** a small head-and-shoulders centered along the bottom of the frame, eye band visible. Apply a strong soft fade at the bottom so the bust dissolves into the lavender background.

### Slide 07 — Final

- **Background:** full-bleed `bg-lavender-light`.
- **Frame:** standard inner frame in `acc-violet`. Corner radius 32 px to match slide 06.
- **Photo:** small head top-left, partially clipped by the artboard edge so only the right half of the face is visible inside the slide. Eye band visible.
- **Text stack** (centered horizontally, vertically centered in the safe area):
  1. Heading: "¿Quién sigue?" (Outfit 700, 78 px, `text-near-black`).
  2. Separator: §4.2, 16 px below the heading.
  3. Body: "Seguime para conocer a las personas detrás del debate más importante del siglo." (Outfit 400, 50 px, `text-near-black @ 65% opacity`, line-height 1.50, max width 720 px, text-align center).
  4. Handle: "@UNPIBEDECOMPU" (Outfit 300, 41 px, `acc-violet`, all caps, +0.18 em tracking, 32 px below the body).

---

## 6. Build order in Illustrator (suggested)

1. Create one document with seven 1080 × 1080 artboards.
2. Create the swatches in §2.
3. Place the source photo (`background/profile_picture.webp`) once on a hidden master layer; copy/paste in place to each artboard so all instances stay color-matched. Apply the recipe in §4.5 per slide.
4. Save the frame, separator, and pill tag from §4.1–4.3 as **Symbols** (Window → Symbols → New Symbol). Drag them to each artboard so a future tweak propagates everywhere.
5. Save the character styles in §3 (Window → Type → Character Styles → New). Apply them to text frames as you build each slide.
6. Build the timeline bracket in §4.4 as a single set of three open paths, one per slide, all sharing the same stroke profile.
7. Lay out each slide per §5.

## 7. Export

- File → Export → Export for Screens → Artboards → All → PNG, scale 1× → save to `Geoffrey Hinton/slides_illustrator/`.
- Resulting filenames: `01_portada.png` … `07_final.png`, each 1080 × 1080.
- For Instagram, JPG quality 90+ is also fine; PNG keeps the magenta-on-lavender edges crisper.

## 8. Asset references

- **Photo:** `Geoffrey Hinton/background/profile_picture.webp` (and `profile_picture_no_background.png` if you want to feather the bust).
- **Published slides (ground truth):** `Geoffrey Hinton/slides/01_portada.png` … `07_final.png`.
- **Existing HTML implementation (for cross-checking exact CSS values):** `Geoffrey Hinton/Geoffrey_Hinton.html`.

## 9. Notes on visible differences from `carrousel_description.md`

The `carrousel_description.md` in this folder describes a 9-slide expansion of this story (each timeline year on its own slide, plus a "para pensar" slide and a "qué sigue" slide). The published deck is a 7-slide condensation. This Illustrator spec follows the **published 7-slide deck** because that's what's in `slides/`. If you want to produce the 9-slide version instead, the same components in §4 plus the character styles in §3 are sufficient — only §5 (per-slide layout) needs to be swapped for the 9-slide layout described in `carrousel_description.md`.
