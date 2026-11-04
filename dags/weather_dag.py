"""Airflow DAG: ingest hourly weather and build dbt analytics models."""

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = "/opt/project"

default_args = {
    "owner": "data-engineering",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="weather_pipeline",
    description="Extract weather API data, validate it, load DuckDB, and build dbt marts.",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    max_active_runs=1,
    tags=["data-engineering", "weather", "duckdb", "dbt"],
) as dag:
    ingest = BashOperator(
        task_id="extract_validate_load",
        bash_command=f"cd {PROJECT_DIR} && python src/pipeline.py",
    )

    transform = BashOperator(
        task_id="dbt_build",
        bash_command=f"cd {PROJECT_DIR}/dbt_project && dbt build --profiles-dir .",
    )

    ingest >> transform
