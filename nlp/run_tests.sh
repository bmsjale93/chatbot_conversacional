#!/bin/bash

# ===============================================
# Lanzador de tests de la plataforma NLP
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
        "tests.test_score_manager"
        "tests.test_puntuacion"
        "tests.test_empathy_utils"
        "tests.test_conversacion_empatica"
        "tests.test_guardado_conversacion"
        "tests.test_evaluacion_final"
        "tests.test_flujo_completo"
    )

    # Descripciones paralelas
    declare -a DESCRIPCIONES=(
        "✔️ Limpieza de textos. Objetivo: eliminar ruido, símbolos o espacios duplicados. Ej: '¡Hola!' → 'hola'"
        "✔️ Procesamiento del mensaje. Normalización, tokenización y lematización del input."
        "✔️ Verificación de funcionamiento de la caché (Redis). Comprobar que guarda y recupera."
        "✔️ Evaluación del modelo de emociones (BERT). Se prueba si detecta emociones como 'feliz', 'triste', etc."
        "✔️ Detección de lenguaje inapropiado. Ejemplo: 'odio' → bloqueado"
        "✔️ Guarda en MongoDB un mensaje, la emoción detectada y la respuesta."
        "✔️ Coordinación del flujo de conversación. Prueba respuestas y transiciones entre estados."
        "✔️ Detecta la intención del usuario. Ej: 'Gracias' → intención: 'agradecer'"
        "✔️ Controlador maestro de diálogo. Dirige el flujo según contexto y fase."
        "✔️ Gestión de estado conversacional en Redis (cargar, guardar, borrar)."
        "✔️ Simula una conversación completa con el asistente, de principio a fin."
        "✔️ Gestión de puntuación emocional. Asigna valores numéricos a cada respuesta."
        "✔️ Test de puntuación acumulada. Verifica el total final generado."
        "✔️ Test de funciones de empatía y aclaración. Verifica si el sistema identifica respuestas ambiguas ('no sé', 'quizás') y genera respuestas empáticas adaptadas. Ejemplo: 'no lo sé' → respuesta aclaratoria."
        "✔️ Simulación completa de una conversación real que incluye una respuesta ambigua del usuario. Se espera que el sistema interrumpa el flujo para aclarar la pregunta antes de continuar. Además, verifica que la puntuación emocional final se calcule y almacene correctamente."
        "✔️ Verifica que las interacciones relevantes se registran correctamente en MongoDB. Se simulan varias preguntas/respuestas con puntuaciones acumuladas y se comprueba que todos los campos obligatorios se han guardado."
        "✔️ Verifica el cierre emocional del flujo de conversación. Se evalúa el resumen emocional, la percepción de empatía y el correcto almacenamiento en MongoDB."
        "✔️ Verifica todo el flujo conversacional: entrada de mensaje, gestión por controlador, puntuación, almacenamiento en Redis y MongoDB. Certifica el funcionamiento final de todo el sistema."
    )

    # Iterar sobre los tests
    for i in "${!TESTS[@]}"; do
        TEST="${TESTS[$i]}"
        DESCRIP="${DESCRIPCIONES[$i]}"

        echo "----------------------------------------------"
        echo "🔎 Ejecutando: $TEST"
        echo "🧠 Descripción: $DESCRIP"
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

# Guardar histórico dentro del contenedor
docker exec nlp_service bash -c "
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
docker exec -i nlp_service python scripts/generar_grafica_tests.py

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