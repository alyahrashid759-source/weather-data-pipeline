# Interview Walkthrough

Use this guide to explain the project clearly and accurately. Do not describe the local pipeline or Airflow deployment as production-deployed unless you have actually run and deployed those components.

## 60-second project explanation

"I built a batch ELT pipeline that retrieves hourly weather observations for four cities from the Open-Meteo API. Python handles extraction, response parsing, and data contract validation. I load the validated records into a DuckDB raw layer using a transaction and a city-plus-timestamp business key so reruns are idempotent. dbt then creates a typed staging model and a daily city-level analytics mart. I added pytest coverage, Ruff linting, and GitHub Actions CI, and supplied an Airflow DAG to schedule ingestion before transformation."

## Design decisions

### Why separate extraction, quality, loading, and transformation?
Each stage has one responsibility. This makes failures easier to isolate, tests easier to write, and future changes less risky.

### Why validate before loading?
Invalid records should fail before they contaminate the warehouse. Checks cover required fields, valid city and timestamp strings, duplicate business keys, finite numeric measurements, and reasonable domain ranges.

### What makes the load idempotent?
The business key is (city, observed_at). The loader deletes matching keys and inserts the incoming records in one transaction. Reprocessing the same batch leaves one row per business key.

### Why use a raw layer and dbt?
The raw table preserves ingested observations. dbt owns SQL transformations separately from ingestion code, making staging and analytics logic version-controlled, testable, and easier to maintain.

### Why DuckDB?
DuckDB keeps the project easy to run locally without provisioning a cloud database. It is suitable for a small analytical portfolio demonstration. For a multi-user or cloud production workload, I would evaluate a managed warehouse such as Redshift, Snowflake, or BigQuery based on scale, concurrency, governance, and cost.

### What does CI prove?
The workflow runs Ruff, pytest, and dbt parse. This verifies linting, automated test behavior, and dbt project parsing. It does not by itself prove a live API execution, a successful full dbt build against live data, or a running Airflow deployment.

## Limitations and next production steps

- Add retry/backoff with bounded handling for transient API failures.
- Add structured logs, metrics, alerting, and a run-level audit table.
- Add incremental backfills and explicit late-arriving-data handling.
- Store raw API payloads in durable object storage for replay and lineage.
- Deploy orchestration and warehouse components in a cloud environment.
- Add infrastructure as code, environment-specific configuration, and secrets management.
- Define data retention, access controls, and operational SLAs.

## Resume bullet (use after your local run succeeds)

Built an end-to-end Python ELT pipeline ingesting hourly API data for four cities, enforcing data-quality contracts, and performing transactional, idempotent loads into DuckDB; developed dbt staging and daily analytics models, pytest coverage, Ruff linting, GitHub Actions CI, and an Airflow orchestration DAG.

Only claim successful end-to-end execution and Airflow scheduling after you have run and verified them.
