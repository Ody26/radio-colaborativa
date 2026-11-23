#!/bin/sh
set -eu

export URL_PUBLICA_MUSIC_CATALOG="${URL_PUBLICA_MUSIC_CATALOG:-http://localhost:8001}"
export URL_PUBLICA_ROOM_QUEUE="${URL_PUBLICA_ROOM_QUEUE:-http://localhost:8002}"
export URL_PUBLICA_REALTIME_SYNC="${URL_PUBLICA_REALTIME_SYNC:-ws://localhost:8003}"

envsubst '${URL_PUBLICA_MUSIC_CATALOG} ${URL_PUBLICA_ROOM_QUEUE} ${URL_PUBLICA_REALTIME_SYNC}' \
  < /etc/nginx/configuracion.template.json \
  > /usr/share/nginx/html/assets/configuracion.json
