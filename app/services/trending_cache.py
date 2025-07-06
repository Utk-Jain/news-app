import json
import logging

import app.context as context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[trending_cache]")

TRENDING_TTL_SECONDS = 300  # 5 minutes


def get_geo_key(lat: float, lon: float, precision: int = 1) -> str:
    rounded_lat = round(lat, precision)
    rounded_lon = round(lon, precision)
    return f"trending:{rounded_lat}:{rounded_lon}"


def get_cached_trending(lat: float, lon: float) -> list | None:
    key = get_geo_key(lat, lon)
    cached = context.redis_client.get(key)
    if cached:
        return json.loads(cached)
    return None


def set_cached_trending(lat: float, lon: float, articles: list):
    key = get_geo_key(lat, lon)
    context.redis_client.setex(key, TRENDING_TTL_SECONDS, json.dumps(articles))
    logger.info(f"Cached trending articles for {key} with TTL {TRENDING_TTL_SECONDS} seconds")