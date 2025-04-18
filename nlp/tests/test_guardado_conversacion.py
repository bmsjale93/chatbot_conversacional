import uuid
import time
from pymongo import MongoClient
from core.database import guardar_interaccion_completa
from core.score_manager import eliminar_puntuaciones, asignar_puntuacion

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

    # Limpiar cualquier documento anterior por seguridad
    coleccion.delete_many({"session_id": session_id})

    # Simulamos que el usuario ha recibido puntuaciones
    asignar_puntuacion(session_id, "frecuencia", "todos los días")  # 3
    asignar_puntuacion(session_id, "duracion", "unas horas")        # 1
    asignar_puntuacion(session_id, "intensidad", "7")               # 2

    # Simulamos el guardado de interacciones reales
    guardar_interaccion_completa(session_id, "preguntar_frecuencia",
                                 "¿Con qué frecuencia sientes tristeza?", "Todos los días")
    guardar_interaccion_completa(session_id, "preguntar_duracion",
                                 "¿Cuánto tiempo dura?", "Unas horas")
    guardar_interaccion_completa(session_id, "preguntar_intensidad",
                                 "¿Nivel del 1 al 10?", "7")

    # Esperamos a que se guarde en MongoDB
    time.sleep(1)

    # Verificamos que los documentos estén correctamente guardados
    resultados = list(coleccion.find({"session_id": session_id}))
    assert len(
        resultados) == 3, f"❌ Se esperaban 3 documentos, encontrados {len(resultados)}."

    for doc in resultados:
        print(f"✅ Registro verificado: estado = {doc['estado']}")
        assert "pregunta" in doc
        assert "respuesta_usuario" in doc
        assert "emocion" in doc
        assert doc["emocion"] in ["negativo", "neutro", "positivo"], f"❌ Emoción no válida: {doc['emocion']}"
        assert "puntuacion" in doc
        assert isinstance(doc["puntuacion"], int)
        assert "timestamp" in doc

    # Limpiar datos de prueba
    coleccion.delete_many({"session_id": session_id})
    eliminar_puntuaciones(session_id)

    print("🎯 Test de guardado de conversación con emoción completado correctamente.\n")


if __name__ == "__main__":
    test_guardado_interacciones_conversacion()
