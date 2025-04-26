#!/bin/bash

# ===============================================
# Lanzador maestro de tests para Frontend y NLP
# ===============================================

INICIO_GLOBAL=$(date +%s)

# Función para lanzar un grupo de tests
lanzar_tests() {
    local nombre="$1"
    local path="$2"
    local script="$path/run_tests.sh"

    echo ""
    echo "=============================================="
    echo "🚀 Lanzando tests de $nombre..."
    echo "Ruta: $script"
    echo "=============================================="
    echo ""

    if [ -d "$path" ]; then
        if [ -f "$script" ]; then
            bash "$script"
            RESULTADO=$?
            if [ $RESULTADO -eq 0 ]; then
                echo "✅ Tests de $nombre completados correctamente."
            else
                echo "❌ Tests de $nombre con errores."
            fi
        else
            echo "⚠️ No se encontró el script de tests en: $script"
        fi
    else
        echo "⚠️ No se encontró el directorio: $path"
    fi
}

# Lanzar tests del Frontend
lanzar_tests "FRONTEND" "frontend"

# Lanzar tests del NLP
lanzar_tests "NLP" "nlp"

FIN_GLOBAL=$(date +%s)
DURACION_GLOBAL=$((FIN_GLOBAL - INICIO_GLOBAL))

echo ""
echo "=============================================="
echo "🎯 Ejecución completa de todos los tests"
echo "🕒 Duración total: ${DURACION_GLOBAL}s"
echo "=============================================="
