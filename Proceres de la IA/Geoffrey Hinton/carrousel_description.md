### Geoffrey Hinton — Especificación del carrusel · Opción B

*7 slides · Paleta Lavanda + Lila Suave · Outfit · Marco Interior*

**Paleta**
- `#9b5de5` — violeta acento
- `#f0e8ff` — lavanda clara
- `#e4d4ff` — lavanda profunda
- `#1a1a1a` — texto principal
- `#ffffff` — blanco

**Tipografía:** Outfit (única familia, variación por peso)

**Composición fija para todos los slides**
- Tamaño: `200×200px` (se escala al ancho del frame)
- Padding externo (slide → marco): `10px` en todos los lados
- Marco: `border: 1.5px solid` · `border-radius: 4px` · `padding: 16px`
- Layout interno: `display: flex` · `flex-direction: column`

---

**Slide 01 · Quién es**

- Fondo: `#9b5de5`
- Marco: `border: 1.5px solid rgba(255,255,255,.4)`
- Layout: `justify-content: flex-end` · `gap: 8px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `Profesionales de la IA` | `0.48rem` · `letter-spacing: .18em` · `uppercase` · `rgba(255,255,255,.7)` |
| Nombre | `Geoffrey Hinton` | `1.1rem` · `weight 900` · `#ffffff` · `line-height: 1.1` |
| Bajada | `El científico que le enseñó a las máquinas a pensar hoy dice que se arrepiente.` | `0.62rem` · `rgba(255,255,255,.8)` · `line-height: 1.4` |
| Tags | `Premio Turing 2018` · `Premio Nobel 2024` · `Ex-Google` | `0.48rem` · `padding: 2px 8px` · `border: 1px solid rgba(255,255,255,.4)` · `border-radius: 20px` · `rgba(255,255,255,.8)` · flex row · `gap: 6px` · `flex-wrap: wrap` |

---

**Slide 02 · Qué hizo · 1986**

- Fondo: `#f0e8ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `gap: 10px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `Trayectoria` | `0.48rem` · `letter-spacing: .15em` · `uppercase` · `#9b5de5` |
| Row | flex · `gap: 8px` · `align-items: flex-start` | — |
| Año | `1986` | `0.52rem` · `weight 700` · `#9b5de5` · `width: 32px` · `flex-shrink: 0` |
| Cuerpo | `Publicó la fórmula que le permite a las computadoras aprender de sus propios errores — una idea que casi nadie tomaba en serio.` | `0.56rem` · `#1a1a1a` · `line-height: 1.5` |

---

**Slide 03 · Qué hizo · 2012**

- Fondo: `#f0e8ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `gap: 10px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `Trayectoria` | `0.48rem` · `letter-spacing: .15em` · `uppercase` · `#9b5de5` |
| Row | flex · `gap: 8px` · `align-items: flex-start` | — |
| Año | `2012` | `0.52rem` · `weight 700` · `#9b5de5` · `width: 32px` · `flex-shrink: 0` |
| Cuerpo | `Un programa que entrenó junto a sus alumnos ganó una competencia mundial de reconocimiento de imágenes, y en pocos años esa idea estaría dentro de todo: los celulares, los autos, los asistentes de voz.` | `0.56rem` · `#1a1a1a` · `line-height: 1.5` |

---

**Slide 04 · El quiebre**

- Fondo: `#f0e8ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `gap: 10px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `El quiebre` | `0.48rem` · `letter-spacing: .15em` · `uppercase` · `#9b5de5` |
| Separador | — | `width: 24px` · `height: 1.5px` · `background: #9b5de5` |
| Cuerpo | `En 2023, los sistemas de IA empezaron a comportarse de formas que él no esperaba ver hasta dentro de décadas, y ahí decidió que tenía que hablar.` | `0.6rem` · `#1a1a1a` · `opacity: .75` · `line-height: 1.7` |

---

**Slide 05 · Qué dijo**

- Fondo: `#e4d4ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `gap: 10px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Comillas | `"` | `1.8rem` · `weight 900` · `#9b5de5` · `opacity: .2` · `line-height: 1` |
| Cita | `Creo que la probabilidad de que esto ponga en riesgo a la humanidad está entre el 10 y el 20 por ciento.` | `0.72rem` · `weight 600` · `italic` · `#1a1a1a` · `line-height: 1.6` |
| Separador | — | `width: 24px` · `height: 1.5px` · `background: #9b5de5` |
| Atribución | `Geoffrey Hinton · 2023` | `0.5rem` · `letter-spacing: .1em` · `uppercase` · `#9b5de5` |

---

**Slide 06 · Para pensar**

- Fondo: `#f0e8ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `align-items: center` · `gap: 8px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `Para pensar` | `0.48rem` · `letter-spacing: .18em` · `uppercase` · `#9b5de5` |
| Separador | — | `width: 24px` · `height: 1.5px` · `background: #9b5de5` |
| Pregunta | `¿Cuánto riesgo aceptarías para algo que no elegiste?` | `0.9rem` · `weight 700` · `#1a1a1a` · `text-align: center` · `line-height: 1.3` |

---

**Slide 07 · Qué sigue**

- Fondo: `#f0e8ff`
- Marco: `border: 1.5px solid #9b5de5`
- Layout: `justify-content: center` · `align-items: center` · `gap: 8px`

| Elemento | Contenido | Tipografía |
|---|---|---|
| Label | `Próximo perfil` | `0.48rem` · `letter-spacing: .18em` · `uppercase` · `#9b5de5` |
| Separador | — | `width: 24px` · `height: 1.5px` · `background: #9b5de5` |
| CTA | `Seguinos para conocer a las personas detrás del debate más importante del siglo.` | `0.58rem` · `#1a1a1a` · `opacity: .65` · `text-align: center` · `line-height: 1.5` · `max-width: 130px` |
| Handle | `@unpibedecompu` | `0.48rem` · `letter-spacing: .18em` · `uppercase` · `#9b5de5` · `margin-top: 4px` |
