# Sistema de Diseño — Estilo General

Este documento resume las decisiones visuales que aplican a todos los pilares de contenido. El proceso completo de decisión (paletas y tipografías consideradas, criterios de selección) vive en [`style_decision_process/`](./style_decision_process/).

## Paleta: Lavanda + Lila Suave

| Rol | Nombre | HEX |
|---|---|---|
| Fondo principal | Lavanda clara | `#f0e8ff` |
| Fondo secundario | Lavanda profunda | `#e4d4ff` |
| Acento | Violeta medio | `#9b5de5` |
| Texto | Negro suave | `#1a1a1a` |

**Regla de uso:** fondos lavanda (clara o profunda) como base dominante en la mayoría de los slides · violeta `#9b5de5` para acentos, tags, separadores y el elemento gráfico distintivo de cada pilar · negro suave `#1a1a1a` para todo el texto · el acento violeta también sirve como fondo sólido en slides de cierre/CTA, con texto en blanco.

## Tipografía: Outfit

Una única familia (Google Fonts, `Outfit`), variando solo por peso:

| Peso | Uso |
|---|---|
| `900` | Datos/números destacados, elementos gráficos de fondo |
| `700` | Títulos principales y de sección |
| `600 italic` | Citas |
| `400` | Cuerpo de texto |
| `300` | Labels y tags — siempre `letter-spacing: .15em`, `uppercase` |

## Reglas de composición compartidas

- **Tamaño de slide:** `1080×1080 px` (Instagram nativo)
- **Padding de contenido:** `86px` en todos los lados (salvo que el elemento gráfico del pilar redefina el margen exterior)
- **Separador entre secciones:** línea de `130px × 8px` en color acento
- **Labels de sección:** `2.6rem`, `letter-spacing: .15em`, `uppercase`, peso `300`

## Principio del elemento gráfico

Cada pilar tiene **un único elemento gráfico decorativo distintivo** que lo diferencia visualmente de los demás, manteniendo la misma paleta y tipografía. No se combinan múltiples elementos decorativos en un mismo pilar, y se evitan degradados, texturas o paletas institucionales — el objetivo es coherencia y minimalismo, no ruido visual.

| Pilar | Elemento gráfico distintivo |
|---|---|
| [Teoría de la IA](./teoria_de_la_ia.md) | Corchetes Técnicos |
| [Profesionales de la IA](./profesionales_de_la_ia.md) | Marco Interior |
| [Historias de los Riesgos Existenciales](./historias_de_los_riesgos_existenciales.md) | Número de Archivo |
| [Gobernanza de la IA](./gobernanza_de_la_ia.md) | Cruces Decorativas |
| AI Safety | Círculos Decorativos |
| Noticias de la IA | Palabras grandes repetidas |

Para el detalle de contenido slide por slide de cada pilar, ver el `template_description.md` dentro de la carpeta de ese pilar.
