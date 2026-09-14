from pathlib import Path
from datetime import date, timedelta
import os
import psycopg2
import requests
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential


def load_cities(config_path: str | Path) -> list[dict]:
    with open(config_path, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file)

    return config["cities"]

def get_connection():
    return psycopg2.connect(
        host=os.environ["WAREHOUSE_HOST"],
        port=os.environ["WAREHOUSE_PORT"],
        dbname=os.environ["WAREHOUSE_DB"],
        user=os.environ["WAREHOUSE_USER"],
        password=os.environ["WAREHOUSE_PASSWORD"],
    )

def extract_weather(config_path: str | Path, date: str) -> list[dict]:
    cities = load_cities(config_path)

    rows = []

    for city in cities:
        response = fetch_weather(city, date)
        row = normalize_weather(city, response)
        rows.append(row)

    return rows
   
def load_weather(row: dict) -> None:
    conn = get_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO raw.weather_daily (
                    city,
                    latitude,
                    longitude,
                    date,
                    weather_code,
                    temperature_2m_max,
                    temperature_2m_min,
                    precipitation_sum,
                    wind_speed_10m_max
                )
                VALUES (
                    %(city)s,
                    %(latitude)s,
                    %(longitude)s,
                    %(date)s,
                    %(weather_code)s,
                    %(temperature_2m_max)s,
                    %(temperature_2m_min)s,
                    %(precipitation_sum)s,
                    %(wind_speed_10m_max)s
                )
                ON CONFLICT (city, date)
                DO UPDATE SET
                    latitude = EXCLUDED.latitude,
                    longitude = EXCLUDED.longitude,
                    weather_code = EXCLUDED.weather_code,
                    temperature_2m_max = EXCLUDED.temperature_2m_max,
                    temperature_2m_min = EXCLUDED.temperature_2m_min,
                    precipitation_sum = EXCLUDED.precipitation_sum,
                    wind_speed_10m_max = EXCLUDED.wind_speed_10m_max,
                    loaded_at = CURRENT_TIMESTAMP
                """,
                row,
            )

        conn.commit()

    finally:
        conn.close()  
        
def load_weather_rows(rows: list[dict]) -> None:
    for row in rows:
        load_weather(row)          

def run_ingestion(config_path: str | Path, date: str) -> None:
    cities = load_cities(config_path)

    for city in cities:
        response = fetch_weather(city, date)
        row = normalize_weather(city, response)
        load_weather(row)
        
@retry(
    stop=stop_after_attempt(3),                                 #"I added a 10-second HTTP timeout and up to three retry attempts with exponential backoff, so transient network failures don't immediately fail the pipeline."
    wait=wait_exponential(multiplier=1, min=2, max=10),
)
def fetch_weather(city: dict, date: str) -> dict:
    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "start_date": date,
        "end_date": date,
        "daily": (
            "weather_code,"
            "temperature_2m_max,"
            "temperature_2m_min,"
            "precipitation_sum,"
            "wind_speed_10m_max"
        ),
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()
def normalize_weather(city: dict, response: dict) -> dict:
    daily = response["daily"]

    return {
        "city": city["name"],
        "latitude": city["latitude"],
        "longitude": city["longitude"],
        "date": daily["time"][0],
        "weather_code": daily["weather_code"][0],
        "temperature_2m_max": daily["temperature_2m_max"][0],
        "temperature_2m_min": daily["temperature_2m_min"][0],
        "precipitation_sum": daily["precipitation_sum"][0],
        "wind_speed_10m_max": daily["wind_speed_10m_max"][0],
    }
def run_ingestion_range(
    config_path: str | Path,
    start_date: str,
    end_date: str,
) -> None:
    current_date = date.fromisoformat(start_date)
    final_date = date.fromisoformat(end_date)

    while current_date <= final_date:
        rows = extract_weather(
            config_path,
            current_date.isoformat(),
        )
        load_weather_rows(rows)
        current_date += timedelta(days=1)