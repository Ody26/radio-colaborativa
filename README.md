# radio-colaborativa

Plataforma web de radio colaborativa en tiempo real: salas sin registro, cola de canciones ordenada por votos, reproducción sincronizada, chat y soundboard.

## Arquitectura

| Componente | Tecnología | Puerto |
|---|---|---|
| `frontend-app` | Ionic + Angular, servido por Nginx | 8100 |
| `music-catalog-service` | Python / FastAPI | 8001 |
| `room-queue-service` | Python / FastAPI + Redis | 8002 |
| `realtime-sync-service` | Python / FastAPI + WebSockets + Redis | 8003 |
| `redis` | Redis 7 (en memoria, sin persistencia) | 6379 (solo red interna) |

Todos los contenedores comparten la red `radio-network`. El código común de los servicios Python está en `shared/radio_comun` y los contratos de API y eventos en [`docs/contratos.md`](docs/contratos.md).

## Puesta en marcha

Requisitos: Docker con Docker Compose v2.

```bash
cp .env.example .env
docker compose up --build
```

Antes de levantar el sistema, reemplaza en `.env` los valores de `JWT_SECRET_KEY` y `CLAVE_SERVICIOS_INTERNOS`. Para generar una clave:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Cada servicio expone `GET /salud` y su documentación interactiva en `/docs` (por ejemplo, http://localhost:8002/docs).

## Estructura

```text
.
├── docker-compose.yml
├── docs/contratos.md
├── shared/radio_comun/          # configuración, cliente Redis y salud
└── services/
    ├── music-catalog-service/
    ├── room-queue-service/
    └── realtime-sync-service/
```
