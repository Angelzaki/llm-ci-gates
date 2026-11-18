# Integración con rag-eval-platform

[`rag-eval-platform`](https://github.com/Angelzaki/rag-eval-platform) genera resultados de evaluación en `results/*.json` con esta forma:

```json
{
  "scenario": "scenario_a",
  "overall": 0.8972,
  "suites": [
    { "name": "retrieval", "score": 1.0, "passed": 5, "failed": 0, "details": [] },
    { "name": "faithfulness", "score": 0.8889 }
  ]
}
```

`llm-ci-gates` solo usa `overall` y `suites[].name` / `suites[].score`; el resto se ignora.

## Uso local

1. En `rag-eval-platform`, generar los resultados del escenario.
2. Copiar `results/scenario_a.json` a este repositorio, o apuntar directamente a la ruta:

```bash
cp ../rag-eval-platform/results/scenario_a.json samples/scenario_a.json
python -m llm_ci_gates --metrics samples/scenario_a.json --thresholds samples/thresholds.yaml
```

O sin copiar:

```bash
python -m llm_ci_gates --metrics ../rag-eval-platform/results/scenario_a.json
```

Exit code `0` = PASS, `2` = FAIL.

## Uso en CI

En el workflow del repositorio que contiene el sistema RAG:

```yaml
- name: Evaluación RAG
  run: python -m rag_eval --scenario scenario_a

- name: Gate de calidad
  run: |
    pip install git+https://github.com/Angelzaki/llm-ci-gates.git
    python -m llm_ci_gates --metrics results/scenario_a.json --thresholds ci/thresholds.yaml
```

Cualquier exit code distinto de `0` hace fallar el job y, con branch protection, bloquea el merge.

## Umbrales propios

Las claves del archivo de umbrales son `overall` y `suite.<nombre>`. Para exigir más en una suite concreta:

```yaml
overall: 0.85
suite.retrieval: 0.80
suite.faithfulness: 0.85
suite.abstention: 0.75
```

Una suite que no aparece en las métricas pero sí en los umbrales falla el gate. Ver [CONCLUSIONS.md](CONCLUSIONS.md) antes de bajar cualquier mínimo.

## Integración con doc-compliance-local

[`doc-compliance-local`](https://github.com/Angelzaki/doc-compliance-local) escribe `results/compliance_report.json` con `overall_pct`, `critical_gaps` y `requirements[]`.

`llm-ci-gates` lo aplana así:

| Campo origen | Clave del gate |
|---|---|
| `overall_pct` | `overall` (= pct/100) |
| `critical_gaps` vacío | `critical_ok` = 1.0 |
| `critical_gaps` con ítems | `critical_ok` = 0.0 |
| `requirements[].score` | `req.<ID>` (p.ej. `req.ES-02`) |

```bash
# En doc-compliance-local
python -m doc_compliance check --es --out results

# Gate (PASS si score alto y sin brechas críticas)
python -m llm_ci_gates \
  --metrics ../doc-compliance-local/results/compliance_report.json \
  --thresholds samples/thresholds_compliance.yaml
```

Muestras versionadas: `samples/compliance_ok.json` (100%, Cumple) y `samples/compliance_fail.json` (~8.8%, 6 críticas).

El CI de `doc-compliance-local` ya corre este gate tras `check --es` (PASS) y `check --es --gap` (exit 2).

## Integración con knowledge-ops-console

[`knowledge-ops-console`](https://github.com/Angelzaki/knowledge-ops-console) escribe `results/eval.json` con:

```json
{ "metrics": { "pass_rate": 1.0, "recall@4": 1.0, "citation_hit": 1.0, "abstention_correct": 1.0 } }
```

Aplanado:

| Origen | Clave gate |
|---|---|
| `metrics.pass_rate` | `overall` |
| `metrics.recall@4` | `suite.retrieval` |
| `metrics.citation_hit` | `suite.citation` |
| `metrics.abstention_correct` | `suite.abstention` |

```bash
python -m knowledge_ops eval --all
python -m llm_ci_gates --metrics results/eval.json --thresholds ci/thresholds_knops.yaml
python -m llm_ci_gates --metrics results/eval_adversarial.json --thresholds ci/thresholds_adversarial.yaml
```

El CI de `knowledge-ops-console` ejecuta ambos gates tras `eval --all`.
