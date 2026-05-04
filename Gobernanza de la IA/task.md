# Gobernanza de la IA — Task

## Objetivo principal
Hacer del conocimiento común que el actual desarrollo acelerado de la IA es peligroso. La tecnología de IA es tan peligrosa como la tecnología nuclear, y debe gestionarse con las mismas precauciones.

## Objetivo del pilar
Cubrir el estado actual de la regulación, la política y la coordinación internacional de la IA — la Ley de IA de la UE, órdenes ejecutivas, organismos internacionales propuestos, la Declaración de Bletchley, y cómo podría verse realmente una supervisión significativa.

## Alineación con el objetivo principal
Este pilar completa directamente la analogía nuclear. La razón por la que la tecnología nuclear no acabó con la civilización no es la suerte — es el OIEA, el TNP, los tratados de armas y décadas de difícil diplomacia. La tesis implica que se necesita una gobernanza equivalente para la IA. Este pilar hace ese argumento explícito y muestra a la audiencia cómo se ve el camino a seguir.

---

## Proceso

### 1. Crear `source.md`

Investigar y documentar el mecanismo de gobernanza con las siguientes secciones:

- El mecanismo: qué es, cuándo surgió, quién lo impulsó
- El problema que intenta resolver: por qué existe esta regulación o propuesta
- Qué propone o establece concretamente: alcance, obligaciones, prohibiciones
- Lo que funciona: qué aspectos son efectivos o prometedores
- Lo que no alcanza: brechas, limitaciones, lo que queda sin regular
- El precedente nuclear como modelo: cómo el OIEA o el TNP sirven de referencia
- Citas directas de expertos, policymakers o investigadores relevantes
- Lecturas recomendadas

Cada sección debe incluir sus fuentes al final como links de Markdown.

### 2. Crear `estructure_original.md`

Crear `estructure_original.md`, usando la información de `source.md` y la estructura narrativa definida en `narrative_structure.md`.

### 3. Crear `estructure_one_sentence.md`

- Crear `estructure_one_sentence.md` derivada de `estructure_original.md`.
- Usar la menor cantidad de oraciones por slide, en lo posible 1 sola.
- Sin jerga legal o técnica, para el público general.
- La insuficiencia de la regulación actual debe sentirse como urgencia, no como crítica académica.

### 4. Crear `carrousel_description.md`

Especificación completa de diseño y texto por slide, derivada de `estructure_one_sentence.md`. Incluye fondo, cruces decorativas, layout y tabla con cada elemento de texto junto a sus specs tipográficas exactas. Tomar como referencia `template_description.md` y `template.html`.

### 5. Crear `[Nombre_Tema].html`

- Crear archivo HTML interactivo del carrusel, basado en `carrousel_description.md`.
- Nombrar el archivo con el nombre del tema en formato `Nombre_Tema.html` y ubicarlo en el directorio `Gobernanza de la IA/Nombre Tema`.
- Tomar `template.html` como referencia.
- El label del pilar muestra solo el título ("Gobernanza de la IA"), sin el número.
- Los labels de categorización interna — Por qué importa, Qué dice, Lo que falta, El modelo — **no deben aparecer en los slides**. Son categorías de trabajo, no contenido visible.

Consultame antes de pasar al siguiente paso
