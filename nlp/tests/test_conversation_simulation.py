from core.conversation_controller import gestionar_mensaje
import uuid


def test_conversacion_completa():
    print("\n🚀 Iniciando simulación completa de conversación...\n")

    # Generamos un ID de sesión único para no interferir con otras sesiones
    session_id = str(uuid.uuid4())

    # PASO 1: El primer mensaje simplemente inicia la presentación
    print("\n📨 [0] Usuario inicia conversación...")
    respuesta = gestionar_mensaje(session_id, "Hola")
    print(f"🤖 Asistente responde: {respuesta['mensaje']}")

    # Verificamos que el bot haya pasado a consentimiento
    if respuesta.get("estado") != "consentimiento":
        print("❌ Error: no se pasó correctamente a consentimiento tras la presentación.")
        return

    # PASO 2 en adelante: Mensajes simulados que enviaría un usuario
    mensajes_usuario = [
        "Sí, quiero continuar",               # Consentimiento
        "Carlos",                              # Nombre
        "Masculino",                           # Identidad
        "Sí, he estado triste",                # Exploración de tristeza
        "Casi todos los días",                 # Frecuencia
        "Unas horas",                          # Duración
        "7"                                    # Intensidad
    ]

    for idx, mensaje in enumerate(mensajes_usuario, 1):
        print(f"\n📨 [{idx}] Usuario dice: {mensaje}")
        respuesta = gestionar_mensaje(session_id, mensaje)
        print(f"🤖 Asistente responde: {respuesta['mensaje']}")

        if respuesta.get("estado") == "fin":
            print("\n✅ La conversación terminó correctamente.")
            break

    print("\n🎯 Simulación de conversación completada.\n")


# Ejecutar si se corre directamente
if __name__ == "__main__":
    test_conversacion_completa()
