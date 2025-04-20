#!/bin/bash

# ===============================================
# Lanzador de tests del Frontend Gradio
# ===============================================
INICIO=$(date +%s)

# Directorios
REPORTS_DIR="test_reports"
HISTORICO="$REPORTS_DIR/historico_tests.csv"

# Crear carpeta de reportes si no existe
mkdir -p "$REPORTS_DIR"

# Fecha para informe
FECHA=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVO="$REPORTS_DIR/test_report_${FECHA}.txt"

echo ""
echo "=============================================="
echo "🚀 Iniciando ejecución de todos los tests..."
echo "Los resultados se guardarán en: $ARCHIVO"
echo "=============================================="
echo ""

# Variables de métricas
TOTAL_TESTS=0
TESTS_OK=0
TESTS_FAIL=0

# Redirigir la salida completa al archivo de log
{
    echo "=============================================="
    echo "📋 Resultados de la ejecución de tests"
    echo "Fecha y hora: $(date)"
    echo "=============================================="
    echo ""

    # Array de tests
    declare -a TESTS=(
        "tests.test_conexion_gradio"
        "tests.test_gradio_integration"
        "tests.test_gestionar_conversacion"
    )

    # Descripciones paralelas
    declare -a DESCRIPCIONES=(
        "✔️ Verifica que el frontend puede comunicarse con el backend correctamente."
        "✔️ Verifica que el flujo completo Gradio ↔ Backend funciona según lo esperado."
        "✔️ Verifica que el backend procese correctamente una conversación completa usando gestionar_mensaje(). Simula un flujo real desde el frontend y comprueba la estructura de la respuesta: mensaje, estado y sugerencias."
    )

    # Iterar sobre los tests
    for i in "${!TESTS[@]}"; do
        TEST="${TESTS[$i]}"
        DESCRIP="${DESCRIPCIONES[$i]}"

        echo "----------------------------------------------"
        echo "🔎 Ejecutando: $TEST"
        echo "🧠 Descripción: $DESCRIP"
        echo "----------------------------------------------"

        docker exec -i frontend_gradio python -m "$TEST"

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

# Guardar histórico dentro del contenedor
docker exec frontend_gradio bash -c "
    mkdir -p /app/test_reports &&
    if [ ! -f /app/test_reports/historico_tests.csv ]; then
        echo 'fecha,total_tests,tests_ok,tests_fail' > /app/test_reports/historico_tests.csv
    fi
    echo '$(date +"%Y-%m-%d %H:%M:%S"),$TOTAL_TESTS,$TESTS_OK,$TESTS_FAIL' >> /app/test_reports/historico_tests.csv
"

# Generar gráfica
echo ""
echo "----------------------------------------------"
echo "📈 Generando gráfica de evolución de tests..."
echo "----------------------------------------------"
docker exec -i frontend_gradio python scripts/generar_grafica_tests.py

# Mensaje final
echo ""
echo "=============================================="
echo "✅ Finalizado. Consulta:"
echo "   - Informe individual: $ARCHIVO"
echo "   - Histórico de tests: /app/test_reports/historico_tests.csv"
echo "   - Gráfica evolución:  /app/test_reports/historico_tests.png"
echo "=============================================="

FIN=$(date +%s)
DURACION=$((FIN - INICIO))
echo "🕒 Duración total de tests: ${DURACION}s"
