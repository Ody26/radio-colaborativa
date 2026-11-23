import re
from radio_comun import claves

from app.configuracion import CAPACIDAD_MAXIMA_SALA
from tests.conftest import autorizacion

PATRON_CODIGO = re.compile(r"^[ABCDEFGHJKMNPQRSTUVWXYZ23456789]{6}$")

async def test_crear_sala_genera_codigo_valido(cliente):
    respuesta = await cliente.post("/api/salas", json={"nombre": "Viernes de rock"})
    assert respuesta.status_code == 201
    sala = respuesta.json()
    assert PATRON_CODIGO.match(sala["codigo"])
    assert sala["nombre"] == "Viernes de rock"
    assert sala["participantes_conectados"] == 0

async def test_crear_sala_sin_nombre_usa_el_codigo(cliente):
    respuesta = await cliente.post("/api/salas")
    sala = respuesta.json()
    assert sala["nombre"] == f"Sala {sala['codigo']}"

async def test_crear_sala_rechaza_nombre_con_html(cliente):
    respuesta = await cliente.post("/api/salas", json={"nombre": "<b>Sala</b>"})
    assert respuesta.status_code == 422
    assert "etiquetas HTML" in respuesta.json()["detail"]

async def test_claves_de_la_sala_tienen_vencimiento(cliente, redis, sala):
    assert await redis.ttl(claves.sala(sala["id_sala"])) > 0
    assert await redis.ttl(claves.codigo_sala(sala["codigo"])) > 0

async def test_obtener_sala_acepta_codigo_en_minusculas(cliente, sala):
    respuesta = await cliente.get(f"/api/salas/{sala['codigo'].lower()}")
    assert respuesta.status_code == 200
    assert respuesta.json()["id_sala"] == sala["id_sala"]


async def test_obtener_sala_inexistente_devuelve_404(cliente):
    respuesta = await cliente.get("/api/salas/ZZZZZZ")
    assert respuesta.status_code == 404
    assert respuesta.json()["detail"] == "La sala no existe o ya expiró"

async def test_unirse_asigna_apodo_y_token(cliente, sala):
    respuesta = await cliente.post(f"/api/salas/{sala['codigo']}/unirse")
    assert respuesta.status_code == 201
    sesion = respuesta.json()
    assert sesion["token"]
    assert 3 <= len(sesion["participante"]["apodo"]) <= 20
    assert sesion["sala"]["id_sala"] == sala["id_sala"]

async def test_unirse_con_apodo_repetido_devuelve_409(cliente, sala):
    await cliente.post(f"/api/salas/{sala['codigo']}/unirse", json={"apodo": "Odeth"})
    respuesta = await cliente.post(f"/api/salas/{sala['codigo']}/unirse", json={"apodo": "ODETH"})
    assert respuesta.status_code == 409

async def test_unirse_con_apodo_corto_devuelve_422(cliente, sala):
    respuesta = await cliente.post(f"/api/salas/{sala['codigo']}/unirse", json={"apodo": "ab"})
    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "El apodo debe tener entre 3 y 20 caracteres"

async def test_unirse_a_sala_llena_devuelve_409(cliente, redis, sala):
    conexiones = {f"conexion-{i}": f"participante-{i}" for i in range(CAPACIDAD_MAXIMA_SALA)}
    await redis.hset(claves.conexiones(sala["id_sala"]), mapping=conexiones)

    respuesta = await cliente.post(f"/api/salas/{sala['codigo']}/unirse")
    assert respuesta.status_code == 409
    assert "llena" in respuesta.json()["detail"]

async def test_cambiar_apodo_emite_token_nuevo_y_libera_el_anterior(cliente, sala):
    ruta = f"/api/salas/{sala['codigo']}"
    sesion = (await cliente.post(f"{ruta}/unirse", json={"apodo": "Gerardo"})).json()
    respuesta = await cliente.patch(
        f"{ruta}/participantes/yo", json={"apodo": "Gera"}, headers=autorizacion(sesion["token"])
    )

    assert respuesta.status_code == 200
    nueva_sesion = respuesta.json()
    assert nueva_sesion["participante"]["apodo"] == "Gera"
    assert nueva_sesion["token"] != sesion["token"]
    otra = await cliente.post(f"{ruta}/unirse", json={"apodo": "Gerardo"})
    assert otra.status_code == 201

async def test_cambiar_apodo_publica_evento(cliente, redis, sala):
    ruta = f"/api/salas/{sala['codigo']}"
    sesion = (await cliente.post(f"{ruta}/unirse")).json()
    suscripcion = redis.pubsub()
    await suscripcion.subscribe(claves.canal_eventos(sala["id_sala"]))
    await suscripcion.get_message(timeout=1)

    await cliente.patch(f"{ruta}/participantes/yo", json={"apodo": "Nuevo apodo"}, headers=autorizacion(sesion["token"]))
    mensaje = await suscripcion.get_message(ignore_subscribe_messages=True, timeout=1)
    assert mensaje is not None
    assert '"participante.actualizado"' in mensaje["data"]
    await suscripcion.aclose()

async def test_token_de_otra_sala_es_rechazado(cliente, sala):
    otra_sala = (await cliente.post("/api/salas")).json()
    sesion = (await cliente.post(f"/api/salas/{otra_sala['codigo']}/unirse")).json()

    respuesta = await cliente.get(f"/api/salas/{sala['codigo']}/participantes", headers=autorizacion(sesion["token"]))
    assert respuesta.status_code == 401

async def test_listar_participantes_requiere_token(cliente, sala):
    respuesta = await cliente.get(f"/api/salas/{sala['codigo']}/participantes")
    assert respuesta.status_code == 401

async def test_listar_participantes_en_orden_de_llegada(cliente, sala):
    ruta = f"/api/salas/{sala['codigo']}"
    primera = (await cliente.post(f"{ruta}/unirse", json={"apodo": "Primera"})).json()
    await cliente.post(f"{ruta}/unirse", json={"apodo": "Segundo"})
    respuesta = await cliente.get(f"{ruta}/participantes", headers=autorizacion(primera["token"]))
    assert [p["apodo"] for p in respuesta.json()] == ["Primera", "Segundo"]