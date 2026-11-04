-- Run after python src/pipeline.py and dbt build.
-- Connect to data/warehouse.duckdb with DuckDB.

-- 1. Daily city-level metrics.
SELECT obs_date, city, avg_temp_c, min_temp_c, max_temp_c,
       avg_humidity_pct, max_wind_kmh
FROM main.daily_weather
ORDER BY obs_date DESC, city;

-- 2. Latest available daily record for each city.
SELECT * EXCLUDE (row_num)
FROM (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY city ORDER BY obs_date DESC
    ) AS row_num
    FROM main.daily_weather
)
WHERE row_num = 1
ORDER BY city;

-- 3. Compare average temperatures across cities.
SELECT city,
       ROUND(AVG(avg_temp_c), 1) AS period_avg_temp_c,
       ROUND(MAX(max_temp_c), 1) AS period_high_temp_c
FROM main.daily_weather
GROUP BY city
ORDER BY period_avg_temp_c DESC;

-- 4. Find the windiest city-days.
SELECT city, obs_date, max_wind_kmh
FROM main.daily_weather
ORDER BY max_wind_kmh DESC
LIMIT 10;

-- 5. Duplicate business keys in raw layer (expected: zero rows).
SELECT city, observed_at, COUNT(*) AS record_count
FROM raw.weather
GROUP BY city, observed_at
HAVING COUNT(*) > 1;

-- 6. Raw-layer freshness and volume.
SELECT MAX(CAST(observed_at AS TIMESTAMP)) AS latest_observation_utc,
       MAX(loaded_at) AS latest_load_utc,
       COUNT(*) AS raw_record_count
FROM raw.weather;

-- 7. Compare raw and mart row counts at their respective grains.
SELECT 'raw hourly observations' AS dataset, COUNT(*) AS row_count
FROM raw.weather
UNION ALL
SELECT 'daily city aggregates', COUNT(*)
FROM main.daily_weather;
