from __future__ import annotations

import argparse
import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from llm_ci_gates.gates import run_gate

console = Console()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="llm-ci")
    parser.add_argument("--metrics", default="samples/metrics.json")
    parser.add_argument("--thresholds", default="samples/thresholds.yaml")
    args = parser.parse_args(argv)

    report = run_gate(Path(args.metrics), Path(args.thresholds))
    table = Table(title="LLM CI Gates")
    table.add_column("metric")
    table.add_column("value", justify="right")
    table.add_column("min", justify="right")
    table.add_column("ok")
    for c in report["checks"]:
        table.add_row(
            c["metric"],
            "—" if c["value"] is None else f"{c['value']:.2f}",
            str(c["min"]),
            "PASS" if c["ok"] else "FAIL",
        )
    console.print(table)
    console.print("GATE PASS" if report["ok"] else "GATE FAIL")
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["ok"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
