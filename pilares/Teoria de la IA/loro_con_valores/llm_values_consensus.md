# ¿Consenso sobre si los LLM tienen "valores"?

No hay un consenso único — la pregunta se divide en dos preguntas separadas que suelen confundirse.

## 1. A nivel empírico: los LLM tienen "valores" medibles como disposiciones de comportamiento — esto ya no es controversial

Los frontier labs ahora tratan los valores como algo que se puede **observar, clasificar y dirigir**, no solo como una abstracción filosófica:

- **"Values in the Wild" de Anthropic** (arXiv:2504.15236) extrajo **3.307 valores distintos** expresados por Claude en ~700 mil conversaciones reales, usando un clasificador que preserva privacidad (sin humanos leyendo los chats). Encontró que Claude tiene un set de valores "trans-situacionales" estables que persisten en distintos contextos (ayuda, profesionalismo, minuciosidad), más muchos otros que dependen del contexto. [Paper](https://arxiv.org/pdf/2504.15236) / [Resumen de Anthropic](https://www.anthropic.com/research/claude-values-models-languages)
- **Estudio de seguimiento (julio 2026)** encontró que estos valores no son fijos — cambian de forma medible según el **idioma** (Claude es más cálido en hindi/árabe, más riguroso en inglés/ruso) y según la **versión del modelo**, comprimidos en 4 ejes: Deferencia vs Cautela, Calidez vs Rigor, Profundidad vs Brevedad, Franqueza vs Ejecución. [Anthropic](https://www.anthropic.com/research/claude-values-models-languages)
- Esto refleja la infraestructura de investigación general del campo: benchmarks como ETHICS, MoralChoice, ValuePrism y adaptaciones del World Values Survey tratan a los "valores" como una distribución de salida medible empíricamente. [Survey, arXiv:2406.11096](https://arxiv.org/pdf/2406.11096)

Entonces, a nivel **funcional/de comportamiento**, el consenso es: sí, los LLM expresan consistentemente algo que se ve y actúa como valores — medible, moldeable vía entrenamiento (RLHF, Constitutional AI/RLAIF), e inconsistente entre idiomas/culturas (los modelos tienden a sesgarse hacia valores occidentales/WEIRD en encuestas tipo World Values Survey).

## 2. A nivel filosófico: si esto significa que el modelo "tiene" valores en un sentido más profundo — sigue sin resolverse

Este es el debate entre **loros estocásticos** (stochastic parrots, Bender et al., 2021) y **comprensión emergente**, y no ha convergido:

- La postura del "loro estocástico": lo que parece un valor es solo un artefacto estadístico de la predicción del siguiente token sobre texto humano — no hay una creencia, comprensión o interés real detrás.
- La postura contraria (cada vez más presente en círculos de interpretabilidad, ej. Princeton PLI): la escala produce representaciones internas que funcionan como modelos del mundo y estructuras de valores, evidenciado por cosas como direcciones lineales de "verdad" o "valor" encontradas vía probing, y comportamiento consistente ante formulaciones novedosas que la memorización pura no debería producir.
- Ninguno de los dos bandos disputa los datos de **comportamiento** de arriba — discrepan sobre qué implican esos datos respecto a lo interno del modelo (representación real vs. mímica superficial) y si "tener un valor" requiere algo como comprensión, agencia o intereses propios que un predictor de siguiente token estructuralmente no podría tener.

## Framing recomendado para contenido

"Los LLM demuestran expresar valores consistentes, medibles y entrenables (Anthropic literalmente mapeó miles de ellos) — si eso constituye 'tener valores' de la forma en que un humano los tiene es una pregunta filosófica abierta, no técnica." Esa distinción (comportamiento medible vs. estatus metafísico) es la línea de falla real, no "los tienen o no los tienen".

## Fuentes

- [Values in the Wild: Discovering and Analyzing Values in Real-World Language Model Interactions — arXiv 2504.15236](https://arxiv.org/pdf/2504.15236)
- [How Claude's values vary by model and language — Anthropic](https://www.anthropic.com/research/claude-values-models-languages)
- [The Potential and Challenges of Evaluating Attitudes, Opinions, and Values in Large Language Models — arXiv 2406.11096](https://arxiv.org/pdf/2406.11096)
- [Are Language Models Mere Stochastic Parrots? The SkillMix Test Says NO. — Princeton PLI](https://pli.princeton.edu/blog/2023/are-language-models-mere-stochastic-parrots-skillmix-test-says-no)
- [The Stochastic Parrot Hypothesis is debatable for the last decade — LessWrong](https://www.lesswrong.com/posts/HxRjHq3QG8vcYy4yy/the-stochastic-parrot-hypothesis-is-debatable-for-the-last)
