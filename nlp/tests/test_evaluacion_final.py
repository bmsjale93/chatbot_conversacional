import uuid
import time
from pymongo import MongoClient
from core.score_manager import eliminar_puntuaciones
from core.conversation_flow import procesar_mensaje

MONGO_URL = "mongodb://db:27017"
DB_NAME = "chatbot"
COLLECTION_NAME = "historial"


def obtener_coleccion():
    cliente = MongoClient(MONGO_URL)
    return cliente[DB_NAME][COLLECTION_NAME]


def test_evaluacion_final_con_almacenamiento():
    print("\n🧪 Test: Evaluación final y retroalimentación emocional")

    session_id = str(uuid.uuid4())
    datos = {}

    # Limpiar registros previos
    coleccion = obtener_coleccion()
    coleccion.delete_many({"session_id": session_id})
    eliminar_puntuaciones(session_id)

    pasos = [
        ("preguntar_frecuencia", "Todos los días"),
        ("preguntar_duracion", "Unas horas"),
        ("preguntar_intensidad", "8"),
        ("mostrar_resumen", ""),
        ("preguntar_empatia", "9")
    ]

    estado = "preguntar_frecuencia"

    for paso_estado, respuesta in pasos:
        salida, datos = procesar_mensaje(session_id, respuesta, estado, datos)
        estado = salida["estado"]
        print(
            f"✅ [{paso_estado}] → Usuario: '{respuesta}' → Bot: '{salida['mensaje'][:60]}...'")

    time.sleep(1)

    resultados = list(coleccion.find({"session_id": session_id}))
    assert len(
        resultados) >= 3, "❌ No se han registrado correctamente las interacciones."

    resumen = datos.get("resumen", {})
    assert resumen.get("evaluacion") in [
        "leve", "moderado", "grave"], "❌ Evaluación no generada."

    empatia = datos.get("valoracion_empatia", -1)
    assert isinstance(
        empatia, int) and 0 <= empatia <= 10, "❌ Valoración de empatía no válida."

    print("🎯 Test de evaluación emocional final completado con éxito.")

    coleccion.delete_many({"session_id": session_id})
    eliminar_puntuaciones(session_id)


if __name__ == "__main__":
    test_evaluacion_final_con_almacenamiento()
