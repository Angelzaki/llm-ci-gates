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
    """Normaliza JSON de rag-eval, doc-compliance, knowledge-ops u otros a claves planas."""
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
    # knowledge-ops-console: { "metrics": { "pass_rate": 1.0, "recall@4": 1.0, ... } }
    nested = metrics.get("metrics")
    if isinstance(nested, dict):
        for k, v in nested.items():
            if isinstance(v, (int, float)):
                key = str(k).replace("@", "_at_")
                flat[key] = float(v)
                flat[f"metric.{key}"] = float(v)
        if "pass_rate" in nested and isinstance(nested["pass_rate"], (int, float)):
            flat["overall"] = float(nested["pass_rate"])
        if "abstention_correct" in nested and isinstance(nested["abstention_correct"], (int, float)):
            flat["suite.abstention"] = float(nested["abstention_correct"])
        if "citation_hit" in nested and isinstance(nested["citation_hit"], (int, float)):
            flat["suite.citation"] = float(nested["citation_hit"])
        if nested.get("recall@4") is not None and isinstance(nested["recall@4"], (int, float)):
            flat["suite.retrieval"] = float(nested["recall@4"])
    # prompt-firewall batch_report.json
    if "accuracy" in metrics and isinstance(metrics["accuracy"], (int, float)):
        flat["overall"] = float(metrics["accuracy"])
        flat["accuracy"] = float(metrics["accuracy"])
    if "precision" in metrics and isinstance(metrics["precision"], (int, float)):
        flat["precision"] = float(metrics["precision"])
    if "recall" in metrics and isinstance(metrics["recall"], (int, float)):
        flat["recall"] = float(metrics["recall"])
    # support-copilot experiment report
    if "passed" in metrics and "total" in metrics:
        total = metrics["total"]
        if isinstance(total, (int, float)) and total:
            flat["overall"] = float(metrics["passed"]) / float(total)
            flat["pass_rate"] = flat["overall"]
    if "grounded_ok" in metrics and "grounded_total" in metrics:
        gt = metrics["grounded_total"]
        if isinstance(gt, (int, float)) and gt:
            flat["suite.grounded"] = float(metrics["grounded_ok"]) / float(gt)
    if "escalate_ok" in metrics and "escalate_total" in metrics:
        et = metrics["escalate_total"]
        if isinstance(et, (int, float)) and et:
            flat["suite.escalate"] = float(metrics["escalate_ok"]) / float(et)
    if "abstain_ok" in metrics and "abstain_total" in metrics:
        at = metrics["abstain_total"]
        if isinstance(at, (int, float)) and at:
            flat["suite.abstain"] = float(metrics["abstain_ok"]) / float(at)
    if "rbac_ok" in metrics and "rbac_total" in metrics:
        rt = metrics["rbac_total"]
        if isinstance(rt, (int, float)) and rt:
            flat["suite.rbac"] = float(metrics["rbac_ok"]) / float(rt)
    for k, v in metrics.items():
        if isinstance(v, (int, float)) and k not in flat:
            flat[k] = float(v)
    return flat


def run_gate(metrics_path: Path, thresholds_path: Path) -> dict:
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    thresholds = load_thresholds(thresholds_path)
    return evaluate(flatten_metrics(metrics), thresholds)
