#!/bin/bash

echo ""
echo "==============================="
echo " Ejecutando todos los tests... "
echo "==============================="

# Ejecutar cada test manualmente
docker exec -it nlp_service python -m tests.test_cleaner
docker exec -it nlp_service python -m tests.test_processor
docker exec -it nlp_service python -m tests.test_cache
docker exec -it nlp_service python -m tests.test_emotion_model
docker exec -it nlp_service python -m tests.test_security
docker exec -it nlp_service python -m tests.test_response_save

echo ""
echo "==============================="
echo " Todos los tests ejecutados ✅ "
echo "==============================="
