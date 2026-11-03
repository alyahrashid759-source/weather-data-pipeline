"""Idempotent load of raw rows into DuckDB (swap for BigQuery/Snowflake in prod)."""
import duckdb

DB_PATH = "data/warehouse.duckdb"


def load_raw(rows: list[dict], db_path: str = DB_PATH) -> int:
    con = duckdb.connect(db_path)
    con.execute("CREATE SCHEMA IF NOT EXISTS raw")
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS raw.weather (
            city VARCHAR, observed_at VARCHAR,
            temperature_c DOUBLE, humidity_pct DOUBLE, wind_kmh DOUBLE,
            loaded_at TIMESTAMP DEFAULT current_timestamp
        )
        """
    )
    # Idempotency: remove overlapping keys, then insert (reruns never duplicate)
    con.executemany(
        "DELETE FROM raw.weather WHERE city = ? AND observed_at = ?",
        [(r["city"], r["observed_at"]) for r in rows],
    )
    con.executemany(
        "INSERT INTO raw.weather (city, observed_at, temperature_c, humidity_pct, wind_kmh) "
        "VALUES (?, ?, ?, ?, ?)",
        [(r["city"], r["observed_at"], r["temperature_c"], r["humidity_pct"], r["wind_kmh"]) for r in rows],
    )
    con.close()
    return len(rows)
