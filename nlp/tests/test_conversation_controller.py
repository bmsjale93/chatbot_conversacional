from core.conversation_controller import gestionar_mensaje
from core.conversation_state import guardar_estado_usuario, borrar_estado_usuario
import uuid

# Usamos un session_id único para todos los tests
SESSION_ID = str(uuid.uuid4())


def inicializar_estado(estado_actual="presentacion", datos=None):
    """Crea o resetea el estado en Redis para cada test."""
    guardar_estado_usuario(SESSION_ID, {
        "estado_actual": estado_actual,
        "datos_guardados": datos or {}
    })


def test_flujo_presentacion_afirmativo():
    print("🔎 Test: Flujo presentación - respuesta afirmativa...")
    inicializar_estado("presentacion")
    gestionar_mensaje(SESSION_ID, "Hola")
    inicializar_estado("consentimiento")
    respuesta = gestionar_mensaje(SESSION_ID, "Sí, quiero continuar")
    assert respuesta["estado"] == "preguntar_nombre", "❌ Debería pasar a preguntar nombre."
    print("✅ Flujo presentación afirmativo correcto.")


def test_flujo_presentacion_negativo():
    print("🔎 Test: Flujo presentación - respuesta negativa...")
    inicializar_estado("consentimiento")
    respuesta = gestionar_mensaje(SESSION_ID, "No deseo continuar")
    assert respuesta["estado"] == "fin", "❌ Debería finalizar la conversación."
    print("✅ Flujo presentación negativo correcto.")


def test_flujo_nombre_proporcionado():
    print("🔎 Test: Flujo pedir nombre...")
    inicializar_estado("preguntar_nombre")
    respuesta = gestionar_mensaje(SESSION_ID, "Alex")
    assert respuesta["estado"] == "preguntar_identidad", "❌ Debería pasar a preguntar identidad."
    print("✅ Flujo pedir nombre correcto.")


def test_flujo_identidad_proporcionada():
    print("🔎 Test: Flujo pedir identidad...")
    inicializar_estado("preguntar_identidad", {"nombre_usuario": "Alex"})
    respuesta = gestionar_mensaje(SESSION_ID, "Masculino")
    assert respuesta["estado"] == "inicio_exploracion_tristeza", "❌ Debería pasar a inicio exploración tristeza."
    print("✅ Flujo pedir identidad correcto.")


def test_flujo_inicio_exploracion_afirmativo():
    print("🔎 Test: Inicio exploración tristeza - afirmativo...")
    inicializar_estado("inicio_exploracion_tristeza",
                       {"nombre_usuario": "Alex"})
    respuesta = gestionar_mensaje(SESSION_ID, "Sí, me he sentido triste")
    assert respuesta["estado"] == "preguntar_frecuencia", "❌ Debería pasar a preguntar frecuencia."
    print("✅ Flujo exploración tristeza afirmativo correcto.")


def test_flujo_inicio_exploracion_negativo():
    print("🔎 Test: Inicio exploración tristeza - negativo...")
    inicializar_estado("inicio_exploracion_tristeza",
                       {"nombre_usuario": "Alex"})
    respuesta = gestionar_mensaje(SESSION_ID, "No, no estoy triste")
    assert respuesta["estado"] == "fin", "❌ Debería finalizar la conversación."
    print("✅ Flujo exploración tristeza negativo correcto.")


def test_flujo_frecuencia_a_duracion():
    print("🔎 Test: Frecuencia -> Duración...")
    inicializar_estado("preguntar_frecuencia")
    respuesta = gestionar_mensaje(SESSION_ID, "Todos los días")
    assert respuesta["estado"] == "preguntar_duracion", "❌ Debería pasar a preguntar duración."
    print("✅ Flujo frecuencia -> duración correcto.")


def test_flujo_duracion_a_intensidad():
    print("🔎 Test: Duración -> Intensidad...")
    inicializar_estado("preguntar_duracion")
    respuesta = gestionar_mensaje(SESSION_ID, "Dura varias horas")
    assert respuesta["estado"] == "preguntar_intensidad", "❌ Debería pasar a preguntar intensidad."
    print("✅ Flujo duración -> intensidad correcto.")


def test_flujo_finalizacion():
    print("🔎 Test: Finalización conversación...")

    # 1. Desde intensidad hasta mostrar resumen
    inicializar_estado("preguntar_intensidad")
    respuesta = gestionar_mensaje(SESSION_ID, "8")
    assert respuesta["estado"] == "mostrar_resumen", "❌ Debería pasar a mostrar_resumen."

    # 2. Desde mostrar resumen hasta preguntar empatía
    respuesta = gestionar_mensaje(SESSION_ID, "Ok")
    assert respuesta["estado"] == "preguntar_empatia", "❌ Debería pasar a preguntar_empatia."

    # 3. Desde preguntar empatía hasta cierre_final
    respuesta = gestionar_mensaje(SESSION_ID, "9")
    assert respuesta["estado"] == "cierre_final", "❌ Debería finalizar la conversación."

    print("✅ Flujo finalización completo correcto.")


if __name__ == "__main__":
    print("\n🚀 Iniciando tests de Conversation Controller...\n")
    test_flujo_presentacion_afirmativo()
    test_flujo_presentacion_negativo()
    test_flujo_nombre_proporcionado()
    test_flujo_identidad_proporcionada()
    test_flujo_inicio_exploracion_afirmativo()
    test_flujo_inicio_exploracion_negativo()
    test_flujo_frecuencia_a_duracion()
    test_flujo_duracion_a_intensidad()
    test_flujo_finalizacion()
    print("\n🎯 Todos los tests de Conversation Controller pasaron correctamente.\n")
    borrar_estado_usuario(SESSION_ID)
