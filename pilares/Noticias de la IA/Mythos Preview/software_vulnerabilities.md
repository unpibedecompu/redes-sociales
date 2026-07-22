# Software con Vulnerabilidades Descubiertas por Mythos Preview

> Basado en reportes formales de Anthropic (red.anthropic.com), la Cloud Security Alliance, Project Glasswing y cobertura periodística especializada (abril–junio 2026).

---

## Contexto

Claude Mythos Preview es un modelo de IA general de Anthropic que demostró ser capaz de descubrir y explotar vulnerabilidades de software a escala industrial. Identificó más de **23,000 vulnerabilidades potenciales** en más de **1,000 proyectos open source**, de las cuales 1,726 han sido confirmadas por firmas externas —más de 1,000 calificadas como "alta" o "crítica" severidad.

Anthropic lanzó **Project Glasswing** para coordinar el parcheo responsable antes de que actores hostiles puedan replicar capacidades similares.

---

## Sistemas Operativos

| Software | Vulnerabilidad Notable | Detalles |
|---|---|---|
| **Linux Kernel** | Escalación de privilegios a root | Mythos encadenó múltiples vulnerabilidades del kernel para escalar de usuario ordinario a control total del sistema |
| **OpenBSD** | Bug en TCP SACK (27 años de antigüedad) | Permite a un atacante remoto crashear cualquier host OpenBSD que responda por TCP |
| **FreeBSD** | RCE en implementación NFS (CVE-2026-4747, 17 años) | Permite a un atacante no autenticado obtener control completo del servidor desde cualquier punto de internet |
| **Windows** | Múltiples vulnerabilidades | Incluido en "todos los sistemas operativos principales" según el reporte formal |
| **macOS** | Múltiples vulnerabilidades | Incluido en "todos los sistemas operativos principales" según el reporte formal |

---

## Navegadores Web

| Software | Vulnerabilidades Encontradas | Exploits Desarrollados |
|---|---|---|
| **Mozilla Firefox** | 271 zero-days | 181 exploits funcionales (incluyendo un chain de 4 vulns con JIT heap spray que escapó el sandbox del renderer y del OS) |
| **Google Chrome / Chromium** | Confirmado en "todos los navegadores principales" | — |
| **Apple Safari** | Confirmado en "todos los navegadores principales" | — |
| **Microsoft Edge** | Confirmado en "todos los navegadores principales" | — |

---

## Librerías y Componentes de Software

| Software | Vulnerabilidad Notable | CVE / Detalles |
|---|---|---|
| **FFmpeg** | Bug en codec H.264 (16 años de antigüedad) | Componente de media distribuido en casi todos los navegadores modernos y pipelines de video |
| **wolfSSL** | Verificación incorrecta de certificados ECDSA | CVE-2026-5194 — acepta digests más pequeños de lo permitido al verificar certificados (CWE-295) |
| **OpenSSL** | Mencionado en proyectos OSS auditados | Parte del ecosistema de 1,000+ proyectos escaneados |
| **curl** | Mencionado en proyectos OSS auditados | Parte del ecosistema de 1,000+ proyectos escaneados |

---

## Scope General (Project Glasswing)

Mythos escaneó más de **1,000 proyectos de software open source críticos**. Anthropic no ha publicado la lista completa (99% de los hallazgos permanecen bajo divulgación responsable), pero los reportes formales confirman que las vulnerabilidades afectan:

- Todos los **sistemas operativos principales** (Linux, Windows, macOS, FreeBSD, OpenBSD)
- Todos los **navegadores web principales** (Chrome, Firefox, Safari, Edge)
- **Infraestructura crítica** de internet (librerías de red, TLS/SSL, codecs multimedia)
- Software con décadas de auditoría humana previa — Mythos encontró bugs que sobrevivieron 27 años de revisión

---

## Estadísticas Clave

| Métrica | Valor |
|---|---|
| Vulnerabilidades potenciales detectadas | 23,000+ |
| Proyectos OSS escaneados | 1,000+ |
| Vulnerabilidades confirmadas por firmas externas | 1,726 |
| Calificadas "alta" o "crítica" | 1,000+ |
| Críticas/altas estimadas al finalizar escaneo | ~6,200 |
| Ya parcheadas | 75 críticas/altas |
| Vulnerabilidades sin parchear | ~99% |

---

## Fuentes

- [Claude Mythos Preview — red.anthropic.com (reporte formal)](https://red.anthropic.com/2026/mythos-preview/)
- [Project Glasswing — Anthropic](https://www.anthropic.com/glasswing)
- [Claude Mythos: AI Vulnerability Discovery and Containment Failures — Cloud Security Alliance](https://labs.cloudsecurityalliance.org/research/ai-vuln-discovery-containment-claude-mythos-v1-0-csa-styled/)
- [Anthropic: Mythos Detected 23,000 Potential Vulnerabilities Across 1,000 OSS Projects — SecurityWeek](https://www.securityweek.com/anthropic-mythos-detected-23000-potential-vulnerabilities-across-1000-oss-projects/)
- [Claude Mythos Has Found 271 Zero-Days in Firefox — Schneier on Security](https://www.schneier.com/blog/archives/2026/04/claude-mythos-has-found-271-zero-days-in-firefox.html)
- [Behind the Scenes: Hardening Firefox with Claude Mythos Preview — Mozilla Hacks](https://hacks.mozilla.org/2026/05/behind-the-scenes-hardening-firefox/)
- [Anthropic's Claude Mythos Preview: The AI Cybersecurity Inflection Point — Bishop Fox](https://bishopfox.com/blog/anthropics-claude-mythos-preview-the-ai-cybersecurity-inflection-point)
- [Project Glasswing: What Mythos Showed Us — Cloudflare Blog](https://blog.cloudflare.com/cyber-frontier-models/)
- [When AI Becomes the Cyber Attacker: Mythos and What Comes Next — Data Protection Report](https://www.dataprotectionreport.com/2026/05/when-ai-becomes-the-cyber-attacker-mythos-and-what-comes-next/)
- [Claude Mythos Preview Exposes Hidden Code Flaws Fast — IEEE Spectrum](https://spectrum.ieee.org/anthropic-claude-mythos-preview-code)
- [Mythos Detected 23,000 Vulnerabilities Across 1,000 OSS Projects — Slashdot](https://news.slashdot.org/story/26/05/26/2026259/mythos-detected-23000-vulnerabilities-across-1000-oss-projects)
