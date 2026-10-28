"""One small refinement step: recipe -> model.glb -> render -> logged comparison.

Usage (from experiments/video_to_3d):
  python -P scripts/step.py iterations/iter_N "what I changed and why"   # apply recipe.json, render, log
  python -P scripts/step.py iterations/iter_N --revert K                  # restore recipe + model of step K

iterations/iter_N/recipe.json:
{
  "base": "iterations/iter_2/model_raw.glb",  # raw mesh to start from (relative to experiments/video_to_3d)
  "post": {...},        # generate.py post-processing (clip, body scale, texture lift, skin...) - see generate.py
  "fit": {...} | null,  # refine.fit_silhouette options - deform mesh to match the video outlines
  "project": {...} | null,  # refine.project_texture options - paint video frames onto the texture
  "unlit": false        # true: KHR_materials_unlit, renderer shows texture colours without extra shading
}
Every step is saved in iterations/iter_N/steps/ (step_K.json, step_K.png, step_K.glb) and appended to
steps.jsonl, so steps can be compared and reverted.
"""
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT  # noqa: E402


def log_rows(it: Path):
    p = it / "steps.jsonl"
    return [json.loads(l) for l in p.read_text().splitlines() if l.strip()] if p.exists() else []


def build(it: Path, recipe: dict, notes: list):
    import trimesh
    from generate import postprocess
    from refine import fit_silhouette, project_texture, set_unlit
    tmp = it / "_post.glb"
    postprocess(ROOT / recipe["base"], tmp, recipe.get("post", {}))
    mesh = trimesh.load(str(tmp), force="mesh", process=False)
    if recipe.get("fit"):
        mesh = fit_silhouette(mesh, recipe["fit"], log=notes.append)
    if recipe.get("project"):
        mesh = project_texture(mesh, recipe["project"], log=notes.append, out_dir=it)
    mesh.export(str(it / "model.glb"))
    if recipe.get("unlit"):
        set_unlit(it / "model.glb")
    tmp.unlink(missing_ok=True)


def main():
    it = Path(sys.argv[1]).resolve()
    steps = it / "steps"
    steps.mkdir(exist_ok=True)
    rows = log_rows(it)
    if len(sys.argv) > 3 and sys.argv[2] == "--revert":
        k = int(sys.argv[3])
        shutil.copy(steps / f"step_{k}.json", it / "recipe.json")
        shutil.copy(steps / f"step_{k}.glb", it / "model.glb")
        subprocess.run([sys.executable, "-P", str(ROOT / "scripts" / "render.py"), str(it)], check=True,
                       capture_output=True)
        print(f"reverted to step {k}")
        return
    desc = sys.argv[2] if len(sys.argv) > 2 else ""
    recipe = json.loads((it / "recipe.json").read_text())
    t0 = time.time()
    notes = []
    build(it, recipe, notes)
    r = subprocess.run([sys.executable, "-P", str(ROOT / "scripts" / "render.py"), str(it)], capture_output=True,
                       text=True)
    if r.returncode:
        print(r.stderr[-2000:])
        sys.exit(1)
    m = json.loads((it / "metrics.json").read_text())
    k = len(rows) + 1
    per = {a: v["silhouette_iou"] for a, v in m.items() if isinstance(v, dict) and "silhouette_iou" in v}
    col = [v["mean_color_diff"] for v in m.values() if isinstance(v, dict) and v.get("mean_color_diff") is not None]
    row = {"step": k, "desc": desc, "mean_iou": m["mean_silhouette_iou"],
           "mean_color_diff": round(sum(col) / len(col), 1) if col else None, "per_angle_iou": per,
           "notes": notes, "seconds": round(time.time() - t0)}
    with open(it / "steps.jsonl", "a") as fh:
        fh.write(json.dumps(row) + "\n")
    shutil.copy(it / "recipe.json", steps / f"step_{k}.json")
    shutil.copy(it / "comparison.png", steps / f"step_{k}.png")
    shutil.copy(it / "model.glb", steps / f"step_{k}.glb")
    prev = rows[-1]["mean_iou"] if rows else None
    best = max([r["mean_iou"] for r in rows], default=None)
    print(json.dumps({"step": k, "mean_iou": row["mean_iou"], "delta_vs_prev": None if prev is None else round(row["mean_iou"] - prev, 3),
                      "best_before": best, "mean_color_diff": row["mean_color_diff"], "per_angle_iou": per,
                      "notes": notes, "comparison": str(steps / f"step_{k}.png"), "seconds": row["seconds"]}, indent=1))


if __name__ == "__main__":
    main()
