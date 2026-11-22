from decouple import Csv, config


def obtener_url_redis() -> str:
    return config("REDIS_URL", default="redis://localhost:6379/0")


def obtener_origenes_cors() -> list[str]:
    return config("CORS_ORIGINS", default="http://localhost:8100", cast=Csv())
