# Fuentes: RLVR en frontier labs (coding, math y otras tareas)

Fuentes que confirman que los laboratorios de punta usan RLVR (Reinforcement Learning with Verifiable Rewards) para código, matemática y otras tareas de razonamiento.

## OpenAI (o1 / o3)

- [OpenAI o1 System Card — OpenAI](https://openai.com/index/openai-o1-system-card/) / [versión arXiv](https://arxiv.org/abs/2412.16720) — confirma que o1 se entrena con RL a gran escala sobre cadena de razonamiento, y que se entrena para usar herramientas como ejecución de código, permitiéndole "verificar si el código generado compila, pasa los tests provistos" — descripción directa de entrenamiento con recompensa verificable para programación.
- [Competitive Programming with Large Reasoning Models — arXiv 2502.06807](https://arxiv.org/pdf/2502.06807) — detalla entrenamiento RL en programación competitiva con recompensas basadas en pass/fail de tests.

## DeepSeek

- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via RL — arXiv 2501.12948](https://arxiv.org/pdf/2501.12948) — la descripción técnica pública más clara de RLVR a escala frontier: recompensas de precisión (accuracy rewards) basadas en reglas (respuesta correcta en matemática, código que pasa tests) más recompensas de formato, evitando explícitamente un reward model aprendido para prevenir reward hacking.

## Anthropic

- [Job posting: Research Engineer, Code RL — Anthropic](https://job-boards.greenhouse.io/anthropic/jobs/5254364008) — describe un equipo dedicado a usar RL (incluyendo señales verificables de herramientas/tests reales) para mejorar la capacidad de Claude de escribir, editar, testear y debuggear software real.
- [Reinforcement Learning from Human Feedback — arXiv 2504.12501](https://arxiv.org/pdf/2504.12501) — contexto sobre los métodos de Anthropic (Constitutional AI, RLAIF) para comparar con RLVR.

## Moonshot AI (Kimi)

- [Kimi K2 Technical Report — arXiv 2507.20534](https://arxiv.org/pdf/2507.20534) — describe el "Verifiable Rewards Gym", un sistema de recompensa binaria (1/0) basado en reglas que cubre Matemática, STEM, Lógica, Código, Seguimiento de instrucciones y Seguridad. Una de las descripciones de ingeniería más explícitas de infraestructura RLVR publicadas.

## Qwen (Alibaba)

- Múltiples trabajos sobre la familia **Qwen2.5** usan recompensas verificables (exact-match, 1/0) para ganancias de razonamiento matemático vía RL, reflejando el paradigma RLVR en el ecosistema open-weight.

## Fuentes generales / de contexto

- [Reinforcement Learning with Verifiable Rewards Implicitly Incentivizes Correct Reasoning in Base LLMs — arXiv 2506.14245](https://arxiv.org/pdf/2506.14245) — paper de investigación que analiza la mecánica de RLVR across modelos de distintos labs.
- [Awesome-RLVR — GitHub (opendilab)](https://github.com/opendilab/awesome-RLVR) — lista curada y actualizada de papers/modelos RLVR, útil como bibliografía viva.
- [RL Beyond the Verifiable — Tanay Jaipuria](https://www.tanayj.com/p/rl-beyond-the-verifiable) — buen explicador de por qué RLVR funciona bien en dominios verificables (matemática, código) pero no en tareas abiertas.
- [DeepSeek R1's recipe to replicate o1 — Interconnects (Nathan Lambert)](https://www.interconnects.ai/p/deepseek-r1-recipe-for-o1) — análisis técnico bien considerado que conecta los enfoques de OpenAI y DeepSeek.

## Nota

Los papers de **DeepSeek-R1** y el **OpenAI o1 System Card** son las fuentes primarias más citables para la afirmación "los frontier labs usan RLVR para código/matemática" — el primero por detalle metodológico, el segundo por confirmar la práctica en OpenAI aunque con menos detalle técnico.
