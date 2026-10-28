// Exporta las escenas HTML a MP4 (1080x640, 30 fps) cuadro por cuadro.
// Abre Chrome headless, llama a render(t) de cada página, captura el SVG y arma el video con ffmpeg.
//
// Uso: node render_mp4.mjs                      (todas las escenas)
//      node render_mp4.mjs escena_2_servicial   (solo esas)
import { spawn, execFileSync } from "node:child_process";
import { mkdtempSync, readdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const CHROME = "C:/Program Files/Google/Chrome/Application/chrome.exe";
const FPS = 30, W = 1080, H = 640, PAD = 16;   // el SVG queda en (16, 16) por el padding del body
const PORT = 9333;
const here = dirname(fileURLToPath(import.meta.url));

const wanted = process.argv.slice(2);
const scenes = readdirSync(here)
  .filter(f => /^escena_.*\.html$/.test(f))
  .filter(f => !wanted.length || wanted.some(w => f.startsWith(w)))
  .sort();

const profile = mkdtempSync(join(tmpdir(), "chrome-render-"));
const chrome = spawn(CHROME, [
  "--headless=new", "--disable-gpu", "--hide-scrollbars", `--remote-debugging-port=${PORT}`,
  `--user-data-dir=${profile}`, `--window-size=${W + 2 * PAD},${H + 2 * PAD}`, "about:blank",
], { stdio: "ignore" });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function connect() {
  for (let i = 0; i < 50; i++) {
    try {
      const targets = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
      const page = targets.find(t => t.type === "page");
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(200);
  }
  throw new Error("Chrome no respondió");
}

const ws = new WebSocket(await connect());
await new Promise(r => ws.addEventListener("open", r, { once: true }));
let nextId = 1;
const pending = new Map();
ws.addEventListener("message", ev => {
  const msg = JSON.parse(ev.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(msg.error.message)) : resolve(msg.result);
  }
});
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const id = nextId++;
  pending.set(id, { resolve, reject });
  ws.send(JSON.stringify({ id, method, params }));
});
const evaluate = async expr => (await send("Runtime.evaluate", { expression: expr, returnByValue: true })).result.value;

await send("Page.enable");
await send("Emulation.setDeviceMetricsOverride", { width: W + 2 * PAD, height: H + 2 * PAD, deviceScaleFactor: 1, mobile: false });

try {
  for (const file of scenes) {
    const name = file.replace(/\.html$/, "");
    const url = pathToFileURL(join(here, file)).href + "?t=0";
    await send("Page.navigate", { url });
    for (let i = 0; i < 50 && (await evaluate("document.readyState")) !== "complete"; i++) await sleep(100);
    await evaluate("document.fonts.ready.then(() => true)");

    const duration = await evaluate("DURATION");
    const frames = Math.round(duration * FPS);
    const dir = mkdtempSync(join(tmpdir(), `${name}-`));
    for (let i = 0; i < frames; i++) {
      await evaluate(`render(${i / FPS})`);
      const { data } = await send("Page.captureScreenshot", {
        format: "png", clip: { x: PAD, y: PAD, width: W, height: H, scale: 1 },
      });
      writeFileSync(join(dir, `${String(i).padStart(4, "0")}.png`), Buffer.from(data, "base64"));
    }
    const out = join(here, `${name}.mp4`);
    execFileSync("ffmpeg", ["-v", "error", "-y", "-framerate", String(FPS), "-i", join(dir, "%04d.png"),
      "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16", out]);
    rmSync(dir, { recursive: true, force: true });
    console.log(`${name}.mp4  ${frames} cuadros (${duration} s)`);
  }
} finally {
  ws.close();
  chrome.kill();
  await sleep(500);
  rmSync(profile, { recursive: true, force: true, maxRetries: 5 });
}
