import uuid
import time
from core.conversation_controller import gestionar_mensaje
from core.score_manager import obtener_puntuaciones
from core.conversation_state import obtener_estado_usuario, borrar_estado_usuario
from pymongo import MongoClient

MONGO_URL = "mongodb://db:27017"
DB_NAME = "chatbot"
COLLECTION = "historial"

# Flujo completo esperado con estados finales tras cada mensaje
FLUJO_COMPLETO = [
    ("Hola", "consentimiento"),
    ("Sí, quiero continuar", "preguntar_nombre"),
    ("Lucía", "preguntar_identidad"),
    ("Femenino", "inicio_exploracion_tristeza"),
    ("Sí, últimamente me siento triste", "preguntar_frecuencia"),
    ("Todos los días", "preguntar_duracion"),
    ("Unas horas", "preguntar_intensidad"),
    ("9", "mostrar_resumen"),
    ("", "preguntar_empatia"),
    ("7", "cierre_final")
]

def obtener_documentos_mongo(session_id):
    cliente = MongoClient(MONGO_URL)
    return list(cliente[DB_NAME][COLLECTION].find({"session_id": session_id}))

def test_flujo_completo_integrado():
    print("\n🚀 Iniciando test de flujo completo del proyecto...\n")

    session_id = str(uuid.uuid4())
    for idx, (mensaje, estado_esperado) in enumerate(FLUJO_COMPLETO, 1):
        print(f"📨 [{idx}] Usuario dice: {mensaje}")
        respuesta = gestionar_mensaje(session_id, mensaje)
        print(f"🤖 Asistente responde: {respuesta['mensaje']}")
        print(f"📌 Estado recibido: {respuesta['estado']} (esperado: {estado_esperado})")
        assert respuesta["estado"] == estado_esperado, f"❌ Estado inesperado: {respuesta['estado']}"

    # Verificar puntuación emocional final
    puntuaciones = obtener_puntuaciones(session_id)
    print(f"\n📊 Puntuación final acumulada: {puntuaciones}")
    assert puntuaciones["total"] > 0, "❌ La puntuación final debería ser mayor que cero"

    # Verificar estado en Redis
    estado = obtener_estado_usuario(session_id)
    assert estado["estado_actual"] == "cierre_final", "❌ El estado final en Redis no coincide"
    print("✅ Estado final en Redis verificado.")

    # Verificar registros en MongoDB
    time.sleep(1)
    registros = obtener_documentos_mongo(session_id)
    assert len(registros) >= 5, f"❌ Se esperaban al menos 5 interacciones, se encontraron {len(registros)}"
    for doc in registros:
        assert "estado" in doc
        assert "emocion" in doc
        assert doc["emocion"] in ["positivo", "neutro", "negativo"], f"❌ Emoción no válida: {doc['emocion']}"
        assert "puntuacion" in doc
    print("✅ Registros en MongoDB verificados.")

    # Limpiar estado de Redis
    borrar_estado_usuario(session_id)

    print("\n🎯 Test de flujo completo del proyecto finalizado correctamente.\n")

if __name__ == "__main__":
    test_flujo_completo_integrado()
