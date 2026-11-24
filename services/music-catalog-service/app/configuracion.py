from dataclasses import dataclass
from functools import lru_cache
from decouple import config
from radio_comun.limite_frecuencia import LimiteFrecuencia

LIMITE_BUSQUEDAS = LimiteFrecuencia(accion="busqueda", maximo=20, ventana_segundos=60)

@dataclass(frozen=True)
class ConfiguracionCatalogo:
    jamendo_client_id: str
    ttl_cache_segundos: int
    tiempo_espera_segundos: float

@lru_cache
def obtener_configuracion_catalogo() -> ConfiguracionCatalogo:
    ttl = config("TTL_CACHE_CATALOGO_SEGUNDOS", default=600, cast=int)
    espera = config("TIEMPO_ESPERA_PROVEEDORES_SEGUNDOS", default=5.0, cast=float)
    if ttl <= 0 or espera <= 0:
        raise ValueError("TTL_CACHE_CATALOGO_SEGUNDOS y TIEMPO_ESPERA_PROVEEDORES_SEGUNDOS deben ser positivos")
    return ConfiguracionCatalogo(config("JAMENDO_CLIENT_ID", default=""), ttl, espera)