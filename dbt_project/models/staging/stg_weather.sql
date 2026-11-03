select
    city,
    cast(observed_at as timestamp) as observed_at,
    temperature_c,
    humidity_pct,
    wind_kmh
from raw.weather
where temperature_c is not null
