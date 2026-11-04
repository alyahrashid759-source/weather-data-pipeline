# Weather Data Engineering Pipeline

An end-to-end batch ELT portfolio project that ingests hourly weather observations for four cities, validates the data, loads it into DuckDB, transforms it with dbt, and supports scheduled orchestration with Apache Airflow.

> **Project status:** Core Python ingestion, validation, DuckDB loading, dbt models, and automated CI are implemented. Airflow is provided as an orchestration DAG and requires an Airflow runtime configured with this repository mounted at `/opt/project`.

## Architecture

```text
Open-Meteo Forecast API
        |
        v
Python extraction (4 cities; hourly observations)
        |
        v
Data contract and quality validation
        |
        v
DuckDB: raw.weather (idempotent transactional load)
        |
        v
dbt staging model: stg_weather
        |
        v
dbt mart: daily_weather
        |
        v
Analytics / BI consumption

Apache Airflow: schedules ingestion -> dbt build
GitHub Actions: lint -> pytest -> dbt parse
```

## Engineering practices demonstrated

- **API ingestion:** HTTP timeouts, status checks, response-shape validation, and consistent hourly-array validation.
- **Data quality:** required fields, numeric types, finite values, domain ranges, and duplicate business-key checks.
- **Idempotency:** observations are keyed by `(city, observed_at)`; reruns replace matching keys rather than duplicating records.
- **Transactional loading:** DuckDB writes are committed as a unit and rolled back on failure.
- **ELT:** raw data is retained in the warehouse and transformed in version-controlled dbt SQL.
- **Testing:** pytest covers parsing, invalid data, duplicate observations, and idempotent loading.
- **CI:** GitHub Actions runs Ruff, pytest, and dbt project parsing on pushes and pull requests.

## Technology stack

Python 3.11, Requests, DuckDB, dbt-duckdb, Apache Airflow, pytest, Ruff, GitHub Actions.

## Quick start

Python 3.11 is the recommended local runtime.

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\\Scripts\\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Run the ingestion pipeline from the repository root:

```bash
python src/pipeline.py
```

Build the dbt staging and mart models:

```bash
cd dbt_project
dbt debug --profiles-dir .
dbt build --profiles-dir .
```

Run tests and lint:

```bash
cd ..
pytest -q
ruff check src tests dags --ignore E401,E402
```

The DuckDB file is created at `data/warehouse.duckdb` and is intentionally excluded from Git.

## Query the analytics mart

After a successful ingestion and dbt build:

```python
import duckdb

connection = duckdb.connect("data/warehouse.duckdb", read_only=True)
print(connection.sql("SELECT * FROM main.daily_weather ORDER BY obs_date DESC, city").df())
connection.close()
```

## Airflow orchestration

The DAG is `dags/weather_dag.py`. Configure an Airflow environment with:

- This repository available at `/opt/project` on the scheduler and worker.
- The same Python dependencies installed in the Airflow worker image.
- The `weather_pipeline` DAG enabled.

The DAG runs extraction and loading first, followed by `dbt build`. Airflow itself is not installed by the lightweight local requirements file.

## Repository layout

```text
src/                         Python ingestion and data quality
  extract.py                 Open-Meteo API extraction and parsing
  quality.py                 Data contract validation
  load.py                    Transactional, idempotent DuckDB load
  pipeline.py                Pipeline entry point
dags/                        Apache Airflow DAG
dbt_project/                 dbt project, profile, staging and mart models
tests/                       Unit and integration tests
.github/workflows/ci.yml     Continuous integration
data/                        Local DuckDB warehouse (gitignored)
```

## Data source

Weather data is retrieved from the public [Open-Meteo Forecast API](https://open-meteo.com/). No API key is required for this demonstration.

## Limitations and production extensions

This is a portfolio-scale batch pipeline, not a high-availability production weather platform. A production deployment would add a managed warehouse, secret/configuration management, observability and alerting, schema evolution, backfills, infrastructure as code, and a deployed Airflow environment.

## Author

Built as a hands-on Data Engineering portfolio project.


## Portfolio documentation

- [Architecture, data flow, and data contract](docs/architecture.md)
- [Example analytics and data-quality SQL](docs/analytics_queries.sql)
- [Interview walkthrough and design decisions](docs/interview_guide.md)

## Local verification checklist

Run these from the repository root after installing the requirements:

```bash
python src/pipeline.py
pytest -q
ruff check src tests dags --ignore E401,E402
```

Then build the dbt models:

```bash
cd dbt_project
dbt debug --profiles-dir .
dbt build --profiles-dir .
```

Finally, inspect the mart using the SQL examples in [docs/analytics_queries.sql](docs/analytics_queries.sql). The local execution and Airflow runtime should be verified on the machine/environment where they are installed before describing them as successfully run.
