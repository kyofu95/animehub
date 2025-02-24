from redis.asyncio import ConnectionPool, Redis

from app.core.config import redis_settings

pool = ConnectionPool.from_url(f"redis://{redis_settings.host}:{redis_settings.port}/0")


def get_redis() -> Redis:
    """
    Create and return a Redis client instance.

    This function returns a Redis client configured to use a shared connection pool,
    which is established using the Redis settings defined in the application's configuration.

    Returns:
        Redis: A Redis client instance with connection pooling and response decoding enabled.
    """

    redis = Redis(connection_pool=pool, decode_responses=True)
    return redis
