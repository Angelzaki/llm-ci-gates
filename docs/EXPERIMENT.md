# Experimento

Objetivo: comprobar que el gate deja pasar métricas sanas y bloquea una regresión, con código de salida distinguible (`0` / `2`).

Umbrales usados (`samples/thresholds.yaml`):

```yaml
overall: 0.80
suite.retrieval: 0.70
suite.faithfulness: 0.70
suite.abstention: 0.70
```

## Comandos

```bash
python -m llm_ci_gates --metrics samples/metrics.json        # exit 0
python -m llm_ci_gates --metrics samples/metrics_fail.json   # exit 2
```

## Caso 1 — `samples/metrics.json` (PASS)

| Check | Valor | Mínimo | Resultado |
|---|---:|---:|---|
| overall | 0.90 | 0.80 | PASS |
| suite.retrieval | 1.00 | 0.70 | PASS |
| suite.faithfulness | 1.00 | 0.70 | PASS |
| suite.abstention | 0.83 | 0.70 | PASS |

Veredicto: `GATE PASS`, exit code `0`.

## Caso 2 — `samples/metrics_fail.json` (FAIL)

| Check | Valor | Mínimo | Resultado |
|---|---:|---:|---|
| overall | 0.55 | 0.80 | FAIL |
| suite.retrieval | 0.40 | 0.70 | FAIL |
| suite.faithfulness | 0.50 | 0.70 | FAIL |
| suite.abstention | 0.50 | 0.70 | FAIL |

Veredicto: `GATE FAIL`, exit code `2`.

## Caso 3 — resultados reales de `rag-eval-platform`

Se pasó `results/scenario_a.json` y `results/scenario_b.json` del repositorio `rag-eval-platform` directamente como `--metrics`, sin transformación.

| Check | scenario_a | scenario_b | Mínimo |
|---|---:|---:|---:|
| overall | 0.8972 | 0.9773 | 0.80 |
| suite.retrieval | 1.0000 | 1.0000 | 0.70 |
| suite.faithfulness | 0.8889 | 1.0000 | 0.70 |
| suite.abstention | 0.8500 | 0.8333 | 0.70 |

Ambos escenarios: `GATE PASS`, exit code `0`.

## Caso 4 — `doc-compliance-local` (checklist ES)

Umbrales: `samples/thresholds_compliance.yaml` (`overall ≥ 0.85`, `critical_ok = 1.0`).

```bash
python -m llm_ci_gates --metrics samples/compliance_ok.json --thresholds samples/thresholds_compliance.yaml
python -m llm_ci_gates --metrics samples/compliance_fail.json --thresholds samples/thresholds_compliance.yaml
```

| Muestra | overall | critical_ok | Exit |
|---|---:|---:|---|
| `compliance_ok.json` (`docs_ok_es`) | 1.00 | 1.0 | 0 PASS |
| `compliance_fail.json` (`docs_gap_es`) | 0.088 | 0.0 | 2 FAIL |

## Lectura de resultados

- El aplanado acepta `overall`+`suites` (rag-eval) y `overall_pct`+`critical_gaps`+`requirements` (doc-compliance).
- Una política con score “aceptable” pero brechas críticas sigue en FAIL por `critical_ok`.
- Los tests y el CI cubren ambos contratos.
