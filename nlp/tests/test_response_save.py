import os
import sys
import time
from datetime import datetime
from pymongo import MongoClient
from core.response_generator import generar_respuesta

# Aseguramos que la raíz esté en el path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Configuración de conexión a MongoDB
MONGO_URL = os.getenv("DATABASE_URL", "mongodb://db:27017")
NOMBRE_DB = "chatbot"
NOMBRE_COLECCION = "historial"


def conectar_mongo():
    """Conectar a MongoDB y devolver la colección."""
    try:
        cliente = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        cliente.server_info()  # Validamos conexión
        return cliente[NOMBRE_DB][NOMBRE_COLECCION]
    except Exception as e:
        print(f"[❌ ERROR] No se pudo conectar a MongoDB: {e}")
        return None


def imprimir_resultado(doc: dict):
    """Mostrar bonito el contenido de un documento recuperado."""
    print("\n--- Registro guardado en MongoDB ---")
    print(
        f"📝 Mensaje Usuario: {doc.get('mensaje_usuario', '[No encontrado]')}")
    print(
        f"💬 Respuesta Sistema: {doc.get('respuesta_sistema', '[No encontrado]')}")
    print(f"🎭 Emoción Detectada: {doc.get('emocion', '[No encontrado]')}")
    print(f"🕓 Fecha/Hora UTC: {doc.get('timestamp', '[No encontrado]')}")
    print("------------------------------------------\n")


def test_guardar_respuesta():
    """Test para verificar el guardado de una respuesta en MongoDB."""
    print("\n🚀 Iniciando test de guardado en MongoDB...")

    coleccion = conectar_mongo()
    if coleccion is None:
        print("[❌ ERROR] Sin acceso a base de datos. Test cancelado.")
        return

    # Texto de prueba
    texto_prueba = "Hoy me siento feliz de lograr mis metas."

    # Generamos una respuesta simulada
    resultado = generar_respuesta(texto_prueba)

    # Esperamos un poco por seguridad
    time.sleep(2)

    # Buscamos el último documento guardado
    doc = coleccion.find_one(
        {"mensaje_usuario": texto_prueba},
        sort=[("_id", -1)]
    )

    if doc:
        imprimir_resultado(doc)
        print("[✅ OK] Registro encontrado y verificado en MongoDB.")
    else:
        print("[❌ ERROR] No se encontró el mensaje en la base de datos.")


# Ejecutamos si se corre directamente
if __name__ == "__main__":
    test_guardar_respuesta()
    print("\n🎯 Test de MongoDB completado.\n")
