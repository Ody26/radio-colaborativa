from typing import Annotated
from fastapi import APIRouter, Body, status
from radio_comun.seguridad import crear_token
from app.dependencias import ParticipanteAutenticado, RedisDep, SalaSolicitada
from app.schemas.participante import CambioApodo, Participante, SesionParticipante, UnirseSala
from app.schemas.sala import SalaCrear, SalaPublica
from app.services import salas

router = APIRouter(prefix="/api/salas", tags=["Salas"])

def _crear_sesion(sala: SalaPublica, participante: Participante) -> SesionParticipante:
    token = crear_token(sala.id_sala, participante.id_participante, participante.apodo)
    return SesionParticipante(token=token.token, expira_en=token.expira_en, participante=participante, sala=sala)

@router.post("", response_model=SalaPublica, status_code=status.HTTP_201_CREATED)
async def crear_sala(redis: RedisDep, datos: Annotated[SalaCrear | None, Body()] = None) -> SalaPublica:
    return await salas.crear_sala(redis, datos.nombre if datos else None)

@router.get("/{codigo}", response_model=SalaPublica)
async def obtener_sala(sala: SalaSolicitada) -> SalaPublica:
    return sala

@router.post("/{codigo}/unirse", response_model=SesionParticipante, status_code=status.HTTP_201_CREATED)
async def unirse_a_sala(
    sala: SalaSolicitada,
    redis: RedisDep,
    datos: Annotated[UnirseSala | None, Body()] = None,
) -> SesionParticipante:
    participante = await salas.unirse_a_sala(redis, sala, datos.apodo if datos else None)
    return _crear_sesion(sala, participante)

@router.patch("/{codigo}/participantes/yo", response_model=SesionParticipante)
async def cambiar_apodo(
    sala: SalaSolicitada,
    claims: ParticipanteAutenticado,
    redis: RedisDep,
    datos: CambioApodo,
) -> SesionParticipante:
    participante = await salas.cambiar_apodo(redis, sala, claims.id_participante, datos.apodo)
    return _crear_sesion(sala, participante)

@router.get("/{codigo}/participantes", response_model=list[Participante])
async def listar_participantes(sala: SalaSolicitada, _: ParticipanteAutenticado, redis: RedisDep) -> list[Participante]:
    return await salas.listar_participantes(redis, sala.id_sala)
