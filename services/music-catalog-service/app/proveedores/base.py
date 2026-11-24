from typing import Protocol
from radio_comun.modelos import Pista, Proveedor

class ErrorProveedor(Exception):
    pass

class ProveedorMusica(Protocol):
    nombre: Proveedor
    async def buscar(self, consulta: str, limite: int) -> list[Pista]: ...
    async def obtener_pista(self, id_pista: str) -> Pista | None: ...
