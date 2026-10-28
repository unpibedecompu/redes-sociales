"""Render the WhatsApp chat animation to an mp4 (1080x1920, 30fps, with the voice note audio).

Usage:
  python render.py "<chat.html query string>" <audio file> <output.mp4>

Example (from chat_wpp/, with `python -m http.server 8765` running in the project folder):
  python render.py "contact=Claude&audio=../edicion/ai_voice.mp4&avatar=../images/claude.svg" ^
      ../edicion/ai_voice.mp4 ../edicion/chat_claude.mp4

Uses Playwright's fake clock so every frame is captured at an exact time, regardless
of how long each screenshot takes. CSS animations are stepped manually for the same reason.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8765/chat_wpp/chat.html"
FPS = 30
TAIL_MS = 1000  # hold the final frame after the animation ends
W, H = 432, 768  # 9:16 viewport in CSS px (render mode stretches the phone to fill it)
SCALE = 2.5  # 432x768 * 2.5 = 1080x1920

STEP_CSS_ANIMATIONS = """dt => {
  for (const a of document.getAnimations()) {
    a.pause();
    a.__t = (a.__t ?? 0) + dt;
    a.currentTime = a.__t;
  }
}"""


def main(query, audio, out):
    frames = Path(tempfile.mkdtemp(prefix="chat_frames_"))
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=SCALE)
            page.clock.install()
            page.goto(f"{BASE}?{query}&render=1")
            page.evaluate("() => window.__ready")
            page.evaluate("() => document.fonts.ready")
            # Stop time from flowing on its own; from here on only run_for() advances it
            page.clock.pause_at(page.evaluate("() => Date.now()") + 100)
            t0 = page.evaluate("() => performance.now()")
            page.evaluate("() => { runAnimation(); }")

            i, elapsed, done_at = 0, 0, None
            while True:
                page.evaluate(STEP_CSS_ANIMATIONS, 0)  # pause newly created animations
                page.screenshot(path=frames / f"{i:05d}.png")
                i += 1
                target = round(i * 1000 / FPS)
                dt = target - elapsed
                page.clock.run_for(dt)
                page.evaluate(STEP_CSS_ANIMATIONS, dt)
                elapsed = target
                if done_at is None and page.evaluate("() => !!window.__done"):
                    done_at = elapsed
                if done_at is not None and elapsed - done_at >= TAIL_MS:
                    break
            audio_start_ms = round(page.evaluate("() => window.__audioStart") - t0)
            browser.close()

        print(f"{i} frames, audio starts at {audio_start_ms} ms")
        subprocess.run([
            "ffmpeg", "-y", "-v", "error",
            "-framerate", str(FPS), "-i", str(frames / "%05d.png"),
            "-i", audio,
            "-filter_complex", f"[0:v]scale=1080:1920:flags=lanczos,format=yuv420p[v];"
                               f"[1:a]adelay={audio_start_ms}:all=1,apad[a]",
            "-map", "[v]", "-map", "[a]", "-shortest",
            "-c:v", "libx264", "-crf", "14", "-preset", "slow", "-r", str(FPS),
            "-c:a", "aac", "-b:a", "192k",
            out,
        ], check=True)
        print("wrote", out)
    finally:
        shutil.rmtree(frames, ignore_errors=True)


if __name__ == "__main__":
    main(*sys.argv[1:4])
