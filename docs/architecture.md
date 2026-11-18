# Arquitectura

`llm-ci-gates` es un paso de CI que convierte métricas de evaluación de un sistema LLM/RAG en una decisión binaria: el PR puede mergearse o no.

## Flujo CI/CD

```mermaid
flowchart LR
  PR[Pull request] --> T[pytest<br/>tests unitarios]
  T --> E[Evaluación RAG<br/>rag-eval-platform]
  E --> M[(metrics.json<br/>overall + suites)]
  M --> G{llm-ci<br/>gate}
  TH[(thresholds.yaml)] --> G
  G -- exit 0 PASS --> OK[Check verde<br/>merge permitido]
  G -- exit 2 FAIL --> BLK[Check rojo<br/>merge bloqueado]
```

## Componentes

```mermaid
flowchart TB
  CLI[cli.py<br/>argparse + rich] --> RG[gates.run_gate]
  RG --> LM[Lee metrics JSON]
  RG --> LT[load_thresholds<br/>yaml o json]
  LM --> FL[Aplana métricas<br/>overall, suite.nombre]
  FL --> EV[evaluate<br/>valor >= mínimo]
  LT --> EV
  EV --> OUT[Tabla + JSON<br/>exit 0 o 2]
```

| Módulo | Responsabilidad |
|---|---|
| `src/llm_ci_gates/cli.py` | Parseo de argumentos, tabla `rich`, línea JSON final y código de salida. |
| `src/llm_ci_gates/gates.py` | Carga de métricas y umbrales, aplanado de `suites[]` y evaluación `valor >= mínimo`. |

Reglas de evaluación:

- Cada clave del archivo de umbrales es un check. Las suites se nombran `suite.<nombre>`.
- Una métrica ausente en el archivo de métricas cuenta como FAIL (no se asume cumplida).
- El gate falla si cualquier check falla; no hay promedios que compensen.

## Referencia AWS

Despliegue de referencia para ejecutar el gate dentro de un pipeline gestionado. Es un diagrama conceptual: no incluye credenciales ni recursos creados por este repositorio.

```mermaid
flowchart LR
  DEV[Desarrollador] -->|git push / PR| GH[Repositorio Git]
  GH -->|webhook| CP[CodePipeline]
  CP --> CB1[CodeBuild<br/>pip install + pytest]
  CB1 --> CB2[CodeBuild<br/>evaluación RAG]
  CB2 -->|results/*.json| S3[(S3<br/>métricas versionadas)]
  S3 --> CB3[CodeBuild<br/>python -m llm_ci_gates]
  CB3 -->|exit 0| APP[Aprobación / merge]
  CB3 -->|exit 2| FAIL[Pipeline falla<br/>merge bloqueado]
  CB3 --> CW[CloudWatch Logs<br/>tabla + JSON del gate]
  SSM[SSM Parameter Store<br/>ruta de umbrales] -.-> CB3
  IAM[IAM role de CodeBuild<br/>mínimo privilegio] -.-> CB3
```

Notas de la referencia:

- El rol IAM de CodeBuild solo necesita lectura sobre el bucket de métricas y escritura de logs.
- Los umbrales viven en el repositorio (`samples/thresholds.yaml` o un archivo propio), de modo que cambiarlos pasa por revisión de código.
- El mismo contenedor del `Dockerfile` puede usarse como imagen de build en CodeBuild.
