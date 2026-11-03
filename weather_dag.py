"""Airflow DAG: ingest, then dbt build, every day."""
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {"retries": 2, "retry_delay": timedelta(minutes=5)}

with DAG(
    dag_id="weather_pipeline",
    start_date=datetime(2025, 1, 1),
    schedule="@daily",
    catchup=False,
    default_args=default_args,
    tags=["data-engineering"],
) as dag:
    ingest = BashOperator(task_id="ingest", bash_command="cd /opt/project && python src/pipeline.py")
    transform = BashOperator(
        task_id="dbt_build",
        bash_command="cd /opt/project/dbt_project && dbt build --profiles-dir .",
    )
    ingest >> transform
