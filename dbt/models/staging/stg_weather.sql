select
    city,
    latitude,
    longitude,
    date,
    weather_code,
    temperature_2m_max,
    temperature_2m_min,
    precipitation_sum,
    wind_speed_10m_max,
    loaded_at
from {{ source('raw', 'weather_daily') }}