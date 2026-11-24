from contextlib import asynccontextmanager
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from radio_comun.configuracion import obtener_origenes_cors, obtener_url_redis
from radio_comun.errores import registrar_manejadores_errores
from radio_comun.redis_cliente import crear_cliente_redis
from radio_comun.salud import crear_router_salud
from radio_comun.seguridad import obtener_configuracion_jwt
from app.configuracion import obtener_configuracion_catalogo
from app.routers import catalogo

NOMBRE_SERVICIO = "music-catalog-service"

@asynccontextmanager
async def lifespan(app: FastAPI):
    obtener_configuracion_jwt()
    configuracion = obtener_configuracion_catalogo()
    app.state.redis = crear_cliente_redis(obtener_url_redis())
    app.state.http = httpx.AsyncClient(
        timeout=httpx.Timeout(configuracion.tiempo_espera_segundos, connect=3.0),
        headers={"User-Agent": "radio-colaborativa/0.1"},
        follow_redirects=True,
    )
    try:
        yield
    finally:
        await app.state.http.aclose()
        await app.state.redis.aclose()


app = FastAPI(
    title="Music Catalog Service",
    description="Búsqueda y normalización de canciones desde Deezer y Jamendo.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=obtener_origenes_cors(),
    allow_methods=["GET"],
    allow_headers=["Authorization", "Content-Type"],
)

registrar_manejadores_errores(app)
app.include_router(crear_router_salud(NOMBRE_SERVICIO))
app.include_router(catalogo.router)
