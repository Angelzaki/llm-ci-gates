from pathlib import Path

from llm_ci_gates.cli import main
from llm_ci_gates.gates import evaluate

ROOT = Path(__file__).resolve().parents[1]
THRESHOLDS = str(ROOT / "samples" / "thresholds.yaml")


def test_cli_exit_0_on_pass():
    assert main(["--metrics", str(ROOT / "samples" / "metrics.json"), "--thresholds", THRESHOLDS]) == 0


def test_cli_exit_2_on_fail():
    assert main(["--metrics", str(ROOT / "samples" / "metrics_fail.json"), "--thresholds", THRESHOLDS]) == 2


def test_missing_metric_fails():
    report = evaluate({"overall": 0.9}, {"overall": 0.8, "suite.faithfulness": 0.7})
    assert report["ok"] is False
    assert report["checks"][1]["value"] is None
