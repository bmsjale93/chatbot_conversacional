from core.score_manager import obtener_puntuaciones, eliminar_puntuaciones
from core.conversation_flow import procesar_mensaje
import uuid


def test_integracion_flujo_con_puntuacion():
    print("\n🚀 Test integración de puntuación en flujo conversacional...\n")
    session_id = str(uuid.uuid4())
    datos = {"nombre_usuario": "Alex"}

    # Fase 1: frecuencia
    procesar_mensaje(session_id, "Todos los días",
                     "preguntar_frecuencia", datos)

    # Fase 2: duración
    procesar_mensaje(session_id, "Unas horas", "preguntar_duracion", datos)

    # Fase 3: intensidad
    procesar_mensaje(session_id, "9", "preguntar_intensidad", datos)

    # Validar resultados
    punt = obtener_puntuaciones(session_id)
    print(f"📊 Puntuaciones registradas: {punt}")
    assert punt["frecuencia"] == 3
    assert punt["duracion"] == 1
    assert punt["intensidad"] == 3
    assert punt["total"] == 7

    print("✅ Integración correcta de puntuación en el flujo conversacional.")
    eliminar_puntuaciones(session_id)


if __name__ == "__main__":
    test_integracion_flujo_con_puntuacion()
