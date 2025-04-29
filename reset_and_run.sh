#!/bin/bash

echo "🛑 Deteniendo y eliminando contenedores..."
docker stop $(docker ps -aq) 2>/dev/null
docker rm $(docker ps -aq) 2>/dev/null

echo "🧹 Eliminando todas las imágenes..."
docker rmi $(docker images -q) --force 2>/dev/null

echo "📦 Construyendo imagen base 'nlp-base' desde Dockerfile.base..."
cd nlp || { echo "❌ No se encontró la carpeta 'nlp'"; exit 1; }
docker build -t nlp-base:latest -f Dockerfile.base . || { echo "❌ Fallo construyendo 'nlp-base'"; exit 1; }
cd ..

echo "🚀 Levantando todos los servicios con Docker Compose..."
docker compose up --build
