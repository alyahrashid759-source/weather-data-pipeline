import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "src"))

import pytest
from extract import parse_rows
from quality import validate, DataQualityError
from load import load_raw

PAYLOAD = {"hourly": {
    "time": ["2025-01-01T00:00", "2025-01-01T01:00"],
    "temperature_2m": [10.0, 11.5],
    "relative_humidity_2m": [80, 78],
    "wind_speed_10m": [5.0, 6.1],
}}


def test_parse_rows():
    rows = parse_rows("London", PAYLOAD)
    assert len(rows) == 2 and rows[0]["city"] == "London"


def test_validate_rejects_bad_temp():
    rows = parse_rows("London", PAYLOAD)
    rows[0]["temperature_c"] = 999
    with pytest.raises(DataQualityError):
        validate(rows)


def test_load_is_idempotent(tmp_path):
    db = str(tmp_path / "t.duckdb")
    rows = parse_rows("London", PAYLOAD)
    load_raw(rows, db)
    load_raw(rows, db)
    import duckdb
    assert duckdb.connect(db).execute("select count(*) from raw.weather").fetchone()[0] == 2
