from fastapi import APIRouter, Request, Response, status
from redis.exceptions import RedisError


def crear_router_salud(nombre_servicio: str) -> APIRouter:
    router = APIRouter(tags=["Salud"])

    @router.get("/salud")
    async def consultar_salud(request: Request, response: Response) -> dict[str, str]:
        try:
            await request.app.state.redis.ping()
            estado_redis = "ok"
        except (RedisError, OSError):
            estado_redis = "no disponible"
            response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"servicio": nombre_servicio, "redis": estado_redis}

    return router
