# apps/dashboard/exchange.py

import logging

import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_KEY = "cambio_usd_brl"
CACHE_TIMEOUT = 60 * 60  # 1 hora


def get_usd_brl_rate() -> float:
    taxa = cache.get(CACHE_KEY)
    if taxa is not None:
        return taxa

    try:
        response = requests.get("https://open.er-api.com/v6/latest/USD", timeout=5)
        response.raise_for_status()
        taxa = response.json()["rates"]["BRL"]
        cache.set(CACHE_KEY, taxa, CACHE_TIMEOUT)
        cache.set(f"{CACHE_KEY}:fallback", taxa, None)  # sem expiração — só rede de segurança
        return taxa
    except Exception as e:
        logger.error("Erro ao buscar cotação USD/BRL: %s", e)
        fallback = cache.get(f"{CACHE_KEY}:fallback")
        return fallback if fallback is not None else 5.50  # último recurso, se nunca funcionou nem uma vez