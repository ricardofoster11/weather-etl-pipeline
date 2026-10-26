import json
import logging
from pathlib import Path

import requests

logger = logging.getLogger(__name__)


def extract_weather_data(
        api_url: str,
        api_key: str,
        api_city: str
) -> dict | list:
    logger.info("Iniciando extração dos dados meteorológicos.")

    params = {
        "q": api_city,
        "units": "metric",
        "appid": api_key
    }

    try:
        response = requests.get(api_url, params=params, timeout=30)
        response.raise_for_status()

        logger.info(
            "Requisição HTTP realizada. Status: %s",
            response.status_code
        )

        data = response.json()

        if not data:
            raise ValueError("Nenhum dado meteorológico encontrado.")

        output_path = Path(__file__).resolve().parent.parent / "data" / "weather_data.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

        logger.info(
            "Dados meteorológicos salvos em: %s",
            output_path
        )

        logger.info("Extração finalizada com sucesso.")

        return data

    except requests.exceptions.RequestException:
        logger.exception("Erro na requisição à API meteorológica.")
        raise

    except (OSError, TypeError, ValueError):
        logger.exception(
            "Erro ao processar ou salvar os dados meteorológicos."
        )
        raise
