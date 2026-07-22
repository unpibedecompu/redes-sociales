# Carrousel Description — International AI Safety Report 2026

## Identidad visual
Hereda el template **Gobernanza de la IA — Cruces Decorativas**: fondos lavanda, cruces SVG en esquinas, tipografía Outfit, separadores de acento.

## Paleta
| Rol | HEX |
|---|---|
| Fondo A (portada, slides impares de contenido) | `#f0e8ff` lavanda clara |
| Fondo B (slides pares de contenido, citas) | `#e4d4ff` lavanda profunda |
| Fondo CTA | `#9b5de5` violeta acento |
| Cruces y acentos | `#9b5de5` |
| Texto principal | `#1a1a1a` |
| Texto sobre acento | `#ffffff` |

## Configuración
- 11 slides · 1080×1080 px · padding exterior 86 px
- ig-track: `width: 1100%` · ig-item: `flex: 0 0 9.09090909%`

---

## Slide 1 — Portada
- **Fondo:** `#f0e8ff` · **Cruces:** acc `opacity .4` · **Layout:** flex column, justify-end
- Label `2.6rem / 300 / uppercase / ls .18em / #9b5de5`: "Gobernanza de la IA · Informe Internacional"
- Título `5.2rem / 700 / lh 1.1 / #1a1a1a`: "El informe que 30 países encargaron para entender la IA"
- Separador `130×8 px / #9b5de5`
- Subtítulo `3.0rem / 400 / lh 1.45 / #1a1a1a op .7`: "Lo que la ciencia consensuada dice sobre el riesgo real del desarrollo de IA"
- Handle `2.6rem / 300 / uppercase / ls .18em / #9b5de5`: "@unpibedecompu"

## Slide 2 — ¿Qué es?
- **Fondo:** `#e4d4ff` · **Cruces:** acc soft `opacity .25` · **Layout:** flex column, justify-center, gap 48
- Label `2.6rem / 300 / uppercase / #9b5de5`: "qué es"
- Título `4.2rem / 700 / lh 1.25`: "El primer análisis científico global sobre IA de propósito general"
- Separador
- Tres filas (flex row, gap 20): número/flecha `700 #9b5de5` + texto `2.9rem / 400 / lh 1.55 / op .8`
  - `30` países solicitantes, más de 100 expertos científicos participantes
  - `→` Coordinado por Yoshua Bengio, Université de Montréal
  - `→` Objetivo: generar evidencia compartida para que los gobiernos puedan actuar

## Slide 3 — Desbalance de capacidades
- **Fondo:** `#f0e8ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 36
- Label: "mejora en capacidades"
- Título `3.8rem / 700 / lh 1.2`: "La IA resuelve olimpiadas de matemáticas. Pero el avance no es parejo."
- Separador
- Grid 2 columnas, gap 28:
  - **Columna izq** (`bg rgba(155,93,229,.12)`, border-radius 20, padding 32): label "Formal / Técnico" `2.2rem / 700 / #9b5de5 / uppercase`, ítems `2.1rem / #1a1a1a op .85` (Olimpiada de Matemáticas / Código de competición / Escritura estructurada), barra de progreso 90% acc
  - **Columna der** (`bg rgba(26,26,26,.06)`, padding 32): label "Abierto / Cotidiano" `2.2rem / 700 / #1a1a1a op .6`, ítems `2.1rem / op .65` (Razonamiento causal / Consistencia lógica / Comprensión contextual), barra de progreso 52% `rgba(26,26,26,.35)`

## Slide 4 — Trayectoria
- **Fondo:** `#e4d4ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 40
- Label: "trayectoria"
- Título `4.0rem / 700 / lh 1.2`: "¿Qué sigue? Depende de si hay un cuello de botella."
- Separador
- Tres bloques apilados (flex row, emoji + texto), border-left 6px:
  1. 🛑 **Se detiene** — borde `rgba(26,26,26,.2)`, bg `rgba(26,26,26,.04)`, label op .5
  2. ➡️ **Mantiene el ritmo** — borde `#9b5de5`, bg `rgba(155,93,229,.07)`, label `#9b5de5`
  3. ⚡ **Se acelera — ya ocurre** — borde `#1a1a1a`, bg `rgba(26,26,26,.08)`, label `700 #1a1a1a`

## Slide 5 — Riesgos: mal uso
- **Fondo:** `#f0e8ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 40
- Label: "riesgos severos · mal uso"
- Título `4.0rem / 700 / lh 1.2`: "La IA reduce el costo de hacer daño a escala masiva"
- Separador
- Tres bloques (flex row, emoji + texto, border-left 6px acc, bg `rgba(155,93,229,.07)`, border-radius 14):
  1. 🎭 Fraudes, estafas, manipulación e imágenes íntimas no consensuales `2.3rem / lh 1.5`
  2. 💻 Ciberataques más veloces y sofisticados + sublabel `→ Ver: Mythos Preview` en `#9b5de5`
  3. ⚗️ Armas biológicas: reducción de la barrera de acceso para actores sin expertise

## Slide 6 — Riesgos: trabajo y automation bias
- **Fondo:** `#e4d4ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 44
- Label: "riesgos severos · impacto sistémico"
- Título `4.0rem / 700`: "Dos riesgos que se refuerzan mutuamente"
- Separador
- Dos bloques card (border-radius 20, padding 32, gap 14 interno):
  - Card 1 `bg rgba(155,93,229,.08)`: label "Mercado laboral" `2.4rem / 700 / #9b5de5 / uppercase`, body `2.6rem / lh 1.6`
  - Card 2 `bg rgba(26,26,26,.05)`: label "Global Automation Bias" `2.4rem / 700 / #1a1a1a / uppercase`, body `2.6rem / lh 1.6 / op .75`

## Slide 7 — Riesgos: pérdida de control
- **Fondo:** `#f0e8ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 54
- Label: "riesgos severos · pérdida de control"
- Título `4.2rem / 700 / lh 1.25`: "Sistemas que aprenden a perseguir objetivos que no les asignamos"
- Separador
- Cuerpo `3.1rem / 400 / lh 1.7 / op .75`: explicación del riesgo y por qué es difícil de revertir

## Slide 8 — Brechas científicas (quote layout)
- **Fondo:** `#e4d4ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 36
- Label: "gestión de riesgos · brechas científicas"
- Comillas decorativas `9.7rem / 900 / #9b5de5 op .2`, mt -20
- Cita `3.0rem / 600 / italic / lh 1.6 / #1a1a1a`, mt -60 (overlap con comillas)
- Separador
- Fuente `2.4rem / 300 / uppercase / ls .1em / #9b5de5`: "International AI Safety Report 2026"

## Slide 9 — Capacidad institucional
- **Fondo:** `#f0e8ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 44
- Label: "gestión de riesgos · instituciones"
- Título `4.0rem / 700 / lh 1.2`: "Lo que hay que construir: evidencia más rápida, coordinación sin fronteras"
- Separador
- Dos bullets (dot `10×10 / #9b5de5` + texto `2.9rem / lh 1.6 / op .8`), gap 28

## Slide 10 — Cita institucional
- **Fondo:** `#e4d4ff` · **Cruces:** acc soft · **Layout:** flex column, justify-center, gap 43
- Comillas decorativas `9.7rem / 900 / #9b5de5 op .2`
- Cita `3.9rem / 600 / italic / lh 1.6`, mt -50 (overlap)
- Separador
- Fuente `2.7rem / 300 / uppercase / ls .1em / #9b5de5`: "International AI Safety Report 2026"

## Slide 11 — CTA
- **Fondo:** `#9b5de5` · **Cruces:** blanco `opacity .4` · **Layout:** flex column, center+center, text-center
- Label `2.6rem / 300 / uppercase / rgba(255,255,255,.7)`: "seguí aprendiendo"
- Título `4.6rem / 700 / lh 1.2 / #ffffff`: "La tecnología no espera. Las instituciones, sí."
- Separador `rgba(255,255,255,.5)`
- Cuerpo `3.0rem / 400 / lh 1.5 / #fff op .8 / max-width 750px`
- Handle `2.6rem / 300 / uppercase / rgba(255,255,255,.9)`: "@unpibedecompu"
