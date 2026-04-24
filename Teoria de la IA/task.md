# Teoría de la IA — Task

## Objetivo principal
Hacer del conocimiento común que el actual desarrollo acelerado de la IA es peligroso. La tecnología de IA es tan peligrosa como la tecnología nuclear, y debe gestionarse con las mismas precauciones.

## Objetivo del pilar
Explicar cómo funciona la IA — arquitecturas, entrenamiento, capacidades y limitaciones — de forma accesible para una audiencia general.

## Alineación con el objetivo principal
Entender cómo funciona la IA es la base para comprender por qué es peligrosa. Este pilar construye la credibilidad y el contexto que hace que tus argumentos de seguridad sean convincentes.

---

## Proceso

### 1. Crear `source.md`

Investigar y documentar el concepto con las siguientes secciones:

- Qué es (definición técnica precisa)
- Cómo funciona (mecanismo central, sin jargon)
- Historia y origen
- Estado actual del campo
- Por qué importa para AI Safety
- Riesgos o limitaciones concretas
- Citas directas de profesionales relevantes
- Conexiones con otros conceptos del pilar
- Lecturas recomendadas

Cada sección debe incluir sus fuentes al final como links de Markdown.

### 2. Crear `estructure_original.md`

Crear `estructure_original.md`, usando la información de source y la estructura base siguiendo la lógica narrativa definida en `narrative_logic.md`.

### 3. Crear `estructure_one_sentence.md`

- Crear `estructure_one_sentece.md` derivada de `estructure_original.md`. Una sola oración por slide, sin lenguaje tecnico, para el publico general.
- Consulta para los puntos con varias opciones en `narrative_logic.md` cual se elige.
- No utilizar palabras como neurona, red neuronal, backpropagation, gradiente. A excepción de que sea el concepto del que se habla. 
- Sí se puede usar el acrónimo IA.

### 4. Crear `carrousel_description.md`

Especificación completa de diseño y texto por slide, derivada de `estructure_one_sentence.md`. Incluye fondo, corchetes, layout y tabla con cada elemento de texto junto a sus specs tipográficas exactas. Tomar como referencia `template_description.md` y `template.html`.

### 5. Crear `[Nombre_Concepto].html`

Archivo HTML interactivo del carrusel, basado en `carrousel_description.md`. Nombrar el archivo con el nombre del concepto en formato `Nombre_Concepto.html` y ubicarlo en el directorio `Teoría de la IA/Nombre Concepto`.

Tomar `template.html` como referencia.

Ask me for approval between each step
