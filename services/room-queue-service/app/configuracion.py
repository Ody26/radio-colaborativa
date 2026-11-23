from dataclasses import dataclass
from datetime import timedelta
from functools import lru_cache
from decouple import config

CAPACIDAD_MAXIMA_SALA = 50
@dataclass(frozen=True)
class ConfiguracionSalas:
    ttl_inactividad: timedelta
    duracion_maxima: timedelta

@lru_cache
def obtener_configuracion_salas() -> ConfiguracionSalas:
    horas_inactividad = config("TTL_SALA_INACTIVA_HORAS", default=2, cast=int)
    horas_maximas = config("TTL_SALA_MAXIMA_HORAS", default=24, cast=int)
    if not 0 < horas_inactividad <= horas_maximas:
        raise ValueError("TTL_SALA_INACTIVA_HORAS debe ser positivo y no mayor que TTL_SALA_MAXIMA_HORAS")
    return ConfiguracionSalas(timedelta(hours=horas_inactividad), timedelta(hours=horas_maximas))
