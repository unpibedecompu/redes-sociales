# Historias de los Riesgos Existenciales — Número de Archivo

Ver [estilo general](./general_style.md) para paleta, tipografía y reglas de composición compartidas.

## Elemento gráfico distintivo

**Número de Archivo** — una fecha o sigla histórica aparece en cada slide como elemento tipográfico de fondo: peso `900`, escala gigante (`30rem`–`42rem`), opacidad muy baja. Es el único elemento gráfico del pilar; no hay marcos, corchetes ni formas adicionales. Transmite peso histórico y urgencia documental.

- Posición variable por slide (esquina inferior derecha, superior izquierda, centrado)
- Opacidad `.07`–`.09` sobre fondos claros; `rgba(255,255,255,.07)` sobre fondo de acento
- Contenido: año completo, sigla del mes, o fragmento del año
- Siempre en `position: absolute`, slide con `overflow: hidden`, y siempre detrás del contenido — nunca tapa texto

## Uso de fondos

Este pilar alterna entre lavanda clara, blanco, lavanda profunda y acento según el tipo de slide — ver el detalle exacto en `template_description.md` de este pilar.
