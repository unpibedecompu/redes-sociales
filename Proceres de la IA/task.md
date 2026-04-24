# Próceres de la IA — Task

## Objetivo principal
Hacer del conocimiento común que el actual desarrollo acelerado de la IA es peligroso. La tecnología de IA es tan peligrosa como la tecnología nuclear, y debe gestionarse con las mismas precauciones.

## Objetivo del pilar
Perfilar a personas importantes en el desarrollo de la IA y en la Seguridad de la IA — investigadores, ingenieros, ejecutivos y críticos — para humanizar el debate y mostrar que expertos serios y con credenciales están profundamente preocupados.

## Alineación con el objetivo principal
La autoridad importa para la persuasión. Mostrar que las personas que construyen esta tecnología están entre las más preocupadas por ella es uno de los argumentos más sólidos que tenés. Contrarresta el rechazo de que las preocupaciones por la seguridad vienen de personas que "no entienden la tecnología".

---

## Proceso

### 1. Crear `source.md`

Investigar y documentar al profesional con las siguientes secciones:

- Educación
- Carrera, enfoque y objetivos
- Impacto en el campo
- Impacto general
- Premios y reconocimientos
- Trabajo actual
- Posición general sobre AI Safety
- Principales preocupaciones directamente relacionada a AI Safety
- Acciones y compromisos públicos en AI Safety
- Citas directas relacionadas con la Seguridad en IA
- El giro: cómo y por qué cambió de opinión
- Conexiones relevantes en el campo (solo figuras con impacto significativo en IA y AI Safety)
- Qué pide concretamente

Cada sección debe incluir sus fuentes al final como links de Markdown.

### 2. Crear `estructure_original.md`

Crear `estructure_original.md`, usando la información de source y la estructura base siguiendo la lógica narrativa definida en `narrative_logic.md`.

### 3. Crear `estructure_one_sentence.md`

- Crear `estructure_one_sentece.md` derivada de `estructure_original.md`. Una sola oración por slide, sin lenguaje tecnico, para el publico general. 
- Consulta que par de slide de los puntos (4.,5.) de `narrative_logic.md` utilizar, y que eventos del punto 2. utilizar.
- No utilizar palabras como neurona, red neuronal, backpropagation. 
- Si se puede usar el acronimo IA.

### 4. Crear `carrousel_description.md`

Especificación completa de diseño y texto por slide, derivada de `estructure_one_sentence.md`. Incluye fondo, marco, layout y tabla con cada elemento de texto junto a sus specs tipográficas exactas. Tomar como referencia `template_description.md` y `template.html`.

### 5. Crear `[Nombre_Apellido].html`

Archivo HTML interactivo del carrusel, basado en `carrousel_description.md`. Nombrar el archivo con el nombre completo del prócer en formato `Nombre_Apellido.html` y ubicarlo en el directorio `Próceres de la IA/Nombre Apellido`.

Tomar `template.html` como referencia.

Ask me for aproval between each step