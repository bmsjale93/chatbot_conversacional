from core.conversation_controller import gestionar_mensaje
from core.score_manager import obtener_puntuaciones
import uuid


def test_conversacion_completa_con_empatia():
    print("\n🚀 Iniciando simulación con nodos de empatía y aclaración...\n")

    session_id = str(uuid.uuid4())

    # Flujo conversacional completo simulando correctamente cada fase
    mensajes = [
        # Fase de presentación y consentimiento
        ("Hola", "consentimiento"),
        ("Sí, quiero continuar", "preguntar_nombre"),
        # Progreso normal
        ("Lucía", "preguntar_identidad"),
        ("Femenino", "inicio_exploracion_tristeza"),
        ("Sí, últimamente me siento triste", "preguntar_frecuencia"),
        ("no lo sé", "preguntar_frecuencia"),  # Ambigua -> aclaración
        ("Todos los días", "preguntar_duracion"),
        ("Unas horas", "preguntar_intensidad"),
        ("9", "fin")
    ]

    for idx, (mensaje, estado_esperado) in enumerate(mensajes, 1):
        print(f"\n📨 [{idx}] Usuario dice: {mensaje}")
        respuesta = gestionar_mensaje(session_id, mensaje)
        print(f"🤖 Asistente responde: {respuesta['mensaje']}")
        print(f"📌 Estado: {respuesta['estado']}")
        assert respuesta[
            "estado"] == estado_esperado, f"❌ Estado inesperado: se esperaba {estado_esperado}"

        if respuesta.get("estado") == "fin":
            print("\n✅ Conversación finalizada correctamente.\n")
            break

    # ✅ Verificación de puntuación emocional acumulada
    puntuacion = obtener_puntuaciones(session_id)
    print("🧠 Puntuación emocional detectada:")
    print(puntuacion)

    assert "frecuencia" in puntuacion
    assert "duracion" in puntuacion
    assert "intensidad" in puntuacion
    assert "total" in puntuacion
    assert puntuacion["total"] >= 5, "❌ Puntuación acumulada inesperadamente baja"
    print("✅ Puntuación registrada correctamente.")

    print("🎯 Simulación completa de conversación con empatía y puntuación finalizada.\n")


if __name__ == "__main__":
    test_conversacion_completa_con_empatia()
