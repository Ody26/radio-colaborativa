import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from functools import lru_cache
from typing import Annotated
import jwt
from decouple import config
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, ValidationError

LONGITUD_MINIMA_CLAVE = 32
CLAIMS_REQUERIDOS = ["sub", "id_sala", "apodo", "iat", "exp"]

@dataclass(frozen=True)
class ConfiguracionJWT:
    clave_secreta: str
    algoritmo: str
    minutos_expiracion: int


@lru_cache
def obtener_configuracion_jwt() -> ConfiguracionJWT:
    clave = config("JWT_SECRET_KEY")
    algoritmo = config("JWT_ALGORITHM", default="HS256")
    minutos = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=240, cast=int)
    if len(clave.encode("utf-8")) < LONGITUD_MINIMA_CLAVE:
        raise ValueError(f"JWT_SECRET_KEY debe contener al menos {LONGITUD_MINIMA_CLAVE} bytes")
    if algoritmo != "HS256":
        raise ValueError("JWT_ALGORITHM debe ser HS256")
    if minutos <= 0:
        raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES debe ser positivo")
    return ConfiguracionJWT(clave, algoritmo, minutos)

class ClaimsToken(BaseModel):
    model_config = ConfigDict(extra="ignore", frozen=True)

    sub: str
    id_sala: str
    apodo: str
    iat: int
    exp: int

    @property
    def id_participante(self) -> str:
        return self.sub

@dataclass(frozen=True)
class TokenEmitido:
    token: str
    expira_en: datetime

def crear_token(id_sala: str, id_participante: str, apodo: str) -> TokenEmitido:
    configuracion = obtener_configuracion_jwt()
    ahora = datetime.now(timezone.utc)
    expira_en = ahora + timedelta(minutes=configuracion.minutos_expiracion)
    token = jwt.encode(
        {"sub": id_participante, "id_sala": id_sala, "apodo": apodo, "iat": ahora, "exp": expira_en},
        configuracion.clave_secreta,
        algorithm=configuracion.algoritmo,
    )
    return TokenEmitido(token=token, expira_en=expira_en)

def decodificar_token(token: str) -> ClaimsToken:
    configuracion = obtener_configuracion_jwt()
    payload = jwt.decode(
        token,
        configuracion.clave_secreta,
        algorithms=[configuracion.algoritmo],
        options={"require": CLAIMS_REQUERIDOS},
    )
    return ClaimsToken.model_validate(payload)

def no_autorizado(detalle: str = "Tu sesión no es válida o venció. Vuelve a unirte a la sala.") -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detalle,
        headers={"WWW-Authenticate": "Bearer"},
    )

esquema_bearer = HTTPBearer(auto_error=False)

async def obtener_claims(
    credenciales: Annotated[HTTPAuthorizationCredentials | None, Depends(esquema_bearer)],
) -> ClaimsToken:
    if credenciales is None:
        raise no_autorizado()
    try:
        return decodificar_token(credenciales.credentials)
    except (jwt.InvalidTokenError, ValidationError):
        raise no_autorizado() from None

ClaimsActuales = Annotated[ClaimsToken, Depends(obtener_claims)]

def verificar_clave_interna(x_clave_interna: Annotated[str | None, Header()] = None) -> None:
    esperada = config("CLAVE_SERVICIOS_INTERNOS", default="")
    if not esperada or not x_clave_interna or not secrets.compare_digest(x_clave_interna, esperada):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido a servicios internos")