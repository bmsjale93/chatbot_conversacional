#!/bin/bash

set -e  # Salir si ocurre un error

mostrar_menu() {
    echo ""
    echo "======================================"
    echo "     GESTOR DE PROYECTO EMOCIONAL     "
    echo "======================================"
    echo "1. Montar proyecto completo"
    echo "2. Resetear el proyecto completo"
    echo "3. Levantar el proyecto (modo silencioso)"
    echo "4. Eliminar contenedores y volúmenes"
    echo "5. Comprobar estado de los contenedores"
    echo "6. Limpiar base de datos"
    echo "7. Salir"
    echo "--------------------------------------"
    echo -n "Selecciona una opción [1-7]: "
}

montar_proyecto() {
    echo "Construyendo imagen base 'nlp-base' desde Dockerfile.base..."
    cd nlp || { echo "Error: carpeta 'nlp' no encontrada"; exit 1; }

    docker build -t nlp-base:latest -f Dockerfile.base . || {
        echo "Error al construir 'nlp-base'"
        exit 1
    }

    cd ..
    echo "Levantando todos los servicios..."
    docker compose up --build -d
}

resetear_proyecto() {
    echo "Deteniendo y eliminando contenedores..."
    docker stop $(docker ps -aq) 2>/dev/null || true
    docker rm $(docker ps -aq) 2>/dev/null || true

    echo "Eliminando todas las imágenes..."
    docker rmi $(docker images -q) --force 2>/dev/null || true

    montar_proyecto
}

levantar_silencioso() {
    echo "Levantando proyecto en modo silencioso..."
    docker compose up -d --build
}

eliminar_contenedores_volumenes() {
    echo "Eliminando contenedores y volúmenes..."
    docker compose down -v
}

comprobar_estado() {
    echo "Estado de los contenedores:"
    docker ps -a
}

limpiar_base_datos() {
    echo "Ejecutando limpieza de la base de datos..."
    python3 limpiar_base.py
}

while true; do
    mostrar_menu
    read opcion
    case $opcion in
        1) montar_proyecto ;;
        2) resetear_proyecto ;;
        3) levantar_silencioso ;;
        4) eliminar_contenedores_volumenes ;;
        5) comprobar_estado ;;
        6) limpiar_base_datos ;;
        7) echo "Saliendo..."; exit 0 ;;
        *) echo "Opción inválida. Intenta de nuevo." ;;
    esac
done
