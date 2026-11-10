// Render de una escena de reel (1080x1920, con render(t) y DURATION) a mp4.
//
//   node explorador/render.js <url> <salida.mp4> [duración]
//   node explorador/render.js --tramos <url>      // imprime TRAMOS y el video de una página de montaje
//
// Usa Firefox: Chromium de Playwright se cae en proot. Imprime "PROGRESO i n" por cada cuadro.
const { firefox } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs");
const os = require("os");
const path = require("path");

const FPS = 30;

async function abrir(url) {
  const navegador = await firefox.launch();
  const pagina = await navegador.newPage({ viewport: { width: 1080, height: 1920 } });
  const errores = [];
  pagina.on("pageerror", e => errores.push(e.message));
  await pagina.goto(url);
  await pagina.waitForLoadState("load");
  await pagina.waitForTimeout(300);
  if (errores.length) throw new Error("Error en la página: " + errores.join("; "));
  return { navegador, pagina };
}

async function tramos(url) {
  const { navegador, pagina } = await abrir(url);
  const info = await pagina.evaluate(() => ({
    tramos: typeof TRAMOS !== "undefined" ? TRAMOS : null,
    video: document.querySelector("video")?.src || null,
  }));
  await navegador.close();
  process.stdout.write(JSON.stringify(info));
}

// los filtros de papel (corte, grano) son pesados: varios Firefox en paralelo, cada uno con su parte de los cuadros
const TRABAJADORES = Math.max(1, Math.min(4, os.cpus().length - 2));

async function render(url, salida, durArg) {
  const fijo = url + (url.includes("?") ? "&" : "?") + "t=0";
  const primero = await abrir(fijo);
  const info = await primero.pagina.evaluate(() => ({
    dur: typeof DURATION !== "undefined" ? DURATION : null,
    render: typeof render === "function",
  }));
  if (!info.dur || !info.render) throw new Error("La página no tiene render(t) y DURATION: no se puede renderizar");
  const dur = durArg ? Number(durArg) : info.dur;

  const n = Math.round(dur * FPS);
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "render-"));
  let hechos = 0, siguiente = 0;
  async function trabajar({ navegador, pagina }) {
    while (siguiente < n) {
      const i = siguiente++;
      // si la duración pedida es más larga que la escena, se queda en el último cuadro
      await pagina.evaluate(t => render(t), Math.min(i / FPS, info.dur - 0.001));
      await pagina.screenshot({ type: "jpeg", quality: 92, path: path.join(dir, String(i).padStart(5, "0") + ".jpg") });
      console.log(`PROGRESO ${++hechos} ${n}`);
    }
    await navegador.close();
  }
  const otros = await Promise.all(Array.from({ length: Math.min(TRABAJADORES, n) - 1 }, () => abrir(fijo)));
  await Promise.all([primero, ...otros].map(trabajar));

  await new Promise((ok, mal) => spawn("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", path.join(dir, "%05d.jpg"),
    "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", salida],
    { stdio: ["ignore", "inherit", "inherit"] }).on("close", c => c === 0 ? ok() : mal(new Error("ffmpeg salió con " + c))));
  fs.rmSync(dir, { recursive: true, force: true });
}

const args = process.argv.slice(2);
(args[0] === "--tramos" ? tramos(args[1]) : render(args[0], args[1], args[2]))
  .catch(e => { console.error(e.message); process.exit(1); });
