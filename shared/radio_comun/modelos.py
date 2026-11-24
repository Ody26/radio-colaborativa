from typing import Literal
from pydantic import BaseModel, field_validator

Proveedor = Literal["deezer", "jamendo"]

class Pista(BaseModel):
    id_pista: str
    proveedor: Proveedor
    titulo: str
    artista: str
    album: str
    portada_url: str
    duracion: int
    audio_url: str

    @field_validator("portada_url", "audio_url")
    @classmethod
    def validar_url(cls, valor: str) -> str:
        if valor and not valor.startswith(("https://", "http://")):
            raise ValueError("La URL del catálogo no es válida")
        return valor
