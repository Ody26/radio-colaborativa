import os
os.environ["JWT_SECRET_KEY"] = "clave-de-pruebas-con-longitud-suficiente-para-hs256"
import pytest
from fakeredis import FakeAsyncRedis
from httpx import ASGITransport, AsyncClient
from app.dependencias import obtener_redis
from app.main import app

@pytest.fixture
async def redis():
    cliente = FakeAsyncRedis(decode_responses=True)
    yield cliente
    await cliente.aclose()

@pytest.fixture
async def cliente(redis):
    app.dependency_overrides[obtener_redis] = lambda: redis
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://pruebas") as cliente:
        yield cliente
    app.dependency_overrides.clear()

@pytest.fixture
async def sala(cliente):
    respuesta = await cliente.post("/api/salas", json={"nombre": "Viernes de rock"})
    return respuesta.json()

def autorizacion(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}