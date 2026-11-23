from datetime import datetime
from functools import partial
from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel
from radio_comun.texto import validar_texto_plano
from app.schemas.sala import SalaPublica

Apodo = Annotated[str, AfterValidator(partial(validar_texto_plano, campo="apodo", minimo=3, maximo=20))]

class Participante(BaseModel):
    id_participante: str
    apodo: str
    unido_en: datetime

class UnirseSala(BaseModel):
    apodo: Apodo | None = None

class CambioApodo(BaseModel):
    apodo: Apodo

class SesionParticipante(BaseModel):
    token: str
    token_tipo: Literal["bearer"] = "bearer"
    expira_en: datetime
    participante: Participante
    sala: SalaPublica