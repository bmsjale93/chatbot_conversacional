#!/bin/bash

# ===============================================
# Lanzador de tests de la plataforma NLP
# ===============================================

# Directorios
REPORTS_DIR="test_reports"
HISTORICO="$REPORTS_DIR/historico_tests.csv"

# Crear carpeta de reportes si no existe
mkdir -p "$REPORTS_DIR"

# Formatear fecha y hora para el nombre del archivo de reporte
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVO="$REPORTS_DIR/test_report_${FECHA}.txt"

echo ""
echo "=============================================="
echo "🚀 Iniciando ejecución de todos los tests..."
echo "Los resultados se guardarán en: $ARCHIVO"
echo "=============================================="
echo ""

# Variables para métricas
TOTAL_TESTS=0
TESTS_OK=0
TESTS_FAIL=0

# Redirigir toda la salida (stdout y stderr) al archivo
{
    echo "=============================================="
    echo "📋 Resultados de la ejecución de tests"
    echo "Fecha y hora: $(date)"
    echo "=============================================="
    echo ""

    declare -a TESTS=(
        "tests.test_cleaner"
        "tests.test_processor"
        "tests.test_cache"
        "tests.test_emotion_model"
        "tests.test_security"
        "tests.test_response_save"
        "tests.test_dialog_manager"
        "tests.test_intent_detector"
        "tests.test_conversation_controller"
        "tests.test_conversation_state"
        "tests.test_conversation_simulation"
    )

    for TEST in "${TESTS[@]}"; do
        echo "----------------------------------------------"
        echo "🔎 Ejecutando: $TEST"
        echo "----------------------------------------------"
        docker exec -i nlp_service python -m "$TEST"

        if [ $? -eq 0 ]; then
            echo "✅ $TEST ejecutado correctamente."
            ((TESTS_OK++))
        else
            echo "❌ Error al ejecutar $TEST."
            ((TESTS_FAIL++))
        fi
        ((TOTAL_TESTS++))
        echo ""
    done

    echo "=============================================="
    echo "✅ Todos los tests procesados."
    echo "=============================================="
} &> "$ARCHIVO"

# ----------------------------------------------
# NUEVA PARTE: Registrar en el contenedor
# ----------------------------------------------

# Crear histórico si no existe en Docker
docker exec nlp_service bash -c "
    mkdir -p /app/test_reports &&
    if [ ! -f /app/test_reports/historico_tests.csv ]; then
        echo 'fecha,total_tests,tests_ok,tests_fail' > /app/test_reports/historico_tests.csv
    fi
"

# Añadir nueva línea
docker exec nlp_service bash -c "
    echo '$(date +"%Y-%m-%d %H:%M:%S"),$TOTAL_TESTS,$TESTS_OK,$TESTS_FAIL' >> /app/test_reports/historico_tests.csv
"

# ----------------------------------------------
# Generar gráfica
# ----------------------------------------------

echo ""
echo "----------------------------------------------"
echo "📈 Generando gráfica de evolución de tests..."
echo "----------------------------------------------"

docker exec -i nlp_service python scripts/generar_grafica_tests.py

echo ""
echo "=============================================="
echo "✅ Finalizado. Consulta:"
echo "   - Informe individual: $ARCHIVO"
echo "   - Histórico de tests: (dentro de contenedor) /app/test_reports/historico_tests.csv"
echo "   - Gráfica evolución: (dentro de contenedor) /app/test_reports/historico_tests.png"
echo "=============================================="
