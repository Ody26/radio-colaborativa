import logging
from radio_comun.errores import RecursoNoEncontrado, ServicioNoDisponible
from radio_comun.modelos import Pista, Proveedor
from redis.asyncio import Redis
from app.proveedores.base import ErrorProveedor, ProveedorMusica
from app.schemas.busqueda import ResultadoBusqueda

logger = logging.getLogger(__name__)

def normalizar_consulta(consulta: str) -> str:
    return " ".join(consulta.casefold().split())

class ServicioCatalogo:
    def __init__(self, redis: Redis, proveedores: list[ProveedorMusica], ttl_cache_segundos: int) -> None:
        self._redis = redis
        self._proveedores = proveedores
        self._ttl = ttl_cache_segundos

    async def buscar(self, consulta: str, limite: int) -> ResultadoBusqueda:
        consulta = normalizar_consulta(consulta)
        resultado_vacio: ResultadoBusqueda | None = None

        for proveedor in self._proveedores:
            clave = f"catalogo:busqueda:{proveedor.nombre}:{limite}:{consulta}"
            guardado = await self._redis.get(clave)
            if guardado is not None:
                resultado = ResultadoBusqueda.model_validate_json(guardado)
            else:
                try:
                    pistas = await proveedor.buscar(consulta, limite)
                except ErrorProveedor as error:
                    logger.warning("Proveedor %s no disponible: %s", proveedor.nombre, error)
                    continue
                resultado = ResultadoBusqueda(proveedor_usado=proveedor.nombre, resultados=pistas)
                await self._redis.set(clave, resultado.model_dump_json(), ex=self._ttl)

            if resultado.resultados:
                return resultado
            resultado_vacio = resultado_vacio or resultado

        if resultado_vacio is not None:
            return resultado_vacio
        raise ServicioNoDisponible("El catálogo de música no responde en este momento. Intenta de nuevo en unos segundos.")

    async def obtener_pista(self, nombre_proveedor: Proveedor, id_pista: str) -> Pista:
        proveedor = next((p for p in self._proveedores if p.nombre == nombre_proveedor), None)
        if proveedor is None:
            raise ServicioNoDisponible(f"El proveedor {nombre_proveedor} no está habilitado")

        clave = f"catalogo:pista:{nombre_proveedor}:{id_pista}"
        guardado = await self._redis.get(clave)
        if guardado is not None:
            return Pista.model_validate_json(guardado)

        try:
            pista = await proveedor.obtener_pista(id_pista)
        except ErrorProveedor as error:
            logger.warning("Proveedor %s no disponible: %s", nombre_proveedor, error)
            raise ServicioNoDisponible("El catálogo de música no responde en este momento.") from error
        if pista is None:
            raise RecursoNoEncontrado("La canción no existe o no se puede reproducir")

        await self._redis.set(clave, pista.model_dump_json(), ex=self._ttl)
        return pista
