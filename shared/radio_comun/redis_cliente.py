from redis.asyncio import Redis


def crear_cliente_redis(url: str) -> Redis:
    return Redis.from_url(
        url,
        decode_responses=True,
        socket_connect_timeout=3,
        health_check_interval=30,
    )
