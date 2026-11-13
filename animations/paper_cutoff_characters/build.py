"""Generates the paper-cutout character parts.

Every part is drawn on the same 400x900 canvas, so any combination lines up when stacked.
Outputs:
  parts/<category>/<nn>_<name>.svg   one standalone file per part (for Premiere / After Effects)
  parts.js                           the same parts as data, loaded by index.html

Run:  python build.py
Colours that the editor can change are written as tokens (PIEL, PIELS, PELO, PELOS) and become
CSS variables with a default, so the standalone files still render with default colours.
"""
import json
import math
import re
import shutil
from pathlib import Path

HERE = Path(__file__).parent
W, H = 400, 900

DEFAULTS = {"PIEL": "#E8B48A", "PIELS": "#C98F66", "PELO": "#3B2A20", "PELOS": "#24180F"}
VARS = {"PIEL": "--piel", "PIELS": "--piel-sombra", "PELO": "--pelo", "PELOS": "--pelo-sombra"}
INK = "#141413"
WHITE = "#FAF9F5"


# ---------- helpers ----------
def mirror(frag):
    """Mirror a left-side fragment onto the right side (x -> 400 - x). Paths must use absolute M/L/Q/C/Z."""
    def pairs(m):
        return re.sub(r"(-?\d+(?:\.\d+)?)[ ,]+(-?\d+(?:\.\d+)?)",
                      lambda p: f"{W - float(p.group(1)):g} {p.group(2)}", m.group(0))
    out = re.sub(r'(?<=\sd=")[^"]*', pairs, frag)
    out = re.sub(r'(?<=points=")[^"]*', pairs, out)
    out = re.sub(r'cx="(-?\d+(?:\.\d+)?)"', lambda m: f'cx="{W - float(m.group(1)):g}"', out)
    return out


def both(frag):
    return frag + mirror(frag)


def P(d, fill, extra=""):
    return f'<path d="{d}" fill="{fill}"{extra}/>'


def tokens_to_style(svg):
    """fill="PIEL" / stroke="PELO" -> style="fill:var(--piel,#...)" (one style attr per element)."""
    def fix(tag):
        t = tag.group(0)
        styles = []
        for attr in ("fill", "stroke"):
            m = re.search(rf'\s{attr}="(PIEL|PIELS|PELO|PELOS)"', t)
            if m:
                tok = m.group(1)
                styles.append(f"{attr}:var({VARS[tok]},{DEFAULTS[tok]})")
                t = t.replace(m.group(0), "")
        if styles:
            t = re.sub(r"(/?>)$", f' style="{";".join(styles)}"\\1', t)
        return t
    return re.sub(r"<[a-zA-Z][^>]*>", fix, svg)


# ---------- HEADS (centre x=200, ~y 98..288; always covers x 124..276 near y 195) ----------
# name, outline, centre y, top y, bottom y, half width  (centre x is always 200)
CABEZAS = [
    ("Ovalada", "M124 192 A76 94 0 1 1 276 192 A76 94 0 1 1 124 192 Z", 192, 98, 286, 76),
    ("Redonda", "M118 196 A82 82 0 1 1 282 196 A82 82 0 1 1 118 196 Z", 196, 114, 278, 82),
    ("Cuadrada", "M126 132 Q126 100 160 100 L240 100 Q274 100 274 132 L274 240 Q274 284 230 286 "
                 "L170 286 Q126 284 126 240 Z", 193, 100, 286, 74),
    ("Corazón", "M122 172 Q122 100 200 100 Q278 100 278 172 Q278 230 236 268 Q214 290 200 290 "
                "Q186 290 164 268 Q122 230 122 172 Z", 195, 100, 290, 78),
    ("Pera", "M140 150 Q140 98 200 98 Q260 98 260 150 L268 200 Q284 286 200 288 Q116 286 132 200 Z", 193, 98, 288, 70),
]
cabezas = [(n, P(d, "PIEL")) for n, d, *_ in CABEZAS]

# fixed face pieces (eyes: two black dots) - not a category, always on top of the head
CARA = both(f'<circle cx="170" cy="190" r="6" fill="{INK}"/>')

# ---------- EARS (left drawn, right mirrored; inner edge hidden behind head) ----------
orejas = [
    ("Redondas", both('<circle cx="124" cy="198" r="19" fill="PIEL"/><circle cx="125" cy="198" r="9" fill="PIELS"/>')),
    ("Chicas", both('<ellipse cx="130" cy="196" rx="12" ry="16" fill="PIEL"/>'
                    '<ellipse cx="128" cy="197" rx="5" ry="8" fill="PIELS"/>')),
    ("Grandes", both(P("M142 170 Q92 146 92 196 Q94 244 142 226 Z", "PIEL")
                     + P("M130 182 Q106 176 108 198 Q110 220 130 214 Z", "PIELS"))),
    ("De elfo", both(P("M142 178 L86 138 Q96 208 142 228 Z", "PIEL")
                     + P("M130 190 L104 166 Q110 204 130 214 Z", "PIELS"))),
    ("Con aros", both(P("M142 174 Q106 168 108 200 Q110 234 142 230 Z", "PIEL")
                      + P("M128 186 Q116 186 117 202 Q118 218 128 216 Z", "PIELS")
                      + '<circle cx="116" cy="240" r="7" fill="none" stroke="#E0B341" stroke-width="4"/>')),
]


# ---------- MOUTHS (a single black line) ----------
def boca(d):
    return f'<path d="{d}" fill="none" stroke="{INK}" stroke-width="4.5" stroke-linecap="round"/>'


bocas = [
    ("Sonrisa", boca("M183 252 Q200 266 217 252")),
    ("Recta", f'<rect x="183" y="255.75" width="34" height="4.5" rx="2.25" fill="{INK}"/>'),
    ("Triste", boca("M183 263 Q200 250 217 263")),
]

# ---------- EYEBROWS (left drawn, mirrored) ----------
cejas = [
    ("Rectas", both(P("M150 164 L190 161 L191 170 L151 173 Z", "PELO"))),
    ("Arqueadas", both(P("M148 172 Q168 150 193 163 L191 170 Q170 160 151 178 Z", "PELO"))),
    ("Enojadas", both(P("M148 157 L195 169 L192 177 L147 166 Z", "PELO"))),
    ("Tupidas", both(P("M146 172 L148 160 L156 163 L161 154 L170 159 L178 152 L185 158 L195 157 L194 171 Z", "PELO"))),
    ("Preocupadas", both(P("M150 167 L193 157 L194 162 L151 173 Z", "PELO"))),
]

# ---------- NOSES ----------
narices = [
    ("Botón", '<circle cx="200" cy="218" r="9" fill="PIELS"/><circle cx="197" cy="215" r="2.5" fill="#fff" opacity=".5"/>'),
    ("Triangular", P("M200 192 L215 228 L188 228 Z", "PIELS")),
    ("Puntiaguda", P("M197 184 L224 225 L195 229 Z", "PIELS")),
    ("Papa", '<ellipse cx="200" cy="219" rx="15" ry="13" fill="PIELS"/>'
             + both(f'<ellipse cx="194" cy="226" rx="3" ry="2" fill="{INK}" opacity=".45"/>')),
    ("Aguileña", P("M195 182 Q220 196 218 222 Q209 232 191 227 Q201 210 195 182 Z", "PIELS")),
]


# ---------- HAIR + BEARDS: cut from an enlarged copy of the current head ----------
# Each piece = (head outline scaled up) intersected with a region (above the hairline / below the cheek line).
# Regions were drawn for the oval head (top y=98) and are shifted by dy = top - 98 for the others.
def cabeza_escalada(h, sx, sy, ay=None):
    _, d, cy, *_ = CABEZAS[h]
    ay = cy if ay is None else ay
    return f'<path d="{d}" transform="translate(200 {ay}) scale({sx} {sy}) translate(-200 {-ay})"/>'


def recorte(uid, h, sx, sy, region, fill="PELO", ay=None, evenodd=False):
    rule = ' clip-rule="evenodd"' if evenodd else ""
    return (f'<clipPath id="{uid}-c">{cabeza_escalada(h, sx, sy, ay)}</clipPath>'
            f'<clipPath id="{uid}-r"><path d="{region}"{rule}/></clipPath>'
            f'<g><g clip-path="url(#{uid}-c)"><g clip-path="url(#{uid}-r)">'
            f'<rect width="{W}" height="{H}" fill="{fill}"/></g></g></g>')


def sube(h):
    return CABEZAS[h][3] - 98


def mover(frag, dy, sx=1.0):
    """shift a fragment drawn for the oval head; optionally stretch it horizontally around x=200"""
    return f'<g transform="translate(200 {dy}) scale({sx:.3f} 1) translate(-200 0)">{frag}</g>'


def pelo_corto(h):
    dy = sube(h)
    reg = (f"M0 0 L400 0 L400 {182+dy} L280 {182+dy} Q270 {128+dy} 236 {120+dy} Q200 {136+dy} 162 {120+dy} "
           f"Q130 {128+dy} 120 {182+dy} L0 {182+dy} Z")
    return "", (recorte(f"pc{h}", h, 1.1, 1.1, reg)
                + mover(P("M188 92 Q220 92 244 112 Q214 104 190 108 Z", "PELOS"), dy, CABEZAS[h][5] / 76))


def pelo_largo(h):
    _, _, cy, top, _, hw = CABEZAS[h]
    dy = sube(h)
    x0, x1 = 200 - hw * 1.14, 200 + hw * 1.14
    atras = (P(CABEZAS[h][1], "PELO", f' transform="translate(200 {cy}) scale(1.14) translate(-200 {-cy})"')
             + P(f"M{x0:.0f} {cy} L{x1:.0f} {cy} L{x1 + 4:.0f} 340 Q250 352 200 344 Q150 352 {x0 - 4:.0f} 340 Z", "PELO"))
    # the face window must end exactly where the region rectangle ends: with evenodd, any part of the
    # window outside the rectangle would be filled with hair (it used to cover the chin and neck)
    ventana = (f"M152 {124+dy} Q206 {150+dy} 250 {126+dy} Q268 {152+dy} 268 {262+dy} L132 {262+dy} "
               f"Q132 {152+dy} 152 {124+dy} Z")
    reg = f"M0 0 L400 0 L400 {262+dy} L0 {262+dy} Z " + ventana
    frente = (recorte(f"pl{h}", h, 1.12, 1.12, reg, evenodd=True)
              + mover(P("M200 84 Q196 104 204 136 L210 136 Q202 108 206 84 Z", "PELOS"), dy))
    return atras, frente


def pelo_afro(h):
    _, _, cy, top, bot, hw = CABEZAS[h]
    hh = (bot - top) / 2
    atras = f'<circle cx="200" cy="{cy - 32}" r="{hw + 20}" fill="PELO"/>'
    for a in range(150, 400, 20):
        if 30 < (a % 360) < 150:
            continue  # leave the bottom open
        r = math.radians(a)
        atras += (f'<circle cx="{200 + (hw + 18) * math.cos(r):.1f}" '
                  f'cy="{cy - 24 + (hh - 6) * math.sin(r):.1f}" r="38" fill="PELO"/>')
    frente = ""
    for i in range(7):
        cx = 200 - 0.84 * hw + i * (1.68 * hw / 6)
        frente += f'<circle cx="{cx:.1f}" cy="{top + 14 - 10 * math.sin(math.pi * i / 6):.1f}" r="19" fill="PELO"/>'
    return atras, frente


def pelo_punk(h):
    dy, k = sube(h), CABEZAS[h][5] / 76
    reg = (f"M0 0 L400 0 L400 {150+dy} L272 {154+dy} Q236 {118+dy} 200 {122+dy} Q164 {118+dy} 128 {154+dy} "
           f"L0 {150+dy} Z")
    puas = (P("M136 130 L136 96 L156 128 L168 72 L186 118 L200 60 L214 118 L232 72 L244 128 L264 96 L264 130 Z", "PELO")
            + P("M200 60 L208 100 L200 116 L192 100 Z", "PELOS"))
    return "", recorte(f"pp{h}", h, 1.06, 1.06, reg) + mover(puas, dy, k)


def pelo_rodete(h):
    _, _, cy, top, _, hw = CABEZAS[h]
    dy = sube(h)
    atras = f'<circle cx="200" cy="{top - 28}" r="36" fill="PELO"/><circle cx="208" cy="{top - 36}" r="14" fill="PELOS"/>'
    reg = (f"M0 0 L400 0 L400 {192+dy} L280 {192+dy} Q276 {130+dy} 230 {116+dy} Q172 {140+dy} 128 {150+dy} "
           f"Q122 {168+dy} 120 {192+dy} L0 {192+dy} Z")
    frente = (recorte(f"pr{h}", h, 1.08, 1.08, reg)
              + P(f"M176 {top - 8} L224 {top - 8} L222 {top + 2} L178 {top + 2} Z", "#D97757"))
    return atras, frente


def pelo_ondulado(h):
    """wide, messy wavy mass: sticks out past the head on top and at the temples, bumpy outline,
    irregular hairline at mid-forehead, puffy sides covering the top half of the ears"""
    _, _, cy, top, _, hw = CABEZAS[h]
    dy, k = sube(h), hw / 76
    estira = f'transform="translate(200 {dy}) scale({k:.3f} 1) translate(-200 0)"'
    # silhouette = enlarged head + a ring of tufts of uneven size (a bit more volume on the left)
    tufos = ""
    ry = cy - top - 4
    for a, r in ((200, 26), (228, 32), (258, 32), (290, 30), (318, 30), (342, 24)):
        t = math.radians(a)
        tufos += f'<circle cx="{200 + (hw - 2) * math.cos(t):.1f}" cy="{cy + ry * math.sin(t):.1f}" r="{r}"/>'
    # wavy hairline (drawn for the oval head, moved and stretched for the others)
    reg = ("M0 0 L400 0 L400 204 L274 204 Q272 172 262 152 Q252 136 238 132 Q228 118 210 124 Q198 116 184 124 "
           "Q166 118 156 132 Q142 136 136 150 Q126 168 126 204 L0 204 Z")
    frente = (f'<clipPath id="po{h}-c">{cabeza_escalada(h, 1.14, 1.08)}{tufos}</clipPath>'
              f'<clipPath id="po{h}-r"><path d="{reg}" {estira}/></clipPath>'
              f'<g clip-path="url(#po{h}-c)"><g clip-path="url(#po{h}-r)">'
              f'<rect width="{W}" height="{H}" fill="PELO"/></g></g>')
    # curls and waves in the darker shade
    rizos = ""
    for d in ("M136 124 Q150 100 178 102 Q192 106 188 118", "M170 90 Q196 74 224 86 Q234 94 226 104",
              "M214 112 Q240 100 260 116", "M158 120 Q180 108 202 116", "M130 162 Q126 142 140 132",
              "M272 160 Q278 140 266 124"):
        rizos += f'<path d="{d}" fill="none" stroke="PELOS" stroke-width="3.5" stroke-linecap="round"/>'
    return "", frente + mover(rizos, dy, k)


def pelo_gorra_militar(h):
    """short back-and-sides (only the temples show) under a 1960s US Army officer's service cap:
    olive crown, dark band, black visor with the gold oak leaves of a field-grade officer, eagle badge"""
    dy, k = sube(h), CABEZAS[h][5] / 76
    reg = (f"M0 {128+dy} L150 {128+dy} Q142 {150+dy} 136 {176+dy} L0 {176+dy} Z "
           f"M400 {128+dy} L250 {128+dy} Q258 {150+dy} 264 {176+dy} L400 {176+dy} Z")
    gorra = (P("M108 106 Q106 76 200 68 Q294 76 292 106 Q290 118 270 120 L130 120 Q110 118 108 106 Z", "#5E6646")
             + P("M124 84 Q200 66 276 84 Q240 78 200 78 Q160 78 124 84 Z", "#737C57")
             + P("M130 114 L270 114 L268 138 L132 138 Z", "#3C4230")
             + P("M132 136 L268 136 Q270 150 252 153 Q200 158 148 153 Q130 150 132 136 Z", "#1F1E1C")
             + P("M150 140 Q200 136 250 140 Q200 142 150 143 Z", "#fff", ' opacity=".25"')
             + P("M134 132 L266 132 L266 137 L134 137 Z", "#C9A23A")
             + "".join(f'<ellipse cx="{x}" cy="{146 + abs(x - 200) / 30:.1f}" rx="6" ry="2.6" fill="#C9A23A" '
                       f'transform="rotate({(x - 200) / 6:.0f} {x} 146)"/>' for x in (154, 168, 182, 218, 232, 246))
             + '<circle cx="200" cy="112" r="13" fill="#D4AF37"/>'
             + P("M184 108 Q192 100 200 108 Q208 100 216 108 L210 116 Q200 112 190 116 Z", "#9C7A1E")
             + '<circle cx="200" cy="104" r="3.5" fill="#9C7A1E"/>')
    return "", recorte(f"pg{h}", h, 1.05, 1.05, reg) + mover(gorra, dy, k)


pelos = [("Corto", pelo_corto), ("Largo", pelo_largo), ("Afro", pelo_afro), ("Punk", pelo_punk), ("Rodete", pelo_rodete),
         ("Ondulado", pelo_ondulado), ("Gorra militar", pelo_gorra_militar)]

# beards: the mouth (fixed at y 250..266) stays visible through an evenodd hole
HUECO = "M177 251 Q200 241 223 251 Q221 274 200 277 Q179 274 177 251 Z"
BIGOTE = ("M166 250 Q184 234 200 243 Q216 234 234 250 Q238 259 227 256 Q212 248 200 252 Q188 248 173 256 "
          "Q162 259 166 250 Z")
REG_COMPLETA = ("M0 198 L138 198 Q142 236 164 240 Q200 232 236 240 Q258 236 262 198 L400 198 L400 900 L0 900 Z "
                + HUECO)
REG_CORTA = ("M0 212 L140 212 Q146 240 166 242 Q200 236 234 242 Q254 240 260 212 L400 212 L400 900 L0 900 Z "
             + HUECO)


def fondo_barba(h, sy=1.25):
    """y where the enlarged beard ends below the chin"""
    return 190 + sy * (CABEZAS[h][4] - 190)


def barba_completa(h):
    return recorte(f"bc{h}", h, 1.08, 1.25, REG_COMPLETA, ay=190, evenodd=True) + P(BIGOTE, "PELOS")


def barba_corta(h):
    return recorte(f"bk{h}", h, 1.03, 1.06, REG_CORTA, ay=190, evenodd=True)


def barba_mago(h):
    b = fondo_barba(h)
    return (recorte(f"bm{h}", h, 1.08, 1.25, REG_COMPLETA, ay=190, evenodd=True)
            + P(f"M150 {b - 24:.0f} Q158 {b + 60:.0f} 200 {b + 110:.0f} Q242 {b + 60:.0f} 250 {b - 24:.0f} Z", "PELO")
            + P(f"M200 {b - 20:.0f} Q206 {b + 40:.0f} 200 {b + 96:.0f} Q194 {b + 40:.0f} 200 {b - 20:.0f} Z", "PELOS")
            + P("M164 250 Q182 232 200 243 Q218 232 236 250 Q252 262 246 276 Q240 258 226 256 Q212 248 200 252 "
                "Q188 248 174 256 Q160 258 154 276 Q148 262 164 250 Z", "PELOS"))


barbas = [
    ("Completa", barba_completa),
    ("Corta", barba_corta),
    ("Bigote", lambda h: P(BIGOTE, "PELO")),
    ("Candado", lambda h: P("M184 270 Q200 266 216 270 L213 296 Q200 306 187 296 Z", "PELO")
     + P("M172 249 Q186 240 200 246 Q214 240 228 249 Q226 254 214 251 Q200 248 186 251 Q174 254 172 249 Z", "PELO")),
    ("De mago", barba_mago),
]

# ---------- BODY base (neck, arms, hands, legs - always drawn, under the clothes) ----------
CUERPO = (P("M180 266 L220 266 L222 318 L178 318 Z", "PIELS")
          + both(P("M112 320 L142 320 L132 550 L104 548 Z", "PIEL") + '<circle cx="118" cy="562" r="16" fill="PIEL"/>')
          + both(P("M142 556 L198 556 L194 800 L146 800 Z", "PIEL")))

# ---------- SHIRTS ----------
TORSO = "M140 306 Q200 324 260 306 L276 342 L272 558 L128 558 L124 342 Z"
MANGA_CORTA = "M118 318 L152 306 L150 398 L100 394 Z"
MANGA_LARGA = "M109 318 L152 306 L139 552 L100 548 Z"
PUNO = "M101 530 L139 534 L138 552 L100 548 Z"


def rayas_musculosa(color):
    s = ""
    for y in (380, 424, 468, 512):
        x0 = lambda yy: 138 - 8 * (yy - 360) / 198
        a, b = x0(y), x0(y + 18)
        s += P(f"M{a:.1f} {y} L{W - a:.1f} {y} L{W - b:.1f} {y + 18} L{b:.1f} {y + 18} Z", color)
    return s


remeras = [
    ("Remera", both(P(MANGA_CORTA, "#D97757") + P("M101 380 L150 384 L150 398 L100 394 Z", "#B85F42"))
     + P(TORSO, "#D97757")
     + P("M166 309 Q200 332 234 309 L238 317 Q200 342 162 317 Z", "#B85F42")
     + f'<circle cx="200" cy="410" r="20" fill="{WHITE}"/>'
     + P("M200 396 L205 406 L216 407 L208 414 L210 425 L200 419 L190 425 L192 414 L184 407 L195 406 Z", "#D97757")),
    ("Suéter", both(P(MANGA_LARGA, "#6A9BCC") + P(PUNO, "#4F7FB0"))
     + P(TORSO, "#6A9BCC")
     + P("M125 400 L275 400 L275 426 L125 426 Z", WHITE)
     + P("M125 436 L275 436 L275 446 L125 446 Z", WHITE)
     + P("M128 534 L272 534 L272 558 L128 558 Z", "#4F7FB0")
     + P("M166 309 Q200 332 234 309 L238 318 Q200 344 162 318 Z", "#4F7FB0")),
    ("Camisa", both(P(MANGA_LARGA, "#BFD3E6") + P(PUNO, "#A3BDD6"))
     + P(TORSO, "#BFD3E6")
     + P("M148 388 L180 388 L180 420 L164 428 L148 420 Z", "#A3BDD6")
     + P("M192 322 L208 322 L204 336 L214 440 L200 458 L186 440 L196 336 Z", "#C2463C")
     + both(P("M158 304 L200 322 L182 350 Z", WHITE))),
    ("Buzo", both(P(MANGA_LARGA, "#788C5D") + P(PUNO, "#5F7247"))
     + P(TORSO, "#788C5D")
     + P("M146 302 Q200 284 254 302 Q268 320 242 334 Q200 350 158 334 Q132 320 146 302 Z", "#5F7247")
     + P("M170 306 Q200 296 230 306 Q224 324 200 328 Q176 324 170 306 Z", "#3F4D2C")
     + P("M154 470 L246 470 L258 540 L142 540 Z", "#5F7247")
     + both(P("M186 336 L191 336 L191 396 L186 396 Z", WHITE) + '<circle cx="188.5" cy="398" r="4" fill="#FAF9F5"/>')
     + P("M128 538 L272 538 L272 558 L128 558 Z", "#5F7247")),
    ("Musculosa", P("M150 306 L170 306 Q200 342 230 306 L250 306 L262 360 L270 558 L130 558 L138 360 Z", WHITE)
     + rayas_musculosa("#2F4A6B")),
    # royal-blue suit jacket, light-blue shirt, textured blue tie, white cuffs showing
    ("Traje", both(P(MANGA_LARGA, "#24569A") + P(PUNO, "#EEF2F6")
                   + P("M101 522 L139 526 L139 532 L101 528 Z", "#1A3F73"))
     + P("M140 306 Q200 318 260 306 L276 342 L274 566 L126 566 L124 342 Z", "#24569A")
     + P("M170 308 L230 308 L204 446 L196 446 Z", "#D7E3F0")
     + P("M194 322 L206 322 L203 334 L209 428 L200 440 L191 428 L197 334 Z", "#3D7391")
     + "".join(P(f"M{196 + (i % 2) * 4} {340 + i * 12} L{201 + (i % 2) * 4} {346 + i * 12}", "none",
                 ' stroke="#2C5870" stroke-width="2" stroke-linecap="round"') for i in range(7))
     + both(P("M170 306 L200 322 L184 346 L164 312 Z", "#EEF2F6")
            + P("M144 306 L168 310 L198 448 L170 384 L150 364 L162 348 Z", "#1A3F73"))
     + f'<circle cx="200" cy="474" r="4.5" fill="#12305A"/>'
     + both(P("M144 508 L180 506 L180 512 L144 514 Z", "#1A3F73"))
     + P("M222 398 L250 395 L250 400 L222 403 Z", "#1A3F73")),
    # 1960s US Army green dress uniform (colonel): khaki shirt, black tie, brass buttons, black sleeve braid,
    # ribbons over the left pocket, silver eagles on the shoulder loops
    ("Uniforme militar", both(P(MANGA_LARGA, "#5E6646") + P(PUNO, "#4A5136")
                              + P("M101 508 L139 512 L139 520 L101 516 Z", "#1F1E1C"))
     + P("M140 306 Q200 318 260 306 L276 342 L274 566 L126 566 L124 342 Z", "#5E6646")
     + P("M170 308 L230 308 L204 432 L196 432 Z", "#CDBE93")
     + P("M194 322 L206 322 L203 334 L208 420 L200 432 L192 420 L197 334 Z", "#262624")
     + both(P("M170 306 L200 322 L184 346 L164 312 Z", "#CDBE93")
            + P("M144 306 L168 310 L198 434 L170 380 L150 362 L162 346 Z", "#4A5136")
            + P("M138 310 L168 314 L166 326 L134 322 Z", "#4A5136")
            + P("M146 316 L152 312 L158 316 L156 321 L148 321 Z", "#D6D3CB")
            + '<circle cx="174" cy="350" r="5" fill="#D4AF37"/>'
            + P("M140 394 L182 392 L182 406 L161 413 L140 406 Z", "#4A5136")
            + '<circle cx="161" cy="404" r="3.5" fill="#D4AF37"/>'
            + P("M136 498 L182 496 L182 512 L159 519 L136 512 Z", "#4A5136")
            + '<circle cx="159" cy="510" r="3.5" fill="#D4AF37"/>')
     + "".join(f'<circle cx="200" cy="{y}" r="5" fill="#D4AF37"/><circle cx="198.5" cy="{y - 1.5}" r="1.6" fill="#fff" opacity=".5"/>'
               for y in (452, 482, 512, 542))
     + "".join(P(f"M{220 + c * 12} {368 + r * 9} L{231 + c * 12} {368 + r * 9} L{231 + c * 12} {376 + r * 9} "
                 f"L{220 + c * 12} {376 + r * 9} Z", col)
               for r, fila in enumerate((("#C2463C", "#FAF9F5", "#2F4A6B"), ("#E0B341", "#3F6B3A", "#C2463C")))
               for c, col in enumerate(fila))),
]

# ---------- PANTS ----------
PIERNAS = "M130 546 L270 546 L276 800 L206 800 L200 600 L194 800 L124 800 Z"
pantalones = [
    ("Jean", P(PIERNAS, "#3E5C8A")
     + both(P("M124 784 L194 784 L194 800 L124 800 Z", "#2D4568"))
     + both('<path d="M140 566 Q162 592 172 566" fill="none" stroke="#2D4568" stroke-width="3"/>')
     + P("M130 546 L270 546 L270 562 L130 562 Z", "#5A3B26")
     + P("M190 544 L210 544 L210 564 L190 564 Z", "#E0B341")
     + '<path d="M200 566 L200 600" fill="none" stroke="#2D4568" stroke-width="3"/>'),
    ("Bermudas", P("M130 546 L270 546 L280 690 L208 690 L200 610 L192 690 L120 690 Z", "#C2A878")
     + both(P("M121 676 L193 676 L192 690 L120 690 Z", "#A08A5C"))
     + both(P("M124 600 L146 600 L146 640 L126 640 Z", "#A08A5C"))
     + P("M130 546 L270 546 L270 560 L130 560 Z", "#A08A5C")),
    ("Pollera", P("M134 546 L266 546 L296 704 L104 704 Z", "#C46686")
     + both(P("M160 562 L176 562 L162 704 L138 704 Z", "#A34D6C"))
     + P("M190 562 L210 562 L214 704 L186 704 Z", "#A34D6C")
     + P("M134 546 L266 546 L268 564 L132 564 Z", "#A34D6C")),
    ("De vestir", P(PIERNAS, "#3A3A37")
     + both('<path d="M160 612 L158 798" fill="none" stroke="#262624" stroke-width="3"/>')
     + P("M130 546 L270 546 L270 560 L130 560 Z", "#262624")),
    ("Cargo", P(PIERNAS, "#6B7A4E")
     + both(P("M124 650 L152 650 L152 708 L126 708 Z", "#556240") + P("M123 644 L154 644 L154 660 L123 660 Z", "#4A5536"))
     + both(P("M150 720 L188 720 L187 750 L151 750 Z", "#556240"))
     + P("M130 546 L270 546 L270 560 L130 560 Z", "#556240")),
    ("De traje", P(PIERNAS, "#24569A")
     + both('<path d="M160 612 L158 798" fill="none" stroke="#1A3F73" stroke-width="3"/>')
     + P("M130 546 L270 546 L270 560 L130 560 Z", "#1A3F73")),
    ("Militar", P(PIERNAS, "#5E6646")
     + both('<path d="M160 612 L158 798" fill="none" stroke="#4A5136" stroke-width="3"/>')
     + P("M130 546 L270 546 L270 560 L130 560 Z", "#4A5136")),
]

# ---------- SHOES (left drawn, mirrored) ----------
zapatos = [
    ("Zapatillas", both(P("M142 792 L196 792 L198 830 L124 832 Q114 830 118 818 Q124 806 142 806 Z", WHITE)
                        + P("M116 826 L198 826 L198 840 L120 840 Q112 836 116 826 Z", "#B0AEA5")
                        + P("M150 804 L180 818 L176 826 L146 812 Z", "#D97757"))),
    ("Botas", both(P("M144 734 L196 734 L198 830 L124 832 Q114 830 118 818 Q124 806 144 802 Z", "#7A4E2D")
                   + P("M142 734 L198 734 L198 750 L142 750 Z", "#5A3820")
                   + P("M116 826 L198 826 L198 842 L120 842 Q112 838 116 826 Z", "#3A2614"))),
    ("Vestir", both(P("M144 798 L196 798 L198 834 L122 836 Q112 832 118 820 Q128 808 144 808 Z", "#1F1E1C")
                    + '<ellipse cx="136" cy="818" rx="8" ry="3" fill="#fff" opacity=".35"/>'
                    + P("M180 832 L198 832 L198 842 L180 842 Z", "#1F1E1C"))),
    ("Sandalias", both(P("M146 790 L194 790 L196 830 L130 832 Q120 830 124 820 Q132 810 146 808 Z", "PIEL")
                       + P("M118 828 L198 828 L198 840 L122 840 Q114 836 118 828 Z", "#8A6A4A")
                       + P("M138 806 L196 812 L196 822 L132 818 Z", "#8A6A4A")
                       + P("M160 790 L170 790 L172 812 L160 812 Z", "#8A6A4A"))),
    ("Botitas", both(P("M144 748 L196 748 L198 830 L124 832 Q114 830 118 818 Q124 806 144 802 Z", "#E0B341")
                     + P("M118 814 Q126 804 144 806 L146 832 L124 832 Q112 830 118 814 Z", WHITE)
                     + P("M116 826 L198 826 L198 840 L120 840 Q112 836 116 826 Z", WHITE)
                     + P("M154 760 L184 768 L184 772 L154 764 Z", "#B88E22")
                     + P("M154 776 L184 784 L184 788 L154 780 Z", "#B88E22"))),
]

# category id, label, thumbnail viewBox, parts, can be empty
CATEGORIAS = [
    ("pelo", "Pelo", "60 30 280 280", pelos, True),
    ("barba", "Barba", "96 180 208 240", barbas, True),
    ("cabeza", "Cabeza", "100 80 200 220", cabezas, False),
    ("boca", "Boca", "160 226 80 56", bocas, False),
    ("cejas", "Cejas", "140 136 120 60", cejas, False),
    ("orejas", "Orejas", "76 140 248 116", orejas, False),
    ("nariz", "Nariz", "160 172 80 70", narices, False),
    ("remera", "Remera", "92 280 216 290", remeras, False),
    ("pantalon", "Pantalón", "96 530 208 290", pantalones, False),
    ("zapatos", "Zapatos", "100 720 200 130", zapatos, False),
]

DEFS = """<defs>
<filter id="sombra" x="-20%" y="-20%" width="150%" height="160%"><feDropShadow dx="3" dy="4" stdDeviation="1.8" flood-color="#2b1d10" flood-opacity="0.32"/></filter>
<filter id="sombra-chica" x="-20%" y="-20%" width="140%" height="150%"><feDropShadow dx="0" dy="1.6" stdDeviation="0.8" flood-color="#2b1d10" flood-opacity="0.3"/></filter>
<filter id="corte" x="-5%" y="-5%" width="110%" height="110%"><feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="2" seed="7" result="n"/><feDisplacementMap in="SourceGraphic" in2="n" scale="3" xChannelSelector="R" yChannelSelector="G"/></filter>
</defs>
<style>.capa > * { filter: url(#sombra-chica); }</style>"""


def slug(s):
    t = s.lower()
    for a, b in zip("áéíóúñ ", "aeioun_"):
        t = t.replace(a, b)
    return t


def standalone(inner):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">\n'
            f'{DEFS}\n<g filter="url(#corte)"><g class="capa" filter="url(#sombra)">{inner}</g></g>\n</svg>\n')


ADAPTAN = {"pelo", "barba"}


def main():
    out = {"ancho": W, "alto": H, "colores": DEFAULTS, "vars": VARS,
           "base": {"cuerpo": tokens_to_style(CUERPO), "cara": tokens_to_style(CARA)},
           "categorias": []}
    parts_dir = HERE / "parts"
    for cid, label, vb, items, opcional in CATEGORIAS:
        d = parts_dir / cid
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)
        cat = {"id": cid, "nombre": label, "vista": vb, "opcional": opcional, "partes": []}
        for i, item in enumerate(items, 1):
            name = item[0]
            if cid in ADAPTAN:  # one version per head shape
                fn = item[1]
                versions = [fn(h) if cid == "pelo" else ("", fn(h)) for h in range(len(CABEZAS))]
                part = {"nombre": name,
                        "atras": [tokens_to_style(bk) for bk, _ in versions],
                        "svg": [tokens_to_style(fr) for _, fr in versions]}
                for h, (hn, *_) in enumerate(CABEZAS):
                    hd = d / f"cabeza_{slug(hn)}"
                    hd.mkdir(exist_ok=True)
                    (hd / f"{i:02d}_{slug(name)}.svg").write_text(
                        standalone(part["atras"][h] + part["svg"][h]), encoding="utf-8")
            else:
                part = {"nombre": name, "svg": tokens_to_style(item[1])}
                (d / f"{i:02d}_{slug(name)}.svg").write_text(standalone(part["svg"]), encoding="utf-8")
            cat["partes"].append(part)
        out["categorias"].append(cat)
    (parts_dir / "_base").mkdir(exist_ok=True)
    (parts_dir / "_base" / "cuerpo.svg").write_text(standalone(out["base"]["cuerpo"]), encoding="utf-8")
    (parts_dir / "_base" / "ojos.svg").write_text(standalone(out["base"]["cara"]), encoding="utf-8")
    (parts_dir / "_base" / "_defs.txt").write_text(DEFS, encoding="utf-8")
    js = "// Generated by build.py - do not edit by hand.\nwindow.PAPEL = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n"
    js += "window.PAPEL.defs = " + json.dumps(DEFS) + ";\n"
    (HERE / "parts.js").write_text(js, encoding="utf-8")
    print("ok:", sum(len(c[3]) for c in CATEGORIAS), "parts")


if __name__ == "__main__":
    main()
