# Run the Weather Pipeline with Docker

This setup runs Apache Airflow with PostgreSQL for Airflow metadata. The pipeline's analytical warehouse remains the DuckDB file at `data/warehouse.duckdb`, shared with the containers through the repository mount.

## Prerequisites

- Docker Desktop installed and running.
- At least 4 GB RAM available to Docker (6 GB is preferable).
- Ports 8080 and the default PostgreSQL container port available.

## Build and start the environment

Run these commands from the repository root (the folder containing `docker-compose.yaml`):

```bash
docker compose down --remove-orphans
docker compose build --no-cache
docker compose up airflow-init
docker compose up -d
docker compose ps
```

The Compose file defines four services: `postgres`, `airflow-init`, `airflow-webserver`, and `airflow-scheduler`. The Airflow image includes Git because dbt's project diagnostics check for the Git executable.

Verify the runtime dependencies inside the webserver container:

```bash
docker compose exec airflow-webserver git --version
docker compose exec airflow-webserver dbt --version
```

Before triggering the DAG, run dbt's connection check and build once inside the same container image:

```bash
docker compose exec airflow-webserver bash -lc "cd /opt/project/dbt_project && dbt debug --profiles-dir ."
docker compose exec airflow-webserver bash -lc "cd /opt/project/dbt_project && dbt build --profiles-dir ."
```

If these commands succeed, open [http://localhost:8080](http://localhost:8080) and sign in with:

- Username: `airflow`
- Password: `airflow`

Find the `weather_pipeline` DAG, unpause it, and use **Trigger DAG** for a manual run. The DAG runs Python ingestion and validation first, then `dbt build`.

## Check logs

```bash
docker compose logs --tail=100 airflow-scheduler
docker compose logs --tail=100 airflow-webserver
docker compose logs --tail=100 airflow
```

The final command is useful only if an older/orphaned service named `airflow` still exists; the current Compose stack uses the webserver and scheduler services.

## Stop the environment

```bash
docker compose down
```

To also remove the PostgreSQL metadata and Airflow log volumes (destructive; this resets the local Airflow environment):

```bash
docker compose down --volumes
```

## Notes

- Do not run `pip install` into a running Airflow container. Dependencies are declared in the Dockerfile and installed when the image is built.
- Airflow metadata is stored in PostgreSQL. Weather analytics data is stored separately in DuckDB.
- The Docker image installs Git so `dbt debug` can pass its required-dependency check.
- This Compose file is for local learning and portfolio demonstration, not a hardened production deployment. Change the demo Airflow credentials before exposing the service beyond your own machine.
