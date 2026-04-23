# Template: Próceres de la IA — Marco Interior

## Estilo visual
**Marco Interior** — un borde fino de color acento enmarca todo el contenido dentro de cada slide, con márgenes uniformes de 10px en todos los lados. El marco es el único elemento gráfico; no hay formas adicionales, texturas ni decoraciones.

## Paleta
| Rol | HEX |
|---|---|
| Fondo portada | `#9b5de5` (violeta acento) |
| Fondo slides de contenido | `#f0e8ff` (lavanda clara) |
| Fondo slide de cita | `#e4d4ff` (lavanda profunda) |
| Marco y acentos | `#9b5de5` |
| Texto principal | `#1a1a1a` |

## Tipografía
**Outfit** — familia única, variación por peso.
- Nombre del prócere: `900`
- Títulos de sección: `700`
- Citas: `600 italic`
- Cuerpo: `400`
- Labels / tags: `300`, `letter-spacing: .15em`, `uppercase`

## Estructura de los 6 slides

### 01 · Portada
- Fondo: violeta acento (`#9b5de5`)
- Marco: `rgba(255,255,255,.4)` — blanco semitransparente
- Contenido: nombre del prócere + bajada de una línea + tags de credenciales

### 02 · Trayectoria
- Fondo: lavanda clara
- Marco: violeta acento
- Contenido: 3 hitos cronológicos con año destacado en violeta

### 03 · Contexto de la cita
- Fondo: lavanda clara
- Marco: violeta acento
- Contenido: label + frase fuerte en bold + separador + argumento corto que establece por qué las palabras de esta persona tienen peso antes de leer la cita

### 04 · Cita sobre riesgos de la IA
- Fondo: lavanda profunda
- Marco: violeta acento
- Contenido: comillas decorativas (`opacity: .2`) + cita textual en cursiva + atribución

### 05 · Por qué importa
- Fondo: lavanda clara
- Marco: violeta acento
- Contenido: label + frase fuerte en bold + separador + argumento de 2-3 oraciones

### 06 · Cierre
- Fondo: lavanda clara
- Marco: violeta acento
- Contenido: "próximo perfil" + CTA + @unpibedecompu

## Reglas de composición
- Padding del slide al marco: `10px` en todos los lados
- Padding interior del marco al contenido: `16px`
- Border del marco: `1.5px solid`
- Border-radius del marco: `4px`
- Separador entre secciones: línea de `24px × 1.5px` en acento
- Labels de sección: `0.48rem`, `letter-spacing: .15em`, `uppercase`

## Lógica narrativa
Cada carrusel de Próceres sigue esta secuencia fija:
1. **Quién es** — impacto visual inmediato con el nombre y una bajada que engancha. Una slide.
2. **Qué hizo** — trayectoria cronológica que establece credibilidad. Una slide por evento.
3. **el quiebre** — el contexto que lo lleva a decir la cita. Una slide.
4. **Qué dijo** — cita directa sobre riesgos de la IA, sin intermediarios. Una slide.
5. **Para pensar** - Pregunta abierta para la audiencia basada en la cita y autoridad de la persona. Una slide.
6. **Qué sigue** — CTA para continuar la serie. Una slide.
