"""Lightweight data quality checks run before loading."""


class DataQualityError(Exception):
    pass


def validate(rows: list[dict]) -> None:
    if not rows:
        raise DataQualityError("No rows extracted")
    for r in rows:
        if r["city"] is None or r["observed_at"] is None:
            raise DataQualityError(f"Missing key fields: {r}")
        t = r["temperature_c"]
        if t is not None and not -90 <= t <= 60:
            raise DataQualityError(f"Temperature out of range: {r}")
        h = r["humidity_pct"]
        if h is not None and not 0 <= h <= 100:
            raise DataQualityError(f"Humidity out of range: {r}")
