#!/usr/bin/env bash
set -euo pipefail
python -m llm_ci_gates --metrics "${1:-samples/metrics.json}" --thresholds "${2:-samples/thresholds.yaml}"
