# Template: Historia de los Riesgos Existenciales — Número de Archivo

## Estilo visual
**Número de Archivo** — una fecha o sigla histórica aparece en cada slide como elemento tipográfico de fondo: peso 900, escala gigante, opacidad muy baja. El año es el único elemento gráfico; no hay marcos, corchetes, texturas ni formas adicionales. El estilo transmite peso histórico y urgencia documental.

## Paleta
| Rol | HEX |
|---|---|
| Fondo portada | `#f0e8ff` (lavanda clara) |
| Fondo slides de contenido | `#ffffff` (blanco) |
| Fondo slides de dato/relación | `#f0e8ff` (lavanda clara) |
| Fondo slide de cita | `#e4d4ff` (lavanda profunda) |
| Fondo slide de para pensar | `#e4d4ff` (lavanda profunda) |
| Fondo slide de cierre | `#9b5de5` (violeta acento) |
| Número de fondo (fondos claros) | `#9b5de5` · `opacity: .08` |
| Número de fondo (fondo acento) | `#ffffff` · `opacity: .07` |
| Acentos y separadores | `#9b5de5` |
| Texto principal | `#1a1a1a` |

## Tipografía
**Outfit** — familia única, variación por peso.
- Año / número de fondo: `900`, escala gigante, `opacity: .07–.09`
- Títulos / H1: `700`
- Dato estadístico principal: `900`
- Citas: `600 italic`
- Cuerpo: `400`
- Labels / tags: `300`, `letter-spacing: .15em`, `uppercase`

## Elemento gráfico central: Número de Archivo

El año del evento histórico aparece en todos los slides como fondo tipográfico:
- **Peso:** `font-weight: 900`
- **Tamaño:** entre `30rem` y `42rem` — suficiente para que el número desborde los bordes del slide
- **Posición:** variable por slide — esquina inferior derecha, superior izquierda, centrado
- **Opacidad:** `.07–.09` sobre fondos claros; `rgba(255,255,255,.07)` sobre fondo acento
- **Contenido:** año completo (ej. "1962"), sigla del mes (ej. "OCT"), o fragmento (ej. "'62")
- El número está en `position: absolute` con `overflow: hidden` en el slide
- Siempre detrás del contenido — nunca tapa texto

## Estructura de los slides

### 01 · Portada
- Fondo: lavanda clara (`#f0e8ff`)
- Número de fondo: año completo · `bottom: -60px; right: -30px` · `opacity: .09`
- Contenido: label del pilar + título hook + separador + bajada + @handle

### 02 · El Momento
- Fondo: blanco (`#ffffff`)
- Número de fondo: mes abreviado o año completo · `top: -30px; left: -20px` · `opacity: .07`
- Contenido: label de fecha + título del momento + separador + texto

### 03 · El Margen
- Fondo: lavanda profunda (`#e4d4ff`)
- Número de fondo: año completo · centrado · `opacity: .07`
- Contenido: label + dato estadístico grande (peso 900) + subtítulo del dato + separador + descripción

### 04 · El Paralelo
- Fondo: blanco (`#ffffff`)
- Número de fondo: fragmento del año · `bottom: -40px; right: -20px` · `opacity: .07`
- Contenido: label + texto de conexión con la IA + separador + cuerpo

### 05 · Cita
- Fondo: lavanda profunda (`#e4d4ff`)
- Número de fondo: año completo · `top: -30px; left: -15px` · `opacity: .07`
- Contenido: comillas decorativas (`opacity: .2`) + cita en cursiva + separador + atribución

### 06 · Para pensar
- Fondo: lavanda clara (`#f0e8ff`)
- Número de fondo: año completo · `bottom: -40px; left: -10px` · `opacity: .08`
- Contenido: label + pregunta en bold + separador + frase de anclaje breve

### 07 · CTA
- Fondo: violeta acento (`#9b5de5`)
- Número de fondo: año completo · centrado · `rgba(255,255,255,.07)`
- Contenido: label + CTA + separador + @unpibedecompu

## Reglas de composición
- Tamaño de slide: `1080×1080 px` (Instagram nativo)
- Padding del contenido: `86px` en todos los lados
- Separador entre secciones: línea de `130px × 8px` en acento
- Labels de sección: `2.6rem`, `letter-spacing: .15em`, `uppercase`, `font-weight: 300`
- El número de fondo siempre en `position: absolute`, slide con `overflow: hidden`
