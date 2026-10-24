import logging
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine

from config.logger import setup_logging

setup_logging()
logger = logging.getLogger(__name__)

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)


def create_database_engine() -> Engine:
    logger.info("Iniciando conexão com PostgreSQL")

    try:
        host = os.getenv("POSTGRES_HOST")
        port = os.getenv("POSTGRES_PORT")
        database = os.getenv("POSTGRES_DB")
        user = os.getenv("POSTGRES_USER")
        password = os.getenv("POSTGRES_PASSWORD")

        required_variables = {
            "POSTGRES_HOST": host,
            "POSTGRES_PORT": port,
            "POSTGRES_DB": database,
            "POSTGRES_USER": user,
            "POSTGRES_PASSWORD": password
        }

        for variable_name, variable_value in required_variables.items():
            if not variable_value:
                raise RuntimeError(
                    f"A variável {variable_name} não foi configurada"
                )

        database_url = URL.create(
            drivername="postgresql+psycopg2",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=database
        )

        engine = create_engine(database_url)

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Conexão com PostgreSQL realizada com sucesso")

        return engine

    except Exception:
        logger.exception("Problema ao conectar com o DataBase")
        raise


def load_weather_data(
    table_name: str,
    df: pd.DataFrame,
    engine: Engine
) -> None:

    logger.info("Iniciando carregamento dos dados no PostgreSQL")

    try:
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="append",
            index=False
        )

        logger.info("Dados carregados com sucesso")

        with engine.connect() as connection:
            total_records = connection.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar_one()

        logger.info(
            "Total de registros na tabela: %s",
            total_records
        )
    except Exception:
        logger.exception("Erro ao carregar os dados no PostgreSQL")
        raise
