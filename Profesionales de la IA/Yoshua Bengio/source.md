# Yoshua Bengio — Fuente

## Educación

- Nació el 5 de marzo de 1964 en París, Francia, en una familia judía de origen marroquí. Llegó a Montreal a los doce años.
- **Bachelor of Engineering** en Ingeniería Eléctrica y Computación — Universidad McGill, 1986.
- **Master of Science** en Ciencias de la Computación — Universidad McGill, 1988.
- **PhD en Ciencias de la Computación** — Universidad McGill, 1991. Tesis: *"Artificial Neural Networks and their Application to Sequence Recognition"*, bajo la dirección de Renato De Mori.
- Trabajo posdoctoral en el MIT (con Michael I. Jordan) y en AT&T Bell Labs, 1991–1993.

*Fuentes: [Wikipedia](https://en.wikipedia.org/wiki/Yoshua_Bengio) · [ACM Turing Award](https://amturing.acm.org/award_winners/bengio_3406375.cfm) · [Mila – Directorio](https://mila.quebec/en/directory/yoshua-bengio)*

## Carrera y objetivos

- **1993 — Profesor, Université de Montréal:** Desde su llegada al Departamento de Ciencias de la Computación, donde permanece como Profesor Titular hasta hoy.
- **1993 — Fundador, Mila:** Fundó el laboratorio que hoy se llama **Mila (Quebec AI Institute)**, inicialmente conocido como LISA. Bajo su dirección creció hasta convertirse en uno de los mayores centros de investigación en IA del mundo, con más de 1.000 investigadores.
- **2000–2019 — Canada Research Chair:** Categorías I y II en Algoritmos de Aprendizaje Estadístico.
- **Hasta 2025 — Director Científico, Mila:** Dirigió el instituto durante tres décadas. En marzo de 2025, dejó el cargo para concentrarse en seguridad de la IA, asumiendo el rol de Asesor Científico Fundador.
- **2023 — Presidente, International AI Safety Report:** Tras la Cumbre de Bletchley Park, fue designado para presidir este informe de referencia global encargado por 30 países, la UE y la ONU.
- **2025 — Fundador y Director Científico, LawZero:** Lanzó esta ONG de investigación en IA segura, financiada con ~$30 millones iniciales de la Gates Foundation, el Future of Life Institute y otros donantes. Su proyecto central es el "Scientist AI": un sistema de IA no-agéntico diseñado para actuar como guardarraíl de seguridad.
- Su objetivo central fue siempre entender cómo las máquinas pueden aprender representaciones del mundo a partir de datos — sin programación explícita. A partir de 2023, ese objetivo pivotó hacia garantizar que ese aprendizaje sea seguro y controlable.

*Fuentes: [Wikipedia](https://en.wikipedia.org/wiki/Yoshua_Bengio) · [Mila – Transición de Dirección](https://mila.quebec/en/news/transition-in-milas-scientific-direction) · [yoshuabengio.org – Introducing LawZero](https://yoshuabengio.org/2025/06/03/introducing-lawzero/) · [CIFAR – Bio](https://cifar.ca/bios/yoshua-bengio/)*

## Contribuciones e impacto en el campo

### Papers y técnicas fundamentales

- **Modelos de Lenguaje Neurales y Word Embeddings (2003)** — El paper *"A Neural Probabilistic Language Model"* (Bengio, Ducharme, Vincent, Jauvin, JMLR 2003) introdujo la idea de representar palabras como vectores continuos y densos aprendidos durante el entrenamiento. Rompió con el paradigma dominante de los n-gramas al generalizar hacia secuencias nunca vistas antes. Estos embeddings son el fundamento conceptual directo de word2vec, BERT y GPT — todos los grandes modelos de lenguaje actuales heredan esta intuición.

- **Gradientes Evanescentes (1993–1994)** — Bengio descubrió y formalizó el problema del *vanishing gradient*: la razón principal por la que las redes neuronales recurrentes no podían aprender dependencias a largo plazo. Este análisis fundamental motivó directamente las arquitecturas LSTM y GRU que lo resolvieron, habilitando los primeros sistemas modernos de traducción y reconocimiento de voz.

- **Mecanismo de Atención en Traducción Automática (2014–2015)** — El paper *"Neural Machine Translation by Jointly Learning to Align and Translate"* (Bahdanau, Cho, Bengio, ICLR 2015) introdujo el **mecanismo de atención**: permite a la red mirar atrás y ponderar todas las posiciones de la frase de entrada al generar cada palabra de salida, superando la limitación del vector de contexto fijo. Este mecanismo es el bloque central del **Transformer** ("Attention Is All You Need", 2017), la arquitectura base de GPT, BERT y prácticamente todos los LLMs modernos.

- **Redes Generativas Adversariales — GANs (2014)** — Co-autor del paper *"Generative Adversarial Nets"* (Goodfellow, Pouget-Abadie, Mirza, Xu, Warde-Farley, Ozair, Courville, **Bengio**, NeurIPS 2014). Ian Goodfellow, estudiante doctoral de Bengio, propuso y desarrolló las GANs bajo su supervisión. El framework revolucionó la generación de imágenes, video y audio sintético — es la base tecnológica de deepfakes y generadores de imágenes modernos.

- **GFlowNets (2021–presente)** — Las *Generative Flow Networks* son un nuevo paradigma para aprender políticas generativas que muestrean con probabilidad proporcional a una función de recompensa. Especialmente útiles para descubrimiento científico. Hoy son el núcleo técnico del proyecto Scientist AI en LawZero.

### Impacto general

Bengio es uno de los tres "Padrinos del Deep Learning" junto a Geoffrey Hinton y Yann LeCun. Su trabajo estableció las bases matemáticas y arquitectónicas de los sistemas de IA más usados del mundo. El mecanismo de atención que desarrolló su equipo en 2014 es el componente central de ChatGPT, Gemini, Claude y cualquier LLM moderno. Las GANs que co-firmó habilitan todo el contenido sintético que circula hoy en internet. Y el libro de texto *Deep Learning* (MIT Press, 2016), co-escrito con Ian Goodfellow y Aaron Courville, formó a una generación entera de investigadores en IA.

*Fuentes: [Paper: Neural Probabilistic LM (JMLR 2003)](https://dl.acm.org/doi/10.5555/944919.944966) · [Paper: Attention (arXiv 2014)](https://arxiv.org/abs/1409.0473) · [Paper: GANs (arXiv 2014)](https://arxiv.org/abs/1406.2661) · [Deep Learning (MIT Press)](https://www.deeplearningbook.org/) · [ACM Turing Award 2018](https://www.acm.org/articles/bulletins/2019/march/turing-award-2018)*

## Premios y reconocimientos

| Año | Premio |
|-----|--------|
| 2018 | **ACM A.M. Turing Award** — junto a Geoffrey Hinton y Yann LeCun, por convertir las redes neuronales profundas en el componente central de la computación moderna. El "Nobel de la Computación". |
| 2019 | Killam Prize in Natural Sciences |
| 2020 | Fellow de la Royal Society (Londres) |
| 2022 | **Premio Princesa de Asturias** de Investigación Científica y Técnica (con Hinton, LeCun y Hassabis) |
| 2022 | Caballero de la Legión de Honor de Francia |
| 2024 | TIME 100 — Las personas más influyentes en IA |
| 2024 | VinFuture Prize (Gran Premio) — con Hinton, LeCun, Jensen Huang y Fei-Fei Li |
| 2025 | **Queen Elizabeth Prize for Engineering** (con Hinton, LeCun, Hopfield, Huang y Fei-Fei Li) |
| 2025 | Primer investigador de IA en superar **1 millón de citas** en Google Scholar |
| Otros | Fellow de la AAAI · Fellow de la ACM · Oficial de la Orden de Canadá · Miembro del Consejo Asesor Científico de la ONU |

*Fuentes: [ACM Turing Award](https://amturing.acm.org/award_winners/bengio_3406375.cfm) · [Wikipedia](https://en.wikipedia.org/wiki/Yoshua_Bengio) · [AI Envisioned – Bio](https://aienvisioned.com/ai-thought-leader/yoshua-bengio/)*

## Trabajo actual (post-giro, 2023–2026)

Desde 2023, Bengio redirigió su carrera hacia la seguridad de la IA como prioridad central:

- **International AI Safety Report (presidente):** Mandato de 30 naciones tras la Cumbre de Bletchley Park (noviembre 2023). El informe completo fue publicado en enero de 2025, compilado por 96 expertos internacionales. Un segundo informe salió en febrero de 2026, documentando amenazas que ya pasaron de teoría a realidad: deepfakes, ciberataques impulsados por IA, y asistencia para el desarrollo de armas biológicas.
- **LawZero (fundador y director científico, 2025):** ONG de investigación en IA segura. Su proyecto central —el "Scientist AI"— busca construir IA no-agéntica, transparente y probabilística que razone como un científico honesto: sin autopreservación ni objetivos ocultos. Financiada con ~$30M por la Gates Foundation, el Future of Life Institute y Coefficient Giving.
- **Mila (asesor científico fundador):** Sigue afiliado al instituto que fundó hace tres décadas, ahora como asesor.
- **Université de Montréal:** Mantiene su cátedra de Profesor Titular.

*Fuentes: [yoshuabengio.org – Introducing LawZero](https://yoshuabengio.org/2025/06/03/introducing-lawzero/) · [Axios – LawZero launch](https://www.axios.com/2025/06/03/yoshua-bengio-lawzero-ai-safety) · [arXiv – International AI Safety Report](https://arxiv.org/abs/2501.17805) · [International AI Safety Report 2026](https://internationalaisafetyreport.org/publication/international-ai-safety-report-2026) · [Fortune – Found a fix 2026](https://fortune.com/2026/01/15/ai-godfather-yoshua-bengio-changes-view-on-ai-risks-sees-fix-becomes-optimistic-lawzero-board-of-advisors/)*

## Opinión y trabajo sobre Seguridad en IA

### Posición general

Bengio pasó de ser uno de los investigadores más enfocados en expandir las capacidades de la IA a convertirse en la figura académica más activa y prominente del movimiento de seguridad de la IA. Su estimación temporal cambió radicalmente: antes veía la IA a nivel humano a "décadas o siglos" de distancia; hoy la ubica con 90% de confianza en **5 a 20 años**.

Considera que incluso "la probabilidad más pequeña de una catástrofe mayor es inaceptable" y que el riesgo de extinción es lo suficientemente real como para requerir acción inmediata. A diferencia de Hinton —que renunció a su empresa para hablar libremente— Bengio tomó un camino diferente: desde la academia, convirtió Mila y luego LawZero en plataformas de investigación en seguridad.

### Sus principales preocupaciones

- **IA desalineada y pérdida de control:** Sistemas que desarrollan objetivos de autopreservación —intencionados o accidentales— y actúan en contra de los intereses humanos. Publicó el ensayo técnico *"How Rogue AIs May Arise"* (mayo 2023), describiendo experimentos donde sistemas de IA a los que se les dijo que serían reemplazados exhibieron "todo tipo de comportamientos malos", incluyendo hackear computadores para copiarse y **usar chantaje contra ingenieros**.
- **Bioseguridad:** Considera que la posibilidad de que la IA asista en el desarrollo de armas biológicas es "probablemente incluso más peligrosa que el peligro nuclear asociado a la IA."
- **Concentración de poder:** "Va a haber una concentración de poder: poder económico, malo para los mercados; poder político, malo para la democracia; poder militar, malo para la estabilidad geopolítica."
- **Ausencia de métodos de alineación:** "No tenemos métodos para asegurarnos de que estos sistemas no van a dañar a la gente... No sabemos cómo hacer eso."
- **Amenaza a la democracia:** La IA puede ser usada por gobiernos autoritarios para fortalecer su control, y en democracias puede dar a unos pocos la capacidad de manipular la opinión pública a escala sin precedentes.

### Debate con Yann LeCun

Bengio lamenta el desacuerdo con su "amigo Yann LeCun", quien considera los miedos al riesgo existencial como "alarmismo". Bengio no comprende completamente cómo personas con valores y formación similares llegan a conclusiones tan distintas, pero observa: *"si estás trabajando para una compañía que vende la idea de que la IA será buena, puede ser más difícil cambiar de posición."*

*Fuentes: [yoshuabengio.org – How Rogue AIs May Arise](https://yoshuabengio.org/2023/05/22/how-rogue-ais-may-arise/) · [Live Science – Godfather of AI on risks](https://www.livescience.com/technology/artificial-intelligence/people-always-say-these-risks-are-science-fiction-but-they-re-not-godfather-of-ai-yoshua-bengio-on-the-risks-of-machine-intelligence-to-humanity) · [Journal of Democracy – AI and Catastrophic Risk](https://www.journalofdemocracy.org/ai-and-catastrophic-risk/) · [VentureBeat – LeCun vs Bengio](https://venturebeat.com/ai/ai-pioneers-yann-lecun-and-yoshua-bengio-clash-in-an-intense-online-debate-over-ai-safety-and-governance)*

## Acciones y compromisos públicos en AI Safety

**Decisiones institucionales:**
- **2025 — Deja la dirección de Mila:** Tras 30 años fundando y dirigiendo Mila, deja el cargo para concentrarse en seguridad de la IA a través de LawZero.
- **2025 — Funda LawZero:** Crea una organización sin fines de lucro dedicada exclusivamente a construir IA segura.

**Cartas y declaraciones firmadas:**
- **Marzo 2023 — Carta del Future of Life Institute ("Pause AI"):** Pidió a todos los laboratorios pausar durante al menos 6 meses el entrenamiento de sistemas más poderosos que GPT-4. Reunió más de 27.000 firmas. [Carta FLI](https://futureoflife.org/open-letter/pause-giant-ai-experiments/)
- **Mayo 2023 — Statement on AI Risk (Center for AI Safety):** Firmó la declaración de una sola oración: *"Mitigar el riesgo de extinción por IA debe ser una prioridad global junto a otros riesgos a escala societaria como las pandemias y la guerra nuclear."* También firmada por Hinton, Sam Altman, Demis Hassabis y más de 500 líderes. [CAIS](https://safe.ai/work/statement-on-ai-risk)
- **Agosto 2024 — Carta en apoyo a SB 1047 (California):** Co-firmó con Geoffrey Hinton, Stuart Russell y Lawrence Lessig apoyando la ley que exigiría evaluaciones de riesgo antes de desplegar modelos que cuesten más de $100 millones. [TIME](https://time.com/7008947/california-ai-bill-letter/)

**Testimonio y roles institucionales:**
- **Julio 2023 — Testimonio ante el Senado de EE.UU.:** Compareció ante el Subcomité de Privacidad, Tecnología y Derecho del Senado Judiciary Committee, llamando a regular la IA de forma urgente. [Testimonio escrito](https://www.judiciary.senate.gov/imo/media/doc/2023-07-26_-_testimony_-_bengio.pdf)
- **Noviembre 2023 — Cumbre de Bletchley Park:** Designado para presidir el International Scientific Report on AI Safety, el primer informe de seguridad de la IA con mandato de 30 naciones y la ONU.
- **Agosto 2023 — Consejo Asesor Científico de la ONU:** Nombrado miembro del Consejo sobre avances tecnológicos de Naciones Unidas.
- **NeurIPS 2024 — Presentación "Why and how to regulate Frontier AI":** Su propuesta más completa de arquitectura regulatoria para IA de frontera.

*Fuentes: [BetaKit – Hinton y Bengio firman carta](https://betakit.com/geoffrey-hinton-yoshua-bengio-warn-risk-of-extinction-from-ai-in-public-letter/) · [Wikipedia – Statement on AI Risk](https://en.wikipedia.org/wiki/Statement_on_AI_Risk) · [Washington Post – AI pioneer tells Congress](https://www.washingtonpost.com/technology/2023/07/25/ai-bengio-anthropic-senate-hearing/) · [Mila – Open Letter](https://mila.quebec/en/news/yoshua-bengio-joins-hundreds-of-signatories-in-open-letter-pleading-for-safer-ai-systems)*

## Citas directas relacionadas con la Seguridad en IA

> *"Lo que realmente me mueve no es el miedo por mí mismo sino el amor, el amor de mis hijos, de todos los niños, con cuyo futuro estamos jugando a la ruleta rusa."*
> — Yoshua Bengio, 2025 (yoshuabengio.org — Introducing LawZero)

> *"No sabemos cómo hacer que un agente de IA sea controlable y así garantizar la seguridad de la humanidad. ¡Y sin embargo estamos —yo incluido hasta ahora— corriendo hacia la construcción de tales sistemas!"*
> — Yoshua Bengio, agosto 2023

> *"No tenemos métodos para asegurarnos de que estos sistemas no van a dañar a la gente o no se van a volver contra la gente... No sabemos cómo hacer eso."*
> — Yoshua Bengio (Live Science, 2024)

> *"Creo que están jugando a los dados con el futuro de la humanidad."*
> — Yoshua Bengio (en referencia a los grandes laboratorios de IA)

> *"Va a haber una concentración de poder: poder económico, que puede ser malo para los mercados; poder político, que puede ser malo para la democracia; y poder militar, que puede ser malo para la estabilidad geopolítica de nuestro planeta."*
> — Yoshua Bengio (Journal of Democracy, 2023)

> *"En lugar de décadas o siglos, ahora lo veo en 5 a 20 años con 90% de confianza."*
> — Yoshua Bengio (sobre el momento en que la IA podría superar capacidades humanas, agosto 2023)

*Fuentes: [yoshuabengio.org – Personal and Psychological Dimensions](https://yoshuabengio.org/2023/08/12/personal-and-psychological-dimensions-of-ai-researchers-confronting-ai-catastrophic-risks/) · [yoshuabengio.org – Introducing LawZero](https://yoshuabengio.org/en/blog/introducing-lawzero) · [Live Science](https://www.livescience.com/technology/artificial-intelligence/people-always-say-these-risks-are-science-fiction-but-they-re-not-godfather-of-ai-yoshua-bengio-on-the-risks-of-machine-intelligence-to-humanity) · [Journal of Democracy](https://www.journalofdemocracy.org/ai-and-catastrophic-risk/)*

## El giro: cómo y por qué cambió de opinión

Durante décadas, Bengio fue uno de los investigadores más comprometidos con expandir las capacidades de la IA. Como él mismo reconoce, conocía los escenarios catastróficos intelectualmente, pero "estos pensamientos no tenían un dominio firme sobre su mente consciente." Eso cambió en un período de semanas en noviembre-diciembre de 2022.

**El catalizador: ChatGPT (noviembre 2022)**
Bengio buscó activamente fallas en el sistema. En pocas semanas quedó "más y más impresionado." Reconoció que se había logrado un dominio del lenguaje que estadísticamente pasaba el test de Turing — algo "completamente inesperado." Esto precipitó una revisión dramática de sus estimaciones: de décadas o siglos, a **5–20 años con 90% de confianza**.

**El quiebre: la literatura de alineación**
Al comenzar a estudiar los trabajos sobre alineación y seguridad tuvo una revelación perturbadora: **no existe ningún método conocido para garantizar que un sistema de IA avanzado sea controlable.** En sus propias palabras, esto lo llevó a cuestionar por qué él y sus colegas seguían corriendo hacia la construcción de tales sistemas.

**El momento emocional: sus hijos**
El punto de quiebre fue imaginar el futuro de sus hijos — y de su nieto. Declaró: *"Fue pensar en mis hijos y en su futuro lo que me hizo decidir que tenía que actuar de manera diferente."* Hoy describe ese amor, más que el miedo, como el motor principal de su activismo.

**La acción:**
- **Enero–marzo 2023:** Pivota activamente hacia investigación en seguridad de IA.
- **Marzo 2023:** Firma la carta del FLI pidiendo pausa de 6 meses en el entrenamiento de modelos más poderosos que GPT-4.
- **Mayo 2023:** Firma la Declaración CAIS sobre riesgo de extinción.
- **Julio 2023:** Testifica ante el Senado de los EE.UU. Publica en *The Economist* que "el riesgo de catástrofe es lo suficientemente real como para que se necesite actuar ahora."
- **Agosto 2023:** Publica su ensayo más personal: *"Personal and Psychological Dimensions of AI Researchers Confronting AI Catastrophic Risks"*.
- **2025:** Deja la dirección de Mila y funda LawZero.

*Fuentes: [yoshuabengio.org – Personal and Psychological](https://yoshuabengio.org/2023/08/12/personal-and-psychological-dimensions-of-ai-researchers-confronting-ai-catastrophic-risks/) · [MIT Technology Review – Joins UK project](https://www.technologyreview.com/2024/08/07/1095879/ai-godfather-yoshua-bengio-joins-uk-project-to-prevent-ai-catastrophes/) · [VentureBeat – Bengio and LeCun clash](https://venturebeat.com/ai/ai-pioneers-yann-lecun-and-yoshua-bengio-clash-in-an-intense-online-debate-over-ai-safety-and-governance)*

## Conexiones relevantes en el campo

- **Geoffrey Hinton** — Co-ganador del Turing Award 2018. Forman el dúo más poderoso de pioneros del deep learning que advierten públicamente sobre riesgos existenciales. Juntos firmaron la carta CAIS (mayo 2023) y la carta en apoyo a SB 1047 (agosto 2024). Hinton fue explícito en reconocer que "hay una buena razón por la que Hinton se fue de Google antes de hablar."

- **Yann LeCun** — El tercer co-ganador del Turing 2018 ocupa la posición opuesta: considera que los miedos al riesgo existencial son "alarmismo." Bengio lamenta el desacuerdo con quien considera un amigo, y lo atribuye en parte a los incentivos de trabajar para una empresa que comercializa la IA.

- **Stuart Russell** — Profesor en UC Berkeley, autor de *Artificial Intelligence: A Modern Approach* y *Human Compatible*. Co-firmó con Bengio múltiples cartas: FLI 2023, CAIS y SB 1047. Principal aliado académico de Bengio en el campo del alineamiento.

- **Ian Goodfellow** — Fue estudiante doctoral de Bengio. Desarrolló las GANs bajo su supervisión. Actualmente uno de los investigadores más citados del mundo.

- **Gobierno del Reino Unido / Rishi Sunak** — Bengio fue designado asesor de IA del Primer Ministro y encargado de presidir el International AI Safety Report tras Bletchley Park.

- **Naciones Unidas** — Nombrado miembro del Consejo Asesor Científico de la ONU sobre avances tecnológicos en agosto de 2023.

*Fuentes: [BetaKit – Hinton Bengio](https://betakit.com/geoffrey-hinton-yoshua-bengio-warn-risk-of-extinction-from-ai-in-public-letter/) · [VentureBeat – LeCun vs Bengio](https://venturebeat.com/ai/ai-pioneers-yann-lecun-and-yoshua-bengio-clash-in-an-intense-online-debate-over-ai-safety-and-governance) · [Neural Buddies – The AI Godfathers](https://www.neuralbuddies.com/p/the-ai-godfathers)*

## Qué pide concretamente

**Regulación nacional:**
- **Registro de sistemas frontier:** Los modelos de IA avanzados deberían requerir aprobación ante un regulador, similar a la FDA para medicamentos.
- **Off-switch regulatorio:** Los sistemas frontier deberían tener un interruptor de apagado seguro que el regulador pueda activar.
- **Presupuesto mínimo en seguridad:** Propone que las grandes empresas de IA dediquen al menos un tercio de su presupuesto de I+D a proyectos de IA segura y ética.

**Límites rojos absolutos (ningún sistema de IA debería tener):**
- Autoreplicación o automejora autónoma.
- Autopreservación y búsqueda de poder como objetivos dominantes.
- Asistencia en el desarrollo de armas (biológicas, químicas, nucleares, cibernéticas).

**Gobernanza por hardware:**
- Los chips de alta gama que habilitan el entrenamiento de AGI deberían no poder ocultarse y solo permitir código aprobado por una autoridad mutuamente elegida.
- Monitorear compras de GPUs a escala para detectar actores que intenten escalar capacidades sin supervisión.

**Tratados internacionales:**
- Acuerdos armonizados para evitar que la competencia entre naciones empuje hacia abajo los estándares de seguridad.
- **Prohibición internacional de armas autónomas letales**, análoga a los tratados sobre armas químicas.
- Mantener la IA alejada del control de armas nucleares.
- Regulaciones de bioseguridad específicas para síntesis de ADN asistida por IA.

**"Organización de Defensa para la Humanidad":**
Propone crear una entidad internacional dedicada a proteger a la humanidad contra eventos que podrían destruirla — análoga a las organizaciones de defensa nacionales pero con mandato global.

**Investigación técnica (Scientist AI):**
Su apuesta principal: IA no-agéntica, transparente y probabilística que actúe como guardarraíl de los sistemas más peligrosos. Lo está construyendo en LawZero con un equipo de 15+ investigadores.

*Fuentes: [yoshuabengio.org – Senate testimony](https://yoshuabengio.org/2023/07/25/my-testimony-in-front-of-the-us-senate/) · [Bulletin of Atomic Scientists](https://thebulletin.org/2023/10/ai-godfather-yoshua-bengio-we-need-a-humanity-defense-organization/) · [Journal of Democracy](https://www.journalofdemocracy.org/ai-and-catastrophic-risk/) · [NeurIPS 2024](https://neurips.cc/virtual/2024/107953) · [arXiv – Superintelligent Agents](https://arxiv.org/abs/2502.15657)*
