FROM node:24-alpine AS construccion

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:stable-alpine

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY docker/encabezados-seguridad.conf /etc/nginx/encabezados-seguridad.conf
COPY docker/configuracion.template.json /etc/nginx/configuracion.template.json
COPY --chmod=755 docker/40-generar-configuracion.sh /docker-entrypoint.d/
COPY --from=construccion /app/www /usr/share/nginx/html

EXPOSE 8100
