import json
import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

path_name = Path(__file__).resolve().parent.parent / "data" / "weather_data.json"
columns_names_to_drop = ["weather", "weather_icon", "sys.type"]
columns_names_to_rename = {
        "base": "base",
        "visibility": "visibility",
        "dt": "datetime",
        "timezone": "timezone",
        "id": "city_id",
        "name": "city_name",
        "cod": "code",
        "coord.lon": "longitude",
        "coord.lat": "latitude",
        "main.temp": "temperature",
        "main.feels_like": "feels_like",
        "main.temp_min": "temp_min",
        "main.temp_max": "temp_max",
        "main.pressure": "pressure",
        "main.humidity": "humidity",
        "main.sea_level": "sea_level",
        "main.grnd_level": "grnd_level",
        "wind.speed": "wind_speed",
        "wind.deg": "wind_deg",
        "wind.gust": "wind_gust",
        "clouds.all": "clouds",
        "sys.type": "sys_type",
        "sys.id": "sys_id",
        "sys.country": "country",
        "sys.sunrise": "sunrise",
        "sys.sunset": "sunset"
    }
columns_to_normalize_datetime = ["datetime", "sunrise", "sunset"]


def create_dataframe(path_name: Path) -> pd.DataFrame:
    logger.info("Iniciando a criação do DataFrame")

    try:
        path = path_name

        if not path.exists():
            raise FileNotFoundError(
                f"Arquivo não encontrado: {path}"
            )

        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        df = pd.json_normalize(data)
        logger.info(
            "DataFrame criado com %s linhas.", len(df)
        )

        return df

    except (OSError, TypeError, ValueError):
        logger.exception(
            "Erro ao carregar ou normalizar os dados meteorológicos."
        )
        raise


def normalize_weather_columns(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Iniciando a Nomalização do DataFrame")

    try:
        df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

        df_weather = df_weather.rename(columns={
            "id": "weather_id",
            "main": "weather_main",
            "description": "weather_description",
            "icon": "weather_icon"
        })

        df = pd.concat([df, df_weather], axis=1)
        logger.info("Coluna 'weather' normalizada com sucesso")

        return df

    except (OSError, TypeError, ValueError, IndexError, KeyError):
        logger.exception(
            "Erro inesperado ao tentar normalizar do DataFrame."
        )
        raise


def drop_columns(df: pd.DataFrame, columns_names: list[str]) -> pd.DataFrame:
    logger.info("Iniciando a exclusão de colunas do DataFrame")

    try:
        df = df.drop(columns=columns_names)
        logger.info("Colunas excluidas com sucesso")

        return df

    except Exception:
        logger.exception("Erro ao excliur as colunas")
        raise


def rename_columns(df: pd.DataFrame, columns_name: dict[str, str]) -> pd.DataFrame:
    logger.info("Iniciando o rename das colunas")

    try:
        df = df.rename(columns=columns_name)
        logger.info("Colunas renomeadas")

        return df

    except Exception:
        logger.exception("Erro ao tentar renomear as coluanas")
        raise


def normalize_datetime_columns(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:
    logger.info("iniciando normalização das datas")

    try:
        for name in columns_name:
            df[name] = pd.to_datetime(df[name], unit='s', utc=True).dt.tz_convert("America/Sao_Paulo")

        logger.info("Data convertida com sucesso")

        return df

    except Exception:
        logger.exception("Erro ao normalizar as datas")
        raise


def data_transformations() -> pd.DataFrame:
    logger.info("Iniciando processo de transformação do DataFrame")

    df = create_dataframe(path_name)
    df = normalize_weather_columns(df)
    df = drop_columns(df, columns_names_to_drop)
    df = rename_columns(df, columns_names_to_rename)
    df = normalize_datetime_columns(df, columns_to_normalize_datetime)

    logger.info("Tranformações finalizadas")

    return df
