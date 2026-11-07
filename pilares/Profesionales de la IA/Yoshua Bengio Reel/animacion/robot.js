// El robot de "loro con valores" (y del reel de Mythos Preview), en versión papel recortado:
// sin contornos, piezas apiladas con la sombra del editor de personajes (#sombra / .capa) y el corte irregular (#corte).
// Necesita los <defs> del editor (PERSONAJES.defs) en la página.
(() => {
  const BLANCO = "#F6F7F9", SOMBRA = "#CDD2DA", PANTALLA = "#181A24",
        LUZ = "#5CE1F0", LUZ_CLARA = "#BEF6FC";
  const GUARDAPOLVO = "#F1EFE8", GUARDAPOLVO_SOMBRA = "#D8D4C9";

  const capa = html => `<g class="capa" filter="url(#sombra)">${html}</g>`;
  const grados = r => r * 180 / Math.PI;

  /**
   * Brazo-pétalo desde el hombro (hx, hy) hasta la punta (px, py). Con guardapolvo, la manga cubre el tramo de arriba.
   */
  function brazo(hx, hy, px, py, S, conManga) {
    const L = Math.hypot(px - hx, py - hy);
    const giro = grados(Math.atan2(py - hy, px - hx)) - 90;   // el brazo se dibuja hacia +y
    let s = `<g transform="translate(${hx} ${hy}) rotate(${giro})">`;
    s += capa(`<ellipse cx="0" cy="${L / 2}" rx="${15 * S}" ry="${L / 2}" fill="${BLANCO}"/>` +
              `<ellipse cx="0" cy="${L / 2 + 5}" rx="${7 * S}" ry="${Math.max(4, L / 2 - 12 * S)}" fill="${SOMBRA}"/>`);
    if (conManga) {
      const m = L * 0.55;
      s += capa(`<path d="M${-17 * S} 0 L${17 * S} 0 L${15 * S} ${m} L${-15 * S} ${m} Z" fill="${GUARDAPOLVO}"/>` +
                `<rect x="${-16 * S}" y="${m - 6 * S}" width="${32 * S}" height="${6 * S}" fill="${GUARDAPOLVO_SOMBRA}"/>`);
    }
    return s + `</g>`;
  }

  /**
   * SVG del robot. o = {
   *   cx, cy: centro de la cabeza; S: escala (1 = diseño base, cabeza de radio 62)
   *   mirarX, mirarY: hacia dónde mira la cara (-1..1)
   *   manoIzq, manoDer: [x, y] punta de cada brazo (izquierda/derecha del cuadro)
   *   guardapolvo: true para vestirlo de científico
   *   llama: 0..1, largo de la llama del propulsor
   * }
   */
  function svg(o) {
    const { cx, cy, S = 1, mirarX = 0, mirarY = 0, guardapolvo = false, llama = 1 } = o;
    const R = 62 * S;
    const hombro = side => [cx + side * (R - 6 * S), cy + 14 * S];
    const reposo = side => [cx + side * (R + 36 * S), cy + 88 * S];
    const [ix, iy] = o.manoIzq || reposo(-1), [dx, dy] = o.manoDer || reposo(1);
    let s = "";

    // propulsor (con guardapolvo sale por abajo del saco)
    const baseLlama = guardapolvo ? cy + R * 2.45 : cy + R - 6 * S;
    const lg = (0.6 + 0.4 * llama);
    s += capa(`<polygon points="${cx - 20 * S},${baseLlama} ${cx + 20 * S},${baseLlama} ${cx},${baseLlama + 62 * S * lg}" fill="${LUZ}"/>` +
              `<polygon points="${cx - 9 * S},${baseLlama} ${cx + 9 * S},${baseLlama} ${cx},${baseLlama + 36 * S * lg}" fill="${LUZ_CLARA}"/>`);

    if (guardapolvo) {
      const y0 = cy + R * 0.8, y1 = cy + R * 2.5, a0 = R * 0.78, a1 = R * 0.98;
      s += capa(`<path d="M${cx - a0} ${y0} L${cx + a0} ${y0} L${cx + a1} ${y1} L${cx - a1} ${y1} Z" fill="${GUARDAPOLVO}"/>`);
      // solapas, botones y bolsillo con lapiceras
      s += capa(`<path d="M${cx - a0 * 0.55} ${y0} L${cx} ${y0 + R * 0.75} L${cx - a0 * 0.2} ${y0 + R * 0.1} Z" fill="${GUARDAPOLVO_SOMBRA}"/>` +
                `<path d="M${cx + a0 * 0.55} ${y0} L${cx} ${y0 + R * 0.75} L${cx + a0 * 0.2} ${y0 + R * 0.1} Z" fill="${GUARDAPOLVO_SOMBRA}"/>`);
      s += `<path d="M${cx} ${y0 + R * 0.75} L${cx} ${y1}" stroke="${GUARDAPOLVO_SOMBRA}" stroke-width="${2 * S}"/>`;
      for (const k of [0.95, 1.25, 1.55]) s += `<circle cx="${cx + 6 * S}" cy="${cy + R * (0.8 + k)}" r="${3 * S}" fill="${GUARDAPOLVO_SOMBRA}"/>`;
      const bx = cx - a0 * 0.75, by = y0 + R * 0.55;
      s += capa(`<rect x="${bx + 6 * S}" y="${by - 14 * S}" width="${5 * S}" height="${20 * S}" fill="#6A9BCC"/>` +
                `<rect x="${bx + 14 * S}" y="${by - 10 * S}" width="${5 * S}" height="${16 * S}" fill="#D97757"/>` +
                `<rect x="${bx}" y="${by}" width="${28 * S}" height="${22 * S}" fill="${GUARDAPOLVO_SOMBRA}"/>`);
    }

    // brazos (detrás de la cabeza)
    s += brazo(...hombro(-1), ix, iy, S, guardapolvo);
    s += brazo(...hombro(1), dx, dy, S, guardapolvo);

    // orejas y cabeza: un disco gris y encima el blanco corrido, como el original
    for (const side of [-1, 1]) {
      const ex = cx + side * (R - 2 * S);
      s += capa(`<rect x="${ex - 9 * S}" y="${cy - 20 * S}" width="${18 * S}" height="${40 * S}" rx="${8 * S}" fill="${SOMBRA}"/>`);
    }
    s += capa(`<circle cx="${cx}" cy="${cy}" r="${R}" fill="${SOMBRA}"/><circle cx="${cx - 2 * S}" cy="${cy - 4 * S}" r="${R - 6 * S}" fill="${BLANCO}"/>`);

    // pantalla y cara
    const fx = cx + 6 * S * mirarX, fy = cy - S + 4 * S * mirarY;
    let cara = `<ellipse cx="${fx}" cy="${fy}" rx="${48 * S}" ry="${41 * S}" fill="${PANTALLA}"/>`;
    const ojoX = 3 * S * mirarX, ojoY = 4 * S * mirarY;
    for (const ex of [fx - 20 * S, fx + 20 * S]) {
      cara += `<ellipse cx="${ex + ojoX}" cy="${fy - S + ojoY}" rx="${10 * S}" ry="${14 * S}" fill="${LUZ}"/>`;
      cara += `<ellipse cx="${ex + ojoX - 2 * S}" cy="${fy - 6 * S + ojoY}" rx="${3 * S}" ry="${4 * S}" fill="${LUZ_CLARA}"/>`;
      cara += `<path d="M ${ex - 10.3 * S} ${fy - 25.7 * S} A ${11 * S} ${8 * S} 0 0 1 ${ex + 10.3 * S} ${fy - 25.7 * S}"
                 fill="none" stroke="${LUZ}" stroke-width="${3 * S}" stroke-linecap="round"/>`;
    }
    cara += `<path d="M ${fx - 8 * S} ${fy + 21 * S} A ${8 * S} ${8 * S} 0 0 0 ${fx + 8 * S} ${fy + 21 * S} Z" fill="${LUZ}"/>`;
    s += capa(cara);

    return `<g filter="url(#corte)">${s}</g>`;
  }

  window.ROBOT = { svg, colores: { BLANCO, SOMBRA, PANTALLA, LUZ, LUZ_CLARA, GUARDAPOLVO } };
})();
