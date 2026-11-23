from datetime import datetime
from functools import partial
from typing import Annotated, Literal
from pydantic import AfterValidator, BaseModel
from radio_comun.texto import validar_texto_plano

NombreSala = Annotated[str, AfterValidator(partial(validar_texto_plano, campo="nombre", minimo=3, maximo=40))]

class SalaCrear(BaseModel):
    nombre: NombreSala | None = None

class SalaPublica(BaseModel):
    id_sala: str
    codigo: str
    nombre: str
    estado: Literal["activa"]
    fecha_creacion: datetime
    fecha_expiracion: datetime
    participantes_conectados: int
