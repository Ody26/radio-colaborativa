from radio_comun.modelos import Pista, Proveedor
from pydantic import BaseModel

class ResultadoBusqueda(BaseModel):
    proveedor_usado: Proveedor
    resultados: list[Pista]
