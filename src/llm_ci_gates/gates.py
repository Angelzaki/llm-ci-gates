from __future__ import annotations

import json
from pathlib import Path


def load_thresholds(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if path.suffix in {".yaml", ".yml"}:
        import yaml

        return yaml.safe_load(text)
    return json.loads(text)


def evaluate(metrics: dict, thresholds: dict) -> dict:
    checks = []
    ok = True
    for key, minimum in thresholds.items():
        value = metrics.get(key)
        passed = value is not None and value >= minimum
        checks.append({"metric": key, "value": value, "min": minimum, "ok": passed})
        ok = ok and passed
    return {"ok": ok, "checks": checks}


def run_gate(metrics_path: Path, thresholds_path: Path) -> dict:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    thresholds = load_thresholds(thresholds_path)
    flat = {}
    if "overall" in metrics:
        flat["overall"] = metrics["overall"]
    if "score" in metrics:
        flat["score"] = metrics["score"]
    if "suites" in metrics:
        for s in metrics["suites"]:
            flat[f"suite.{s['name']}"] = s["score"]
    # allow direct flat metrics file too
    for k, v in metrics.items():
        if isinstance(v, (int, float)):
            flat[k] = v
    return evaluate(flat, thresholds)
