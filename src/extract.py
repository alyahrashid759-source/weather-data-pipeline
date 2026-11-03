"""Extract hourly weather data from the free Open-Meteo API (no key needed)."""
import requests

API_URL = "https://api.open-meteo.com/v1/forecast"
CITIES = {
    "London": (51.51, -0.13),
    "New York": (40.71, -74.01),
    "Mumbai": (19.08, 72.88),
    "Tokyo": (35.68, 139.69),
}


def fetch_city(city: str, lat: float, lon: float) -> dict:
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,wind_speed_10m",
        "past_days": 2,
        "forecast_days": 1,
    }
    resp = requests.get(API_URL, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_rows(city: str, payload: dict) -> list[dict]:
    h = payload["hourly"]
    return [
        {
            "city": city,
            "observed_at": t,
            "temperature_c": temp,
            "humidity_pct": hum,
            "wind_kmh": wind,
        }
        for t, temp, hum, wind in zip(
            h["time"], h["temperature_2m"], h["relative_humidity_2m"], h["wind_speed_10m"]
        )
    ]


def extract_all() -> list[dict]:
    rows: list[dict] = []
    for city, (lat, lon) in CITIES.items():
        rows.extend(parse_rows(city, fetch_city(city, lat, lon)))
    return rows
