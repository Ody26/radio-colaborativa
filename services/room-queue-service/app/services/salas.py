import secrets
from datetime import datetime, timezone
from uuid import uuid4
from radio_comun import claves
from radio_comun.errores import ConflictoNegocio, RecursoNoEncontrado, ServicioNoDisponible
from radio_comun.eventos import publicar_evento
from redis.asyncio import Redis
from app.configuracion import CAPACIDAD_MAXIMA_SALA, obtener_configuracion_salas
from app.schemas.participante import Participante
from app.schemas.sala import SalaPublica
from app.services.apodos import generar_apodo

ALFABETO_CODIGO = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"
LONGITUD_CODIGO = 6
INTENTOS_GENERACION = 20

def _ahora() -> datetime:
    return datetime.now(timezone.utc)

def generar_codigo() -> str:
    return "".join(secrets.choice(ALFABETO_CODIGO) for _ in range(LONGITUD_CODIGO))

async def _contar_conectados(redis: Redis, id_sala: str) -> int:
    return len(set(await redis.hvals(claves.conexiones(id_sala))))

async def _renovar_vigencia(redis: Redis, sala: SalaPublica) -> None:
    configuracion = obtener_configuracion_salas()
    vence = min(_ahora() + configuracion.ttl_inactividad, sala.fecha_expiracion)
    async with redis.pipeline(transaction=True) as pipeline:
        for clave in (
            claves.sala(sala.id_sala),
            claves.codigo_sala(sala.codigo),
            claves.participantes(sala.id_sala),
            claves.apodos(sala.id_sala),
        ):
            pipeline.expireat(clave, vence)
        await pipeline.execute()

async def _reservar_apodo(redis: Redis, id_sala: str, apodo: str) -> bool:
    return await redis.sadd(claves.apodos(id_sala), apodo.casefold()) == 1

async def crear_sala(redis: Redis, nombre: str | None) -> SalaPublica:
    configuracion = obtener_configuracion_salas()
    id_sala = uuid4().hex
    creada = _ahora()
    for _ in range(INTENTOS_GENERACION):
        codigo = generar_codigo()
        if await redis.set(claves.codigo_sala(codigo), id_sala, nx=True, exat=creada + configuracion.duracion_maxima):
            break
    else:
        raise ServicioNoDisponible("No fue posible generar un código de sala. Intenta de nuevo.")

    sala = SalaPublica(
        id_sala=id_sala,
        codigo=codigo,
        nombre=nombre or f"Sala {codigo}",
        estado="activa",
        fecha_creacion=creada,
        fecha_expiracion=creada + configuracion.duracion_maxima,
        participantes_conectados=0,
    )
    await redis.hset(claves.sala(id_sala), mapping=sala.model_dump(mode="json", exclude={"participantes_conectados"}))
    await _renovar_vigencia(redis, sala)
    return sala

async def obtener_sala(redis: Redis, codigo: str) -> SalaPublica:
    id_sala = await redis.get(claves.codigo_sala(codigo))
    datos = await redis.hgetall(claves.sala(id_sala)) if id_sala else {}
    if not datos:
        raise RecursoNoEncontrado("La sala no existe o ya expiró")
    return SalaPublica(**datos, participantes_conectados=await _contar_conectados(redis, id_sala))

async def obtener_participante(redis: Redis, id_sala: str, id_participante: str) -> Participante:
    datos = await redis.hget(claves.participantes(id_sala), id_participante)
    if datos is None:
        raise RecursoNoEncontrado("No perteneces a esta sala. Vuelve a unirte.")
    return Participante.model_validate_json(datos)

async def unirse_a_sala(redis: Redis, sala: SalaPublica, apodo: str | None) -> Participante:
    if sala.participantes_conectados >= CAPACIDAD_MAXIMA_SALA:
        raise ConflictoNegocio("La sala está llena. Intenta de nuevo más tarde.")

    if apodo is not None:
        if not await _reservar_apodo(redis, sala.id_sala, apodo):
            raise ConflictoNegocio("Ese apodo ya está en uso en la sala")
    else:
        for _ in range(INTENTOS_GENERACION):
            apodo = generar_apodo()
            if await _reservar_apodo(redis, sala.id_sala, apodo):
                break
        else:
            raise ServicioNoDisponible("No fue posible asignar un apodo. Intenta de nuevo.")

    participante = Participante(id_participante=uuid4().hex, apodo=apodo, unido_en=_ahora())
    await redis.hset(claves.participantes(sala.id_sala), participante.id_participante, participante.model_dump_json())
    await _renovar_vigencia(redis, sala)
    return participante

async def cambiar_apodo(redis: Redis, sala: SalaPublica, id_participante: str, nuevo_apodo: str) -> Participante:
    participante = await obtener_participante(redis, sala.id_sala, id_participante)
    apodo_anterior = participante.apodo

    if nuevo_apodo.casefold() != apodo_anterior.casefold():
        if not await _reservar_apodo(redis, sala.id_sala, nuevo_apodo):
            raise ConflictoNegocio("Ese apodo ya está en uso en la sala")
        await redis.srem(claves.apodos(sala.id_sala), apodo_anterior.casefold())

    actualizado = participante.model_copy(update={"apodo": nuevo_apodo})
    await redis.hset(claves.participantes(sala.id_sala), id_participante, actualizado.model_dump_json())
    await _renovar_vigencia(redis, sala)
    await publicar_evento(redis, sala.id_sala, "participante.actualizado", actualizado.model_dump(mode="json"))
    return actualizado

async def listar_participantes(redis: Redis, id_sala: str) -> list[Participante]:
    registros = await redis.hvals(claves.participantes(id_sala))
    participantes = [Participante.model_validate_json(registro) for registro in registros]
    return sorted(participantes, key=lambda participante: participante.unido_en)
