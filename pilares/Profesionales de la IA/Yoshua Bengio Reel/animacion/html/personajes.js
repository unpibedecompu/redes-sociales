// Personajes del reel, armados con las piezas del editor de papel recortado
// (animations/paper_cutoff_characters). Cargar antes: parts.js de ese editor.
//
// Cada personaje es la misma combinación que guarda el editor en la URL, así se puede abrir y retocar:
//   animations/paper_cutoff_characters/index.html#<hash>
(() => {
  const D = window.PAPEL;
  const cats = Object.fromEntries(D.categorias.map(c => [c.id, c]));

  // mismas paletas que el editor
  const PIELES = [
    ["#F6D3B5", "#DDAE88"], ["#E8B48A", "#C98F66"], ["#C98E62", "#A56F45"],
    ["#9C6640", "#7C4D2D"], ["#6E4429", "#53311C"], ["#9FD1B5", "#76AE90"]
  ];
  const PELOS = [
    ["#3B2A20", "#24180F"], ["#141413", "#000000"], ["#8A5A2B", "#6A421C"], ["#E0B341", "#B88E22"],
    ["#C2463C", "#962F27"], ["#D6D3CB", "#A9A59B"], ["#6A9BCC", "#4F7FB0"]
  ];
  const CLAVES = ["piel", "colorPelo", ...D.categorias.map(c => c.id)];
  const desdeHash = h => Object.fromEntries(h.split(".").map((v, i) => [CLAVES[i], Number(v)]));

  const PERSONAJES = {
    // pelo ondulado canoso, barba corta, cabeza ovalada, cejas rectas, nariz triangular, traje azul
    yoshua: desdeHash("1.5.5.1.0.1.0.0.1.5.5.2"),
    // el que maneja: no se le ve la cara. Pelo corto castaño oscuro, sin barba, cabeza cuadrada, buzo y jean
    conductor: desdeHash("2.0.0.-1.2.1.2.1.3.3.0.0"),
    // los chicos (se dibujan con { nino: true }: cuerpo más chico bajo la misma cabeza)
    // hija: pelo largo castaño claro, suéter
    hija: desdeHash("0.2.1.-1.0.1.0.1.0.1.0.0"),
    // hijo: pelo corto castaño, cabeza redonda, remera
    hijo: desdeHash("1.0.0.-1.1.1.0.0.0.0.0.0"),
    // nieto: el más chico, rulos rubios, buzo
    nieto: desdeHash("0.3.5.-1.1.0.1.1.0.3.1.0"),
  };
  const CUERPO = new Set(["cuerpo", "pantalon", "zapatos", "remera"]);

  const ORDEN = ["pelo:atras", "cuerpo", "pantalon", "zapatos", "remera", "orejas", "cabeza", "cara",
                 "boca", "cejas", "nariz", "barba", "pelo"];
  // de espaldas: sin cara, y la cabeza pintada del color del pelo (nuca)
  const ORDEN_ESPALDA = ["cuerpo", "pantalon", "zapatos", "remera", "orejas", "nuca", "pelo:atras", "pelo"];

  const capa = html => `<g class="capa" filter="url(#sombra)">${html}</g>`;

  // ojos propios para poder mirar a un costado y parpadear
  function ojos({ mirar = 0, parpadeo = false } = {}) {
    const dx = mirar * 4;
    if (parpadeo) return `<path d="M163 191 L177 191 M223 191 L237 191" stroke="#141413" stroke-width="3.5" stroke-linecap="round"/>`;
    return `<circle cx="${170 + dx}" cy="190" r="6" fill="#141413"/><circle cx="${230 + dx}" cy="190" r="6" fill="#141413"/>`;
  }

  /**
   * SVG (sin <svg> exterior) del personaje en el lienzo 400x900 del editor.
   * nombre: uno de PERSONAJES, o una combinación suelta como la que da alAzar().
   * opts: { espalda, mirar (-1..1), parpadeo, cejas, boca, nino }  (cejas/boca: índice de pieza, para gestos;
   *         nino: achica el cuerpo debajo del cuello para que lea como chico)
   */
  function armar(nombre, opts = {}) {
    const e = { ...(typeof nombre === "string" ? PERSONAJES[nombre] : nombre) };
    if (opts.cejas !== undefined) e.cejas = opts.cejas;
    if (opts.boca !== undefined) e.boca = opts.boca;
    const [p, ps] = PIELES[e.piel], [h, hs] = PELOS[e.colorPelo];
    const segunCabeza = v => Array.isArray(v) ? v[e.cabeza] : v;
    let s = "";
    const cuerpo = html => opts.nino && html ? `<g transform="translate(200 300) scale(0.72) translate(-200 -300)">${html}</g>` : html;
    for (const k of (opts.espalda ? ORDEN_ESPALDA : ORDEN)) {
      if (k === "cuerpo") { s += cuerpo(capa(D.base.cuerpo)); continue; }
      if (k === "cara") { s += capa(ojos(opts)); continue; }
      if (k === "nuca") {
        s += capa(cats.cabeza.partes[e.cabeza].svg.replace(/var\(--piel(-sombra)?,#[0-9A-Fa-f]+\)/g, "var(--pelo)"));
        continue;
      }
      const [id, sub] = k.split(":");
      const i = e[id];
      if (i < 0) continue;
      const parte = cats[id].partes[i];
      const html = segunCabeza(sub === "atras" ? parte.atras : parte.svg);
      if (html) s += CUERPO.has(id) ? cuerpo(capa(html)) : capa(html);
    }
    // los colores van como variables CSS en el grupo, así dos personajes conviven en la misma escena
    return `<g style="--piel:${p};--piel-sombra:${ps};--pelo:${h};--pelo-sombra:${hs}">${s}</g>`;
  }

  // una persona cualquiera (para multitudes, cámaras de seguridad...). rnd: función 0..1 para que sea reproducible
  function alAzar(rnd = Math.random) {
    const n = k => Math.floor(rnd() * k);
    const e = { piel: n(PIELES.length - 1), colorPelo: n(PELOS.length) };   // la piel verde, solo a propósito
    for (const c of D.categorias) e[c.id] = c.opcional && rnd() < 0.3 ? -1 : n(c.partes.length);
    return e;
  }

  window.PERSONAJES = { armar, alAzar, defs: D.defs, lista: PERSONAJES };
})();
