import os
os.environ["JWT_SECRET_KEY"] = "clave-de-pruebas-con-longitud-suficiente-para-hs256"
os.environ["CLAVE_SERVICIOS_INTERNOS"] = "clave-interna-de-pruebas"
os.environ["JAMENDO_CLIENT_ID"] = "cliente-de-pruebas"

from collections.abc import Callable
import httpx
import pytest
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from radio_comun.seguridad import crear_token
from app.dependencias import obtener_cliente_http, obtener_redis
from app.main import app

ManejadorProveedores = Callable[[httpx.Request], httpx.Response]

class ProveedoresSimulados:
    def __init__(self) -> None:
        self.manejadores: dict[str, ManejadorProveedores] = {}
        self.llamadas: list[str] = []

    def __call__(self, peticion: httpx.Request) -> httpx.Response:
        self.llamadas.append(peticion.url.host)
        manejador = self.manejadores.get(peticion.url.host)
        if manejador is None:
            return httpx.Response(500)
        return manejador(peticion)

@pytest.fixture
async def redis():
    cliente = FakeAsyncRedis(decode_responses=True)
    yield cliente
    await cliente.aclose()

@pytest.fixture
def proveedores() -> ProveedoresSimulados:
    return ProveedoresSimulados()


@pytest.fixture
async def cliente(redis, proveedores):
    http = httpx.AsyncClient(transport=httpx.MockTransport(proveedores))
    app.dependency_overrides[obtener_redis] = lambda: redis
    app.dependency_overrides[obtener_cliente_http] = lambda: http
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://pruebas") as cliente:
        yield cliente
    app.dependency_overrides.clear()
    await http.aclose()

@pytest.fixture
def autorizacion() -> dict[str, str]:
    token = crear_token("sala-de-pruebas", "participante-de-pruebas", "Odeth").token
    return {"Authorization": f"Bearer {token}"}

def pista_deezer(id_pista: int, titulo: str, preview: str = "https://cdns-preview.dzcdn.net/stream/x.mp3") -> dict:
    return {
        "id": id_pista,
        "title": titulo,
        "duration": 215,
        "readable": True,
        "preview": preview,
        "artist": {"name": "Brisa Sur"},
        "album": {"title": "Marea", "cover_medium": "https://e-cdns-images.dzcdn.net/images/cover/1/250x250.jpg"},
    }

def pista_jamendo(id_pista: int, titulo: str) -> dict:
    return {
        "id": str(id_pista),
        "name": titulo,
        "duration": 184,
        "artist_name": "Kora",
        "album_name": "Ciudad",
        "album_image": "https://usercontent.jamendo.com/album.jpg",
        "audio": "https://prod-1.storage.jamendo.com/?trackid=1&format=mp32",
    }

def respuesta_jamendo(resultados: list[dict]) -> httpx.Response:
    return httpx.Response(200, json={"headers": {"status": "success", "code": 0}, "results": resultados})
