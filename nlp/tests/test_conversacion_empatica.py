from core.conversation_controller import gestionar_mensaje
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

    print("🎯 Simulación completa de conversación con empatía finalizada.\n")


if __name__ == "__main__":
    test_conversacion_completa_con_empatia()
