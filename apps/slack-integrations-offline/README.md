# Slack Integrations Offline Pipelines


# Run the piplines 

## Crawl data pipeline
```bash
uv run python -m tools.run --run-collect-crawl-data-pipeline
```

## ETL pipeline
```bash
uv run python -m tools.run --run-etl-pipeline
```

## Compute RAG pipeline
```bash
uv run python -m tools.run --run-compute-rag-pipeline
```