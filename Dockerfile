FROM apache/airflow:2.10.5-python3.11

# Install Git and runtime dependencies for the ingestion task.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Keep Airflow's own environment compatible with the official constraints.
RUN pip install --no-cache-dir \
    "apache-airflow==2.10.5" \
    "requests>=2.32,<3" \
    "duckdb>=1.2,<3" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt"

# Isolate dbt from Airflow's pinned dependencies to avoid protobuf conflicts.
RUN python -m venv /home/airflow/dbt-venv \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir \
    "dbt-core==1.9.4" \
    "dbt-duckdb==1.9.3"

ENV PATH="/home/airflow/dbt-venv/bin:${PATH}"
