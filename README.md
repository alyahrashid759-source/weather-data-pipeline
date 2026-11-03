# Weather Data Pipeline (Batch ELT)

An end-to-end batch data pipeline: **API → validation → warehouse → dbt models → Airflow orchestration → CI**.

## Architecture

```
Open-Meteo API --> extract.py --> quality.py --> load.py --> raw.weather (DuckDB)
                                                                  |
                                                       dbt: stg_weather (view)
                                                                  |
                                                       dbt: daily_weather (mart)
        Orchestrated by Airflow (daily)  |  Tested by pytest + dbt tests in GitHub Actions
```

## Problem solved
Raw hourly weather from multiple cities is messy and arrives continuously. This pipeline ingests it
idempotently, rejects bad data early, and produces an analytics-ready daily table.

## Key design decisions
- **Idempotent loads**: delete-then-insert by (city, observed_at), so reruns never create duplicates.
- **Quality gate before load**: out-of-range or missing values fail the run instead of polluting the warehouse.
- **ELT with dbt**: transformations live in version-controlled SQL with built-in tests.
- **DuckDB locally**: zero setup. Swap `load.py` and the dbt profile for BigQuery or Snowflake in production.

## Run it
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python src/pipeline.py
cd dbt_project && dbt build --profiles-dir .
pytest -q
```

## Project layout
```
src/        extract, quality checks, load, pipeline entrypoint
dags/       Airflow DAG (ingest >> dbt build)
dbt_project/ staging + mart models with tests
tests/      unit tests (parsing, validation, idempotency)
.github/    CI: lint + tests on every push
```

## Next improvements
- Move to BigQuery/Snowflake with Terraform-managed infra
- Add incremental dbt models and freshness checks
- Add alerting on DAG failure
