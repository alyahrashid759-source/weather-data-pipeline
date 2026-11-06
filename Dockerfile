FROM apache/airflow:2.10.5-python3.11

# Git is required by dbt project diagnostics.
USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install Airflow using its official constraints only.
RUN pip install --no-cache-dir \
    "apache-airflow==2.10.5" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.10.5/constraints-3.11.txt"

# Keep ingestion dependencies isolated from Airflow's pinned dependencies.
RUN python -m venv /home/airflow/project-venv \
    && /home/airflow/project-venv/bin/pip install --no-cache-dir \
    "requests>=2.32,<3" \
    "duckdb>=1.2,<3"

# Keep dbt isolated too; its dependency tree can differ from Airflow's.
RUN python -m venv /home/airflow/dbt-venv \
    && /home/airflow/dbt-venv/bin/pip install --no-cache-dir \
    "dbt-core==1.9.4" \
    "dbt-duckdb==1.9.3"

ENV PATH="/home/airflow/dbt-venv/bin:${PATH}"
