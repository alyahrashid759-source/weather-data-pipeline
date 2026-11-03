select
    city,
    cast(observed_at as date) as obs_date,
    round(avg(temperature_c), 1) as avg_temp_c,
    max(temperature_c) as max_temp_c,
    min(temperature_c) as min_temp_c,
    round(avg(humidity_pct), 1) as avg_humidity_pct,
    round(max(wind_kmh), 1) as max_wind_kmh
from {{ ref('stg_weather') }}
group by 1, 2
