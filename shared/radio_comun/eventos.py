import json
from typing import Any
from redis.asyncio import Redis
from radio_comun import claves

async def publicar_evento(redis: Redis, id_sala: str, tipo: str, datos: dict[str, Any]) -> None:
    mensaje = json.dumps({"tipo": tipo, "datos": datos}, ensure_ascii=False)
    await redis.publish(claves.canal_eventos(id_sala), mensaje)