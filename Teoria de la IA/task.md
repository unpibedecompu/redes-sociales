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

### 2. Crear `analogies.md`

- Crear `analogies.md`, escribiendo 5 posible analogias para explicar el concepto, usando la información en `source.md`.

### 3. Crear `estructure_original.md`

- Consultar que analogia se elige de `analogies.md`
- Crear `estructure_original.md`, usando la analogia elegida, la información de `source.md` y la estructura narrativa de `narrative_structure.md`.
- Se pueden usar mas o menos slides según la estructura.

### 4. Crear `estructure_one_sentence.md`

- Consultar que cita y que pregunta se eligieron.
- Crear `estructure_one_sentece.md` derivada de `estructure_original.md`. 
- Usar la menor cantidad de oraciónes por slide, en lo posible 1 sola.
- sin lenguaje tecnico, para el publico general.
- No utilizar palabras como neurona, red neuronal, backpropagation, gradiente. A excepción de que sea el concepto del que se habla. 
- Sí se puede usar el acrónimo IA.

### 5. Crear `carrousel_description.md`

Especificación completa de diseño y texto por slide, derivada de `estructure_one_sentence.md`. Incluye fondo, corchetes, layout y tabla con cada elemento de texto junto a sus specs tipográficas exactas. Tomar como referencia `template_description.md` y `template.html`.

### 6. Crear `[Nombre_Concepto].html`

- Crear archivo HTML interactivo del carrusel, basado en `carrousel_description.md`. Nombrar el archivo con el nombre del concepto en formato `Nombre_Concepto.html` y ubicarlo en el directorio `Teoría de la IA/Nombre Concepto`.
- Tomar `template.html` como referencia.
- El label del pilar muestra solo el título del pilar (ej. "Teoría de la IA"), sin el número ("Pilar 1").
- Los labels de categorización interna — Analogía, El Concepto, AI Safety, Ejemplo, Para pensar — **no deben aparecer en los slides**. Son categorías de trabajo, no contenido visible.

Consultame antes de pasar al siguiente paso
