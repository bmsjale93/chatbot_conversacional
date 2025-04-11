import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from core.response_generator import generar_respuesta
from core.database import guardar_interaccion

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
NOMBRE_DB = "chatbot"
NOMBRE_COLECCION = "historial"


def conectar_mongo():
    try:
        cliente = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        cliente.server_info()
        return cliente[NOMBRE_DB][NOMBRE_COLECCION]
    except Exception as e:
        print(f"[❌ ERROR] No se pudo conectar a MongoDB: {e}")
        return None


def imprimir_resultado(doc: dict):
    print("\n--- Registro guardado en MongoDB ---")
    print(
        f"📝 Mensaje Usuario: {doc.get('mensaje_usuario', '[No encontrado]')}")
    print(
        f"💬 Respuesta Sistema: {doc.get('respuesta_sistema', '[No encontrado]')}")
    print(f"🎭 Emoción Detectada: {doc.get('emocion', '[No encontrado]')}")
    print(f"🕓 Fecha/Hora UTC: {doc.get('timestamp', '[No encontrado]')}")
    print("------------------------------------------\n")


def test_guardar_respuesta():
    print("\n🚀 Iniciando test de guardado en MongoDB...")

    coleccion = conectar_mongo()
    if coleccion is None:
        print("[❌ ERROR] Sin acceso a base de datos. Test cancelado.")
        return

    texto_prueba = "Hoy me siento feliz de lograr mis metas."

    # Generamos respuesta simulada
    resultado = generar_respuesta(texto_prueba)

    # Guardamos manualmente indicando que también guarde el texto original
    guardar_interaccion(
        texto_prueba,
        resultado.get("respuesta"),
        resultado.get("estado_emocional"),
        guardar_texto_original=True  # ¡Aquí el cambio importante!
    )

    # Esperamos un poco para asegurar persistencia
    time.sleep(2)

    # Buscamos por el texto original
    doc = coleccion.find_one(
        {"mensaje_usuario": texto_prueba},
        sort=[("_id", -1)]
    )

    if doc:
        imprimir_resultado(doc)
        print("[✅ OK] Registro encontrado y verificado en MongoDB.")
    else:
        print("[❌ ERROR] No se encontró el mensaje en la base de datos.")


if __name__ == "__main__":
    test_guardar_respuesta()
    print("\n🎯 Test de MongoDB completado.\n")
