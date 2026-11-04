# Architecture and Data Flow

## End-to-end flow

\`\`\`mermaid
flowchart TD
    A[Open-Meteo Forecast API] --> B[Python extractor]
    B --> C[Response parsing and contract checks]
    C --> D[Data quality validation]
    D --> E[(DuckDB raw.weather)]
    E --> F[dbt staging: stg_weather]
    F --> G[dbt mart: daily_weather]
    G --> H[SQL analytics / BI consumer]
    I[Apache Airflow] -->|Schedules and orders| B
    I -->|Runs after ingestion| F
    J[GitHub Actions] --> K[Ruff lint]
    J --> L[pytest]
    J --> M[dbt parse]
\`\`\`

## Component responsibilities

| Component | Responsibility | Reliability mechanism |
|---|---|---|
| Open-Meteo API | Supplies hourly weather observations | HTTP timeout and status validation |
| Python extractor | Fetches configured cities and maps API fields to the project contract | Checks response structure and aligned hourly arrays |
| Quality layer | Rejects invalid, duplicate, missing, non-finite, or out-of-range values | Fails the run before loading |
| DuckDB raw layer | Persists source observations | Transaction and (city, observed_at) business key |
| dbt staging | Casts timestamps and exposes standardized fields | Source and model tests |
| dbt mart | Aggregates observations by city and date | SQL model with schema tests |
| Airflow | Orchestrates ingestion before transformation | Retries and single active DAG run |
| GitHub Actions | Runs code quality and automated tests | CI on pushes and pull requests |

## Data contract

Raw table: raw.weather

| Column | Type | Meaning |
|---|---|---|
| city | VARCHAR | City name |
| observed_at | VARCHAR | Observation timestamp in UTC |
| temperature_c | DOUBLE | Air temperature in Celsius |
| humidity_pct | DOUBLE | Relative humidity percentage |
| wind_kmh | DOUBLE | Wind speed in km/h |
| loaded_at | TIMESTAMP | Warehouse load timestamp |

Analytics table: main.daily_weather

| Column | Meaning |
|---|---|
| city | City name |
| obs_date | UTC observation date |
| avg_temp_c | Average hourly temperature |
| max_temp_c | Maximum hourly temperature |
| min_temp_c | Minimum hourly temperature |
| avg_humidity_pct | Average hourly relative humidity |
| max_wind_kmh | Maximum hourly wind speed |

## Idempotency and failure behavior

The loader replaces incoming records with the same (city, observed_at) key inside a DuckDB transaction. Re-running the same batch therefore does not create duplicate business records. If a database write fails, the transaction is rolled back.

The extractor currently fails the whole batch if a configured city cannot be fetched. This avoids silently publishing a partial city set; a production variant could add per-city retry, quarantine, and partial-success policy.

## Scope

This is a local portfolio implementation. DuckDB is an embedded analytical database, not a managed multi-user warehouse. Airflow requires a separately provisioned runtime and the DAG's configured project path. CI validates lint, tests, and dbt parsing; it does not claim to prove a live API run or an Airflow deployment.
