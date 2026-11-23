from typing import Annotated

from fastapi import Depends, Path, Request
from radio_comun.seguridad import ClaimsActuales, ClaimsToken, no_autorizado
from redis.asyncio import Redis

from app.schemas.sala import SalaPublica
from app.services import salas


def obtener_redis(request: Request) -> Redis:
    return request.app.state.redis


RedisDep = Annotated[Redis, Depends(obtener_redis)]


async def obtener_sala_solicitada(
    codigo: Annotated[str, Path(pattern=r"^[A-Za-z0-9]{6}$", description="Código de 6 caracteres de la sala")],
    redis: RedisDep,
) -> SalaPublica:
    return await salas.obtener_sala(redis, codigo.upper())


SalaSolicitada = Annotated[SalaPublica, Depends(obtener_sala_solicitada)]


async def obtener_participante_de_sala(sala: SalaSolicitada, claims: ClaimsActuales) -> ClaimsToken:
    if claims.id_sala != sala.id_sala:
        raise no_autorizado("Tu sesión no corresponde a esta sala")
    return claims


ParticipanteAutenticado = Annotated[ClaimsToken, Depends(obtener_participante_de_sala)]
