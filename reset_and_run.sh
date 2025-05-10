#!/bin/bash

set -e  # Detener script si ocurre un error

echo "Deteniendo y eliminando contenedores..."
docker stop $(docker ps -aq) 2>/dev/null || true
docker rm $(docker ps -aq) 2>/dev/null || true

echo "Eliminando todas las imágenes..."
docker rmi $(docker images -q) --force 2>/dev/null || true

echo "Construyendo imagen base 'nlp-base' desde Dockerfile.base..."
cd nlp || { echo "Error: carpeta 'nlp' no encontrada"; exit 1; }

docker build -t nlp-base:latest -f Dockerfile.base . || {
    echo "Error al construir 'nlp-base'"
    exit 1
}
cd ..

echo "Iniciando todos los servicios con Docker Compose..."
docker compose up --build -d