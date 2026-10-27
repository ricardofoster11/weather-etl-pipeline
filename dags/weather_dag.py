import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

from airflow.sdk import dag, task
from dotenv import load_dotenv

sys.path.insert(0, "/opt/airflow")
sys.path.insert(0, "/opt/airflow/src")

from config.logger import setup_logging
from extract_data import extract_weather_data
from transform_data import data_transformations
from config.connection import create_database_engine
from load_data import load_weather_data

setup_logging()
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_url = os.getenv("API_URL")
api_key = os.getenv("API_KEY")
api_city = os.getenv("API_CITY")


@dag(
    dag_id="weather_pipeline",
    description="Pipeline ETL - Clima SP",
    default_args={
        "owner": "airflow",
        "depends_on_past": False,
        "retries": 2,
        "retry_delay": timedelta(minutes=2)
    },
    schedule=None,
    start_date=datetime(2026, 10, 26),
    catchup=False,
    tags=["etl", "weather"]
)
def weather_pipeline():

    @task
    def extract():
        extract_weather_data(
            api_url=api_url,
            api_key=api_key,
            api_city=api_city
        )

    @task
    def transform():
        df = data_transformations()
        df.to_parquet("/opt/airflow/data/temp_data.parquet", index=False)

    @task
    def load():
        import pandas as pd
        engine = create_database_engine()

        try:
            df = pd.read_parquet("/opt/airflow/data/temp_data.parquet")
            load_weather_data("weather_sp", df, engine)
        finally:
            engine.dispose()

    extract() >> transform() >> load()


weather_pipeline()
