"""Transactional, idempotent loading of weather observations into DuckDB."""

from __future__ import annotations

from pathlib import Path

import duckdb

DB_PATH = "data/warehouse.duckdb"


def load_raw(rows: list[dict], db_path: str = DB_PATH) -> int:
    """Upsert observations by (city, observed_at) and return rows processed."""
    if not rows:
        return 0

    database = Path(db_path)
    database.parent.mkdir(parents=True, exist_ok=True)

    connection = duckdb.connect(str(database))
    try:
        connection.execute("BEGIN TRANSACTION")
        connection.execute("CREATE SCHEMA IF NOT EXISTS raw")
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS raw.weather (
                city VARCHAR NOT NULL,
                observed_at VARCHAR NOT NULL,
                temperature_c DOUBLE NOT NULL,
                humidity_pct DOUBLE NOT NULL,
                wind_kmh DOUBLE NOT NULL,
                loaded_at TIMESTAMP DEFAULT current_timestamp,
                PRIMARY KEY (city, observed_at)
            )
            """
        )
        connection.executemany(
            "DELETE FROM raw.weather WHERE city = ? AND observed_at = ?",
            [(row["city"], row["observed_at"]) for row in rows],
        )
        connection.executemany(
            """
            INSERT INTO raw.weather
                (city, observed_at, temperature_c, humidity_pct, wind_kmh)
            VALUES (?, ?, ?, ?, ?)
            """,
            [
                (
                    row["city"],
                    row["observed_at"],
                    row["temperature_c"],
                    row["humidity_pct"],
                    row["wind_kmh"],
                )
                for row in rows
            ],
        )
        connection.execute("COMMIT")
        return len(rows)
    except Exception:
        connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
