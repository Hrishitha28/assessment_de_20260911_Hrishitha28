select
    city,
    date,
    latitude,
    longitude,
    weather_code,
    temperature_2m_max,
    temperature_2m_min,
    (temperature_2m_max + temperature_2m_min) / 2.0 as temperature_2m_avg,
    precipitation_sum,
    wind_speed_10m_max
from {{ ref('stg_weather') }}