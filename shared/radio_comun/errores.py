import logging
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)

class ErrorDominio(Exception):
    codigo_http = status.HTTP_400_BAD_REQUEST
    def __init__(self, detalle: str) -> None:
        super().__init__(detalle)
        self.detalle = detalle

class RecursoNoEncontrado(ErrorDominio):
    codigo_http = status.HTTP_404_NOT_FOUND

class ConflictoNegocio(ErrorDominio):
    codigo_http = status.HTTP_409_CONFLICT

class ServicioNoDisponible(ErrorDominio):
    codigo_http = status.HTTP_503_SERVICE_UNAVAILABLE

def _mensaje_validacion(error: dict) -> str:
    campo = error["loc"][-1] if error.get("loc") else "dato"
    match error.get("type"):
        case "missing":
            return f"Falta el campo «{campo}»"
        case "value_error":
            return str(error["ctx"]["error"])
        case _:
            return f"El campo «{campo}» no es válido"

def registrar_manejadores_errores(app: FastAPI) -> None:
    @app.exception_handler(ErrorDominio)
    async def manejar_error_dominio(_: Request, error: ErrorDominio) -> JSONResponse:
        return JSONResponse(status_code=error.codigo_http, content={"detail": error.detalle})

    @app.exception_handler(RequestValidationError)
    async def manejar_error_validacion(_: Request, error: RequestValidationError) -> JSONResponse:
        errores = error.errors()
        detalle = _mensaje_validacion(errores[0]) if errores else "Datos inválidos"
        return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, content={"detail": detalle})

    @app.exception_handler(RedisError)
    async def manejar_error_redis(_: Request, error: RedisError) -> JSONResponse:
        logger.error("Redis no disponible: %s", type(error).__name__)
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "El servicio no está disponible en este momento. Intenta de nuevo en unos segundos."},
        )