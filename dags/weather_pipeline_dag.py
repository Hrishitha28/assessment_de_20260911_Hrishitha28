from datetime import datetime, timedelta

from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from airflow.operators.python import get_current_context
from ingestion.weather_pipeline import extract_weather, load_weather_rows


@dag(
    dag_id="weather_pipeline",
    schedule="@daily",
    start_date=datetime(2026, 9, 1),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=2),
    },
    tags=["weather", "assessment"],
)
def weather_pipeline():

    @task(
        task_id="extract_weather",
        execution_timeout=timedelta(minutes=10),
    )
    def extract_task():
        context = get_current_context()
        logical_date = context["logical_date"]

        return extract_weather(
            "/opt/airflow/config/cities.yml",
            logical_date.strftime("%Y-%m-%d"),
        )

    @task(
        task_id="load_weather",
        execution_timeout=timedelta(minutes=10),
    )
    def load_task(rows):
        load_weather_rows(rows)

    dbt_run = BashOperator(
        task_id="dbt_run",
        bash_command="cd /opt/airflow/dbt && dbt run",
        execution_timeout=timedelta(minutes=10),
    )

    dbt_test = BashOperator(
        task_id="dbt_test",
        bash_command="cd /opt/airflow/dbt && dbt test",
        execution_timeout=timedelta(minutes=10),
    )

    rows = extract_task()
    load = load_task(rows)

    rows >> load >> dbt_run >> dbt_test


weather_pipeline()