"""Unit tests for extraction parsing, quality checks, and warehouse loading."""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import duckdb
import pytest

from extract import parse_rows
from load import load_raw
from quality import DataQualityError, validate

PAYLOAD = {
    "hourly": {
        "time": ["2025-01-01T00:00", "2025-01-01T01:00"],
        "temperature_2m": [10.0, 11.5],
        "relative_humidity_2m": [80, 78],
        "wind_speed_10m": [5.0, 6.1],
    }
}


def test_parse_rows_maps_hourly_observations():
    rows = parse_rows("London", PAYLOAD)
    assert len(rows) == 2
    assert rows[0] == {
        "city": "London",
        "observed_at": "2025-01-01T00:00",
        "temperature_c": 10.0,
        "humidity_pct": 80,
        "wind_kmh": 5.0,
    }


def test_parse_rows_rejects_inconsistent_array_lengths():
    payload = {"hourly": {**PAYLOAD["hourly"], "wind_speed_10m": [5.0]}}
    with pytest.raises(ValueError, match="inconsistent lengths"):
        parse_rows("London", payload)


def test_validate_accepts_valid_rows():
    validate(parse_rows("London", PAYLOAD))


def test_validate_rejects_out_of_range_temperature():
    rows = parse_rows("London", PAYLOAD)
    rows[0]["temperature_c"] = 999
    with pytest.raises(DataQualityError, match="out-of-range temperature_c"):
        validate(rows)


def test_validate_rejects_null_measurements():
    rows = parse_rows("London", PAYLOAD)
    rows[0]["humidity_pct"] = None
    with pytest.raises(DataQualityError, match="null/invalid humidity_pct"):
        validate(rows)


def test_validate_rejects_duplicate_observations():
    rows = parse_rows("London", PAYLOAD)
    rows.append(rows[0].copy())
    with pytest.raises(DataQualityError, match="Duplicate"):
        validate(rows)


def test_load_is_idempotent(tmp_path):
    database = str(tmp_path / "warehouse.duckdb")
    rows = parse_rows("London", PAYLOAD)

    assert load_raw(rows, database) == 2
    assert load_raw(rows, database) == 2

    with duckdb.connect(database, read_only=True) as connection:
        count = connection.execute("SELECT COUNT(*) FROM raw.weather").fetchone()[0]
    assert count == 2


def test_load_empty_batch_does_not_create_database(tmp_path):
    database = tmp_path / "empty.duckdb"
    assert load_raw([], str(database)) == 0
    assert not database.exists()
