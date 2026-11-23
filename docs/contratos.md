# Contratos entre servicios

Referencia común para el backend y el frontend. Cualquier cambio de un contrato se hace primero aquí, en el mismo PR que lo implementa.

## Convenciones

- Fechas en ISO 8601 UTC (`2026-11-22T23:00:00Z`), salvo los campos de reloj de reproducción, que van en milisegundos desde época (`*_ms`).
- Todos los errores, incluidos los de validación, responden `{"detail": "Mensaje en español para el usuario"}` con un único texto listo para mostrar.
- Autenticación con `Authorization: Bearer <token>` en HTTP. El token solo es válido para la sala con la que se emitió.
- Claims del token: `sub` (id del participante), `id_sala`, `apodo`, `iat` y `exp` (4 h). Al cambiar el apodo se emite un token nuevo.
- Textos de usuario (nombre de sala, apodo, chat): sin etiquetas HTML ni caracteres de control. Apodo de 3 a 20 caracteres, único en la sala sin distinguir mayúsculas; nombre de sala de 3 a 40.
- Endpoints `/internal/*`: solo entre servicios, con cabecera `X-Clave-Interna: <CLAVE_SERVICIOS_INTERNOS>`.

| Código | Uso |
|---|---|
| 401 | Token ausente, vencido o de otra sala |
| 404 | Sala o elemento inexistente |
| 409 | Conflicto con una regla de negocio (sala llena, apodo repetido, canción duplicada, límites de cola) |
| 422 | Datos de entrada inválidos |
| 429 | Límite de frecuencia excedido; incluye cabecera `Retry-After` en segundos |
| 503 | Dependencia externa no disponible |

## Modelos

```text
SalaPublica        { id_sala, codigo, nombre, estado, fecha_creacion, fecha_expiracion, participantes_conectados }
Participante       { id_participante, apodo, unido_en }
SesionParticipante { token, token_tipo: "bearer", expira_en, participante: Participante, sala: SalaPublica }
Pista              { id_pista, proveedor: "deezer" | "jamendo", titulo, artista, album, portada_url, duracion, audio_url }
ElementoCola       { id_elemento, pista: Pista, agregado_por: Participante, agregado_en, votos_favor, votos_contra, puntaje, mi_voto: -1 | 0 | 1 }
EstadoReproduccion { estado: "reproduciendo" | "en_espera", elemento: ElementoCola | null, iniciado_en_ms, duracion }
MensajeChat        { id_mensaje, participante: Participante, texto, enviado_en }
```

`duracion` siempre en segundos y corresponde a lo que el proveedor permite reproducir. `codigo` tiene 6 caracteres de `ABCDEFGHJKMNPQRSTUVWXYZ23456789` (sin `I`, `L`, `O`, `0` ni `1` para evitar confusiones); las rutas lo aceptan sin distinguir mayúsculas.

## room-queue-service (:8002)

| Método | Ruta | Cuerpo | Respuesta | Auth |
|---|---|---|---|---|
| POST | `/api/salas` | `{ nombre? }` (cuerpo opcional) | 201 `SalaPublica` | No |
| GET | `/api/salas/{codigo}` | — | `SalaPublica` | No |
| POST | `/api/salas/{codigo}/unirse` | `{ apodo? }` (cuerpo opcional) | 201 `SesionParticipante` | No |
| PATCH | `/api/salas/{codigo}/participantes/yo` | `{ apodo }` | `SesionParticipante` con token nuevo | Sí |
| GET | `/api/salas/{codigo}/participantes` | — | `Participante[]` | Sí |
| GET | `/api/salas/{codigo}/cola` | — | `ElementoCola[]` ordenada | Sí |
| POST | `/api/salas/{codigo}/cola` | `{ proveedor, id_pista }` | 201 `ElementoCola` | Sí |
| PUT | `/api/salas/{codigo}/cola/{id_elemento}/voto` | `{ valor: 1 \| -1 }` | `ElementoCola` | Sí |
| DELETE | `/api/salas/{codigo}/cola/{id_elemento}/voto` | — | `ElementoCola` | Sí |
| POST | `/internal/salas/{id_sala}/siguiente` | — | `{ elemento: ElementoCola \| null }` | Interna |

Al agregar una canción solo se envía `proveedor` e `id_pista`; los metadatos los obtiene room-queue desde music-catalog.

## music-catalog-service (:8001)

| Método | Ruta | Respuesta | Auth |
|---|---|---|---|
| GET | `/api/catalogo/buscar?q=&limite=20` | `{ proveedor_usado, resultados: Pista[] }` | Sí |
| GET | `/internal/pistas/{proveedor}/{id_pista}` | `Pista` | Interna |

Si Deezer falla o no responde a tiempo, la búsqueda se repite en Jamendo y `proveedor_usado` lo indica.

## realtime-sync-service (:8003)

Conexión: `WS /ws/salas/{codigo}`. El primer mensaje del cliente debe ser `autenticar` dentro de los primeros 5 s.

Todos los mensajes, en ambos sentidos, usan el sobre:

```json
{ "tipo": "chat.mensaje", "datos": { } }
```

### Cliente → servidor

| tipo | datos |
|---|---|
| `autenticar` | `{ token }` |
| `chat.enviar` | `{ texto }` (máx. 280 caracteres) |
| `efecto.enviar` | `{ id_efecto }` |
| `tiempo.ping` | `{ cliente_ms }` |
| `reproduccion.fallo` | `{ id_elemento }` |

### Servidor → cliente

| tipo | datos |
|---|---|
| `sala.estado` | `{ sala, participantes, reproduccion: EstadoReproduccion, mensajes: MensajeChat[] }` (tras autenticar y al reconectar) |
| `participante.unido` / `participante.salio` / `participante.actualizado` | `Participante` |
| `cola.actualizada` | `{ cola: ElementoCola[] }` sin `mi_voto`; el cliente lo conserva por su cuenta |
| `chat.mensaje` | `MensajeChat` |
| `efecto.reproducir` | `{ id_efecto, participante }` |
| `reproduccion.estado` | `EstadoReproduccion` |
| `reproduccion.omitida` | `{ id_elemento, motivo }` |
| `tiempo.pong` | `{ cliente_ms, servidor_ms }` |
| `error` | `{ detalle, reintentar_en? }` |

Códigos de cierre: `4401` token inválido, `4404` sala inexistente, `4409` sala llena.

Efectos disponibles: `aplausos`, `risas`, `bocina`, `redoble`, `campana`, `abucheo`.

## Redis

Un único Redis compartido. Cada clave pertenece al servicio que la escribe; los demás solo la leen.

| Clave | Tipo | Dueño |
|---|---|---|
| `sala:{id_sala}` | Hash | room-queue |
| `sala:codigo:{codigo}` | String → `id_sala` | room-queue |
| `sala:{id_sala}:participantes` | Hash `id_participante → JSON` | room-queue |
| `sala:{id_sala}:apodos` | Set | room-queue |
| `sala:{id_sala}:cola` | Sorted Set `id_elemento → puntaje compuesto` | room-queue |
| `sala:{id_sala}:elemento:{id_elemento}` | Hash | room-queue |
| `sala:{id_sala}:votos:{id_elemento}` | Hash `id_participante → ±1` | room-queue |
| `sala:{id_sala}:pistas_en_cola` | Set `proveedor:id_pista` | room-queue |
| `sala:{id_sala}:secuencia` | String (contador) | room-queue |
| `sala:{id_sala}:reproduccion` | Hash | realtime-sync |
| `sala:{id_sala}:chat` | List (últimos 100) | realtime-sync |
| `sala:{id_sala}:conexiones` | Hash `id_conexion → id_participante` | realtime-sync |
| `catalogo:busqueda:{proveedor}:{consulta}` | String JSON con TTL | music-catalog |
| `limite:{accion}:{id_sala}:{id_participante}` | Sorted Set (ventana deslizante) | cada servicio |

Puntaje compuesto de la cola: `puntaje × 1 000 000 − secuencia`, para que en empate gane la canción agregada primero.

Canal Pub/Sub por sala: `sala:{id_sala}:eventos`, con el mismo sobre que el WebSocket. room-queue publica `cola.actualizada` y `participante.actualizado`; realtime-sync los retransmite a los clientes.

## Límites de frecuencia

| Acción | Límite | Servicio |
|---|---|---|
| Votos | 10 cada 10 s | room-queue |
| Altas de canciones | 5 por minuto | room-queue |
| Búsquedas | 20 por minuto | music-catalog |
| Mensajes de chat | 5 cada 10 s | realtime-sync |
| Efectos de sonido | 1 cada 3 s | realtime-sync |
