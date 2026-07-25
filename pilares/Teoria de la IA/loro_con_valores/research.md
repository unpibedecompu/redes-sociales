# Cómo entrenan los LLM los frontier labs (2024-2026)

Investigación sobre el pipeline de entrenamiento que usan los laboratorios de punta (OpenAI, Anthropic, DeepSeek, Meta, Google, Nvidia, etc.) para producir sus modelos actuales. Ordenado cronológicamente según en qué etapa del entrenamiento ocurre cada técnica.

## Resumen del pipeline (orden real)

```
1. Pretraining (preentrenamiento)
2. Mid-training (annealing / curriculum tardío)
3. Post-training
   3.1 SFT (Supervised Fine-Tuning) — "cold start"
   3.2 Alineamiento de preferencias: RLHF clásico (PPO) / DPO / RLAIF (Constitutional AI)
   3.3 RL con recompensas verificables (RLVR): razonamiento, matemática, código, uso de herramientas
   3.4 Distilación (de modelos "razonadores" grandes a modelos chicos/rápidos)
```

La intuición del usuario (pretraining → postraining → RLHF → RL para programar) es básicamente correcta, pero en los labs de punta esto ya no es una secuencia lineal simple: es un pipeline modular donde cada etapa ataca un tipo distinto de "alineamiento" (de comportamiento, de preferencia, y de lógica/razonamiento).

---

## 1. Pretraining

El modelo aprende a predecir el siguiente token sobre un corpus masivo de texto (billones de tokens: web, libros, código, papers, etc.). Acá se forma el "conocimiento" del modelo. Es la etapa que más compute consume (semanas a meses de entrenamiento distribuido).

- Llama 3 (405B) se preentrenó sobre ~15 billones de tokens multilingües (vs. 1.8T de Llama 2), con pipelines de limpieza y deduplicación cada vez más sofisticados.
- El consenso 2025-2026 es que la **calidad de los datos importa más que la cantidad cruda**: modelos chicos entrenados con datos curados/verificados igualan a modelos grandes entrenados con datos promedio. Esto matiza las leyes de escala de Chinchilla (que asumían calidad uniforme de datos y proponían ~20 tokens de entrenamiento por parámetro).

## 2. Mid-training (etapa intermedia, "annealing")

Etapa que se popularizó como concepto separado desde 2025 (Allen AI la formalizó). Es la última fase del preentrenamiento: se baja el learning rate ("annealing") y se cambia la mezcla de datos para sobre-representar código, matemática y datos tipo instrucción, antes de pasar al post-training. DeepSeek-V3, Qwen3 y YuLan-Mini, por ejemplo, hacen upsampling de matemática/código/ciencia en esta fase para mejorar razonamiento.

## 3. Post-training

### 3.1 SFT (Supervised Fine-Tuning / instruction tuning)

Se afina el modelo preentrenado con pares (instrucción → respuesta deseada), para que deje de ser un "autocompletador de texto" y empiece a comportarse como asistente que sigue instrucciones. Usa muchísimos menos datos que el pretraining (millones de ejemplos curados en vez de billones de tokens). Nemotron 3 Super, por ejemplo, usó ~7M de ejemplos de SFT.

Tendencia 2025-2026: el SFT dejó de ser el "producto final" y pasó a ser sobre todo el **cold start** que prepara al modelo para la etapa de RL siguiente (esto es explícito en el paper de DeepSeek-R1).

### 3.2 Alineamiento de preferencias humanas

**RLHF clásico (estilo InstructGPT/ChatGPT):**
1. SFT sobre demostraciones humanas.
2. Entrenar un modelo de recompensa (reward model) con comparaciones humanas (A es mejor que B).
3. Optimizar la política con RL (PPO) contra ese reward model.

Este es el pipeline que popularizó InstructGPT (OpenAI, 2022) y que se convirtió en la base de ChatGPT y GPT-4.

**DPO (Direct Preference Optimization):** alternativa más simple/estable a PPO que optimiza directamente sobre pares de preferencias sin entrenar un reward model separado ni hacer RL online. Fue el estándar en 2024 (Llama 3, Tülu 3), pero según revisiones de 2026 está empezando a desaparecer de las recetas de los labs más de punta, quedando más como herramienta para bootstrapping de modelos base más débiles.

**RLAIF / Constitutional AI (Anthropic, Claude):** en vez de depender solo de feedback humano, se usa una "constitución" (documento con principios, inspirado en cosas como la Declaración Universal de los DD.HH. y las políticas de uso de Anthropic) para que el propio modelo:
1. Fase supervisada: genera respuestas, se autocritica contra los principios de la constitución, y se re-entrena sobre las respuestas revisadas.
2. Fase de RL: un modelo de IA (no humanos) juzga qué respuesta es mejor según la constitución, se entrena un modelo de preferencias con esas comparaciones sintéticas, y se hace RLHF normal pero con feedback de IA en vez de feedback humano — de ahí el nombre RLAIF (RL from AI Feedback).

### 3.3 RL con recompensas verificables (RLVR) — acá entra el "RL para programar"

Esta es la pieza que el usuario mencionó como "RL para hacer mejor al modelo en programación". La idea central: en vez de usar un reward model entrenado sobre preferencias humanas (subjetivo y hackeable), se usa una **recompensa verificable automáticamente**:
- En matemática: ¿la respuesta final coincide con el resultado correcto?
- En código: ¿el código pasa los tests unitarios / compila / corre?
- En otros dominios: verificación formal, o auto-consistencia cuando no hay ground truth.

Esto da una señal binaria (1/0) sin cuello de botella humano, permitiendo entrenar con millones de verificaciones por día, y reduce mucho el "reward hacking" (un test pasa o no pasa, no es negociable).

Origen del concepto: DeepSeekMath y Tülu 3. Popularizado a gran escala por:

- **DeepSeek-R1** (DeepSeek, enero 2025): pipeline de 4 etapas — (1) "cold start" con una pequeña cantidad de datos de cadena de razonamiento larga (long CoT) para afinar el modelo base; (2) RL orientado a razonamiento puro (con recompensa de consistencia de idioma para evitar mezcla de idiomas); (3) SFT con datos generados por rejection sampling combinando razonamiento y no-razonamiento; (4) segunda etapa de RL para alinear con preferencias humanas de utilidad e inocuidad. Usan **GRPO (Group Relative Policy Optimization)**, que elimina la necesidad de un modelo crítico separado (a diferencia de PPO) normalizando la recompensa dentro de un grupo de respuestas muestreadas para el mismo prompt. Su variante DeepSeek-R1-Zero mostró que se puede incentivar razonamiento **sin SFT previo**, con RL puro directo sobre el modelo base — emergen solas conductas como auto-verificación, reflexión y el famoso "aha moment" donde el modelo se detiene a re-evaluar su propio razonamiento.
- **OpenAI o1 / o3** (OpenAI, 2024-2025): "modelos de razonamiento grandes" (LRM) entrenados con RL a gran escala para que aprendan a usar su cadena de pensamiento de forma productiva antes de responder — aprenden a corregir errores, romper pasos difíciles en pasos más simples, e intentar estrategias distintas cuando la actual no funciona. Un hallazgo clave de OpenAI: el rendimiento escala tanto con más cómputo de entrenamiento (RL) como con más cómputo de inferencia (dejar "pensar" más tiempo al modelo, test-time compute).
- **DAPO** (ByteDance/Tsinghua): variante de GRPO que estabiliza el razonamiento en horizontes largos (token-level policy gradients), logrando resultados comparables con muchos menos pasos de entrenamiento.

### 3.4 Distilación

Paso final cada vez más usado: destilar el conocimiento/razonamiento de modelos grandes entrenados con RL hacia modelos más chicos y baratos de servir (ej. las versiones "distill" de DeepSeek-R1 sobre Qwen/Llama). Tendencia más nueva (2026): distilación multi-teacher on-policy (MOPD) — se entrenan varios modelos "especialistas" de dominio (cada uno con su propio SFT + RL) y después se consolida todo en un modelo "estudiante" general que aprende de varios profesores a la vez (usando divergencia KL inversa), en vez de tener un solo pipeline monolítico de RL.

---

## Línea de tiempo simplificada para redes / guión

1. **Pretraining**: leer internet, aprender lenguaje y conocimiento del mundo (billones de tokens).
2. **Mid-training**: últimos ajustes de la fase de preentrenamiento, subiendo la proporción de código/matemática.
3. **SFT**: le enseñan a comportarse como asistente (seguir instrucciones), con ejemplos curados.
4. **RLHF / Constitutional AI / DPO**: ajustan el modelo para que sea más útil, más seguro y "converse mejor", según preferencias humanas (o de otra IA juzgando según principios escritos).
5. **RLVR (RL con recompensas verificables)**: acá es donde entra específicamente el entrenamiento para programar y hacer matemática — el modelo prueba soluciones, un verificador automático (tests, checker de resultado) le dice si acertó o no, y mejora por prueba y error a gran escala. Esto es lo que hizo emerger a los "modelos de razonamiento" (o1, o3, DeepSeek-R1).
6. **Distilación** (opcional): se comprime todo ese conocimiento/razonamiento en modelos más chicos y rápidos.

---

## Fuentes

- [Frontier post-training recipe review with Finbarr Timbers — interconnects.ai](https://www.interconnects.ai/p/frontier-post-training-recipe-review)
- [Post-Training in 2026: GRPO, DAPO, RLVR & Beyond — llm-stats.com](https://llm-stats.com/blog/research/post-training-techniques-2026)
- [Post-Training LLMs Guide: SFT, RLHF, DPO & GRPO Explained (2026) — Sundeep Teki](https://www.sundeepteki.org/advice/the-complete-guide-to-post-training-llms-how-sft-rlhf-dpo-and-grpo-shape-llms)
- [Reinforcement Learning for LLM Post-Training: A Survey — arXiv 2407.16216](https://arxiv.org/pdf/2407.16216)
- [Foundation model training data: How frontier labs build pre-training datasets at scale — Toloka](https://toloka.ai/blog/how-frontier-labs-build-pre-training-datasets/)
- [What's the deal with mid-training? — Vintage Data](https://vintagedata.org/blog/posts/what-is-mid-training)
- [DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning — arXiv 2501.12948](https://arxiv.org/pdf/2501.12948)
- [DeepSeek-R1 incentivizes reasoning in LLMs through reinforcement learning — Nature](https://www.nature.com/articles/s41586-025-09422-z)
- [Pipeline for Training DeepSeek-R1 — Medium (DhanushKumar)](https://medium.com/@danushidk507/pipeline-for-training-deepseek-r1-0d99933c3b4f)
- [DeepSeek-R1: Redefining Reasoning with Reinforcement Learning — Medium (Sushant Gautam)](https://sushantgautm.medium.com/deepseek-r1-redefining-reasoning-with-reinforcement-learning-1e2bc9f38bda)
- [deepseek-ai/DeepSeek-R1 — Hugging Face model card](https://huggingface.co/deepseek-ai/DeepSeek-R1)
- [Learning to reason with LLMs — OpenAI (o1)](https://openai.com/index/learning-to-reason-with-llms/)
- [OpenAI o1 System Card — OpenAI](https://cdn.openai.com/o1-system-card.pdf)
- [Notes on OpenAI's new o1 chain-of-thought models — Simon Willison](https://simonwillison.net/2024/Sep/12/openai-o1/)
- [o1: A Technical Primer — LessWrong](https://www.lesswrong.com/posts/byNYzsfFmb2TpYFPW/o1-a-technical-primer)
- [LLM Reasoning in OpenAI o-Series Models — Baeldung](https://www.baeldung.com/cs/chatgpt-o1-o3)
- [Constitutional AI: Harmlessness from AI Feedback — Anthropic](https://www.anthropic.com/research/constitutional-ai-harmlessness-from-ai-feedback)
- [Constitutional AI: Harmlessness from AI Feedback — arXiv 2212.08073](https://arxiv.org/pdf/2212.08073)
- [Constitutional AI: How Anthropic Trains Models Using Written Principles — TDWI](https://tdwi.org/blogs/ai-101/2026/05/constitutional-ai.aspx)
- [Constitutional AI: How Anthropic Teaches Claude Right from Wrong — Medium (Ramdhan Hidayat)](https://medium.com/@ramdhanhdy/constitutional-ai-how-anthropic-teaches-claude-right-from-wrong-6caeb351c5e9)
- [Teaching Claude why — Anthropic](https://www.anthropic.com/research/teaching-claude-why)
- [RLVR Explained: Reinforcement Learning with Verifiable Rewards, Examples, Risks, and FAQs — Medium (Adnan Masood)](https://medium.com/@adnanmasood/rlvr-explained-reinforcement-learning-with-verifiable-rewards-examples-risks-and-faqs-89815659bd76)
- [Reinforcement Learning from Verifiable Rewards — Label Studio](https://labelstud.io/blog/reinforcement-learning-from-verifiable-rewards/)
- [Training language models to follow instructions with human feedback (InstructGPT) — arXiv 2203.02155](https://arxiv.org/abs/2203.02155)
- [AI Paper Review: InstructGPT — freeCodeCamp](https://www.freecodecamp.org/news/ai-paper-review-training-language-models-to-follow-instructions-with-human-feedback-instructgpt/)
- [LLM Training: RLHF and Its Alternatives — Ahead of AI (Sebastian Raschka)](https://magazine.sebastianraschka.com/p/llm-training-rlhf-and-its-alternatives)
- [Supervised Fine-Tuning Guide: Master SFT in July 2026 — Thunder Compute](https://www.thundercompute.com/blog/supervised-fine-tuning-guide)
- [Supervised Fine Tuning: Enhancing Your LLM Accuracy in 2026 — Label Your Data](https://labelyourdata.com/articles/llm-fine-tuning/supervised-fine-tuning)
- [The Llama 3 Herd of Models — arXiv (ar5iv) 2407.21783](https://ar5iv.labs.arxiv.org/html/2407.21783)
- [arXiv Dive: How Meta Trained Llama 3.1 — Oxen.ai](https://www.oxen.ai/blog/llama-3-1-herd-of-models)
- [LLM Scaling Laws: Analysis from AI Researchers — AIMultiple](https://aimultiple.com/llm-scaling-laws)
