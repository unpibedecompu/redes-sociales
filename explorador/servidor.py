#!/usr/bin/env python3
"""Explorador local de animaciones.

Sirve todo el repo (así funcionan los caminos relativos de cada animación) y agrega
/explorador/lista.json con todos los .html y .mp4 del repo, y el render a mp4:
    /explorador/render/iniciar?ruta=...    arranca (o encola) el render
    /explorador/render/estado?ruta=...     {estado, progreso, mensaje}
    /explorador/render/descargar?ruta=...  baja el mp4
Los mp4 quedan en explorador/renders/ y se reusan mientras no cambie nada en la carpeta de la animación.
Las páginas de montaje (con TRAMOS y un <video>) se arman con ffmpeg: el video real con las escenas encima.
Para renderizar hace falta `npm install` en explorador/ (Playwright Firefox) y ffmpeg.

    python3 explorador/servidor.py          # http://localhost:8765/explorador/
    python3 explorador/servidor.py 9000     # otro puerto
"""
import json
import os
import subprocess
import sys
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

RAIZ = Path(__file__).resolve().parent.parent
AQUI = Path(__file__).resolve().parent
RENDERS = AQUI / "renders"
FPS = 30
IGNORAR = {".git", "node_modules", "explorador", "__pycache__"}
TIPOS = {".html": "animacion", ".mp4": "video"}


def lista():
    archivos = []
    for carpeta, subcarpetas, nombres in os.walk(RAIZ):
        subcarpetas[:] = sorted(d for d in subcarpetas if d not in IGNORAR and not d.startswith("."))
        for nombre in sorted(nombres):
            tipo = TIPOS.get(Path(nombre).suffix.lower())
            if not tipo:
                continue
            ruta = Path(carpeta, nombre)
            archivos.append({
                "ruta": ruta.relative_to(RAIZ).as_posix(),
                "tipo": tipo,
                "modificado": ruta.stat().st_mtime,
            })
    return archivos


# ---------------- render a mp4 ----------------
trabajos = {}                     # ruta -> {estado, progreso, mensaje}
un_render_a_la_vez = threading.Lock()


def salida_de(ruta):
    return RENDERS / (ruta.replace("/", "__").removesuffix(".html") + ".mp4")


def ultima_modificacion(ruta):
    """Lo más nuevo entre la carpeta de la animación (html, js...) y las piezas de los personajes."""
    carpeta = (RAIZ / ruta).parent
    fechas = [f.stat().st_mtime for f in carpeta.iterdir() if f.is_file() and f.suffix.lower() != ".mp4"]
    partes = RAIZ / "animations/paper_cutoff_characters/parts.js"
    if partes.exists():
        fechas.append(partes.stat().st_mtime)
    return max(fechas)


def al_dia(ruta):
    mp4 = salida_de(ruta)
    return mp4.exists() and mp4.stat().st_mtime > ultima_modificacion(ruta)


def url_de(ruta, puerto):
    return f"http://localhost:{puerto}/" + quote(ruta)


def correr_render(url, salida, dur, avance):
    """node render.js; avance(i, n) con cada cuadro."""
    cmd = ["node", str(AQUI / "render.js"), url, str(salida)] + ([f"{dur:.3f}"] if dur else [])
    proc = subprocess.Popen(cmd, cwd=AQUI, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    for linea in proc.stdout:
        if linea.startswith("PROGRESO"):
            _, i, n = linea.split()
            avance(int(i), int(n))
    if proc.wait() != 0:
        raise RuntimeError(proc.stderr.read().strip() or "falló el render")


def renderizar(ruta, puerto):
    t = trabajos[ruta]
    with un_render_a_la_vez:
        try:
            t.update(estado="renderizando", progreso=0, mensaje="Abriendo la animación…")
            RENDERS.mkdir(exist_ok=True)
            salida = salida_de(ruta)
            temporal = salida.with_suffix(".tmp.mp4")
            info = json.loads(subprocess.run(["node", str(AQUI / "render.js"), "--tramos", url_de(ruta, puerto)],
                                             cwd=AQUI, capture_output=True, text=True, check=True).stdout or "{}")
            if info.get("tramos") and info.get("video"):
                montar(ruta, info, temporal, puerto, t)
            else:
                def avance(i, n):
                    t.update(progreso=i / n, mensaje=f"Cuadro {i} de {n}")
                correr_render(url_de(ruta, puerto), temporal, None, avance)
            temporal.replace(salida)
            t.update(estado="listo", progreso=1, mensaje="Listo")
        except Exception as e:  # noqa: BLE001 - el mensaje va a la página
            t.update(estado="error", mensaje=str(e)[-400:])


def montar(ruta, info, salida, puerto, t):
    """Montaje: cada escena renderizada a la duración de su tramo y encima del video real, con su audio."""
    carpeta = (RAIZ / ruta).parent
    video = RAIZ / unquote(urlparse(info["video"]).path).lstrip("/")
    escenas = [(a, b, src) for a, b, src, *_ in info["tramos"] if src]
    total = sum(round((b - a) * FPS) for a, b, _ in escenas)
    hechos = 0
    partes = []
    for k, (a, b, src) in enumerate(escenas):
        parte = RENDERS / f"{salida_de(ruta).stem}__{k}.mp4"
        base = hechos

        def avance(i, n, k=k, base=base):
            t.update(progreso=(base + i) / total * 0.95, mensaje=f"Escena {k + 1} de {len(escenas)}: cuadro {i} de {n}")
        correr_render(url_de((carpeta / src).relative_to(RAIZ).as_posix(), puerto), parte, b - a, avance)
        hechos += round((b - a) * FPS)
        partes.append((a, b, parte))
    t.update(mensaje="Uniendo con el video…")
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(video)]
    for _, _, parte in partes:
        cmd += ["-i", str(parte)]
    filtros, ultimo = [f"[0:v]fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1[v0]"], "v0"
    for i, (a, b, _) in enumerate(partes, start=1):
        filtros.append(f"[{i}:v]setpts=PTS-STARTPTS+{a}/TB[e{i}]")
        filtros.append(f"[{ultimo}][e{i}]overlay=enable='between(t,{a},{b})':eof_action=pass[v{i}]")
        ultimo = f"v{i}"
    cmd += ["-filter_complex", ";".join(filtros), "-map", f"[{ultimo}]", "-map", "0:a?",
            "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k",
            "-movflags", "+faststart", str(salida)]
    subprocess.run(cmd, check=True, capture_output=True)
    for _, _, parte in partes:
        parte.unlink(missing_ok=True)


class Handler(SimpleHTTPRequestHandler):
    def responder_json(self, datos, codigo=200):
        cuerpo = json.dumps(datos).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path.startswith("/explorador/render/"):
            ruta = parse_qs(url.query).get("ruta", [""])[0]
            archivo = (RAIZ / ruta).resolve()
            if not ruta.endswith(".html") or RAIZ not in archivo.parents or not archivo.exists():
                return self.responder_json({"estado": "error", "mensaje": "Ruta inválida"}, 400)
            accion = url.path.rsplit("/", 1)[1]
            if accion == "iniciar":
                t = trabajos.get(ruta)
                if al_dia(ruta) and not (t and t["estado"] in ("en cola", "renderizando")):
                    trabajos[ruta] = {"estado": "listo", "progreso": 1, "mensaje": "Listo (ya estaba renderizado)"}
                elif not t or t["estado"] in ("listo", "error"):
                    trabajos[ruta] = {"estado": "en cola", "progreso": 0, "mensaje": "Esperando otro render…"}
                    threading.Thread(target=renderizar, args=(ruta, self.server.server_address[1]), daemon=True).start()
                return self.responder_json(trabajos[ruta])
            if accion == "estado":
                return self.responder_json(trabajos.get(ruta, {"estado": "nada", "progreso": 0, "mensaje": ""}))
            if accion == "descargar":
                mp4 = salida_de(ruta)
                if not mp4.exists():
                    return self.responder_json({"estado": "error", "mensaje": "Todavía no está renderizado"}, 404)
                nombre = Path(ruta).stem + ".mp4"
                self.send_response(200)
                self.send_header("Content-Type", "video/mp4")
                self.send_header("Content-Length", str(mp4.stat().st_size))
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(nombre)}")
                self.end_headers()
                with open(mp4, "rb") as f:
                    while bloque := f.read(1 << 20):
                        self.wfile.write(bloque)
                return
        if url.path == "/explorador/lista.json":
            return self.responder_json(lista())
        if self.path in ("/", ""):
            self.send_response(302)
            self.send_header("Location", "/explorador/")
            self.end_headers()
            return
        super().do_GET()

    def end_headers(self):
        # siempre la última versión de cada animación al recargar
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    puerto = int(sys.argv[1]) if len(sys.argv) > 1 else 8765
    servidor = ThreadingHTTPServer(("127.0.0.1", puerto), partial(Handler, directory=str(RAIZ)))
    print(f"Explorador en http://localhost:{puerto}/explorador/")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
