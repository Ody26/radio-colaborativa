from typing import Any
import httpx
from radio_comun.modelos import Pista
from app.proveedores.base import ErrorProveedor

URL_API = "https://api.jamendo.com/v3.0"

class ProveedorJamendo:
    nombre = "jamendo"
    def __init__(self, cliente: httpx.AsyncClient, client_id: str) -> None:
        self._cliente = cliente
        self._client_id = client_id

    async def buscar(self, consulta: str, limite: int) -> list[Pista]:
        resultados = await self._consultar({"search": consulta, "limit": limite})
        return [self._convertir(resultado) for resultado in resultados if resultado.get("audio")]

    async def obtener_pista(self, id_pista: str) -> Pista | None:
        resultados = await self._consultar({"id": id_pista, "limit": 1})
        return self._convertir(resultados[0]) if resultados and resultados[0].get("audio") else None

    async def _consultar(self, parametros: dict[str, Any]) -> list[dict[str, Any]]:
        try:
            respuesta = await self._cliente.get(
                f"{URL_API}/tracks/",
                params={"client_id": self._client_id, "format": "json", "audioformat": "mp32", **parametros},
            )
            respuesta.raise_for_status()
            datos = respuesta.json()
        except (httpx.HTTPError, ValueError) as error:
            raise ErrorProveedor(f"Jamendo no respondió correctamente: {type(error).__name__}") from error

        if datos.get("headers", {}).get("status") != "success":
            raise ErrorProveedor("Jamendo devolvió un error")
        return datos.get("results", [])

    @staticmethod
    def _convertir(resultado: dict[str, Any]) -> Pista:
        return Pista(
            id_pista=str(resultado["id"]),
            proveedor="jamendo",
            titulo=resultado["name"],
            artista=resultado.get("artist_name", ""),
            album=resultado.get("album_name", ""),
            portada_url=resultado.get("album_image") or resultado.get("image") or "",
            duracion=int(resultado["duration"]),
            audio_url=resultado["audio"],
        )
