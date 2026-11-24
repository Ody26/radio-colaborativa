from typing import Annotated
import httpx
from fastapi import Depends, Request
from radio_comun.limite_frecuencia import verificar_limite
from radio_comun.seguridad import ClaimsActuales, ClaimsToken
from redis.asyncio import Redis
from app.configuracion import LIMITE_BUSQUEDAS, obtener_configuracion_catalogo
from app.proveedores.base import ProveedorMusica
from app.proveedores.deezer import ProveedorDeezer
from app.proveedores.jamendo import ProveedorJamendo
from app.services.catalogo import ServicioCatalogo

def obtener_redis(request: Request) -> Redis:
    return request.app.state.redis

def obtener_cliente_http(request: Request) -> httpx.AsyncClient:
    return request.app.state.http

RedisDep = Annotated[Redis, Depends(obtener_redis)]
ClienteHttpDep = Annotated[httpx.AsyncClient, Depends(obtener_cliente_http)]

def obtener_servicio_catalogo(redis: RedisDep, cliente: ClienteHttpDep) -> ServicioCatalogo:
    configuracion = obtener_configuracion_catalogo()
    proveedores: list[ProveedorMusica] = [ProveedorDeezer(cliente)]
    if configuracion.jamendo_client_id:
        proveedores.append(ProveedorJamendo(cliente, configuracion.jamendo_client_id))
    return ServicioCatalogo(redis, proveedores, configuracion.ttl_cache_segundos)

ServicioCatalogoDep = Annotated[ServicioCatalogo, Depends(obtener_servicio_catalogo)]

async def controlar_busquedas(claims: ClaimsActuales, redis: RedisDep) -> ClaimsToken:
    await verificar_limite(redis, LIMITE_BUSQUEDAS, claims.id_sala, claims.id_participante)
    return claims
