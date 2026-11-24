from typing import Any
import httpx
from radio_comun.modelos import Pista
from app.proveedores.base import ErrorProveedor

URL_API = "https://api.deezer.com"
DURACION_PREVIEW_SEGUNDOS = 30
CODIGO_SIN_DATOS = 800

class ErrorProveedorSinDatos(ErrorProveedor):
    pass

class ProveedorDeezer:
    nombre = "deezer"

    def __init__(self, cliente: httpx.AsyncClient) -> None:
        self._cliente = cliente
    async def buscar(self, consulta: str, limite: int) -> list[Pista]:
        datos = await self._consultar("/search", {"q": consulta, "limit": limite})
        pistas = (self._convertir(elemento) for elemento in datos.get("data", []))
        return [pista for pista in pistas if pista is not None]

    async def obtener_pista(self, id_pista: str) -> Pista | None:
        try:
            datos = await self._consultar(f"/track/{id_pista}", {})
        except ErrorProveedorSinDatos:
            return None
        return self._convertir(datos)

    async def _consultar(self, ruta: str, parametros: dict[str, Any]) -> dict[str, Any]:
        try:
            respuesta = await self._cliente.get(f"{URL_API}{ruta}", params=parametros)
            respuesta.raise_for_status()
            datos = respuesta.json()
        except (httpx.HTTPError, ValueError) as error:
            raise ErrorProveedor(f"Deezer no respondió correctamente: {type(error).__name__}") from error

        if "error" in datos:
            if datos["error"].get("code") == CODIGO_SIN_DATOS:
                raise ErrorProveedorSinDatos()
            raise ErrorProveedor(f"Deezer devolvió un error: {datos['error'].get('type')}")
        return datos

    @staticmethod
    def _convertir(elemento: dict[str, Any]) -> Pista | None:
        if not elemento.get("preview") or elemento.get("readable") is False:
            return None
        album = elemento.get("album") or {}
        return Pista(
            id_pista=str(elemento["id"]),
            proveedor="deezer",
            titulo=elemento["title"],
            artista=(elemento.get("artist") or {}).get("name", ""),
            album=album.get("title", ""),
            portada_url=album.get("cover_medium") or "",
            duracion=min(int(elemento.get("duration") or DURACION_PREVIEW_SEGUNDOS), DURACION_PREVIEW_SEGUNDOS),
            audio_url=elemento["preview"],
        )
