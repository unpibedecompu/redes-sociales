// Biblioteca para usar personajes del editor en escenas animadas. Cargar antes: parts.js (mismo directorio).
//
// Cada proyecto guarda sus personajes en su propio animacion/html/personajes.js, solo como lista:
//
//   window.PERSONAJES = PERSONAJES_PAPEL.crear({
//     // comentario con cómo se ve
//     coronel: "1.5.6.2.2.0.0.1.3.6.6.2",
//   });
//
// El código es el mismo que guarda el editor en la URL, así se puede abrir y retocar:
//   animations/paper_cutoff_characters/index.html#<código>
// Orden: piel . colorPelo . pelo . barba . cabeza . boca . cejas . orejas . nariz . remera . pantalón . zapatos
// (el código guarda posiciones en las listas de build.py: agregar piezas siempre al final de cada lista)
//
// En la escena: PERSONAJES.armar("coronel", { boca: 1, parpadeo: true, mirar: -0.6 })
(() => {
  const D = window.PAPEL;
  const cats = Object.fromEntries(D.categorias.map(c => [c.id, c]));

  // mismas paletas que el editor (index.html)
  const PIELES = [
    ["#F6D3B5", "#DDAE88"], ["#E8B48A", "#C98F66"], ["#C98E62", "#A56F45"],
    ["#9C6640", "#7C4D2D"], ["#6E4429", "#53311C"], ["#9FD1B5", "#76AE90"]
  ];
  const PELOS = [
    ["#3B2A20", "#24180F"], ["#141413", "#000000"], ["#8A5A2B", "#6A421C"], ["#E0B341", "#B88E22"],
    ["#C2463C", "#962F27"], ["#D6D3CB", "#A9A59B"], ["#6A9BCC", "#4F7FB0"]
  ];
  const CLAVES = ["piel", "colorPelo", ...D.categorias.map(c => c.id)];

  // código del editor -> combinación. Avisa en la consola si no coincide con las piezas actuales
  function desdeHash(h, nombre = h) {
    const v = h.split(".").map(Number);
    const problemas = [];
    if (v.length !== CLAVES.length) problemas.push(`tiene ${v.length} números y el editor usa ${CLAVES.length}`);
    CLAVES.forEach((k, i) => {
      const c = cats[k], n = c ? c.partes.length : (k === "piel" ? PIELES : PELOS).length;
      const min = c && c.opcional ? -1 : 0;
      if (i < v.length && !(Number.isInteger(v[i]) && v[i] >= min && v[i] < n))
        problemas.push(`${k}=${v[i]} no existe (va de ${min} a ${n - 1})`);
    });
    if (problemas.length) console.error(`personaje "${nombre}" (${h}): ${problemas.join("; ")}`);
    return Object.fromEntries(CLAVES.map((k, i) => [k, v[i] ?? (cats[k] && cats[k].opcional ? -1 : 0)]));
  }

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

  // piezas de disfraz: solo a propósito, nunca en una persona al azar (y así las multitudes ya hechas no cambian).
  // alAzar elige entre las primeras N piezas de cada lista, así que los disfraces tienen que quedar al final
  const DISFRACES = new Set(["Gorra militar", "Uniforme militar", "Militar"]);
  const comunes = Object.fromEntries(D.categorias.map(c => [c.id, c.partes.filter(p => !DISFRACES.has(p.nombre)).length]));

  // una persona cualquiera (para multitudes, cámaras de seguridad...). rnd: función 0..1 para que sea reproducible
  function alAzar(rnd = Math.random) {
    const n = k => Math.floor(rnd() * k);
    const e = { piel: n(PIELES.length - 1), colorPelo: n(PELOS.length) };   // la piel verde, solo a propósito
    for (const c of D.categorias) e[c.id] = c.opcional && rnd() < 0.3 ? -1 : n(comunes[c.id]);
    return e;
  }

  /** lista: { nombre: "código del editor" }. Devuelve { armar, alAzar, defs, lista } */
  function crear(lista) {
    const PERSONAJES = Object.fromEntries(Object.entries(lista).map(([k, h]) => [k, desdeHash(h, k)]));

    /**
     * SVG (sin <svg> exterior) del personaje en el lienzo 400x900 del editor.
     * nombre: uno de la lista, o una combinación suelta como la que da alAzar().
     * opts: { espalda, mirar (-1..1), parpadeo, cejas, boca, nino }  (cejas/boca: índice de pieza, para gestos;
     *         nino: achica el cuerpo debajo del cuello para que lea como chico)
     */
    function armar(nombre, opts = {}) {
      const base = typeof nombre === "string" ? PERSONAJES[nombre] : nombre;
      if (!base) throw new Error(`no hay personaje "${nombre}" en personajes.js`);
      const e = { ...base };
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

    return { armar, alAzar, defs: D.defs, lista: PERSONAJES };
  }

  window.PERSONAJES_PAPEL = { crear, desdeHash, PIELES, PELOS, CLAVES };
})();
