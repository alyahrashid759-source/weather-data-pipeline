"""Data quality checks applied before records enter the warehouse."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping


class DataQualityError(ValueError):
    """Raised when extracted weather records violate the data contract."""


REQUIRED_FIELDS = (
    "city",
    "observed_at",
    "temperature_c",
    "humidity_pct",
    "wind_kmh",
)


def validate(rows: Iterable[Mapping]) -> None:
    """Validate required keys, uniqueness, numeric values, and domain ranges."""
    records = list(rows)
    if not records:
        raise DataQualityError("No rows extracted")

    seen_keys: set[tuple[str, str]] = set()
    for row_number, row in enumerate(records, start=1):
        missing = [field for field in REQUIRED_FIELDS if field not in row]
        if missing:
            raise DataQualityError(
                f"Row {row_number} is missing required fields: {', '.join(missing)}"
            )

        city = row["city"]
        observed_at = row["observed_at"]
        if not isinstance(city, str) or not city.strip():
            raise DataQualityError(f"Row {row_number} has an invalid city")
        if not isinstance(observed_at, str) or not observed_at.strip():
            raise DataQualityError(f"Row {row_number} has an invalid observed_at")

        key = (city, observed_at)
        if key in seen_keys:
            raise DataQualityError(f"Duplicate weather observation: {key}")
        seen_keys.add(key)

        for field, lower, upper in (
            ("temperature_c", -90, 60),
            ("humidity_pct", 0, 100),
            ("wind_kmh", 0, 400),
        ):
            value = row[field]
            if value is None or isinstance(value, bool):
                raise DataQualityError(f"Row {row_number} has null/invalid {field}")
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise DataQualityError(f"Row {row_number} has non-numeric {field}")
            if not lower <= value <= upper:
                raise DataQualityError(
                    f"Row {row_number} has out-of-range {field}: {value}"
                )
