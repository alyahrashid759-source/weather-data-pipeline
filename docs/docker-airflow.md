# Run the Weather Pipeline with Docker

This setup runs Apache Airflow with PostgreSQL for Airflow metadata. The pipeline's analytical warehouse remains the DuckDB file at `data/warehouse.duckdb`, shared with the containers through the repository mount.

## Prerequisites

- Docker Desktop installed and running.
- At least 4 GB RAM available to Docker (6 GB is preferable).
- Ports 8080 and the default PostgreSQL container port available.

## Start the environment

Run these commands from the repository root (the folder containing `docker-compose.yaml`):

```bash
docker compose build
docker compose up airflow-init
docker compose up -d
docker compose ps
```

Open [http://localhost:8080](http://localhost:8080) and sign in with:

- Username: `airflow`
- Password: `airflow`

Find the `weather_pipeline` DAG, unpause it, and use **Trigger DAG** for a manual run. The DAG runs Python ingestion and validation first, then `dbt build`.

## Check logs

```bash
docker compose logs --tail=100 airflow-scheduler
docker compose logs --tail=100 airflow-webserver
```

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
- This Compose file is for local learning and portfolio demonstration, not a hardened production deployment. Change the demo Airflow credentials before exposing the service beyond your own machine.
