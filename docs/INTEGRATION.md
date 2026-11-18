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
