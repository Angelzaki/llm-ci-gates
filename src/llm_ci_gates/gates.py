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


def flatten_metrics(metrics: dict) -> dict:
    """Normaliza JSON de rag-eval, doc-compliance u otros a claves planas."""
    flat: dict = {}
    if "overall" in metrics and isinstance(metrics["overall"], (int, float)):
        flat["overall"] = float(metrics["overall"])
    if "score" in metrics and isinstance(metrics["score"], (int, float)):
        flat["score"] = float(metrics["score"])
    # doc-compliance-local: overall_pct 0-100 + critical_gaps + requirements[]
    if "overall_pct" in metrics and isinstance(metrics["overall_pct"], (int, float)):
        flat["overall"] = float(metrics["overall_pct"]) / 100.0
        flat["overall_pct"] = float(metrics["overall_pct"])
    if "critical_gaps" in metrics and isinstance(metrics["critical_gaps"], list):
        flat["critical_ok"] = 1.0 if len(metrics["critical_gaps"]) == 0 else 0.0
        flat["critical_gaps_count"] = float(len(metrics["critical_gaps"]))
    if "requirements" in metrics and isinstance(metrics["requirements"], list):
        for req in metrics["requirements"]:
            if not isinstance(req, dict):
                continue
            rid = req.get("id")
            score = req.get("score")
            if rid is not None and isinstance(score, (int, float)):
                flat[f"req.{rid}"] = float(score)
    if "suites" in metrics and isinstance(metrics["suites"], list):
        for s in metrics["suites"]:
            if isinstance(s, dict) and "name" in s and isinstance(s.get("score"), (int, float)):
                flat[f"suite.{s['name']}"] = float(s["score"])
    for k, v in metrics.items():
        if isinstance(v, (int, float)) and k not in flat:
            flat[k] = float(v)
    return flat


def run_gate(metrics_path: Path, thresholds_path: Path) -> dict:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    thresholds = load_thresholds(thresholds_path)
    return evaluate(flatten_metrics(metrics), thresholds)
