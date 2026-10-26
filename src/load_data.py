import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

logger = logging.getLogger(__name__)


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
