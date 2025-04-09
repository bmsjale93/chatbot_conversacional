#!/bin/bash

# Crear carpeta tests/ si no existe (en el raíz del proyecto)
mkdir -p ../tests

# Formatear fecha y hora para nombre de archivo
FECHA=$(date +"%Y-%m-%d_%H:%M:%S")
ARCHIVO="../tests/test_${FECHA}.txt"

echo ""
echo "==============================="
echo " Ejecutando todos los tests... "
echo "==============================="
echo ""
echo "Los resultados se guardarán en: $ARCHIVO"
echo ""

# Redirigir la salida estándar y de error al archivo
{
    echo "==============================="
    echo "     Resultados de Tests"
    echo "Fecha y hora: $(date)"
    echo "==============================="

    echo ""
    echo ">> Ejecutando test_cleaner"
    docker exec -i nlp_service python -m tests.test_cleaner

    echo ""
    echo ">> Ejecutando test_processor"
    docker exec -i nlp_service python -m tests.test_processor

    echo ""
    echo ">> Ejecutando test_cache"
    docker exec -i nlp_service python -m tests.test_cache

    echo ""
    echo ">> Ejecutando test_emotion_model"
    docker exec -i nlp_service python -m tests.test_emotion_model

    echo ""
    echo ">> Ejecutando test_security"
    docker exec -i nlp_service python -m tests.test_security

    echo ""
    echo ">> Ejecutando test_response_save"
    docker exec -i nlp_service python -m tests.test_response_save

    echo ""
    echo "==============================="
    echo " Todos los tests ejecutados ✅ "
    echo "==============================="
} &> "$ARCHIVO"

echo ""
echo "==============================="
echo " Todos los tests ejecutados ✅ "
echo "Resultados guardados en: $ARCHIVO"
echo "==============================="