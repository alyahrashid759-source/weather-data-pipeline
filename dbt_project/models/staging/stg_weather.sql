select
    city,
    cast(observed_at as timestamp) as observed_at,
    cast(observed_at as date) as obs_date,
    temperature_c,
    humidity_pct,
    wind_kmh,
    loaded_at
from {{ source('raw', 'weather') }}
