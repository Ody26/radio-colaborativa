from typing import Annotated
from fastapi import APIRouter, Depends, Path, Query
from radio_comun.modelos import Pista, Proveedor
from radio_comun.seguridad import verificar_clave_interna
from app.dependencias import ServicioCatalogoDep, controlar_busquedas
from app.schemas.busqueda import ResultadoBusqueda

router = APIRouter(tags=["Catálogo"])

@router.get("/api/catalogo/buscar", response_model=ResultadoBusqueda, dependencies=[Depends(controlar_busquedas)])
async def buscar_canciones(
    servicio: ServicioCatalogoDep,
    q: Annotated[str, Query(min_length=2, max_length=100, description="Título o artista")],
    limite: Annotated[int, Query(ge=1, le=25)] = 20,
) -> ResultadoBusqueda:
    return await servicio.buscar(q, limite)

@router.get(
    "/internal/pistas/{proveedor}/{id_pista}",
    response_model=Pista,
    dependencies=[Depends(verificar_clave_interna)],
    include_in_schema=False,
)
async def obtener_pista(
    servicio: ServicioCatalogoDep,
    proveedor: Proveedor,
    id_pista: Annotated[str, Path(pattern=r"^\d{1,20}$")],
) -> Pista:
    return await servicio.obtener_pista(proveedor, id_pista)
