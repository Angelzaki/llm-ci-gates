from pathlib import Path

from llm_ci_gates.gates import run_gate

ROOT = Path(__file__).resolve().parents[1]


def test_pass_and_fail():
    ok = run_gate(ROOT / "samples" / "metrics.json", ROOT / "samples" / "thresholds.yaml")
    bad = run_gate(ROOT / "samples" / "metrics_fail.json", ROOT / "samples" / "thresholds.yaml")
    assert ok["ok"] is True
    assert bad["ok"] is False
