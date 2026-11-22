from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from radio_comun.configuracion import obtener_origenes_cors, obtener_url_redis
from radio_comun.redis_cliente import crear_cliente_redis
from radio_comun.salud import crear_router_salud

NOMBRE_SERVICIO = "room-queue-service"


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.redis = crear_cliente_redis(obtener_url_redis())
    try:
        yield
    finally:
        await app.state.redis.aclose()


app = FastAPI(
    title="Room Queue Service",
    description="Gestión de salas, identidades temporales, cola de reproducción y votos.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=obtener_origenes_cors(),
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(crear_router_salud(NOMBRE_SERVICIO))
