import uuid
import time
from pymongo import MongoClient
from core.database import guardar_interaccion_completa
from core.score_manager import eliminar_puntuaciones

# Configuración de conexión a MongoDB
MONGO_URL = "mongodb://db:27017"
DB_NAME = "chatbot"
COLLECTION_NAME = "historial"


def obtener_coleccion():
    cliente = MongoClient(MONGO_URL)
    return cliente[DB_NAME][COLLECTION_NAME]


def test_guardado_interacciones_conversacion():
    print("\n🚀 Iniciando test de guardado completo de conversación...")

    session_id = str(uuid.uuid4())
    coleccion = obtener_coleccion()

    # Eliminar previos por seguridad
    coleccion.delete_many({"session_id": session_id})

    # Simulamos 3 interacciones de conversación
    guardar_interaccion_completa(
        session_id, "preguntar_nombre", "¿Con qué nombre?", "Lucía", "neutral", 0)
    guardar_interaccion_completa(
        session_id, "preguntar_duracion", "¿Cuánto tiempo dura?", "Unas horas", "negativo", 3)
    guardar_interaccion_completa(
        session_id, "preguntar_intensidad", "¿Nivel del 1 al 10?", "7", "negativo", 5)

    # Esperamos a que MongoDB registre todo
    time.sleep(1)

    # Buscamos por session_id
    resultados = list(coleccion.find({"session_id": session_id}))
    assert len(
        resultados) == 3, f"❌ Se esperaban 3 documentos, encontrados {len(resultados)}."

    for doc in resultados:
        assert "estado" in doc
        assert "pregunta" in doc
        assert "respuesta_usuario" in doc
        assert "timestamp" in doc
        assert "puntuacion" in doc
        print(f"✅ Registro encontrado en estado: {doc['estado']}")

    # Limpiar
    coleccion.delete_many({"session_id": session_id})
    eliminar_puntuaciones(session_id)

    print("🎯 Test de guardado de conversación completado correctamente.\n")


if __name__ == "__main__":
    test_guardado_interacciones_conversacion()
