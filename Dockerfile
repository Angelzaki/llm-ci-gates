FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY pyproject.toml README.md ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY samples ./samples
COPY tests ./tests

ENTRYPOINT ["python", "-m", "llm_ci_gates"]
CMD ["--metrics", "samples/metrics.json", "--thresholds", "samples/thresholds.yaml"]
