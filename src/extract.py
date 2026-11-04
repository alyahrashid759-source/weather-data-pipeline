"""Extract hourly weather observations from the Open-Meteo forecast API."""

from __future__ import annotations

import requests

API_URL = "https://api.open-meteo.com/v1/forecast"
CITIES = {
    "London": (51.51, -0.13),
    "New York": (40.71, -74.01),
    "Mumbai": (19.08, 72.88),
    "Tokyo": (35.68, 139.69),
}
HOURLY_FIELDS = (
    "temperature_2m",
    "relative_humidity_2m",
    "wind_speed_10m",
)


def fetch_city(city: str, lat: float, lon: float) -> dict:
    """Fetch recent and forecast hourly weather for one configured city."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_FIELDS),
        "past_days": 2,
        "forecast_days": 1,
        "timezone": "UTC",
    }
    response = requests.get(API_URL, params=params, timeout=(5, 30))
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict) or "hourly" not in payload:
        raise ValueError(f"Unexpected Open-Meteo response for {city}")
    return payload


def parse_rows(city: str, payload: dict) -> list[dict]:
    """Convert an Open-Meteo hourly response into one row per timestamp."""
    try:
        hourly = payload["hourly"]
        columns = [hourly["time"], *(hourly[field] for field in HOURLY_FIELDS)]
    except (KeyError, TypeError) as exc:
        raise ValueError("Open-Meteo response is missing hourly fields") from exc

    lengths = {len(column) for column in columns}
    if len(lengths) != 1:
        raise ValueError("Open-Meteo hourly arrays have inconsistent lengths")

    return [
        {
            "city": city,
            "observed_at": observed_at,
            "temperature_c": temperature,
            "humidity_pct": humidity,
            "wind_kmh": wind,
        }
        for observed_at, temperature, humidity, wind in zip(*columns, strict=True)
    ]


def extract_all() -> list[dict]:
    """Fetch all configured cities. Fail the run if any city cannot be extracted."""
    rows: list[dict] = []
    for city, (latitude, longitude) in CITIES.items():
        rows.extend(parse_rows(city, fetch_city(city, latitude, longitude)))
    return rows
