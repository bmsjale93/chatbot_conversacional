# nlp/tests/test_cache.py

from core.cache import redis_client, obtener_cache, guardar_cache
import sys
import os
import time
import json

# Añadimos la carpeta raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def test_cache_redis():
    print("\n==============================================")
    print("🚀 Iniciando Test de Funcionalidad de Redis...")
    print("==============================================\n")

    if redis_client is None:
        print("[❌ ERROR] No hay conexión disponible a Redis. Test cancelado.\n")
        return

    # Definimos los datos de prueba
    texto_prueba = "Estoy muy contento con los resultados."
    respuesta_prueba = {
        "estado_emocional": "positivo",
        "respuesta": "¡Me alegra saberlo! Cuéntame más si quieres."
    }

    print("[1] Guardando entrada de prueba en Redis...")
    guardar_cache(texto_prueba, respuesta_prueba, expiracion_segundos=60)

    # Esperamos un momento para asegurar que el guardado sea correcto
    time.sleep(1)

    print("[2] Recuperando entrada guardada desde Redis...")
    resultado = obtener_cache(texto_prueba)

    if resultado is None:
        print("[❌ FALLO] No se pudo recuperar el valor desde Redis.\n")
    else:
        print("\n✅ Registro Recuperado Correctamente:")
        print(f"- Texto Original: {texto_prueba}")
        print(f"- Estado Emocional: {resultado.get('estado_emocional')}")
        print(f"- Respuesta Sugerida: {resultado.get('respuesta')}")
        print("----------------------------------------------")

        # Comprobaciones adicionales
        assert resultado.get(
            "estado_emocional") == respuesta_prueba["estado_emocional"], "[❌ FALLO] Estado emocional no coincide."
        assert resultado.get(
            "respuesta") == respuesta_prueba["respuesta"], "[❌ FALLO] Respuesta sugerida no coincide."

        print("\n🎯 Todas las comprobaciones fueron exitosas. Redis funcionando correctamente.\n")


if __name__ == "__main__":
    test_cache_redis()
