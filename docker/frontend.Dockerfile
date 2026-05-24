#   ____ _                 _  ____      _ _           _   _             ___
#  / ___| | ___  _   _  __| |/ ___|___ | | | ___  ___| |_(_) ___  _ __ / _ \ _ __  _ __
# | |   | |/ _ \| | | |/ _` | |   / _ \| | |/ _ \/ __| __| |/ _ \| `_ \| | | | `_ \| `_ |
# | |___| | (_) | |_| | (_| | |__| (_) | | |  __/ (__| |_| | (_) | | | | |_| | |_) | |_) |
#  \____|_|\___/ \__,_|\__,_|\____\___/|_|_|\___|\___|\__|_|\___/|_| |_|\___/| .__/| .__/
#                                                                            |_|   |_|
# Projet : CloudCollectionApp
# Date de creation : 2026-05-03
# Auteurs : Codex et Binda Sébastien
#
FROM node:20-alpine AS build

WORKDIR /app

ARG APP_VERSION=dev
ENV VITE_APP_VERSION=${APP_VERSION}

COPY frontend/package*.json ./
RUN npm ci

COPY frontend .
RUN npm run build

FROM nginx:1.27-alpine

ARG APP_VERSION=dev
ENV USER_COLLECTION_MAX_UPLOAD_BYTES=104857600
ENV NGINX_ENVSUBST_FILTER="^USER_COLLECTION_MAX_UPLOAD_BYTES$"
LABEL org.opencontainers.image.version="${APP_VERSION}"

COPY docker/nginx.conf /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
