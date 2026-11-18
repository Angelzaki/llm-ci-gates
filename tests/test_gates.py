from pathlib import Path

from llm_ci_gates.gates import run_gate

ROOT = Path(__file__).resolve().parents[1]


def test_pass_and_fail():
    ok = run_gate(ROOT / "samples" / "metrics.json", ROOT / "samples" / "thresholds.yaml")
    bad = run_gate(ROOT / "samples" / "metrics_fail.json", ROOT / "samples" / "thresholds.yaml")
    assert ok["ok"] is True
    assert bad["ok"] is False


def test_doc_compliance_ok_and_fail():
    thr = ROOT / "samples" / "thresholds_compliance.yaml"
    ok = run_gate(ROOT / "samples" / "compliance_ok.json", thr)
    bad = run_gate(ROOT / "samples" / "compliance_fail.json", thr)
    assert ok["ok"] is True
    assert bad["ok"] is False
    by_metric = {c["metric"]: c for c in bad["checks"]}
    assert by_metric["critical_ok"]["ok"] is False
    assert by_metric["overall"]["value"] < 0.2


def test_flatten_compliance_req_scores():
    from llm_ci_gates.gates import flatten_metrics
    import json

    data = json.loads((ROOT / "samples" / "compliance_ok.json").read_text(encoding="utf-8"))
    flat = flatten_metrics(data)
    assert flat["overall"] == 1.0
    assert flat["critical_ok"] == 1.0
    assert flat["req.ES-02"] == 1.0


def test_knowledge_ops_eval_gate():
    thr = ROOT / "samples" / "thresholds_knops.yaml"
    ok = run_gate(ROOT / "samples" / "knops_eval_ok.json", thr)
    bad = run_gate(ROOT / "samples" / "knops_eval_fail.json", thr)
    assert ok["ok"] is True
    assert bad["ok"] is False
    assert any(c["metric"] == "overall" and c["ok"] for c in ok["checks"])


def test_flatten_support_and_firewall():
    from llm_ci_gates.gates import flatten_metrics

    support = flatten_metrics(
        {
            "total": 28,
            "passed": 28,
            "grounded_ok": 16,
            "grounded_total": 16,
            "escalate_ok": 12,
            "escalate_total": 12,
        }
    )
    assert support["overall"] == 1.0
    assert support["suite.grounded"] == 1.0
    assert support["suite.escalate"] == 1.0

    firewall = flatten_metrics({"accuracy": 0.95, "precision": 1.0, "recall": 0.9, "total": 34})
    assert firewall["overall"] == 0.95
    assert firewall["precision"] == 1.0

