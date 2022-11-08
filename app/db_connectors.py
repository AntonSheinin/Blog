# pylint: disable=missing-module-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=maybe-no-member


from redis_om import get_redis_connection
import aioredis


REDIS_HOST = 'redis-data'
REDIS_URL = 'redis://redis-cache'
REDIS_DATA_PORT = 6379
REDIS_CACHE_PORT = 6378

redis_data = get_redis_connection(host=REDIS_HOST, port=REDIS_DATA_PORT, decode_responses=True)
redis_cache = aioredis.from_url(
    url=REDIS_URL,
    port=REDIS_CACHE_PORT,
    encoding="utf8",
    decode_responses=True,
    health_check_interval=10,
    socket_connect_timeout=5,
    retry_on_timeout=True,
    socket_keepalive=True
)
