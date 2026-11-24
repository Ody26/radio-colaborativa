import math
import time
from dataclasses import dataclass
from uuid import uuid4

from redis.asyncio import Redis
from radio_comun.errores import LimiteFrecuenciaExcedido

# Ventana deslizante atómica: devuelve 0 si la acción se permite o los milisegundos que faltan para reintentar.
_SCRIPT_VENTANA_DESLIZANTE = """
local clave = KEYS[1]
local ahora = tonumber(ARGV[1])
local ventana = tonumber(ARGV[2])
local maximo = tonumber(ARGV[3])
redis.call('ZREMRANGEBYSCORE', clave, 0, ahora - ventana)
if redis.call('ZCARD', clave) >= maximo then
  local primero = redis.call('ZRANGE', clave, 0, 0, 'WITHSCORES')
  return tonumber(primero[2]) + ventana - ahora
end
redis.call('ZADD', clave, ahora, ARGV[4])
redis.call('PEXPIRE', clave, ventana)
return 0
"""

@dataclass(frozen=True)
class LimiteFrecuencia:
    accion: str
    maximo: int
    ventana_segundos: int

async def verificar_limite(redis: Redis, limite: LimiteFrecuencia, id_sala: str, id_participante: str) -> None:
    clave = f"limite:{limite.accion}:{id_sala}:{id_participante}"
    espera_ms = await redis.eval(
        _SCRIPT_VENTANA_DESLIZANTE,
        1,
        clave,
        int(time.time() * 1000),
        limite.ventana_segundos * 1000,
        limite.maximo,
        uuid4().hex,
    )
    if int(espera_ms) > 0:
        raise LimiteFrecuenciaExcedido(max(1, math.ceil(int(espera_ms) / 1000)))
