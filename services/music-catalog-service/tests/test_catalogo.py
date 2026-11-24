import httpx
from tests.conftest import pista_deezer, pista_jamendo, respuesta_jamendo

CLAVE_INTERNA = {"X-Clave-Interna": "clave-interna-de-pruebas"}

async def test_busqueda_normaliza_resultados_de_deezer(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(
        200, json={"data": [pista_deezer(1, "Marea alta"), pista_deezer(2, "Sin audio", preview="")]}
    )

    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "marea"}, headers=autorizacion)

    assert respuesta.status_code == 200
    datos = respuesta.json()
    assert datos["proveedor_usado"] == "deezer"
    assert len(datos["resultados"]) == 1
    pista = datos["resultados"][0]
    assert pista == {
        "id_pista": "1",
        "proveedor": "deezer",
        "titulo": "Marea alta",
        "artista": "Brisa Sur",
        "album": "Marea",
        "portada_url": "https://e-cdns-images.dzcdn.net/images/cover/1/250x250.jpg",
        "duracion": 30,
        "audio_url": "https://cdns-preview.dzcdn.net/stream/x.mp3",
    }

async def test_usa_jamendo_si_deezer_falla(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(503)
    proveedores.manejadores["api.jamendo.com"] = lambda _: respuesta_jamendo([pista_jamendo(7, "Ciudad dormida")])

    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "ciudad"}, headers=autorizacion)

    datos = respuesta.json()
    assert datos["proveedor_usado"] == "jamendo"
    assert datos["resultados"][0]["duracion"] == 184

async def test_usa_jamendo_si_deezer_devuelve_error_en_el_cuerpo(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(
        200, json={"error": {"type": "Exception", "code": 4}}
    )
    proveedores.manejadores["api.jamendo.com"] = lambda _: respuesta_jamendo([pista_jamendo(7, "Ciudad dormida")])

    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "ciudad"}, headers=autorizacion)

    assert respuesta.json()["proveedor_usado"] == "jamendo"

async def test_usa_jamendo_si_deezer_no_encuentra_nada(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(200, json={"data": []})
    proveedores.manejadores["api.jamendo.com"] = lambda _: respuesta_jamendo([pista_jamendo(7, "Ciudad dormida")])

    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "ciudad"}, headers=autorizacion)

    assert respuesta.json()["proveedor_usado"] == "jamendo"

async def test_devuelve_503_si_ningun_proveedor_responde(cliente, autorizacion):
    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "nada"}, headers=autorizacion)

    assert respuesta.status_code == 503
    assert "catálogo" in respuesta.json()["detail"]

async def test_segunda_busqueda_igual_sale_de_cache(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(
        200, json={"data": [pista_deezer(1, "Marea alta")]}
    )

    await cliente.get("/api/catalogo/buscar", params={"q": "Marea"}, headers=autorizacion)
    await cliente.get("/api/catalogo/buscar", params={"q": "  marea "}, headers=autorizacion)
    assert proveedores.llamadas.count("api.deezer.com") == 1


async def test_busqueda_requiere_token(cliente):
    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "marea"})

    assert respuesta.status_code == 401

async def test_busqueda_rechaza_consulta_muy_corta(cliente, autorizacion):
    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "a"}, headers=autorizacion)

    assert respuesta.status_code == 422

async def test_limite_de_busquedas_por_minuto(cliente, proveedores, autorizacion):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(
        200, json={"data": [pista_deezer(1, "Marea alta")]}
    )
    for _ in range(20):
        await cliente.get("/api/catalogo/buscar", params={"q": "marea"}, headers=autorizacion)
    respuesta = await cliente.get("/api/catalogo/buscar", params={"q": "marea"}, headers=autorizacion)

    assert respuesta.status_code == 429
    assert int(respuesta.headers["Retry-After"]) >= 1

async def test_pista_interna_requiere_clave(cliente):
    respuesta = await cliente.get("/internal/pistas/deezer/1")

    assert respuesta.status_code == 403

async def test_pista_interna_devuelve_metadatos(cliente, proveedores):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(200, json=pista_deezer(1, "Marea alta"))
    respuesta = await cliente.get("/internal/pistas/deezer/1", headers=CLAVE_INTERNA)

    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Marea alta"

async def test_pista_interna_inexistente_devuelve_404(cliente, proveedores):
    proveedores.manejadores["api.deezer.com"] = lambda _: httpx.Response(
        200, json={"error": {"type": "DataException", "code": 800}}
    )

    respuesta = await cliente.get("/internal/pistas/deezer/999", headers=CLAVE_INTERNA)
    assert respuesta.status_code == 404