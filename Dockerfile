FROM apache/airflow:2.10.5-python3.11

USER airflow

# Keep Airflow pinned to its official Python 3.11 constraints, then add
# the dbt-duckdb adapter used by this portfolio project.
RUN pip install --no-cache-dir \
    "apache-airflow==2.10.5" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt" \
    && pip install --no-cache-dir \
    "dbt-core==1.9.4" \
    "dbt-duckdb==1.9.3" \
    "requests>=2.32,<3"
